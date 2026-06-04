import os
import json
import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import Json, RealDictCursor
from typing import Any, Dict, List, Optional

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

DATABASE_URL = os.getenv("DATABASE_URL")


def _get_conn():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL not set in environment")
    return psycopg2.connect(DATABASE_URL)


def init_db() -> None:
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            # create users table
            cur.execute(
                """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
            )
            """
            )

            # create analyses table
            cur.execute(
                """
            CREATE TABLE IF NOT EXISTS analyses (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                resource_group TEXT,
                resources_scanned INTEGER,
                issues_found INTEGER,
                estimated_savings TEXT,
                analysis_result JSONB,
                status TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
            )
            """
            )
        conn.commit()
    finally:
        conn.close()


def save_analysis(
    user_id: Optional[int],
    resource_group: str,
    resources_scanned: int = 0,
    issues_found: int = 0,
    estimated_savings: Optional[str] = None,
    analysis_result: Optional[Dict[str, Any]] = None,
    status: str = "running",
) -> int:
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
            INSERT INTO analyses (user_id, resource_group, resources_scanned, issues_found, estimated_savings, analysis_result, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
            """,
                (
                    user_id,
                    resource_group,
                    resources_scanned,
                    issues_found,
                    estimated_savings,
                    Json(analysis_result) if analysis_result is not None else None,
                    status,
                ),
            )
            new_id = cur.fetchone()[0]
        conn.commit()
        return new_id
    finally:
        conn.close()


def update_analysis(analysis_id: int, **fields) -> None:
    if not fields:
        return
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            set_clauses = []
            values = []
            for k, v in fields.items():
                if k == "analysis_result":
                    set_clauses.append(f"{k} = %s")
                    values.append(Json(v))
                else:
                    set_clauses.append(f"{k} = %s")
                    values.append(v)
            values.append(analysis_id)
            sql = f"UPDATE analyses SET {', '.join(set_clauses)} WHERE id = %s"
            cur.execute(sql, tuple(values))
        conn.commit()
    finally:
        conn.close()


def update_analysis_if_running(analysis_id: int, **fields) -> int:
    if not fields:
        return 0
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            set_clauses = []
            values = []
            for k, v in fields.items():
                if k == "analysis_result":
                    set_clauses.append(f"{k} = %s")
                    values.append(Json(v))
                else:
                    set_clauses.append(f"{k} = %s")
                    values.append(v)
            values.append(analysis_id)
            values.append("running")
            sql = f"UPDATE analyses SET {', '.join(set_clauses)} WHERE id = %s AND status = %s"
            cur.execute(sql, tuple(values))
            rowcount = cur.rowcount
        conn.commit()
        return rowcount
    finally:
        conn.close()


def get_analyses_for_user(user_id: int) -> List[Dict[str, Any]]:
    conn = _get_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT id, resource_group, resources_scanned, issues_found, estimated_savings, analysis_result, status, created_at FROM analyses WHERE user_id = %s ORDER BY created_at DESC",
                (user_id,),
            )
            rows = cur.fetchall()
            return [dict(r) for r in rows]
    finally:
        conn.close()


def create_user(email: str, password_hash: str) -> int:
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (email, password_hash) VALUES (%s, %s) RETURNING id",
                (email, password_hash),
            )
            new_id = cur.fetchone()[0]
        conn.commit()
        return new_id
    finally:
        conn.close()


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    conn = _get_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id, email, password_hash, created_at FROM users WHERE email = %s", (email,))
            row = cur.fetchone()
            return dict(row) if row else None
    finally:
        conn.close()


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    conn = _get_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id, email, created_at FROM users WHERE id = %s", (user_id,))
            row = cur.fetchone()
            return dict(row) if row else None
    finally:
        conn.close()
