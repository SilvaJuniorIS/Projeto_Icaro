from __future__ import annotations

import os
import unittest
from io import BytesIO

os.environ.setdefault("ICARO_AUTH_USER", "admin")
os.environ.setdefault("ICARO_AUTH_PASSWORD", "icaro123")
os.environ.setdefault("ICARO_AUTH_SECRET", "test-secret")

from fastapi.testclient import TestClient
from openpyxl import Workbook

from api import app


class UploadTest(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        # login
        resp = self.client.post(
            "/auth/login",
            data={"usuario": "admin", "senha": "icaro123"},
            follow_redirects=False,
        )
        self.cookies = resp.cookies

    def _create_processo(self) -> int:
        resp = self.client.post(
            "/processos",
            json={"titulo": "Upload Test", "descricao_objeto": "Test"},
            cookies=self.cookies,
        )
        return resp.json()["id"]

    def test_csv_upload(self) -> None:
        pid = self._create_processo()
        csv_content = "descricao;quantidade;unidade\nCaneta azul;100;unidade\nLapis preto;50;unidade\n"
        resp = self.client.post(
            "/itens/importar-arquivo",
            data={"processo_id": str(pid)},
            files={"arquivo": ("itens.csv", csv_content.encode("utf-8"), "text/csv")},
            cookies=self.cookies,
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data["ids"]), 2)
        self.assertEqual(len(data["itens"]), 2)

    def test_xlsx_upload(self) -> None:
        pid = self._create_processo()
        wb = Workbook()
        ws = wb.active
        ws.append(["descricao", "quantidade", "unidade"])
        ws.append(["Mouse USB", 10, "unidade"])
        ws.append(["Teclado USB", 5, "unidade"])
        buf = BytesIO()
        wb.save(buf)
        buf.seek(0)

        resp = self.client.post(
            "/itens/importar-arquivo",
            data={"processo_id": str(pid)},
            files={"arquivo": ("itens.xlsx", buf.read(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            cookies=self.cookies,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()["ids"]), 2)

    def test_invalid_file_rejected(self) -> None:
        pid = self._create_processo()
        resp = self.client.post(
            "/itens/importar-arquivo",
            data={"processo_id": str(pid)},
            files={"arquivo": ("file.txt", b"random content", "text/plain")},
            cookies=self.cookies,
        )
        self.assertEqual(resp.status_code, 400)


if __name__ == "__main__":
    unittest.main()
