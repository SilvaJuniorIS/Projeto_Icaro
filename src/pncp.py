from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

import requests

from src.text_utils import palavras_texto, tokens_texto


BASE_URL = "https://pncp.gov.br/api/consulta"
MODALIDADE_PADRAO = "6"
MODALIDADES_ESTRATEGIA = {
    "precisa": ["6"],
    "equilibrada": ["6", "8", "7", "4"],
    "abrangente": ["6", "8", "7", "4", "5", "9"],
}

_MODALIDADE_CODIGOS = {
    "leilao": "1",
    "leilao eletronico": "1",
    "dialogo competitivo": "2",
    "concurso": "3",
    "concorrencia": "4",
    "concorrencia eletronica": "4",
    "concorrencia presencial": "5",
    "pregao": "6",
    "pregao eletronico": "6",
    "pregao eletronico srp": "6",
    "pregao presencial": "7",
    "dispensa": "8",
    "dispensa de licitacao": "8",
    "inexigibilidade": "9",
    "inexigibilidade de licitacao": "9",
    "credenciamento": "12",
}

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


def normalizar_modalidade_id(valor: str | None) -> str | None:
    """Converte nomes usuais de modalidade para o codigo aceito pela API do PNCP."""
    bruto = (valor or "").strip()
    if not bruto:
        return None
    if bruto.isdigit():
        return bruto
    chave = " ".join(palavras_texto(bruto))
    return _MODALIDADE_CODIGOS.get(chave)


def similaridade_jaccard(texto_a: str, texto_b: str) -> float:
    tokens_a = _tokens(texto_a)
    tokens_b = _tokens(texto_b)
    if not tokens_a or not tokens_b:
        return 0.0
    union = len(tokens_a | tokens_b)
    return len(tokens_a & tokens_b) / union if union else 0.0


def _cobertura_tokens(texto_referencia: str, texto_resultado: str) -> float:
    referencia = _tokens(texto_referencia)
    if not referencia:
        return 0.0
    resultado = _tokens(texto_resultado)
    return len(referencia & resultado) / len(referencia)


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


def _texto_busca_item(item: dict[str, Any]) -> str:
    return " ".join(
        str(item.get(campo) or "")
        for campo in ("objeto", "orgao", "unidade", "modalidade", "situacao")
    )


def _filtrar_resultados_por_termo(resultados: list[dict[str, Any]], termo: str, *, estrito: bool = False) -> list[dict[str, Any]]:
    tokens = _tokens(termo)
    if not tokens or not estrito:
        return resultados
    filtrados: list[dict[str, Any]] = []
    for item in resultados:
        texto_tokens = _tokens(_texto_busca_item(item))
        if tokens <= texto_tokens or tokens & texto_tokens:
            filtrados.append(item)
    return filtrados


def _modalidades_para_busca(modalidade_id: str | None, estrategia: str) -> list[str]:
    modalidade_codigo = normalizar_modalidade_id(modalidade_id)
    if modalidade_codigo:
        return [modalidade_codigo]
    chave = (estrategia or "equilibrada").strip().lower()
    return MODALIDADES_ESTRATEGIA.get(chave, MODALIDADES_ESTRATEGIA["equilibrada"])


def _dias_desde_publicacao(data_publicacao: str) -> int | None:
    if not data_publicacao:
        return None
    bruto = data_publicacao[:10]
    for formato in ("%Y-%m-%d", "%d/%m/%Y", "%Y%m%d"):
        try:
            return max(0, (date.today() - datetime.strptime(bruto, formato).date()).days)
        except ValueError:
            continue
    return None


def _pontuar_resultado(item: dict[str, Any], referencia: str) -> dict[str, Any]:
    texto = _texto_busca_item(item)
    similaridade = similaridade_jaccard(referencia, texto)
    cobertura = _cobertura_tokens(referencia, texto)
    dias = _dias_desde_publicacao(str(item.get("data_publicacao") or ""))
    recencia = 0.0 if dias is None else max(0.0, 1 - min(dias, 730) / 730)
    valor = 1.0 if float(item.get("valor_estimado") or 0) > 0 else 0.0
    score = (similaridade * 0.55) + (cobertura * 0.30) + (recencia * 0.10) + (valor * 0.05)
    item["similaridade"] = round(score, 4)
    item["similaridade_pct"] = round(score * 100, 1)
    item["cobertura_termos_pct"] = round(cobertura * 100, 1)
    return item


def buscar_contratacoes_contextual(
    termo: str,
    texto_referencia: str,
    data_inicial: str | None = None,
    data_final: str | None = None,
    uf: str | None = None,
    ufs: list[str] | None = None,
    modalidade_id: str | None = None,
    tamanho_pagina: int = 12,
    buscar_variantes: bool = True,
    max_consultas: int = 4,
    estrategia: str = "equilibrada",
    similaridade_minima: float = 0.0,
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
    filtros_uf = [u.strip().upper() for u in (ufs or []) if u and u.strip()]
    if not filtros_uf and uf:
        filtros_uf = [uf.strip().upper()]
    filtros_uf = list(dict.fromkeys(filtros_uf))
    if not filtros_uf:
        filtros_uf = [None]
    modalidades = _modalidades_para_busca(modalidade_id, estrategia)
    max_chamadas = 36
    chamadas = 0

    for filtro_uf in filtros_uf:
        for modalidade in modalidades:
            for consulta in consultas:
                if chamadas >= max_chamadas:
                    break
                chamadas += 1
                pacote = buscar_contratacoes(
                    consulta,
                    data_inicial=data_inicial,
                    data_final=data_final,
                    uf=filtro_uf,
                    modalidade_id=modalidade,
                    pagina=1,
                    tamanho_pagina=tamanho_pagina,
                    filtrar_termo=False,
                )
                if not pacote.get("ok"):
                    err = str(pacote.get("erro") or "Falha na consulta")
                    if err not in erros_parciais:
                        erros_parciais.append(err)
                    continue
                partes_label = [consulta, f"modalidade {modalidade}"]
                if filtro_uf:
                    partes_label.append(filtro_uf)
                consulta_label = " / ".join(partes_label)
                for item in pacote.get("resultados") or []:
                    chave = _chave_resultado(item)
                    if chave not in agregados:
                        agregados[chave] = {**item, "consultas_atingiram": [consulta_label]}
                    elif consulta_label not in agregados[chave].get("consultas_atingiram", []):
                        agregados[chave].setdefault("consultas_atingiram", []).append(consulta_label)
            if chamadas >= max_chamadas:
                break
        if chamadas >= max_chamadas:
            break

    resultados = list(agregados.values())
    for item in resultados:
        _pontuar_resultado(item, referencia)

    if similaridade_minima > 0:
        resultados = [r for r in resultados if float(r.get("similaridade") or 0) >= similaridade_minima]
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
        "modalidades": modalidades,
        "chamadas": chamadas,
        "texto_referencia": referencia,
        "total_unicos": len(resultados),
        "resultados": resultados,
    }


def _normalizar_item(item: dict[str, Any]) -> dict[str, Any]:
    orgao = item.get("orgaoEntidade") or {}
    unidade = item.get("unidadeOrgao") or {}
    fornecedor = item.get("fornecedor") or {}
    return {
        "numero_controle": item.get("numeroControlePNCP") or item.get("numeroControlePncp") or "",
        "objeto": item.get("objetoCompra") or item.get("objetoContratacao") or item.get("objeto") or "",
        "orgao": orgao.get("razaoSocial") or orgao.get("nome") or "",
        "unidade": unidade.get("nomeUnidade") or unidade.get("nome") or "",
        "fornecedor": (
            fornecedor.get("nome")
            or fornecedor.get("razaoSocial")
            or fornecedor.get("nomeRazaoSocialFornecedor")
            or item.get("nomeRazaoSocialFornecedor")
            or item.get("fornecedorNome")
            or item.get("nomeFornecedor")
            or ""
        ),
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
    filtrar_termo: bool = True,
) -> dict[str, Any]:
    hoje = date.today()
    data_final = data_final or hoje.strftime("%Y%m%d")
    data_inicial = data_inicial or (hoje - timedelta(days=180)).strftime("%Y%m%d")
    tamanho_solicitado = max(10, int(tamanho_pagina or 10))
    tamanho_pagina_api = max(50, tamanho_solicitado) if termo else tamanho_solicitado
    params = {
        "dataInicial": data_inicial,
        "dataFinal": data_final,
        "pagina": pagina,
        "tamanhoPagina": tamanho_pagina_api,
    }
    if uf:
        params["uf"] = uf.upper()
    modalidade_codigo = normalizar_modalidade_id(modalidade_id) or MODALIDADE_PADRAO
    if modalidade_codigo:
        params["codigoModalidadeContratacao"] = modalidade_codigo

    url = f"{BASE_URL}/v1/contratacoes/publicacao"
    try:
        response = requests.get(url, params=params, timeout=12)
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        fonte = getattr(exc.response, "url", None) or getattr(response, "url", None) if "response" in locals() else url
        detalhe = ""
        if getattr(exc, "response", None) is not None:
            detalhe = (exc.response.text or "").strip()[:300]
        return {
            "ok": False,
            "erro": f"Falha ao consultar PNCP: {exc}" + (f" | Detalhe: {detalhe}" if detalhe else ""),
            "fonte": fonte,
            "resultados": [],
        }

    dados = payload.get("data") or payload.get("content") or payload.get("resultado") or []
    resultados = _filtrar_resultados_por_termo([_normalizar_item(item) for item in dados], termo, estrito=filtrar_termo)
    return {
        "ok": True,
        "fonte": response.url,
        "pagina": payload.get("pagina") or pagina,
        "total_registros": payload.get("totalRegistros") or payload.get("totalElements"),
        "resultados": resultados[:tamanho_solicitado],
    }
