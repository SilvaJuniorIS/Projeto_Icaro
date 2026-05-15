from __future__ import annotations

import re
import unicodedata


def normalizar_texto(texto: str) -> str:
    decomposed = unicodedata.normalize("NFKD", texto or "")
    sem_acentos = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    return sem_acentos.lower()


def tokens_texto(texto: str, tamanho_minimo: int = 3) -> set[str]:
    normalizado = normalizar_texto(texto)
    return {
        token
        for token in re.findall(r"[a-z0-9]+", normalizado)
        if len(token) >= tamanho_minimo
    }


def palavras_texto(texto: str, tamanho_minimo: int = 3) -> list[str]:
    normalizado = normalizar_texto(texto)
    return [
        token
        for token in re.findall(r"[a-z0-9]+", normalizado)
        if len(token) >= tamanho_minimo
    ]
