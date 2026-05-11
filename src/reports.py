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


def _fmt_money(value: Any) -> str:
    if value is None:
        return "-"
    return f"R$ {float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _texto(value: Any) -> str:
    text = str(value or "").strip()
    return text or "-"


def gerar_relatorio_markdown(processo_id: int, output_dir: Path | str = OUTPUT_DIR) -> Path | None:
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

    linhas = [
        f"# Relatorio administrativo - {_texto(processo.get('titulo'))}",
        "",
        f"Gerado em: {snapshot['gerado_em']}",
        "",
        "## 1. Identificacao do processo",
        "",
        f"- Objeto: {_texto(processo.get('descricao_objeto'))}",
        f"- Categoria: {_texto(processo.get('categoria'))}",
        f"- Unidade: {_texto(processo.get('unidade'))}",
        f"- Quantidade estimada: {_texto(processo.get('quantidade'))}",
        f"- Local de execucao/entrega: {_texto(processo.get('local_execucao'))}",
        f"- Responsavel: {_texto(processo.get('responsavel'))}",
        f"- Status: {_texto(processo.get('status'))}",
        "",
        "## 2. Pesquisa de precos",
        "",
        f"- Fontes registradas: {resumo.get('fontes_total', 0)}",
        f"- Fontes aproveitadas: {resumo.get('fontes_aproveitadas', 0)}",
        f"- Fontes descartadas: {resumo.get('fontes_descartadas', 0)}",
        f"- Menor valor: {_fmt_money(resumo.get('menor'))}",
        f"- Maior valor: {_fmt_money(resumo.get('maior'))}",
        f"- Media: {_fmt_money(resumo.get('media'))}",
        f"- Mediana: {_fmt_money(resumo.get('mediana'))}",
        f"- Preco estimado sugerido pela mediana: {_fmt_money(resumo.get('preco_estimado_mediana'))}",
        f"- Outliers identificados pelo criterio IQR: {resumo.get('outliers', 0)}",
        "",
        "### Fontes consultadas",
        "",
        "| Uso | Tipo | Item | Valor unitario | Orgao | Fornecedor | Justificativa/observacoes |",
        "| --- | --- | --- | ---: | --- | --- | --- |",
    ]

    if fontes:
        for fonte in fontes:
            uso = "Aproveitada" if fonte.get("aproveitada") else "Descartada"
            observacao = fonte.get("justificativa_descarte") or fonte.get("observacoes")
            linhas.append(
                "| "
                + " | ".join(
                    [
                        uso,
                        _texto(fonte.get("fonte_tipo")),
                        _texto(fonte.get("descricao_item")),
                        _fmt_money(fonte.get("valor_unitario")),
                        _texto(fonte.get("orgao")),
                        _texto(fonte.get("fornecedor")),
                        _texto(observacao),
                    ]
                )
                + " |"
            )
    else:
        linhas.append("| - | - | Nenhuma fonte registrada | - | - | - | - |")

    linhas.extend(
        [
            "",
            "## 3. Atas para possivel adesao",
            "",
            f"- Atas registradas: {resumo_atas.get('atas_total', 0)}",
            f"- Atas vigentes ou sem data final informada: {resumo_atas.get('atas_vigentes', 0)}",
            f"- Atas potencialmente aderentes: {resumo_atas.get('atas_potencialmente_aderentes', 0)}",
            "",
            "| Aderencia | Ata | Orgao gerenciador | Fornecedor | Valor unitario | Vigencia | Observacoes |",
            "| --- | --- | --- | --- | ---: | --- | --- |",
        ]
    )

    if atas:
        for ata in atas:
            vigencia = f"{_texto(ata.get('vigencia_inicio'))} a {_texto(ata.get('vigencia_fim'))}"
            linhas.append(
                "| "
                + " | ".join(
                    [
                        _texto(ata.get("aderencia")),
                        _texto(ata.get("numero")),
                        _texto(ata.get("orgao_gerenciador")),
                        _texto(ata.get("fornecedor")),
                        _fmt_money(ata.get("valor_unitario")),
                        vigencia,
                        _texto(ata.get("observacoes")),
                    ]
                )
                + " |"
            )
    else:
        linhas.append("| - | Nenhuma ata registrada | - | - | - | - | - |")

    linhas.extend(
        [
            "",
            "## 4. Checklist administrativo inicial",
            "",
            f"- [{'x' if fontes else ' '}] Ha fontes de preco registradas.",
            f"- [{'x' if resumo.get('fontes_aproveitadas', 0) >= 3 else ' '}] Ha pelo menos tres fontes aproveitadas.",
            f"- [{'x' if resumo.get('fontes_descartadas', 0) == 0 else ' '}] Descartes foram evitados ou devem estar justificados.",
            f"- [{'x' if atas else ' '}] Atas de registro de precos foram verificadas quando cabivel.",
            f"- [{'x' if resumo_atas.get('atas_potencialmente_aderentes', 0) else ' '}] Ha ata potencialmente aderente para analise de carona.",
            "- [ ] Responsavel deve revisar adequacao tecnica, juridica e regulamentacao local.",
            "",
            "## 5. Observacao",
            "",
            "Este relatorio apoia a instrucao administrativa e nao substitui a analise tecnica, juridica ou de controle interno.",
            "",
        ]
    )

    filename = f"icaro_relatorio_{processo_id}_{_safe_name(processo['titulo'])}_{now_iso().replace(':', '-')}.md"
    path = output_dir / filename
    path.write_text("\n".join(linhas), encoding="utf-8")
    return path


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
