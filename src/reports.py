from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from src.config import OUTPUT_DIR
from src.db import export_snapshot, now_iso


def _safe_name(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_-]+", "_", value.strip())[:60].strip("_")
    return slug or "processo"


def _auto_width(ws) -> None:
    for column_cells in ws.columns:
        width = max(len(str(cell.value or "")) for cell in column_cells)
        ws.column_dimensions[get_column_letter(column_cells[0].column)].width = min(max(width + 2, 12), 60)


def _style_header(ws, row: int = 1) -> None:
    fill = PatternFill("solid", fgColor="1F4E5F")
    for cell in ws[row]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = fill
        cell.alignment = Alignment(horizontal="center")


def gerar_xlsx_processo(processo_id: int, output_dir: Path | str = OUTPUT_DIR) -> Path | None:
    snapshot = export_snapshot(processo_id)
    if not snapshot:
        return None

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    processo: dict[str, Any] = snapshot["processo"]
    resumo: dict[str, Any] = snapshot["resumo"]
    resumo_atas: dict[str, Any] = snapshot["resumo_atas"]
    fontes: list[dict[str, Any]] = snapshot["fontes"]
    atas: list[dict[str, Any]] = snapshot["atas"]

    wb = Workbook()
    ws = wb.active
    ws.title = "Resumo"
    ws.append(["Campo", "Valor"])
    for chave in [
        "amostras",
        "fontes_total",
        "fontes_aproveitadas",
        "fontes_descartadas",
        "menor",
        "maior",
        "media",
        "mediana",
        "preco_estimado_mediana",
        "preco_estimado_media",
        "q1",
        "q3",
        "limite_inferior",
        "limite_superior",
        "outliers",
    ]:
        ws.append([chave, resumo.get(chave)])
    for chave in ["atas_total", "atas_vigentes", "atas_potencialmente_aderentes"]:
        ws.append([chave, resumo_atas.get(chave)])
    _style_header(ws)
    _auto_width(ws)

    ws_proc = wb.create_sheet("Processo")
    ws_proc.append(["Campo", "Valor"])
    for chave, valor in processo.items():
        ws_proc.append([chave, valor])
    _style_header(ws_proc)
    _auto_width(ws_proc)

    ws_fontes = wb.create_sheet("Fontes")
    headers = [
        "id",
        "fonte_tipo",
        "descricao_item",
        "valor_unitario",
        "quantidade",
        "orgao",
        "fornecedor",
        "uf",
        "municipio",
        "url",
        "data_referencia",
        "data_acesso",
        "aproveitada",
        "justificativa_descarte",
        "observacoes",
    ]
    ws_fontes.append(headers)
    for fonte in fontes:
        ws_fontes.append([fonte.get(header) for header in headers])
    _style_header(ws_fontes)
    _auto_width(ws_fontes)

    ws_atas = wb.create_sheet("Atas")
    ata_headers = [
        "id",
        "numero",
        "orgao_gerenciador",
        "fornecedor",
        "objeto",
        "item",
        "valor_unitario",
        "vigencia_inicio",
        "vigencia_fim",
        "quantidade_registrada",
        "quantidade_disponivel_estimativa",
        "url",
        "aderencia",
        "observacoes",
    ]
    ws_atas.append(ata_headers)
    for ata in atas:
        ws_atas.append([ata.get(header) for header in ata_headers])
    _style_header(ws_atas)
    _auto_width(ws_atas)

    filename = f"icaro_processo_{processo_id}_{_safe_name(processo['titulo'])}_{now_iso().replace(':', '-')}.xlsx"
    path = output_dir / filename
    wb.save(path)
    return path
