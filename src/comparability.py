from __future__ import annotations

import re
from statistics import median
from typing import Any


def _tokens(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]+", text.lower())
        if len(token) >= 3
    }


def _similaridade(a: str, b: str) -> float:
    tokens_a = _tokens(a)
    tokens_b = _tokens(b)
    if not tokens_a or not tokens_b:
        return 0.0
    return len(tokens_a & tokens_b) / len(tokens_a | tokens_b)


def avaliar_comparabilidade(snapshot: dict[str, Any]) -> dict[str, Any]:
    processo = snapshot.get("processo", {})
    objeto = processo.get("descricao_objeto", "")
    fontes = snapshot.get("fontes", [])
    valores = [
        float(fonte.get("valor_unitario") or 0)
        for fonte in fontes
        if fonte.get("aproveitada") and float(fonte.get("valor_unitario") or 0) > 0
    ]
    referencia = median(valores) if valores else None

    itens = []
    for fonte in fontes:
        valor = float(fonte.get("valor_unitario") or 0)
        similaridade = _similaridade(objeto, fonte.get("descricao_item", ""))
        desvio = None
        if referencia and valor > 0:
            desvio = ((valor - referencia) / referencia) * 100
        score = 0
        score += 45 * similaridade
        if fonte.get("aproveitada"):
            score += 20
        if desvio is None:
            score += 10
        elif abs(desvio) <= 25:
            score += 25
        elif abs(desvio) <= 50:
            score += 12
        if fonte.get("uf") and processo.get("local_execucao") and fonte["uf"].lower() in processo["local_execucao"].lower():
            score += 10
        score = round(min(score, 100), 1)
        itens.append(
            {
                "fonte_id": fonte.get("id"),
                "descricao_item": fonte.get("descricao_item", ""),
                "fonte_tipo": fonte.get("fonte_tipo", ""),
                "valor_unitario": valor,
                "similaridade_objeto": round(similaridade, 3),
                "desvio_percentual_mediana": round(desvio, 2) if desvio is not None else None,
                "score": score,
                "classificacao": "alta" if score >= 70 else "media" if score >= 45 else "baixa",
            }
        )

    return {
        "referencia_mediana": referencia,
        "itens": sorted(itens, key=lambda item: item["score"], reverse=True),
    }
