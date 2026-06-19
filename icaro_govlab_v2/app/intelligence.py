from __future__ import annotations

import math
import re
import statistics
import unicodedata
from typing import Any


STOPWORDS = {
    "de",
    "da",
    "do",
    "das",
    "dos",
    "para",
    "com",
    "sem",
    "por",
    "em",
    "unidade",
    "material",
    "servico",
    "fornecimento",
}


def normalize_text(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text or "")
    plain = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    normalized = plain.lower()
    normalized = re.sub(r"\br(\d{2})\b", r"r\1 \1", normalized)
    normalized = re.sub(r"\baro\s+(\d{2})\b", r"aro \1 r\1", normalized)
    return normalized


def tokens(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]+", normalize_text(text))
        if len(token) >= 2 and token not in STOPWORDS
    }


def suggest_keywords(description: str, technical_notes: str = "") -> list[str]:
    joined = f"{description} {technical_notes}".strip()
    ordered: list[str] = []
    for token in re.findall(r"[a-z0-9]+", normalize_text(joined)):
        if len(token) < 2 or token in STOPWORDS or token in ordered:
            continue
        ordered.append(token)
    return ordered[:12]


def similarity(left: str, right: str) -> float:
    left_tokens = tokens(left)
    right_tokens = tokens(right)
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / len(left_tokens | right_tokens)


def semantic_relation(left: str, right: str) -> dict[str, Any]:
    score = similarity(left, right)
    if score >= 0.7:
        status = "equivalente"
    elif score >= 0.30:
        status = "relacionado"
    else:
        status = "divergente"
    return {
        "score": round(score, 4),
        "status": status,
        "shared_terms": sorted(tokens(left) & tokens(right)),
        "left_only": sorted(tokens(left) - tokens(right)),
        "right_only": sorted(tokens(right) - tokens(left)),
    }


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    k = (len(ordered) - 1) * p
    floor = math.floor(k)
    ceil = math.ceil(k)
    if floor == ceil:
        return ordered[int(k)]
    return ordered[floor] * (ceil - k) + ordered[ceil] * (k - floor)


def detect_outliers(values: list[float]) -> set[float]:
    if len(values) < 4:
        return set()
    q1 = percentile(values, 0.25)
    q3 = percentile(values, 0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    return {value for value in values if value < lower or value > upper}


def calculation_summary(values: list[float]) -> dict[str, Any]:
    accepted = [float(value) for value in values if float(value) > 0]
    outliers = detect_outliers(accepted)
    clean = [value for value in accepted if value not in outliers]
    basis = clean or accepted
    if not basis:
        return {
            "mean": None,
            "median": None,
            "min_price": None,
            "max_price": None,
            "deviation": None,
            "source_count": len(values),
            "accepted_count": 0,
            "outliers": sorted(outliers),
        }
    mean = statistics.fmean(basis)
    median = statistics.median(basis)
    deviation = statistics.pstdev(basis) if len(basis) > 1 else 0.0
    return {
        "mean": round(mean, 2),
        "median": round(median, 2),
        "min_price": round(min(basis), 2),
        "max_price": round(max(basis), 2),
        "deviation": round(deviation, 2),
        "source_count": len(values),
        "accepted_count": len(basis),
        "outliers": sorted(outliers),
    }
