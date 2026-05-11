from __future__ import annotations

from typing import Any


def gerar_checklist(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    processo = snapshot.get("processo", {})
    fontes = snapshot.get("fontes", [])
    atas = snapshot.get("atas", [])
    resumo = snapshot.get("resumo", {})
    resumo_atas = snapshot.get("resumo_atas", {})

    itens = [
        {
            "id": "objeto_descrito",
            "grupo": "Objeto",
            "titulo": "Objeto descrito",
            "ok": bool(processo.get("descricao_objeto")),
            "detalhe": "Descricao do objeto preenchida.",
        },
        {
            "id": "responsavel_identificado",
            "grupo": "Governanca",
            "titulo": "Responsavel identificado",
            "ok": bool(processo.get("responsavel")),
            "detalhe": "Registre a equipe ou servidor responsavel pela pesquisa.",
        },
        {
            "id": "fontes_registradas",
            "grupo": "Pesquisa de precos",
            "titulo": "Fontes de preco registradas",
            "ok": len(fontes) > 0,
            "detalhe": f"{len(fontes)} fonte(s) registrada(s).",
        },
        {
            "id": "minimo_tres_fontes",
            "grupo": "Pesquisa de precos",
            "titulo": "Minimo de tres fontes aproveitadas",
            "ok": int(resumo.get("fontes_aproveitadas") or 0) >= 3,
            "detalhe": f"{resumo.get('fontes_aproveitadas', 0)} fonte(s) aproveitada(s).",
        },
        {
            "id": "descartes_justificados",
            "grupo": "Pesquisa de precos",
            "titulo": "Descartes justificados",
            "ok": all(
                fonte.get("aproveitada")
                or bool(fonte.get("justificativa_descarte") or fonte.get("observacoes"))
                for fonte in fontes
            ),
            "detalhe": "Fontes descartadas devem ter justificativa registrada.",
        },
        {
            "id": "metodo_calculo",
            "grupo": "Memoria de calculo",
            "titulo": "Metodo estatistico calculado",
            "ok": resumo.get("preco_estimado_mediana") is not None,
            "detalhe": "Mediana usada como referencia inicial para o preco estimado.",
        },
        {
            "id": "outliers_avaliados",
            "grupo": "Memoria de calculo",
            "titulo": "Valores extremos avaliados",
            "ok": int(resumo.get("outliers") or 0) == 0,
            "detalhe": f"{resumo.get('outliers', 0)} outlier(s) identificado(s) pelo criterio IQR.",
        },
        {
            "id": "atas_verificadas",
            "grupo": "Atas e caronas",
            "titulo": "Atas verificadas",
            "ok": len(atas) > 0,
            "detalhe": f"{resumo_atas.get('atas_total', 0)} ata(s) registrada(s).",
        },
        {
            "id": "atas_aderentes",
            "grupo": "Atas e caronas",
            "titulo": "Aderencia das atas classificada",
            "ok": all(ata.get("aderencia") and ata.get("aderencia") != "indefinida" for ata in atas) if atas else False,
            "detalhe": f"{resumo_atas.get('atas_potencialmente_aderentes', 0)} ata(s) potencialmente aderente(s).",
        },
        {
            "id": "relatorio_emitido",
            "grupo": "Relatorio",
            "titulo": "Relatorio administrativo pronto para emissao",
            "ok": bool(fontes) and resumo.get("preco_estimado_mediana") is not None,
            "detalhe": "Exporte MD, XLSX ou DOCX apos revisar as evidencias.",
        },
    ]
    total = len(itens)
    concluidos = sum(1 for item in itens if item["ok"])
    for item in itens:
        item["progresso"] = {"concluidos": concluidos, "total": total}
    return itens
