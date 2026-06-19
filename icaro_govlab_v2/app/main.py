from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles

from app.db import BASE_DIR, DB_PATH, connect, init_db, now_iso
from app.intelligence import normalize_text, semantic_relation
from app.repository import (
    create_basket,
    create_basket_item,
    create_item_source,
    export_markdown_report,
    generate_calculation_memory,
    get_basket,
    get_basket_item,
    json_dumps,
    list_basket_items,
    list_baskets,
    list_sources_for_item,
)
from app.schemas import (
    AutomatedSearchRequest,
    BasketItemRequest,
    BasketRequest,
    ItemSourceRequest,
    SearchLogRequest,
)
from app.search import search_compras_gov_item, search_pncp_item


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Icaro GovLab v2", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=BASE_DIR / "app" / "static"), name="static")


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return (BASE_DIR / "app" / "static" / "index.html").read_text(encoding="utf-8")


@app.get("/health")
def health() -> dict[str, str]:
    init_db()
    return {"status": "ok", "architecture": "basket-item-source-price-memory"}


@app.post("/api/baskets")
def api_create_basket(req: BasketRequest) -> dict[str, Any]:
    return {"basket": create_basket(req.model_dump())}


@app.get("/api/baskets")
def api_list_baskets() -> dict[str, Any]:
    return {"baskets": list_baskets()}


@app.get("/api/baskets/{basket_id}")
def api_get_basket(basket_id: int) -> dict[str, Any]:
    basket = get_basket(basket_id)
    if not basket:
        raise HTTPException(status_code=404, detail="Cesta nao encontrada")
    items = list_basket_items(basket_id)
    return {"basket": basket, "items": items}


@app.post("/api/items")
def api_create_item(req: BasketItemRequest) -> dict[str, Any]:
    try:
        return {"item": create_basket_item(req.model_dump())}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/api/items/{item_id}")
def api_get_item(item_id: int) -> dict[str, Any]:
    item = get_basket_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item nao encontrado")
    return {"item": item, "sources": list_sources_for_item(item_id)}


@app.post("/api/items/{item_id}/search")
def api_search_item_values(item_id: int, req: AutomatedSearchRequest) -> dict[str, Any]:
    item = get_basket_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item nao encontrado")

    all_candidates: list[dict[str, Any]] = []
    saved_sources: list[dict[str, Any]] = []
    issues: list[dict[str, str]] = []
    requested_sources = set(req.source_types or ["pncp"])

    if "pncp" in requested_sources:
        candidates, pncp_issues = search_pncp_item(
            item,
            query=req.query,
            start_date=req.start_date,
            end_date=req.end_date,
            page_size=req.page_size,
        )
        all_candidates.extend(candidates)
        issues.extend(issue.__dict__ for issue in pncp_issues)

    if "compras_gov" in requested_sources:
        candidates, compras_issues = search_compras_gov_item(
            item,
            query=req.query,
            page_size=req.page_size,
        )
        all_candidates.extend(candidates)
        issues.extend(issue.__dict__ for issue in compras_issues)

    unsupported = requested_sources - {"pncp", "compras_gov"}
    for source_type in sorted(unsupported):
        issues.append(
            {
                "source_type": source_type,
                "message": "Fonte prevista na arquitetura, mas conector automatico ainda nao implementado.",
            }
        )

    if req.save_results:
        for candidate in all_candidates:
            try:
                saved_sources.append(create_item_source(candidate))
            except ValueError as exc:
                issues.append({"source_type": candidate["source_type"], "message": str(exc)})

    with connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO search_logs (
                basket_id, basket_item_id, source_type, query, normalized_query,
                status, results_count, error, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item["basket_id"],
                item_id,
                ",".join(sorted(requested_sources)),
                req.query or item["description"],
                normalize_text(req.query or item["description"]),
                "completed" if saved_sources or all_candidates else "completed_without_values",
                len(saved_sources) if req.save_results else len(all_candidates),
                "; ".join(issue["message"] for issue in issues),
                now_iso(),
            ),
        )

    return {
        "item": item,
        "candidates": all_candidates,
        "saved_sources": saved_sources,
        "issues": issues,
        "summary": {
            "message": "Busca concluida. O sistema salva somente resultados com valor unitario rastreavel.",
            "searched_sources": sorted(requested_sources),
            "saved_count": len(saved_sources),
            "candidate_count": len(all_candidates),
        },
    }


@app.post("/api/sources")
def api_create_source(req: ItemSourceRequest) -> dict[str, Any]:
    try:
        return {"source": create_item_source(req.model_dump())}
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/api/baskets/{basket_id}/calculate")
def api_calculate_basket(basket_id: int) -> dict[str, Any]:
    if not get_basket(basket_id):
        raise HTTPException(status_code=404, detail="Cesta nao encontrada")
    return {"memory": generate_calculation_memory(basket_id)}


@app.get("/api/baskets/{basket_id}/report.md", response_class=PlainTextResponse)
def api_report_markdown(basket_id: int) -> str:
    try:
        return export_markdown_report(basket_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/api/search-logs")
def api_search_log(req: SearchLogRequest) -> dict[str, Any]:
    payload = req.model_dump()
    normalized = payload.get("normalized_query") or normalize_text(payload["query"])
    with connect(DB_PATH) as conn:
        cur = conn.execute(
            """
            INSERT INTO search_logs (
                basket_id, basket_item_id, source_type, query, normalized_query,
                status, results_count, error, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload["basket_id"],
                payload.get("basket_item_id"),
                payload["source_type"],
                payload["query"],
                normalized,
                payload["status"],
                int(payload.get("results_count") or 0),
                payload.get("error", ""),
                now_iso(),
            ),
        )
        return {"id": int(cur.lastrowid)}


@app.post("/api/intelligence/compare")
def api_compare_descriptions(payload: dict[str, str]) -> dict[str, Any]:
    return semantic_relation(payload.get("left", ""), payload.get("right", ""))


@app.post("/api/normalization-rules")
def api_create_normalization_rule(payload: dict[str, str]) -> dict[str, Any]:
    with connect(DB_PATH) as conn:
        cur = conn.execute(
            """
            INSERT INTO normalization_rules (
                pattern, replacement, category, active, notes, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                payload["pattern"],
                payload["replacement"],
                payload.get("category", ""),
                1,
                payload.get("notes", ""),
                now_iso(),
            ),
        )
    return {"id": int(cur.lastrowid)}
