import os
import json
import asyncpg
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
pool = None


async def init_db():
    global pool

    pool = await asyncpg.create_pool(
        DATABASE_URL,
        min_size=1,
        max_size=10
    )

    async with pool.acquire() as conn:

        await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT NOW()
        )
        """)

        await conn.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            resource_group TEXT,
            resources_scanned INTEGER,
            issues_found INTEGER,
            estimated_savings TEXT,
            analysis_result JSONB,
            status TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        )
        """)

        print("Database initialized")


# ---------------- USERS ----------------

async def create_user(email, password_hash):
    async with pool.acquire() as conn:
        return await conn.fetchrow("""
            INSERT INTO users(email, password_hash)
            VALUES($1,$2)
            RETURNING id,email
        """, email, password_hash)


async def get_user_by_email(email):
    async with pool.acquire() as conn:
        return await conn.fetchrow("""
            SELECT * FROM users WHERE email=$1
        """, email)


# ---------------- ANALYSIS ----------------

async def save_analysis(
    user_id,
    resource_group,
    resources_scanned,
    analysis
):

    issues_found = len(analysis.get("issues", []))
    estimated_savings = analysis.get("estimated_total_monthly_savings", "Unknown")

    async with pool.acquire() as conn:
        return await conn.fetchval("""
            INSERT INTO analyses(
                user_id,
                resource_group,
                resources_scanned,
                issues_found,
                estimated_savings,
                analysis_result,
                status
            )
            VALUES($1,$2,$3,$4,$5,$6,$7)
            RETURNING id
        """,
        user_id,
        resource_group,
        resources_scanned,
        issues_found,
        estimated_savings,
        json.dumps(analysis),
        "completed"
        )


async def get_analysis_history(user_id):
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT
                id,
                resource_group,
                resources_scanned,
                issues_found,
                estimated_savings,
                status,
                created_at
            FROM analyses
            WHERE user_id=$1
            ORDER BY created_at DESC
        """, user_id)

        return [dict(r) for r in rows]


async def get_analysis_by_id(analysis_id, user_id):
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT * FROM analyses
            WHERE id=$1 AND user_id=$2
        """, analysis_id, user_id)

        if not row:
            return None

        result = dict(row)

        # IMPORTANT FIX: always decode JSON
        if isinstance(result.get("analysis_result"), str):
            try:
                result["analysis_result"] = json.loads(result["analysis_result"])
            except:
                result["analysis_result"] = {
                    "summary": "Unable to parse model response",
                    "issues": [],
                    "suggestions": [],
                    "resources": []
                }

        return result