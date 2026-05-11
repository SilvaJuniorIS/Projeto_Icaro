from __future__ import annotations

from statistics import mean, median


def _percentil_ordenado(valores: list[float], percentil: float) -> float:
    if len(valores) == 1:
        return valores[0]

    posicao = (len(valores) - 1) * percentil
    base = int(posicao)
    fracao = posicao - base
    if base + 1 < len(valores):
        return valores[base] + fracao * (valores[base + 1] - valores[base])
    return valores[base]


def calcular_resumo_precos(valores: list[float]) -> dict[str, float | int | None]:
    validos = sorted(float(v) for v in valores if v and float(v) > 0)
    if not validos:
        return {
            "amostras": 0,
            "menor": None,
            "maior": None,
            "media": None,
            "mediana": None,
            "q1": None,
            "q3": None,
            "limite_inferior": None,
            "limite_superior": None,
            "outliers": 0,
        }

    q1 = _percentil_ordenado(validos, 0.25)
    q3 = _percentil_ordenado(validos, 0.75)
    iqr = q3 - q1
    limite_inferior = q1 - 1.5 * iqr
    limite_superior = q3 + 1.5 * iqr
    outliers = [
        valor
        for valor in validos
        if len(validos) >= 4 and (valor < limite_inferior or valor > limite_superior)
    ]

    return {
        "amostras": len(validos),
        "menor": min(validos),
        "maior": max(validos),
        "media": mean(validos),
        "mediana": median(validos),
        "q1": q1,
        "q3": q3,
        "limite_inferior": limite_inferior if len(validos) >= 4 else None,
        "limite_superior": limite_superior if len(validos) >= 4 else None,
        "outliers": len(outliers),
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
