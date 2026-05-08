from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal


FonteTipo = Literal[
    "pncp",
    "ata_registro_precos",
    "painel_precos",
    "fornecedor",
    "midia_especializada",
    "outro",
]


@dataclass
class ObjetoContratacao:
    descricao: str
    categoria: str = ""
    unidade: str = "unidade"
    quantidade: float = 1
    local_execucao: str = ""
    prazo: str = ""
    observacoes: str = ""


@dataclass
class FontePreco:
    fonte_tipo: FonteTipo
    descricao_item: str
    valor_unitario: float
    quantidade: float = 1
    orgao: str = ""
    fornecedor: str = ""
    uf: str = ""
    municipio: str = ""
    url: str = ""
    data_referencia: str = ""
    data_acesso: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    aproveitada: bool = True
    justificativa_descarte: str = ""


@dataclass
class AtaRegistroPreco:
    numero: str
    orgao_gerenciador: str
    fornecedor: str
    objeto: str
    item: str
    valor_unitario: float
    vigencia_inicio: str = ""
    vigencia_fim: str = ""
    quantidade_registrada: float = 0
    quantidade_disponivel_estimativa: float = 0
    url: str = ""
    aderencia: Literal["alta", "media", "baixa", "indefinida"] = "indefinida"

