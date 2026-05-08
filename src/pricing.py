from __future__ import annotations

from statistics import mean, median


def calcular_resumo_precos(valores: list[float]) -> dict[str, float | int | None]:
    validos = sorted(float(v) for v in valores if v and float(v) > 0)
    if not validos:
        return {
            "amostras": 0,
            "menor": None,
            "maior": None,
            "media": None,
            "mediana": None,
        }

    return {
        "amostras": len(validos),
        "menor": min(validos),
        "maior": max(validos),
        "media": mean(validos),
        "mediana": median(validos),
    }


def sugerir_preco_estimado(valores: list[float], metodo: str = "mediana") -> float | None:
    resumo = calcular_resumo_precos(valores)
    if not resumo["amostras"]:
        return None

    if metodo == "menor":
        return resumo["menor"]
    if metodo == "media":
        return resumo["media"]
    return resumo["mediana"]

