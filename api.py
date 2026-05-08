from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from src.db import (
    create_fonte,
    create_processo,
    delete_fonte,
    export_snapshot,
    get_processo,
    init_db,
    list_fontes,
    list_processos,
    resumo_pesquisa,
)


app = FastAPI(title="Projeto Icaro")


class ProcessoRequest(BaseModel):
    titulo: str
    descricao_objeto: str
    categoria: str = ""
    unidade: str = "unidade"
    quantidade: float = 1
    local_execucao: str = ""
    prazo: str = ""
    responsavel: str = ""
    status: str = "rascunho"


class FontePrecoRequest(BaseModel):
    processo_id: int
    fonte_tipo: str = "pncp"
    descricao_item: str
    valor_unitario: float = Field(gt=0)
    quantidade: float = 1
    orgao: str = ""
    fornecedor: str = ""
    uf: str = ""
    municipio: str = ""
    url: str = ""
    data_referencia: str = ""
    data_acesso: str = ""
    aproveitada: bool = True
    justificativa_descarte: str = ""
    observacoes: str = ""


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/", response_class=HTMLResponse)
def dashboard() -> str:
    return open("dashboard.html", encoding="utf-8").read()


@app.get("/health")
def health() -> dict[str, str]:
    init_db()
    return {"status": "ok"}


@app.get("/processos")
def processos() -> list[dict[str, Any]]:
    return list_processos()


@app.post("/processos")
def criar_processo(req: ProcessoRequest) -> dict[str, Any]:
    processo_id = create_processo(req.model_dump())
    return {"id": processo_id, "processo": get_processo(processo_id)}


@app.get("/processos/{processo_id}")
def obter_processo(processo_id: int) -> dict[str, Any]:
    processo = get_processo(processo_id)
    if not processo:
        raise HTTPException(status_code=404, detail="Processo nao encontrado")
    return {
        "processo": processo,
        "fontes": list_fontes(processo_id),
        "resumo": resumo_pesquisa(processo_id),
    }


@app.post("/fontes")
def criar_fonte(req: FontePrecoRequest) -> dict[str, Any]:
    if not get_processo(req.processo_id):
        raise HTTPException(status_code=404, detail="Processo nao encontrado")
    fonte_id = create_fonte(req.model_dump())
    return {
        "id": fonte_id,
        "fontes": list_fontes(req.processo_id),
        "resumo": resumo_pesquisa(req.processo_id),
    }


@app.delete("/fontes/{fonte_id}")
def excluir_fonte(fonte_id: int) -> dict[str, Any]:
    deleted = delete_fonte(fonte_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Fonte nao encontrada")
    return {"status": "deleted", "id": fonte_id}


@app.get("/processos/{processo_id}/resumo")
def resumo(processo_id: int) -> dict[str, Any]:
    if not get_processo(processo_id):
        raise HTTPException(status_code=404, detail="Processo nao encontrado")
    return resumo_pesquisa(processo_id)


@app.get("/processos/{processo_id}/snapshot")
def snapshot(processo_id: int) -> dict[str, Any]:
    data = export_snapshot(processo_id)
    if not data:
        raise HTTPException(status_code=404, detail="Processo nao encontrado")
    return data

