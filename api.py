from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from src.config import BASE_DIR
from src.checklist import gerar_checklist
from src.comparability import avaliar_comparabilidade
from src.db import (
    create_ata,
    create_fonte,
    create_processo,
    delete_ata,
    delete_fonte,
    export_snapshot,
    get_processo,
    init_db,
    list_atas,
    list_fontes,
    list_processos,
    resumo_atas,
    resumo_pesquisa,
)
from src.pncp import buscar_contratacoes
from src.reports import gerar_relatorio_docx, gerar_relatorio_html, gerar_relatorio_markdown, gerar_xlsx_processo


app = FastAPI(title="Icaro")
app.mount("/assets", StaticFiles(directory=BASE_DIR / "assets"), name="assets")


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


class AtaRequest(BaseModel):
    processo_id: int
    numero: str = ""
    orgao_gerenciador: str = ""
    fornecedor: str = ""
    objeto: str
    item: str = ""
    valor_unitario: float = Field(ge=0)
    vigencia_inicio: str = ""
    vigencia_fim: str = ""
    quantidade_registrada: float = 0
    quantidade_disponivel_estimativa: float = 0
    url: str = ""
    aderencia: str = "indefinida"
    observacoes: str = ""


class PncpBuscaRequest(BaseModel):
    termo: str
    data_inicial: str = ""
    data_final: str = ""
    pagina: int = 1
    tamanho_pagina: int = 10


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
        "atas": list_atas(processo_id),
        "resumo": resumo_pesquisa(processo_id),
        "resumo_atas": resumo_atas(processo_id),
    }


@app.get("/processos/{processo_id}/checklist")
def checklist(processo_id: int) -> dict[str, Any]:
    data = export_snapshot(processo_id)
    if not data:
        raise HTTPException(status_code=404, detail="Processo nao encontrado")
    itens = gerar_checklist(data)
    progresso = itens[0]["progresso"] if itens else {"concluidos": 0, "total": 0}
    return {"checklist": itens, "progresso": progresso}


@app.get("/processos/{processo_id}/comparabilidade")
def comparabilidade(processo_id: int) -> dict[str, Any]:
    data = export_snapshot(processo_id)
    if not data:
        raise HTTPException(status_code=404, detail="Processo nao encontrado")
    return avaliar_comparabilidade(data)


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


@app.post("/atas")
def criar_ata(req: AtaRequest) -> dict[str, Any]:
    if not get_processo(req.processo_id):
        raise HTTPException(status_code=404, detail="Processo nao encontrado")
    ata_id = create_ata(req.model_dump())
    return {
        "id": ata_id,
        "atas": list_atas(req.processo_id),
        "resumo_atas": resumo_atas(req.processo_id),
    }


@app.delete("/atas/{ata_id}")
def excluir_ata(ata_id: int) -> dict[str, Any]:
    deleted = delete_ata(ata_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Ata nao encontrada")
    return {"status": "deleted", "id": ata_id}


@app.get("/processos/{processo_id}/atas")
def atas(processo_id: int) -> dict[str, Any]:
    if not get_processo(processo_id):
        raise HTTPException(status_code=404, detail="Processo nao encontrado")
    return {
        "atas": list_atas(processo_id),
        "resumo_atas": resumo_atas(processo_id),
    }


@app.post("/pncp/buscar")
def pncp_buscar(req: PncpBuscaRequest) -> dict[str, Any]:
    return buscar_contratacoes(
        termo=req.termo,
        data_inicial=req.data_inicial or None,
        data_final=req.data_final or None,
        pagina=req.pagina,
        tamanho_pagina=req.tamanho_pagina,
    )


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


@app.get("/processos/{processo_id}/export/xlsx")
def exportar_xlsx(processo_id: int) -> FileResponse:
    path = gerar_xlsx_processo(processo_id)
    if not path:
        raise HTTPException(status_code=404, detail="Processo nao encontrado")
    return FileResponse(
        path,
        filename=path.name,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@app.get("/processos/{processo_id}/export/md")
def exportar_relatorio_md(processo_id: int) -> FileResponse:
    path = gerar_relatorio_markdown(processo_id)
    if not path:
        raise HTTPException(status_code=404, detail="Processo nao encontrado")
    return FileResponse(
        path,
        filename=path.name,
        media_type="text/markdown; charset=utf-8",
    )


@app.get("/processos/{processo_id}/export/html")
def exportar_relatorio_html(processo_id: int) -> FileResponse:
    path = gerar_relatorio_html(processo_id)
    if not path:
        raise HTTPException(status_code=404, detail="Processo nao encontrado")
    return FileResponse(path, filename=path.name, media_type="text/html; charset=utf-8")


@app.get("/processos/{processo_id}/export/docx")
def exportar_relatorio_docx(processo_id: int) -> FileResponse:
    path = gerar_relatorio_docx(processo_id)
    if not path:
        raise HTTPException(status_code=404, detail="Processo nao encontrado")
    return FileResponse(
        path,
        filename=path.name,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
