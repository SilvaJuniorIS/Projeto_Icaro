from __future__ import annotations

import unittest
import uuid
from pathlib import Path
from unittest.mock import Mock, patch

from fastapi.testclient import TestClient
from requests import HTTPError

from app.db import init_db
from app.intelligence import semantic_relation
from app.main import app
from app.repository import (
    create_basket,
    create_basket_item,
    create_item_source,
    export_markdown_report,
    generate_calculation_memory,
)
from app.search import search_compras_gov_item, search_pncp_item


TMP_ROOT = Path(__file__).resolve().parents[1] / ".tmp_tests"


def temp_db_path() -> Path:
    TMP_ROOT.mkdir(exist_ok=True)
    return TMP_ROOT / f"{uuid.uuid4().hex}.sqlite3"


class IcaroGovLabV2Test(unittest.TestCase):
    def test_semantic_relation_handles_related_tire_descriptions(self) -> None:
        relation = semantic_relation("Pneu aro 16", "Pneu automotivo 205 55 R16")
        self.assertIn(relation["status"], {"relacionado", "equivalente"})
        self.assertIn("pneu", relation["shared_terms"])

    def test_basket_item_source_price_memory_flow(self) -> None:
        db_path = temp_db_path()
        init_db(db_path)
        basket = create_basket(
            {
                "title": "Cesta de pneus",
                "central_object": "Aquisição de pneus para manutenção veicular",
            },
            db_path,
        )
        item = create_basket_item(
            {
                "basket_id": basket["id"],
                "description": "Pneu 205/55 R16",
                "unit": "unidade",
                "quantity": 4,
                "technical_notes": "Pneu automotivo radial.",
            },
            db_path,
        )
        source = create_item_source(
            {
                "basket_item_id": item["id"],
                "source_type": "pncp",
                "origin": "PNCP",
                "url": "https://pncp.gov.br/exemplo",
                "organization": "Municipio Teste",
                "modality": "Pregao",
                "process_number": "123/2026",
                "supplier": "Fornecedor Pneus",
                "contracting_context": "Aquisição de pneu automotivo 205 55 R16 para frota municipal",
                "unit_price": 410.0,
                "quantity": 4,
                "unit": "unidade",
            },
            db_path,
        )
        self.assertEqual(source["prices"][0]["unit_price"], 410.0)
        self.assertEqual(source["validations"][0]["validation_type"], "semantic_similarity")

        memory = generate_calculation_memory(basket["id"], db_path)
        self.assertEqual(memory["items"][0]["summary"]["median"], 410.0)
        self.assertEqual(memory["basket"]["median"], 1640.0)

        report = export_markdown_report(basket["id"], db_path)
        self.assertIn("Pesquisa de mercado defensavel", report)
        self.assertIn("Pneu 205/55 R16", report)

    def test_api_rejects_source_without_context(self) -> None:
        client = TestClient(app)
        basket = client.post(
            "/api/baskets",
            json={"title": "Cesta TI", "central_object": "Material de informatica"},
        ).json()["basket"]
        item = client.post(
            "/api/items",
            json={
                "basket_id": basket["id"],
                "description": "HD SSD 480GB",
                "unit": "unidade",
                "quantity": 2,
            },
        ).json()["item"]
        response = client.post(
            "/api/sources",
            json={
                "basket_item_id": item["id"],
                "source_type": "pncp",
                "origin": "PNCP",
                "url": "",
                "organization": "",
                "contracting_context": "",
                "unit_price": 100,
                "quantity": 1,
            },
        )
        self.assertEqual(response.status_code, 422)

    def test_automated_pncp_search_extracts_traceable_unit_price(self) -> None:
        item = {
            "id": 10,
            "basket_id": 1,
            "description": "Pneu 205/55 R16",
            "unit": "unidade",
            "keywords": ["pneu", "205", "55", "r16"],
        }
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {
            "data": [
                {
                    "numeroControlePNCP": "12345678000199-1-000001/2026",
                    "objetoCompra": "Aquisicao de pneu automotivo 205 55 R16 para frota municipal",
                    "orgaoEntidadeRazaoSocial": "Municipio Teste",
                    "modalidadeNome": "Pregao",
                    "numeroCompra": "1/2026",
                    "fornecedorNome": "Fornecedor Pneus",
                    "valorUnitarioEstimado": 410.0,
                    "quantidade": 4,
                    "unidadeMedida": "unidade",
                }
            ]
        }
        with patch("app.search.requests.get", return_value=response):
            candidates, issues = search_pncp_item(item, query="pneu 205 55 r16")

        self.assertFalse(issues)
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0]["unit_price"], 410.0)
        self.assertEqual(candidates[0]["origin"], "PNCP")
        self.assertIn("Municipio Teste", candidates[0]["organization"])

    def test_automated_pncp_search_does_not_save_global_value_as_unit_price(self) -> None:
        item = {
            "id": 10,
            "basket_id": 1,
            "description": "Monitor LED 24 polegadas",
            "unit": "unidade",
            "keywords": ["monitor", "24"],
        }
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {
            "data": [
                {
                    "objetoCompra": "Aquisicao de monitores LED",
                    "orgaoEntidadeRazaoSocial": "Municipio Teste",
                    "valorTotalEstimado": 80000.0,
                }
            ]
        }
        with patch("app.search.requests.get", return_value=response):
            candidates, issues = search_pncp_item(item, query="monitor 24")

        self.assertEqual(candidates, [])
        self.assertTrue(issues)

    def test_automated_pncp_search_fetches_contracting_items_when_publication_has_no_unit_price(self) -> None:
        item = {
            "id": 10,
            "basket_id": 1,
            "description": "Monitor LED 24 polegadas",
            "unit": "unidade",
            "keywords": ["monitor", "24"],
        }
        publication_response = Mock()
        publication_response.raise_for_status.return_value = None
        publication_response.json.return_value = {
            "data": [
                {
                    "numeroControlePNCP": "12345678000199-1-000001/2026",
                    "objetoCompra": "Aquisicao de equipamentos de informatica",
                    "orgaoEntidadeRazaoSocial": "Municipio Teste",
                    "valorTotalEstimado": 80000.0,
                }
            ]
        }
        item_response = Mock()
        item_response.raise_for_status.return_value = None
        item_response.json.return_value = {
            "data": [
                {
                    "descricao": "Monitor LED 24 polegadas HDMI",
                    "valorUnitarioEstimado": 799.9,
                    "quantidade": 20,
                    "unidadeMedida": "unidade",
                }
            ]
        }
        with patch("app.search.requests.get", side_effect=[publication_response, item_response]):
            candidates, issues = search_pncp_item(item, query="monitor led 24")

        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0]["unit_price"], 799.9)
        self.assertIn("Monitor LED 24", candidates[0]["contracting_context"])

    def test_automated_pncp_search_retries_without_text_query_after_bad_request(self) -> None:
        item = {
            "id": 10,
            "basket_id": 1,
            "description": "HD 1TB",
            "unit": "unidade",
            "keywords": ["hd", "1tb"],
        }
        bad_response = Mock()
        bad_response.status_code = 400
        first = HTTPError("400 Client Error")
        first.response = bad_response

        publication_response = Mock()
        publication_response.raise_for_status.return_value = None
        publication_response.json.return_value = {
            "data": [
                {
                    "numeroControlePNCP": "12345678000199-1-000001/2026",
                    "objetoCompra": "Aquisicao de HD 1TB para computadores",
                    "orgaoEntidadeRazaoSocial": "Municipio Teste",
                    "valorUnitarioEstimado": 250.0,
                }
            ]
        }

        def fake_get(_url, params, timeout):
            response = Mock()
            response.raise_for_status.side_effect = first
            if "q" not in params:
                return publication_response
            return response

        with patch("app.search.requests.get", side_effect=fake_get):
            candidates, issues = search_pncp_item(item, query="hd tera bytes")

        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0]["unit_price"], 250.0)
        self.assertTrue(any("consultas alternativas" in issue.message for issue in issues))

    def test_compras_gov_search_is_paused_when_public_endpoints_are_unstable(self) -> None:
        item = {
            "id": 10,
            "basket_id": 1,
            "description": "HD 4TB",
            "unit": "unidade",
            "catmat_catser": "",
            "keywords": ["hd", "4tb"],
        }
        candidates, issues = search_compras_gov_item(item, query="HD com 4 tera bytes")

        self.assertEqual(candidates, [])
        self.assertEqual(issues[0].source_type, "compras_gov")
        self.assertEqual(issues[0].severity, "info")


if __name__ == "__main__":
    unittest.main()
