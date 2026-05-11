from __future__ import annotations

from datetime import date, timedelta
from typing import Any

import requests


BASE_URL = "https://pncp.gov.br/api/consulta"


def _normalizar_item(item: dict[str, Any]) -> dict[str, Any]:
    orgao = item.get("orgaoEntidade") or {}
    unidade = item.get("unidadeOrgao") or {}
    return {
        "numero_controle": item.get("numeroControlePNCP") or item.get("numeroControlePncp") or "",
        "objeto": item.get("objetoCompra") or item.get("objetoContratacao") or item.get("objeto") or "",
        "orgao": orgao.get("razaoSocial") or orgao.get("nome") or "",
        "unidade": unidade.get("nomeUnidade") or unidade.get("nome") or "",
        "modalidade": item.get("modalidadeNome") or item.get("modalidade") or "",
        "situacao": item.get("situacaoCompraNome") or item.get("situacao") or "",
        "data_publicacao": item.get("dataPublicacaoPncp") or item.get("dataPublicacao") or "",
        "valor_estimado": item.get("valorTotalEstimado") or item.get("valorEstimado") or 0,
        "url": item.get("linkSistemaOrigem") or item.get("url") or "",
    }


def buscar_contratacoes(
    termo: str,
    data_inicial: str | None = None,
    data_final: str | None = None,
    pagina: int = 1,
    tamanho_pagina: int = 10,
) -> dict[str, Any]:
    hoje = date.today()
    data_final = data_final or hoje.strftime("%Y%m%d")
    data_inicial = data_inicial or (hoje - timedelta(days=180)).strftime("%Y%m%d")
    params = {
        "dataInicial": data_inicial,
        "dataFinal": data_final,
        "pagina": pagina,
        "tamanhoPagina": tamanho_pagina,
    }
    if termo:
        params["q"] = termo

    url = f"{BASE_URL}/v1/contratacoes/publicacao"
    try:
        response = requests.get(url, params=params, timeout=12)
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        return {
            "ok": False,
            "erro": f"Falha ao consultar PNCP: {exc}",
            "fonte": url,
            "resultados": [],
        }

    dados = payload.get("data") or payload.get("content") or payload.get("resultado") or []
    return {
        "ok": True,
        "fonte": response.url,
        "pagina": payload.get("pagina") or pagina,
        "total_registros": payload.get("totalRegistros") or payload.get("totalElements"),
        "resultados": [_normalizar_item(item) for item in dados],
    }
