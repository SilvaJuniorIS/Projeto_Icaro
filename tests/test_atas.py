from __future__ import annotations

import os
import unittest

os.environ.setdefault("ICARO_AUTH_USER", "admin")
os.environ.setdefault("ICARO_AUTH_PASSWORD", "icaro123")
os.environ.setdefault("ICARO_AUTH_SECRET", "test-secret")

from fastapi.testclient import TestClient

from api import app


class AtasTest(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        resp = self.client.post(
            "/auth/login",
            data={"usuario": "admin", "senha": "icaro123"},
            follow_redirects=False,
        )
        self.cookies = resp.cookies

    def _create_processo(self) -> int:
        resp = self.client.post(
            "/processos",
            json={"titulo": "Atas Test", "descricao_objeto": "Test atas"},
            cookies=self.cookies,
        )
        return resp.json()["id"]

    def test_crud_ata(self) -> None:
        pid = self._create_processo()

        # Create
        resp = self.client.post(
            "/atas",
            json={
                "processo_id": pid,
                "numero": "ATA-001/2025",
                "orgao_gerenciador": "Orgao A",
                "fornecedor": "Fornecedor X",
                "objeto": "Fornecimento de papel",
                "valor_unitario": 22.50,
                "vigencia_inicio": "2025-01-01",
                "vigencia_fim": "2025-12-31",
                "aderencia": "alta",
            },
            cookies=self.cookies,
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        ata_id = data["id"]
        self.assertEqual(len(data["atas"]), 1)
        self.assertEqual(data["atas"][0]["numero"], "ATA-001/2025")

        # List
        resp = self.client.get(f"/processos/{pid}/atas", cookies=self.cookies)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()["atas"]), 1)

        # Delete
        resp = self.client.delete(f"/atas/{ata_id}", cookies=self.cookies)
        self.assertEqual(resp.status_code, 200)

        # Confirm deleted
        resp = self.client.get(f"/processos/{pid}/atas", cookies=self.cookies)
        self.assertEqual(len(resp.json()["atas"]), 0)

    def test_delete_nonexistent_ata_returns_404(self) -> None:
        resp = self.client.delete("/atas/9999", cookies=self.cookies)
        self.assertEqual(resp.status_code, 404)


if __name__ == "__main__":
    unittest.main()
