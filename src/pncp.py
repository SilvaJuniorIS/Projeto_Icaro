from __future__ import annotations

from datetime import date, timedelta
from typing import Any

import requests

from src.text_utils import palavras_texto, tokens_texto


BASE_URL = "https://pncp.gov.br/api/consulta"

_STOPWORDS_PT = {
    "para",
    "com",
    "sem",
    "por",
    "sobre",
    "entre",
    "ate",
    "tipo",
    "tipos",
    "material",
    "materiais",
    "aquisicao",
    "contratacao",
    "servico",
    "servicos",
    "fornecimento",
    "fornecimentos",
    "objeto",
    "objetos",
    "unidade",
    "unidades",
    "quantidade",
    "quantidades",
    "de",
    "da",
    "do",
    "das",
    "dos",
    "em",
    "no",
    "na",
    "nos",
    "nas",
    "ao",
    "aos",
    "um",
    "uma",
    "uns",
    "umas",
    "ou",
    "e",
    "se",
    "que",
    "como",
    "cada",
    "outro",
    "outra",
    "outros",
    "outras",
}


def _tokens(texto: str) -> set[str]:
    return tokens_texto(texto)


def similaridade_jaccard(texto_a: str, texto_b: str) -> float:
    tokens_a = _tokens(texto_a)
    tokens_b = _tokens(texto_b)
    if not tokens_a or not tokens_b:
        return 0.0
    union = len(tokens_a | tokens_b)
    return len(tokens_a & tokens_b) / union if union else 0.0


def _palavras_significativas(texto: str, limite: int = 14) -> list[str]:
    saida: list[str] = []
    for palavra in palavras_texto(texto):
        if palavra in _STOPWORDS_PT:
            continue
        if palavra not in saida:
            saida.append(palavra)
        if len(saida) >= limite:
            break
    return saida


def montar_consultas_pncp(
    termo: str,
    referencia: str,
    *,
    variantes: bool,
    max_consultas: int,
) -> list[str]:
    consultas: list[str] = []

    def adicionar(frase: str) -> None:
        f = (frase or "").strip()
        if len(f) < 2:
            return
        if f.lower() in {c.lower() for c in consultas}:
            return
        consultas.append(f[:200])

    adicionar(termo)
    if not variantes or len(consultas) >= max_consultas:
        return consultas[:max_consultas]

    ref = (referencia or termo or "").strip()
    palavras = _palavras_significativas(ref, limite=20)
    if len(palavras) >= 3:
        adicionar(" ".join(palavras[:4]))
    if len(palavras) >= 6:
        adicionar(" ".join(palavras[4:8]))
    if len(palavras) >= 2:
        ordenadas = sorted(set(palavras), key=len, reverse=True)
        adicionar(" ".join(ordenadas[:3]))

    return consultas[:max_consultas]


def _chave_resultado(item: dict[str, Any]) -> str:
    numero = item.get("numero_controle") or ""
    if numero:
        return str(numero)
    objeto = (item.get("objeto") or "")[:120]
    orgao = item.get("orgao") or ""
    pub = item.get("data_publicacao") or ""
    return f"{orgao}|{objeto}|{pub}"


def buscar_contratacoes_contextual(
    termo: str,
    texto_referencia: str,
    data_inicial: str | None = None,
    data_final: str | None = None,
    uf: str | None = None,
    modalidade_id: str | None = None,
    tamanho_pagina: int = 12,
    buscar_variantes: bool = True,
    max_consultas: int = 4,
) -> dict[str, Any]:
    referencia = (texto_referencia or "").strip() or (termo or "").strip()
    termo_limpo = (termo or "").strip()
    if not termo_limpo and referencia:
        termo_limpo = referencia[:200]

    consultas = montar_consultas_pncp(
        termo_limpo,
        referencia,
        variantes=buscar_variantes,
        max_consultas=max(1, min(max_consultas, 6)),
    )
    if not consultas:
        return {
            "ok": False,
            "erro": "Nenhum termo de consulta valido",
            "consultas": [],
            "resultados": [],
            "texto_referencia": referencia,
        }

    agregados: dict[str, dict[str, Any]] = {}
    erros_parciais: list[str] = []

    for consulta in consultas:
        pacote = buscar_contratacoes(
            consulta,
            data_inicial=data_inicial,
            data_final=data_final,
            uf=uf,
            modalidade_id=modalidade_id,
            pagina=1,
            tamanho_pagina=tamanho_pagina,
        )
        if not pacote.get("ok"):
            err = str(pacote.get("erro") or "Falha na consulta")
            if err not in erros_parciais:
                erros_parciais.append(err)
            continue
        for item in pacote.get("resultados") or []:
            chave = _chave_resultado(item)
            if chave not in agregados:
                agregados[chave] = {**item, "consultas_atingiram": [consulta]}
            elif consulta not in agregados[chave].get("consultas_atingiram", []):
                agregados[chave].setdefault("consultas_atingiram", []).append(consulta)

    resultados = list(agregados.values())
    for item in resultados:
        objeto = item.get("objeto") or ""
        cabecalho = f"{item.get('orgao') or ''} {item.get('unidade') or ''}"
        sim = max(
            similaridade_jaccard(referencia, objeto),
            similaridade_jaccard(referencia, f"{cabecalho} {objeto}"),
        )
        item["similaridade"] = round(sim, 4)
        item["similaridade_pct"] = round(sim * 100, 1)

    resultados.sort(key=lambda x: float(x.get("similaridade") or 0), reverse=True)

    if not resultados and erros_parciais:
        return {
            "ok": False,
            "erro": erros_parciais[0],
            "erros_parciais": erros_parciais,
            "consultas": consultas,
            "resultados": [],
            "texto_referencia": referencia,
        }

    return {
        "ok": True,
        "erros_parciais": erros_parciais,
        "consultas": consultas,
        "texto_referencia": referencia,
        "total_unicos": len(resultados),
        "resultados": resultados,
    }


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
    uf: str | None = None,
    modalidade_id: str | None = None,
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
    if uf:
        params["uf"] = uf.upper()
    if modalidade_id:
        params["codigoModalidadeContratacao"] = modalidade_id

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
