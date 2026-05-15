from __future__ import annotations

from typing import Any


def gerar_revisao_itens(snapshot: dict[str, Any]) -> dict[str, Any]:
    itens = snapshot.get("itens", [])
    resumo_por_item = {
        int(entry["item"]["id"]): entry.get("resumo", {})
        for entry in snapshot.get("resumo_itens", [])
        if entry.get("item")
    }
    rascunhos_por_item: dict[int, list[dict[str, Any]]] = {}
    for rascunho in snapshot.get("pncp_rascunhos", []):
        item_id = rascunho.get("item_id")
        if item_id is not None:
            rascunhos_por_item.setdefault(int(item_id), []).append(rascunho)

    revisao = []
    for item in itens:
        item_id = int(item["id"])
        resumo = resumo_por_item.get(item_id, {})
        fontes_aproveitadas = int(resumo.get("fontes_aproveitadas") or 0)
        rascunhos = [r for r in rascunhos_por_item.get(item_id, []) if r.get("status") == "rascunho"]
        pendencias = []
        if fontes_aproveitadas == 0:
            pendencias.append("Sem fonte aproveitada.")
        elif fontes_aproveitadas < 3:
            pendencias.append("Menos de 3 fontes aproveitadas.")
        if rascunhos:
            pendencias.append(f"{len(rascunhos)} rascunho(s) PNCP aguardando decisao.")
        if int(resumo.get("outliers") or 0) > 0:
            pendencias.append("Ha outliers no conjunto de precos.")
        if not item.get("termo_busca"):
            pendencias.append("Termo de busca PNCP nao informado.")

        if fontes_aproveitadas >= 3 and not pendencias:
            status = "pronto"
        elif fontes_aproveitadas > 0:
            status = "revisar"
        else:
            status = "pendente"

        revisao.append(
            {
                "item": item,
                "resumo": resumo,
                "rascunhos_abertos": len(rascunhos),
                "status": status,
                "pendencias": pendencias,
            }
        )

    totais = {
        "itens": len(revisao),
        "prontos": sum(1 for item in revisao if item["status"] == "pronto"),
        "revisar": sum(1 for item in revisao if item["status"] == "revisar"),
        "pendentes": sum(1 for item in revisao if item["status"] == "pendente"),
    }
    return {"itens": revisao, "totais": totais}
