from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any
from urllib.parse import quote

import requests

from app.intelligence import normalize_text, semantic_relation


PNCP_PUBLICATION_URL = "https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao"
PNCP_CONSULTA_ITEM_URLS = (
    "https://pncp.gov.br/api/consulta/v1/contratacoes/{numero_controle}/itens",
    "https://pncp.gov.br/api/pncp/v1/orgaos/{cnpj}/compras/{ano}/{sequencial}/itens",
)
PNCP_MODALITY_FALLBACKS = (6, 8, 4, 5, 7)


UNIT_PRICE_KEYS = {
    "valorunitario",
    "valor_unitario",
    "valorunitarioestimado",
    "valorunitariohomologado",
    "valorunitarioreferencia",
    "precoUnitario".lower(),
    "precoestimado",
    "valorhomologado",
    "valornegociado",
    "valorproposta",
    "valoritem",
}


@dataclass
class SearchIssue:
    source_type: str
    message: str
    severity: str = "warning"


def compact_digits(value: str) -> str:
    return "".join(ch for ch in value if ch.isdigit())


def default_period() -> tuple[str, str]:
    end = date.today()
    start = end - timedelta(days=365)
    return compact_digits(start.isoformat()), compact_digits(end.isoformat())


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    if isinstance(value, int | float):
        return float(value)
    normalized = str(value).strip().replace("R$", "").replace(".", "").replace(",", ".")
    try:
        return float(normalized)
    except ValueError:
        return None


def find_first_value(payload: dict[str, Any], candidate_keys: set[str]) -> float | None:
    normalized_candidate_keys = {normalize_key(key) for key in candidate_keys}
    stack: list[Any] = [payload]
    while stack:
        current = stack.pop()
        if isinstance(current, dict):
            for key, value in current.items():
                normalized_key = normalize_key(str(key))
                if normalized_key in normalized_candidate_keys:
                    parsed = as_float(value)
                    if parsed and parsed > 0:
                        return parsed
                if isinstance(value, dict | list):
                    stack.append(value)
        elif isinstance(current, list):
            stack.extend(current)
    return None


def normalize_key(value: str) -> str:
    return "".join(ch for ch in normalize_text(value) if ch.isalnum())


def get_text(payload: dict[str, Any], keys: tuple[str, ...], default: str = "") -> str:
    for key in keys:
        value = payload.get(key)
        if value:
            return str(value)
    return default


def get_results(payload: dict[str, Any]) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    for key in ("data", "items", "content", "resultado", "resultados"):
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    embedded = payload.get("_embedded")
    if isinstance(embedded, dict):
        for value in embedded.values():
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    return []


def text_matches_item(item: dict[str, Any], record: dict[str, Any], query: str = "") -> bool:
    haystack = normalize_text(
        " ".join(
            str(value)
            for key, value in record.items()
            if isinstance(value, str) and key != "raw_payload_json"
        )
    )
    terms = tokens_for_search(query or item["description"])
    if not terms:
        return True
    shared = [term for term in terms if term in haystack]
    return bool(shared)


def tokens_for_search(value: str) -> list[str]:
    ignored = {"de", "da", "do", "das", "dos", "para", "com", "sem", "e"}
    normalized = normalize_query_text(value)
    parts = normalized.split()
    return [part for part in parts if len(part) >= 2 and part not in ignored]


def normalize_query_text(value: str) -> str:
    normalized = normalize_text(value)
    normalized = normalized.replace("pendrve", "pendrive").replace("pen drive", "pendrive")
    normalized = normalized.replace("tera bytes", "tb").replace("terabytes", "tb")
    normalized = normalized.replace("giga bytes", "gb").replace("gigabytes", "gb").replace("gigas", "gb")
    parts = normalized.split()
    expanded = []
    for index, part in enumerate(parts):
        if part in {"tb", "gb"} and index > 0 and parts[index - 1].isdigit():
            expanded.append(parts[index - 1] + part)
        expanded.append(part)
    return " ".join(expanded)


def pncp_publication_link(record: dict[str, Any]) -> str:
    compra_id = get_text(record, ("numeroControlePNCP", "numeroControlePncp", "id"))
    if compra_id:
        return f"https://pncp.gov.br/app/editais/{compra_id}"
    return "https://pncp.gov.br/app/editais"


def parse_numero_controle_pncp(value: str) -> dict[str, str] | None:
    # Formato comum: 00000000000000-1-000001/2026.
    cleaned = str(value or "").strip()
    if not cleaned or "/" not in cleaned:
        return None
    try:
        before_year, ano = cleaned.rsplit("/", 1)
        cnpj, _, sequencial = before_year.split("-", 2)
    except ValueError:
        return None
    sequencial_digits = compact_digits(sequencial)
    if not cnpj or not ano or not sequencial_digits:
        return None
    return {
        "numero_controle": quote(cleaned, safe=""),
        "cnpj": compact_digits(cnpj),
        "ano": compact_digits(ano),
        "sequencial": str(int(sequencial_digits)),
    }


def request_json(url: str, params: dict[str, Any] | None = None, timeout: int = 12) -> dict[str, Any] | list[Any]:
    response = requests.get(url, params=params or {}, timeout=timeout)
    response.raise_for_status()
    return response.json()


def request_first_success(
    url: str,
    variants: list[dict[str, Any]],
    timeout: int,
) -> tuple[dict[str, Any] | list[Any] | None, list[SearchIssue]]:
    issues: list[SearchIssue] = []
    informed_bad_request = False
    for params in variants:
        try:
            return request_json(url, params=params, timeout=timeout), issues
        except requests.HTTPError as exc:
            status = exc.response.status_code if exc.response is not None else ""
            if status == 400 and not informed_bad_request:
                issues.append(
                    SearchIssue(
                        "pncp",
                        "PNCP recusou uma combinacao de filtros; foram tentadas consultas alternativas.",
                        "info",
                    )
                )
                informed_bad_request = True
        except requests.RequestException as exc:
            issues.append(SearchIssue("pncp", f"Falha ao consultar PNCP: {exc}"))
            continue
    return None, issues


def fetch_pncp_item_records(publication: dict[str, Any], timeout: int) -> tuple[list[dict[str, Any]], list[SearchIssue]]:
    numero_controle = get_text(publication, ("numeroControlePNCP", "numeroControlePncp", "id"))
    parsed = parse_numero_controle_pncp(numero_controle)
    if not parsed:
        return [], []

    issues: list[SearchIssue] = []
    for template in PNCP_CONSULTA_ITEM_URLS:
        url = template.format(**parsed)
        try:
            payload = request_json(url, timeout=timeout)
        except requests.RequestException as exc:
            issues.append(SearchIssue("pncp", f"Falha ao consultar itens PNCP em {url}: {exc}"))
            continue
        records = get_results(payload if isinstance(payload, dict) else {"data": payload})
        if records:
            enriched = []
            for record in records:
                merged = {**publication, **record}
                merged.setdefault("numeroControlePNCP", numero_controle)
                enriched.append(merged)
            return enriched, issues
    return [], issues


def build_source_candidate(item: dict[str, Any], record: dict[str, Any]) -> dict[str, Any] | None:
    unit_price = find_first_value(record, UNIT_PRICE_KEYS)
    if not unit_price:
        return None

    context = get_text(
        record,
        (
            "descricao",
            "descricaoCompleta",
            "descricaoItem",
            "materialOuServicoNome",
            "objetoCompra",
            "objeto",
        ),
        default=get_text(record, ("nome",), ""),
    )
    relation = semantic_relation(item["description"], context)
    return {
        "basket_item_id": item["id"],
        "source_type": "pncp",
        "origin": "PNCP",
        "url": pncp_publication_link(record),
        "source_date": get_text(record, ("dataPublicacaoPncp", "dataPublicacao", "dataAberturaProposta")),
        "organization": get_text(record, ("orgaoEntidadeRazaoSocial", "nomeOrgao", "unidadeOrgaoNomeUnidade"), "Nao informado"),
        "modality": get_text(record, ("modalidadeNome", "modalidade"), ""),
        "process_number": get_text(record, ("processo", "numeroCompra", "numeroProcesso"), ""),
        "supplier": get_text(record, ("fornecedorNome", "nomeFornecedor", "razaoSocialFornecedor"), ""),
        "contracting_context": context or item["description"],
        "unit_price": unit_price,
        "quantity": as_float(get_text(record, ("quantidade", "quantidadeItem"), "1")) or 1,
        "unit": get_text(record, ("unidadeMedida", "unidadeFornecimento"), item["unit"]),
        "notes": f"Busca automatica PNCP. Compatibilidade: {relation['status']} ({relation['score']:.2f}).",
        "raw_payload": record,
    }


def search_pncp_item(
    item: dict[str, Any],
    *,
    query: str = "",
    start_date: str = "",
    end_date: str = "",
    page_size: int = 20,
    timeout: int = 12,
) -> tuple[list[dict[str, Any]], list[SearchIssue]]:
    start, end = default_period()
    start_date = compact_digits(start_date) or start
    end_date = compact_digits(end_date) or end
    terms = normalize_query_text(query.strip() or " ".join(item.get("keywords") or []) or item["description"])
    params = {
        "dataInicial": start_date,
        "dataFinal": end_date,
        "pagina": 1,
        "tamanhoPagina": max(1, min(page_size, 10)),
    }
    query_params = {**params, "q": terms}
    modality_variants = [
        {**params, "codigoModalidadeContratacao": modality}
        for modality in PNCP_MODALITY_FALLBACKS
    ]
    issues: list[SearchIssue] = []
    payload, request_issues = request_first_success(
        PNCP_PUBLICATION_URL,
        [query_params, *modality_variants, params],
        timeout,
    )
    issues.extend(request_issues)
    if payload is None:
        return [], issues or [SearchIssue("pncp", "PNCP nao retornou dados para os parametros informados.")]

    records = get_results(payload if isinstance(payload, dict) else {"data": payload})
    candidates = []
    detail_issues: list[SearchIssue] = []
    for record in records:
        candidate = build_source_candidate(item, record)
        if candidate and text_matches_item(item, record, terms):
            candidates.append(candidate)
            continue
        item_records, item_issues = fetch_pncp_item_records(record, timeout)
        detail_issues.extend(item_issues)
        for item_record in item_records:
            relation = semantic_relation(item["description"], get_text(item_record, ("descricao", "descricaoItem", "descricaoCompleta", "objetoCompra")))
            if relation["status"] == "divergente":
                continue
            if not text_matches_item(item, item_record, terms):
                continue
            item_candidate = build_source_candidate(item, item_record)
            if item_candidate:
                candidates.append(item_candidate)
    if records and not candidates:
        issues.append(
            SearchIssue(
                "pncp",
                "PNCP retornou contratacoes, mas nao trouxe valor unitario estruturado para os itens consultados.",
            )
        )
    return deduplicate_candidates(candidates), issues + detail_issues


def search_compras_gov_item(
    item: dict[str, Any],
    *,
    query: str = "",
    page_size: int = 20,
    timeout: int = 12,
) -> tuple[list[dict[str, Any]], list[SearchIssue]]:
    return [], [
        SearchIssue(
            "compras_gov",
            "Conector Compras.gov pausado: os endpoints publicos antigos passaram a retornar 404. A busca continua pelo PNCP.",
            "info",
        )
    ]


def deduplicate_candidates(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str, float]] = set()
    unique = []
    for candidate in candidates:
        key = (
            candidate.get("source_type", ""),
            candidate.get("url", ""),
            float(candidate.get("unit_price") or 0),
        )
        if key in seen:
            continue
        seen.add(key)
        unique.append(candidate)
    return unique
