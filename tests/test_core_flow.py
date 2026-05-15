from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.checklist import gerar_checklist
from src.comparability import avaliar_comparabilidade
from src.db import (
    create_fonte,
    create_item,
    create_processo,
    export_snapshot,
    resumo_item,
)
from src.pricing import calcular_resumo_precos
from src.pncp import similaridade_jaccard


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

    def test_pricing_outlier_summary(self) -> None:
        resumo = calcular_resumo_precos([10, 11, 12, 100])
        self.assertEqual(resumo["outliers"], 1)
        self.assertEqual(resumo["mediana"], 11.5)

    def test_similarity_handles_accents(self) -> None:
        similaridade = similaridade_jaccard("aquisição de serviço de limpeza", "aquisicao servico limpeza predial")
        self.assertGreater(similaridade, 0.4)


if __name__ == "__main__":
    unittest.main()
