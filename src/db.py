from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime
import json
from pathlib import Path
from typing import Any

from src.config import DB_PATH
from src.pricing import calcular_resumo_precos, sugerir_preco_estimado


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


@contextmanager
def connect(db_path: Path | str = DB_PATH):
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db(db_path: Path | str = DB_PATH) -> None:
    with connect(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS processos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                descricao_objeto TEXT NOT NULL,
                categoria TEXT,
                unidade TEXT,
                quantidade REAL DEFAULT 1,
                local_execucao TEXT,
                prazo TEXT,
                responsavel TEXT,
                status TEXT NOT NULL DEFAULT 'rascunho',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS pesquisa_itens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                processo_id INTEGER NOT NULL,
                codigo TEXT,
                descricao TEXT NOT NULL,
                unidade TEXT,
                quantidade REAL DEFAULT 1,
                categoria TEXT,
                termo_busca TEXT,
                especificacao TEXT,
                status TEXT DEFAULT 'pendente',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(processo_id) REFERENCES processos(id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS fontes_preco (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                processo_id INTEGER NOT NULL,
                item_id INTEGER,
                fonte_tipo TEXT NOT NULL,
                descricao_item TEXT NOT NULL,
                valor_unitario REAL NOT NULL,
                quantidade REAL DEFAULT 1,
                orgao TEXT,
                fornecedor TEXT,
                uf TEXT,
                municipio TEXT,
                url TEXT,
                data_referencia TEXT,
                data_acesso TEXT NOT NULL,
                aproveitada INTEGER NOT NULL DEFAULT 1,
                justificativa_descarte TEXT,
                observacoes TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(processo_id) REFERENCES processos(id),
                FOREIGN KEY(item_id) REFERENCES pesquisa_itens(id)
            )
        """)
        columns = {
            row["name"]
            for row in conn.execute("PRAGMA table_info(fontes_preco)").fetchall()
        }
        if "item_id" not in columns:
            conn.execute("ALTER TABLE fontes_preco ADD COLUMN item_id INTEGER")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS atas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                processo_id INTEGER,
                numero TEXT,
                orgao_gerenciador TEXT,
                fornecedor TEXT,
                objeto TEXT,
                item TEXT,
                valor_unitario REAL DEFAULT 0,
                vigencia_inicio TEXT,
                vigencia_fim TEXT,
                quantidade_registrada REAL DEFAULT 0,
                quantidade_disponivel_estimativa REAL DEFAULT 0,
                url TEXT,
                aderencia TEXT DEFAULT 'indefinida',
                observacoes TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(processo_id) REFERENCES processos(id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS pncp_rascunhos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                processo_id INTEGER NOT NULL,
                item_id INTEGER,
                numero_controle TEXT,
                objeto TEXT NOT NULL,
                orgao TEXT,
                unidade TEXT,
                fornecedor TEXT,
                modalidade TEXT,
                situacao TEXT,
                data_publicacao TEXT,
                valor_estimado REAL DEFAULT 0,
                url TEXT,
                similaridade REAL DEFAULT 0,
                consulta TEXT,
                payload_json TEXT,
                status TEXT NOT NULL DEFAULT 'rascunho',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(processo_id) REFERENCES processos(id),
                FOREIGN KEY(item_id) REFERENCES pesquisa_itens(id)
            )
        """)
        pncp_columns = {
            row["name"]
            for row in conn.execute("PRAGMA table_info(pncp_rascunhos)").fetchall()
        }
        if "fornecedor" not in pncp_columns:
            conn.execute("ALTER TABLE pncp_rascunhos ADD COLUMN fornecedor TEXT")


def create_processo(payload: dict[str, Any], db_path: Path | str = DB_PATH) -> int:
    init_db(db_path)
    timestamp = now_iso()
    with connect(db_path) as conn:
        cur = conn.execute(
            """
            INSERT INTO processos (
                titulo, descricao_objeto, categoria, unidade, quantidade,
                local_execucao, prazo, responsavel, status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload["titulo"],
                payload["descricao_objeto"],
                payload.get("categoria", ""),
                payload.get("unidade", "unidade"),
                float(payload.get("quantidade") or 1),
                payload.get("local_execucao", ""),
                payload.get("prazo", ""),
                payload.get("responsavel", ""),
                payload.get("status", "rascunho"),
                timestamp,
                timestamp,
            ),
        )
        return int(cur.lastrowid)


def list_processos(db_path: Path | str = DB_PATH) -> list[dict[str, Any]]:
    init_db(db_path)
    with connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM processos
            ORDER BY updated_at DESC, id DESC
            """
        ).fetchall()
    return [dict(row) for row in rows]


def get_processo(processo_id: int, db_path: Path | str = DB_PATH) -> dict[str, Any] | None:
    init_db(db_path)
    with connect(db_path) as conn:
        row = conn.execute("SELECT * FROM processos WHERE id = ?", (processo_id,)).fetchone()
    return dict(row) if row else None


def create_item(payload: dict[str, Any], db_path: Path | str = DB_PATH) -> int:
    init_db(db_path)
    timestamp = now_iso()
    with connect(db_path) as conn:
        cur = conn.execute(
            """
            INSERT INTO pesquisa_itens (
                processo_id, codigo, descricao, unidade, quantidade, categoria,
                termo_busca, especificacao, status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                int(payload["processo_id"]),
                payload.get("codigo", ""),
                payload["descricao"],
                payload.get("unidade", ""),
                float(payload.get("quantidade") or 1),
                payload.get("categoria", ""),
                payload.get("termo_busca") or payload["descricao"],
                payload.get("especificacao", ""),
                payload.get("status", "pendente"),
                timestamp,
                timestamp,
            ),
        )
        conn.execute("UPDATE processos SET updated_at = ? WHERE id = ?", (timestamp, int(payload["processo_id"])))
        return int(cur.lastrowid)


def create_itens(processo_id: int, itens: list[dict[str, Any]], db_path: Path | str = DB_PATH) -> list[int]:
    ids = []
    for item in itens:
        payload = dict(item)
        payload["processo_id"] = processo_id
        ids.append(create_item(payload, db_path))
    return ids


def list_itens(processo_id: int, db_path: Path | str = DB_PATH) -> list[dict[str, Any]]:
    init_db(db_path)
    with connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM pesquisa_itens
            WHERE processo_id = ?
            ORDER BY id ASC
            """,
            (processo_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def get_item(item_id: int, db_path: Path | str = DB_PATH) -> dict[str, Any] | None:
    init_db(db_path)
    with connect(db_path) as conn:
        row = conn.execute("SELECT * FROM pesquisa_itens WHERE id = ?", (item_id,)).fetchone()
    return dict(row) if row else None


def delete_item(item_id: int, db_path: Path | str = DB_PATH) -> bool:
    init_db(db_path)
    with connect(db_path) as conn:
        row = conn.execute("SELECT processo_id FROM pesquisa_itens WHERE id = ?", (item_id,)).fetchone()
        conn.execute("UPDATE fontes_preco SET item_id = NULL WHERE item_id = ?", (item_id,))
        conn.execute("UPDATE pncp_rascunhos SET item_id = NULL WHERE item_id = ?", (item_id,))
        cur = conn.execute("DELETE FROM pesquisa_itens WHERE id = ?", (item_id,))
        if row:
            conn.execute("UPDATE processos SET updated_at = ? WHERE id = ?", (now_iso(), row["processo_id"]))
        return cur.rowcount > 0


def create_fonte(payload: dict[str, Any], db_path: Path | str = DB_PATH) -> int:
    init_db(db_path)
    with connect(db_path) as conn:
        cur = conn.execute(
            """
            INSERT INTO fontes_preco (
                processo_id, item_id, fonte_tipo, descricao_item, valor_unitario, quantidade,
                orgao, fornecedor, uf, municipio, url, data_referencia, data_acesso,
                aproveitada, justificativa_descarte, observacoes, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                int(payload["processo_id"]),
                int(payload["item_id"]) if payload.get("item_id") else None,
                payload["fonte_tipo"],
                payload["descricao_item"],
                float(payload["valor_unitario"]),
                float(payload.get("quantidade") or 1),
                payload.get("orgao", ""),
                payload.get("fornecedor", ""),
                payload.get("uf", ""),
                payload.get("municipio", ""),
                payload.get("url", ""),
                payload.get("data_referencia", ""),
                payload.get("data_acesso") or now_iso(),
                1 if payload.get("aproveitada", True) else 0,
                payload.get("justificativa_descarte", ""),
                payload.get("observacoes", ""),
                now_iso(),
            ),
        )
        conn.execute(
            "UPDATE processos SET updated_at = ? WHERE id = ?",
            (now_iso(), int(payload["processo_id"])),
        )
        return int(cur.lastrowid)


def list_fontes(processo_id: int, db_path: Path | str = DB_PATH) -> list[dict[str, Any]]:
    init_db(db_path)
    with connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM fontes_preco
            WHERE processo_id = ?
            ORDER BY aproveitada DESC, valor_unitario ASC, id DESC
            """,
            (processo_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def list_fontes_item(item_id: int, db_path: Path | str = DB_PATH) -> list[dict[str, Any]]:
    init_db(db_path)
    with connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM fontes_preco
            WHERE item_id = ?
            ORDER BY aproveitada DESC, valor_unitario ASC, id DESC
            """,
            (item_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def delete_fonte(fonte_id: int, db_path: Path | str = DB_PATH) -> bool:
    init_db(db_path)
    with connect(db_path) as conn:
        row = conn.execute(
            "SELECT processo_id FROM fontes_preco WHERE id = ?",
            (fonte_id,),
        ).fetchone()
        cur = conn.execute("DELETE FROM fontes_preco WHERE id = ?", (fonte_id,))
        if row:
            conn.execute("UPDATE processos SET updated_at = ? WHERE id = ?", (now_iso(), row["processo_id"]))
        return cur.rowcount > 0


def create_pncp_rascunho(payload: dict[str, Any], db_path: Path | str = DB_PATH) -> int:
    init_db(db_path)
    timestamp = now_iso()
    payload_json = payload.get("payload_json", "")
    if isinstance(payload_json, (dict, list)):
        payload_json = json.dumps(payload_json, ensure_ascii=False)
    with connect(db_path) as conn:
        cur = conn.execute(
            """
            INSERT INTO pncp_rascunhos (
                processo_id, item_id, numero_controle, objeto, orgao, unidade, fornecedor,
                modalidade, situacao, data_publicacao, valor_estimado, url,
                similaridade, consulta, payload_json, status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                int(payload["processo_id"]),
                int(payload["item_id"]) if payload.get("item_id") else None,
                payload.get("numero_controle", ""),
                payload.get("objeto", ""),
                payload.get("orgao", ""),
                payload.get("unidade", ""),
                payload.get("fornecedor", ""),
                payload.get("modalidade", ""),
                payload.get("situacao", ""),
                payload.get("data_publicacao", ""),
                float(payload.get("valor_estimado") or 0),
                payload.get("url", ""),
                float(payload.get("similaridade") or 0),
                payload.get("consulta", ""),
                payload_json,
                payload.get("status", "rascunho"),
                timestamp,
                timestamp,
            ),
        )
        conn.execute(
            "UPDATE processos SET updated_at = ? WHERE id = ?",
            (timestamp, int(payload["processo_id"])),
        )
        return int(cur.lastrowid)


def list_pncp_rascunhos(
    processo_id: int,
    item_id: int | None = None,
    status: str | None = None,
    db_path: Path | str = DB_PATH,
) -> list[dict[str, Any]]:
    init_db(db_path)
    clauses = ["processo_id = ?"]
    params: list[Any] = [int(processo_id)]
    if item_id is not None:
        clauses.append("item_id = ?")
        params.append(int(item_id))
    if status:
        clauses.append("status = ?")
        params.append(status)
    with connect(db_path) as conn:
        rows = conn.execute(
            f"""
            SELECT *
            FROM pncp_rascunhos
            WHERE {' AND '.join(clauses)}
            ORDER BY status ASC, similaridade DESC, created_at DESC, id DESC
            """,
            params,
        ).fetchall()
    return [dict(row) for row in rows]


def get_pncp_rascunho(rascunho_id: int, db_path: Path | str = DB_PATH) -> dict[str, Any] | None:
    init_db(db_path)
    with connect(db_path) as conn:
        row = conn.execute("SELECT * FROM pncp_rascunhos WHERE id = ?", (rascunho_id,)).fetchone()
    return dict(row) if row else None


def update_pncp_rascunho_status(
    rascunho_id: int,
    status: str,
    db_path: Path | str = DB_PATH,
) -> bool:
    init_db(db_path)
    with connect(db_path) as conn:
        row = conn.execute("SELECT processo_id FROM pncp_rascunhos WHERE id = ?", (rascunho_id,)).fetchone()
        cur = conn.execute(
            "UPDATE pncp_rascunhos SET status = ?, updated_at = ? WHERE id = ?",
            (status, now_iso(), rascunho_id),
        )
        if row:
            conn.execute("UPDATE processos SET updated_at = ? WHERE id = ?", (now_iso(), row["processo_id"]))
        return cur.rowcount > 0


def delete_pncp_rascunho(rascunho_id: int, db_path: Path | str = DB_PATH) -> bool:
    init_db(db_path)
    with connect(db_path) as conn:
        row = conn.execute("SELECT processo_id FROM pncp_rascunhos WHERE id = ?", (rascunho_id,)).fetchone()
        cur = conn.execute("DELETE FROM pncp_rascunhos WHERE id = ?", (rascunho_id,))
        if row:
            conn.execute("UPDATE processos SET updated_at = ? WHERE id = ?", (now_iso(), row["processo_id"]))
        return cur.rowcount > 0


def create_fonte_from_pncp_rascunho(
    rascunho_id: int,
    payload: dict[str, Any],
    db_path: Path | str = DB_PATH,
) -> int | None:
    rascunho = get_pncp_rascunho(rascunho_id, db_path)
    if not rascunho:
        return None
    fonte_id = create_fonte(
        {
            "processo_id": rascunho["processo_id"],
            "item_id": rascunho.get("item_id"),
            "fonte_tipo": "pncp",
            "descricao_item": rascunho.get("objeto") or "Resultado PNCP",
            "valor_unitario": float(payload.get("valor_unitario") or rascunho.get("valor_estimado") or 0),
            "quantidade": float(payload.get("quantidade") or 1),
            "orgao": rascunho.get("orgao") or rascunho.get("unidade") or "",
            "fornecedor": rascunho.get("fornecedor") or "",
            "uf": payload.get("uf", ""),
            "municipio": "",
            "url": rascunho.get("url", ""),
            "data_referencia": rascunho.get("data_publicacao", ""),
            "aproveitada": bool(payload.get("aproveitada", True)),
            "justificativa_descarte": "",
            "observacoes": payload.get("observacoes", "Fonte criada a partir de rascunho PNCP."),
        },
        db_path,
    )
    update_pncp_rascunho_status(rascunho_id, "usado", db_path)
    return fonte_id


def create_ata(payload: dict[str, Any], db_path: Path | str = DB_PATH) -> int:
    init_db(db_path)
    with connect(db_path) as conn:
        cur = conn.execute(
            """
            INSERT INTO atas (
                processo_id, numero, orgao_gerenciador, fornecedor, objeto, item,
                valor_unitario, vigencia_inicio, vigencia_fim, quantidade_registrada,
                quantidade_disponivel_estimativa, url, aderencia, observacoes, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                int(payload["processo_id"]),
                payload.get("numero", ""),
                payload.get("orgao_gerenciador", ""),
                payload.get("fornecedor", ""),
                payload.get("objeto", ""),
                payload.get("item", ""),
                float(payload.get("valor_unitario") or 0),
                payload.get("vigencia_inicio", ""),
                payload.get("vigencia_fim", ""),
                float(payload.get("quantidade_registrada") or 0),
                float(payload.get("quantidade_disponivel_estimativa") or 0),
                payload.get("url", ""),
                payload.get("aderencia", "indefinida"),
                payload.get("observacoes", ""),
                now_iso(),
            ),
        )
        conn.execute(
            "UPDATE processos SET updated_at = ? WHERE id = ?",
            (now_iso(), int(payload["processo_id"])),
        )
        return int(cur.lastrowid)


def list_atas(processo_id: int, db_path: Path | str = DB_PATH) -> list[dict[str, Any]]:
    init_db(db_path)
    with connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM atas
            WHERE processo_id = ?
            ORDER BY vigencia_fim DESC, aderencia ASC, id DESC
            """,
            (processo_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def delete_ata(ata_id: int, db_path: Path | str = DB_PATH) -> bool:
    init_db(db_path)
    with connect(db_path) as conn:
        row = conn.execute(
            "SELECT processo_id FROM atas WHERE id = ?",
            (ata_id,),
        ).fetchone()
        cur = conn.execute("DELETE FROM atas WHERE id = ?", (ata_id,))
        if row:
            conn.execute("UPDATE processos SET updated_at = ? WHERE id = ?", (now_iso(), row["processo_id"]))
        return cur.rowcount > 0


def resumo_atas(processo_id: int, db_path: Path | str = DB_PATH) -> dict[str, int]:
    hoje = datetime.now().date().isoformat()
    atas = list_atas(processo_id, db_path)
    vigentes = [
        ata
        for ata in atas
        if not ata.get("vigencia_fim") or str(ata["vigencia_fim"]) >= hoje
    ]
    aderentes = [
        ata
        for ata in vigentes
        if ata.get("aderencia") in {"alta", "media"}
    ]
    return {
        "atas_total": len(atas),
        "atas_vigentes": len(vigentes),
        "atas_potencialmente_aderentes": len(aderentes),
    }


def resumo_pesquisa(processo_id: int, db_path: Path | str = DB_PATH) -> dict[str, Any]:
    fontes = list_fontes(processo_id, db_path)
    valores = [
        float(item["valor_unitario"])
        for item in fontes
        if item.get("aproveitada") and float(item.get("valor_unitario") or 0) > 0
    ]
    resumo = calcular_resumo_precos(valores)
    resumo["preco_estimado_mediana"] = sugerir_preco_estimado(valores, "mediana")
    resumo["preco_estimado_media"] = sugerir_preco_estimado(valores, "media")
    resumo["fontes_total"] = len(fontes)
    resumo["fontes_aproveitadas"] = len(valores)
    resumo["fontes_descartadas"] = max(0, len(fontes) - len(valores))
    return resumo


def resumo_item(item_id: int, db_path: Path | str = DB_PATH) -> dict[str, Any]:
    fontes = list_fontes_item(item_id, db_path)
    valores = [
        float(item["valor_unitario"])
        for item in fontes
        if item.get("aproveitada") and float(item.get("valor_unitario") or 0) > 0
    ]
    resumo = calcular_resumo_precos(valores)
    resumo["preco_estimado_mediana"] = sugerir_preco_estimado(valores, "mediana")
    resumo["preco_estimado_media"] = sugerir_preco_estimado(valores, "media")
    resumo["fontes_total"] = len(fontes)
    resumo["fontes_aproveitadas"] = len(valores)
    resumo["fontes_descartadas"] = max(0, len(fontes) - len(valores))
    return resumo


def resumo_itens(processo_id: int, db_path: Path | str = DB_PATH) -> list[dict[str, Any]]:
    itens = list_itens(processo_id, db_path)
    return [
        {
            "item": item,
            "resumo": resumo_item(int(item["id"]), db_path),
        }
        for item in itens
    ]


def export_snapshot(processo_id: int, db_path: Path | str = DB_PATH) -> dict[str, Any]:
    processo = get_processo(processo_id, db_path)
    if not processo:
        return {}
    return {
        "processo": processo,
        "itens": list_itens(processo_id, db_path),
        "resumo_itens": resumo_itens(processo_id, db_path),
        "fontes": list_fontes(processo_id, db_path),
        "pncp_rascunhos": list_pncp_rascunhos(processo_id, db_path=db_path),
        "atas": list_atas(processo_id, db_path),
        "resumo": resumo_pesquisa(processo_id, db_path),
        "resumo_atas": resumo_atas(processo_id, db_path),
        "gerado_em": now_iso(),
    }
