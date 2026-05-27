from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

# Set auth env vars before importing the app
os.environ.setdefault("ICARO_AUTH_USER", "admin")
os.environ.setdefault("ICARO_AUTH_PASSWORD", "icaro123")
os.environ.setdefault("ICARO_AUTH_SECRET", "test-secret")

from fastapi.testclient import TestClient

from api import app
from src.checklist import gerar_checklist
from src.comparability import avaliar_comparabilidade
from src.db import (
    create_fonte,
    create_fonte_from_pncp_rascunho,
    create_item,
    create_pncp_rascunho,
    create_processo,
    export_snapshot,
    list_fontes,
    list_pncp_rascunhos,
    resumo_item,
)
from src.pricing import calcular_resumo_precos
from src.pncp import (
    buscar_contratacoes,
    buscar_contratacoes_contextual,
    normalizar_modalidade_id,
    similaridade_jaccard,
)
from src.review import gerar_revisao_itens


class CoreFlowTest(unittest.TestCase):
    def test_item_price_basket_flow(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "icaro.sqlite3"
            processo_id = create_processo(
                {
                    "titulo": "Pesquisa material de escritorio",
                    "descricao_objeto": "Cesta de material de escritorio",
                    "responsavel": "Compras",
                },
                db_path,
            )
            item_id = create_item(
                {
                    "processo_id": processo_id,
                    "codigo": "001",
                    "descricao": "Papel A4 branco",
                    "unidade": "resma",
                    "quantidade": 100,
                },
                db_path,
            )
            create_fonte(
                {
                    "processo_id": processo_id,
                    "item_id": item_id,
                    "fonte_tipo": "pncp",
                    "descricao_item": "Papel A4 branco resma",
                    "valor_unitario": 25.0,
                    "aproveitada": True,
                },
                db_path,
            )
            create_fonte(
                {
                    "processo_id": processo_id,
                    "item_id": item_id,
                    "fonte_tipo": "fornecedor",
                    "descricao_item": "Papel A4 branco pacote",
                    "valor_unitario": 27.0,
                    "aproveitada": True,
                },
                db_path,
            )

            resumo = resumo_item(item_id, db_path)
            self.assertEqual(resumo["fontes_aproveitadas"], 2)
            self.assertEqual(resumo["preco_estimado_mediana"], 26.0)

            snapshot = export_snapshot(processo_id, db_path)
            self.assertEqual(len(snapshot["itens"]), 1)
            self.assertEqual(len(snapshot["fontes"]), 2)
            self.assertGreaterEqual(len(gerar_checklist(snapshot)), 1)
            comparabilidade = avaliar_comparabilidade(snapshot)
            self.assertEqual(comparabilidade["itens"][0]["classificacao"], "alta")

    def test_pncp_draft_can_be_reviewed_and_converted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "icaro.sqlite3"
            processo_id = create_processo(
                {"titulo": "Pesquisa TI", "descricao_objeto": "Cesta de TI"},
                db_path,
            )
            item_id = create_item(
                {
                    "processo_id": processo_id,
                    "descricao": "Notebook corporativo",
                    "termo_busca": "notebook",
                },
                db_path,
            )
            rascunho_id = create_pncp_rascunho(
                {
                    "processo_id": processo_id,
                    "item_id": item_id,
                    "objeto": "Compra de notebooks corporativos",
                    "orgao": "Orgao teste",
                    "fornecedor": "Fornecedor teste",
                    "valor_estimado": 4500,
                    "similaridade": 0.6,
                },
                db_path,
            )

            snapshot = export_snapshot(processo_id, db_path)
            revisao = gerar_revisao_itens(snapshot)
            self.assertEqual(revisao["itens"][0]["rascunhos_abertos"], 1)
            self.assertEqual(revisao["itens"][0]["status"], "pendente")

            fonte_id = create_fonte_from_pncp_rascunho(
                rascunho_id,
                {"valor_unitario": 4300, "aproveitada": True},
                db_path,
            )
            self.assertIsNotNone(fonte_id)
            self.assertEqual(list_pncp_rascunhos(processo_id, db_path=db_path)[0]["status"], "usado")
            fonte = list_fontes(processo_id, db_path=db_path)[0]
            self.assertEqual(fonte["orgao"], "Orgao teste")
            self.assertEqual(fonte["fornecedor"], "Fornecedor teste")

    def test_pricing_outlier_summary(self) -> None:
        resumo = calcular_resumo_precos([10, 11, 12, 100])
        self.assertEqual(resumo["outliers"], 1)
        self.assertEqual(resumo["mediana"], 11.5)

    def test_similarity_handles_accents(self) -> None:
        similaridade = similaridade_jaccard("aquisição de serviço de limpeza", "aquisicao servico limpeza predial")
        self.assertGreater(similaridade, 0.4)


    def test_pncp_modalidade_normalization_accepts_names(self) -> None:
        self.assertEqual(normalizar_modalidade_id("Pregão"), "6")
        self.assertEqual(normalizar_modalidade_id("Pregao Eletronico"), "6")
        self.assertEqual(normalizar_modalidade_id("Pregão Presencial"), "7")
        self.assertEqual(normalizar_modalidade_id("8"), "8")
        self.assertIsNone(normalizar_modalidade_id("modalidade inexistente"))

    def test_pncp_request_uses_modalidade_code_and_min_page_size(self) -> None:
        class FakeResponse:
            url = "https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao"

            def raise_for_status(self) -> None:
                return None

            def json(self) -> dict[str, list[dict[str, str]]]:
                return {"data": []}

        with patch("src.pncp.requests.get", return_value=FakeResponse()) as mocked_get:
            buscar_contratacoes("processador", modalidade_id="Pregão", tamanho_pagina=1)

        params = mocked_get.call_args.kwargs["params"]
        self.assertEqual(params["codigoModalidadeContratacao"], "6")
        self.assertEqual(params["tamanhoPagina"], 50)
        self.assertNotIn("q", params)

    def test_pncp_request_uses_default_modalidade_when_blank(self) -> None:
        class FakeResponse:
            url = "https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao"

            def raise_for_status(self) -> None:
                return None

            def json(self) -> dict[str, list[dict[str, str]]]:
                return {"data": []}

        with patch("src.pncp.requests.get", return_value=FakeResponse()) as mocked_get:
            buscar_contratacoes("hd 160gb", modalidade_id="", tamanho_pagina=14)

        params = mocked_get.call_args.kwargs["params"]
        self.assertEqual(params["codigoModalidadeContratacao"], "6")
        self.assertNotIn("q", params)

    def test_pncp_contextual_search_expands_ufs(self) -> None:
        with patch(
            "src.pncp.buscar_contratacoes",
            return_value={"ok": True, "resultados": []},
        ) as mocked_busca:
            buscar_contratacoes_contextual(
                "notebook",
                "notebook corporativo",
                ufs=["SP", "RJ"],
                modalidade_id="6",
                buscar_variantes=False,
            )

        ufs = [call.kwargs["uf"] for call in mocked_busca.call_args_list]
        self.assertEqual(ufs, ["SP", "RJ"])

    def test_pncp_contextual_search_uses_balanced_modalidades_when_blank(self) -> None:
        with patch(
            "src.pncp.buscar_contratacoes",
            return_value={"ok": True, "resultados": []},
        ) as mocked_busca:
            buscar_contratacoes_contextual(
                "hd 160gb",
                "hd 160gb",
                modalidade_id="",
                buscar_variantes=False,
                estrategia="equilibrada",
            )

        modalidades = [call.kwargs["modalidade_id"] for call in mocked_busca.call_args_list]
        self.assertEqual(modalidades, ["6", "8", "7", "4"])

    def test_app_requires_login_and_accepts_configured_credentials(self) -> None:
        client = TestClient(app)

        protected = client.get("/app", headers={"accept": "text/html"}, follow_redirects=False)
        self.assertEqual(protected.status_code, 303)
        self.assertEqual(protected.headers["location"], "/login")

        login = client.post(
            "/auth/login",
            data={"usuario": "admin", "senha": "icaro123"},
            follow_redirects=False,
        )
        self.assertEqual(login.status_code, 303)
        self.assertEqual(login.headers["location"], "/app")
        self.assertIn("icaro_session", login.cookies)


if __name__ == "__main__":
    unittest.main()
