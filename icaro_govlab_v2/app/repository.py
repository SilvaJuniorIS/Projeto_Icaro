from __future__ import annotations

from pathlib import Path
from typing import Any

from app.db import DB_PATH, connect, init_db, json_dumps, json_loads, now_iso, row_to_dict
from app.intelligence import calculation_summary, semantic_relation, suggest_keywords


REQUIRED_SOURCE_FIELDS = [
    "origin",
    "url",
    "organization",
    "contracting_context",
]


def make_basket_code(basket_id: int, timestamp: str) -> str:
    date_part = timestamp[:10].replace("-", "")
    return f"ICR-{date_part}-{basket_id:05d}"


def create_basket(payload: dict[str, Any], db_path: Path | str = DB_PATH) -> dict[str, Any]:
    init_db(db_path)
    timestamp = now_iso()
    history = [{"event": "basket_created", "at": timestamp, "message": "Cesta criada."}]
    with connect(db_path) as conn:
        cur = conn.execute(
            """
            INSERT INTO baskets (
                basket_code, title, central_object, category, contracting_context, status,
                version, history_json, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "",
                payload["title"],
                payload["central_object"],
                payload.get("category", ""),
                payload.get("contracting_context", ""),
                payload.get("status", "draft"),
                1,
                json_dumps(history),
                timestamp,
                timestamp,
            ),
        )
        basket_id = int(cur.lastrowid)
        basket_code = payload.get("basket_code") or make_basket_code(basket_id, timestamp)
        conn.execute(
            "UPDATE baskets SET basket_code = ? WHERE id = ?",
            (basket_code, basket_id),
        )
    return get_basket(basket_id, db_path) or {}


def list_baskets(db_path: Path | str = DB_PATH) -> list[dict[str, Any]]:
    init_db(db_path)
    with connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT b.*, COUNT(i.id) AS item_count
            FROM baskets b
            LEFT JOIN basket_items i ON i.basket_id = b.id
            GROUP BY b.id
            ORDER BY b.updated_at DESC, b.id DESC
            """
        ).fetchall()
    baskets = [dict(row) for row in rows]
    for basket in baskets:
        if not basket.get("basket_code"):
            basket["basket_code"] = make_basket_code(int(basket["id"]), basket["created_at"])
    return baskets


def get_basket(basket_id: int, db_path: Path | str = DB_PATH) -> dict[str, Any] | None:
    init_db(db_path)
    with connect(db_path) as conn:
        basket = row_to_dict(conn.execute("SELECT * FROM baskets WHERE id = ?", (basket_id,)).fetchone())
    if basket:
        if not basket.get("basket_code"):
            basket["basket_code"] = make_basket_code(int(basket["id"]), basket["created_at"])
        basket["history"] = json_loads(basket.pop("history_json", "[]"), [])
    return basket


def create_basket_item(payload: dict[str, Any], db_path: Path | str = DB_PATH) -> dict[str, Any]:
    init_db(db_path)
    timestamp = now_iso()
    keywords = payload.get("keywords") or suggest_keywords(payload["description"], payload.get("technical_notes", ""))
    with connect(db_path) as conn:
        basket = conn.execute("SELECT id FROM baskets WHERE id = ?", (int(payload["basket_id"]),)).fetchone()
        if not basket:
            raise ValueError("Cesta nao encontrada")
        cur = conn.execute(
            """
            INSERT INTO basket_items (
                basket_id, lot_group, description, unit, quantity, catmat_catser,
                keywords_json, classifications_json, technical_notes,
                search_history_json, status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                int(payload["basket_id"]),
                payload.get("lot_group", ""),
                payload["description"],
                payload["unit"],
                float(payload.get("quantity") or 1),
                payload.get("catmat_catser", ""),
                json_dumps(keywords),
                json_dumps(payload.get("classifications") or []),
                payload.get("technical_notes", ""),
                json_dumps([]),
                payload.get("status", "pending"),
                timestamp,
                timestamp,
            ),
        )
        conn.execute("UPDATE baskets SET updated_at = ? WHERE id = ?", (timestamp, int(payload["basket_id"])))
        item_id = int(cur.lastrowid)
    return get_basket_item(item_id, db_path) or {}


def get_basket_item(item_id: int, db_path: Path | str = DB_PATH) -> dict[str, Any] | None:
    init_db(db_path)
    with connect(db_path) as conn:
        item = row_to_dict(conn.execute("SELECT * FROM basket_items WHERE id = ?", (item_id,)).fetchone())
    if item:
        item["keywords"] = json_loads(item.pop("keywords_json", "[]"), [])
        item["classifications"] = json_loads(item.pop("classifications_json", "[]"), [])
        item["search_history"] = json_loads(item.pop("search_history_json", "[]"), [])
    return item


def list_basket_items(basket_id: int, db_path: Path | str = DB_PATH) -> list[dict[str, Any]]:
    init_db(db_path)
    with connect(db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM basket_items WHERE basket_id = ? ORDER BY lot_group, id",
            (basket_id,),
        ).fetchall()
    items = []
    for row in rows:
        item = dict(row)
        item["keywords"] = json_loads(item.pop("keywords_json", "[]"), [])
        item["classifications"] = json_loads(item.pop("classifications_json", "[]"), [])
        item["search_history"] = json_loads(item.pop("search_history_json", "[]"), [])
        items.append(item)
    return items


def validate_source_context(payload: dict[str, Any]) -> list[str]:
    missing = [field for field in REQUIRED_SOURCE_FIELDS if not str(payload.get(field) or "").strip()]
    if not payload.get("unit_price") or float(payload.get("unit_price") or 0) <= 0:
        missing.append("unit_price")
    if not payload.get("quantity") or float(payload.get("quantity") or 0) <= 0:
        missing.append("quantity")
    return missing


def create_item_source(payload: dict[str, Any], db_path: Path | str = DB_PATH) -> dict[str, Any]:
    init_db(db_path)
    missing = validate_source_context(payload)
    if missing:
        raise ValueError("Fonte sem contexto minimo: " + ", ".join(missing))
    timestamp = now_iso()
    with connect(db_path) as conn:
        item = conn.execute(
            "SELECT * FROM basket_items WHERE id = ?",
            (int(payload["basket_item_id"]),),
        ).fetchone()
        if not item:
            raise ValueError("Item nao encontrado")
        relation = semantic_relation(item["description"], payload.get("contracting_context", ""))
        source_cur = conn.execute(
            """
            INSERT INTO item_sources (
                basket_id, basket_item_id, source_type, origin, url, source_date,
                access_date, organization, modality, process_number, supplier,
                contracting_context, raw_payload_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                int(item["basket_id"]),
                int(payload["basket_item_id"]),
                payload["source_type"],
                payload["origin"],
                payload["url"],
                payload.get("source_date", ""),
                payload.get("access_date") or timestamp,
                payload["organization"],
                payload.get("modality", ""),
                payload.get("process_number", ""),
                payload.get("supplier", ""),
                payload["contracting_context"],
                json_dumps(payload.get("raw_payload") or {}),
                timestamp,
            ),
        )
        source_id = int(source_cur.lastrowid)
        conn.execute(
            """
            INSERT INTO source_prices (
                item_source_id, unit_price, total_price, quantity, unit,
                accepted, discard_reason, notes, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                source_id,
                float(payload["unit_price"]),
                payload.get("total_price"),
                float(payload.get("quantity") or 1),
                payload.get("unit") or item["unit"],
                1 if payload.get("accepted", True) else 0,
                payload.get("discard_reason", ""),
                payload.get("notes", ""),
                timestamp,
            ),
        )
        validation_status = "ok" if relation["status"] != "divergente" else "warning"
        conn.execute(
            """
            INSERT INTO source_validations (
                item_source_id, validation_type, status, message, created_at
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                source_id,
                "semantic_similarity",
                validation_status,
                f"Similaridade {relation['score']:.2f}: {relation['status']}",
                timestamp,
            ),
        )
        conn.execute("UPDATE baskets SET updated_at = ? WHERE id = ?", (timestamp, int(item["basket_id"])))
    return get_item_source(source_id, db_path) or {}


def get_item_source(source_id: int, db_path: Path | str = DB_PATH) -> dict[str, Any] | None:
    init_db(db_path)
    with connect(db_path) as conn:
        source = row_to_dict(conn.execute("SELECT * FROM item_sources WHERE id = ?", (source_id,)).fetchone())
        if not source:
            return None
        prices = conn.execute("SELECT * FROM source_prices WHERE item_source_id = ?", (source_id,)).fetchall()
        validations = conn.execute("SELECT * FROM source_validations WHERE item_source_id = ?", (source_id,)).fetchall()
    source["prices"] = [dict(row) for row in prices]
    source["validations"] = [dict(row) for row in validations]
    source["raw_payload"] = json_loads(source.pop("raw_payload_json", "{}"), {})
    return source


def list_sources_for_item(item_id: int, db_path: Path | str = DB_PATH) -> list[dict[str, Any]]:
    init_db(db_path)
    with connect(db_path) as conn:
        rows = conn.execute(
            "SELECT id FROM item_sources WHERE basket_item_id = ? ORDER BY id DESC",
            (item_id,),
        ).fetchall()
    return [source for row in rows if (source := get_item_source(int(row["id"]), db_path))]


def generate_calculation_memory(basket_id: int, db_path: Path | str = DB_PATH) -> dict[str, Any]:
    init_db(db_path)
    timestamp = now_iso()
    item_memories: list[dict[str, Any]] = []
    basket_estimates: list[float] = []
    with connect(db_path) as conn:
        items = conn.execute("SELECT * FROM basket_items WHERE basket_id = ?", (basket_id,)).fetchall()
        for item in items:
            price_rows = conn.execute(
                """
                SELECT sp.unit_price
                FROM source_prices sp
                JOIN item_sources src ON src.id = sp.item_source_id
                WHERE src.basket_item_id = ? AND sp.accepted = 1
                """,
                (item["id"],),
            ).fetchall()
            values = [float(row["unit_price"]) for row in price_rows]
            summary = calculation_summary(values)
            estimated_unit = summary["median"] or summary["mean"] or 0
            basket_estimates.append(float(estimated_unit) * float(item["quantity"] or 1))
            payload = {"item": dict(item), "values": values, "summary": summary}
            conn.execute(
                """
                INSERT INTO calculation_memories (
                    basket_id, basket_item_id, scope, mean, median, min_price,
                    max_price, deviation, source_count, accepted_count,
                    outliers_json, methodology, payload_json, generated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    basket_id,
                    item["id"],
                    "item",
                    summary["mean"],
                    summary["median"],
                    summary["min_price"],
                    summary["max_price"],
                    summary["deviation"],
                    summary["source_count"],
                    summary["accepted_count"],
                    json_dumps(summary["outliers"]),
                    "Mediana por item com deteccao IQR de outliers.",
                    json_dumps(payload),
                    timestamp,
                ),
            )
            item_memories.append(payload)
        basket_summary = calculation_summary(basket_estimates)
        conn.execute(
            """
            INSERT INTO calculation_memories (
                basket_id, scope, mean, median, min_price, max_price,
                deviation, source_count, accepted_count, outliers_json,
                methodology, payload_json, generated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                basket_id,
                "basket",
                basket_summary["mean"],
                basket_summary["median"],
                basket_summary["min_price"],
                basket_summary["max_price"],
                basket_summary["deviation"],
                basket_summary["source_count"],
                basket_summary["accepted_count"],
                json_dumps(basket_summary["outliers"]),
                "Soma dos valores estimados por item; cada item e calculado individualmente.",
                json_dumps({"items": item_memories, "estimated_totals": basket_estimates}),
                timestamp,
            ),
        )
    return {
        "basket_id": basket_id,
        "generated_at": timestamp,
        "items": item_memories,
        "basket": basket_summary,
    }


def export_markdown_report(basket_id: int, db_path: Path | str = DB_PATH) -> str:
    basket = get_basket(basket_id, db_path)
    if not basket:
        raise ValueError("Cesta nao encontrada")
    memory = generate_calculation_memory(basket_id, db_path)
    lines = [
        f"# Pesquisa de mercado defensavel - {basket['title']}",
        "",
        f"Objeto central: {basket['central_object']}",
        "",
        "## Metodologia",
        "",
        "A pesquisa foi estruturada por cesta dinamica, com calculo individual por item, fontes rastreaveis e memoria de calculo auditavel.",
        "",
        "## Itens e memoria de calculo",
        "",
        "| Item | Fontes aceitas | Media | Mediana | Menor | Maior | Desvio |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for item_payload in memory["items"]:
        item = item_payload["item"]
        summary = item_payload["summary"]
        lines.append(
            f"| {item['description']} | {summary['accepted_count']} | {summary['mean']} | "
            f"{summary['median']} | {summary['min_price']} | {summary['max_price']} | {summary['deviation']} |"
        )
    lines.extend(
        [
            "",
            "## Valor estimado da cesta",
            "",
            f"- Media dos totais por item: {memory['basket']['mean']}",
            f"- Mediana dos totais por item: {memory['basket']['median']}",
            f"- Fontes consideradas: {sum(item['summary']['accepted_count'] for item in memory['items'])}",
            "",
            "## Rastreabilidade",
            "",
            "Cada preco deve permanecer associado a origem, link, orgao, fornecedor, modalidade, numero do processo e contexto da contratacao.",
        ]
    )
    return "\n".join(lines)
