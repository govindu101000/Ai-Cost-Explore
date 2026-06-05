from fastapi import (
    FastAPI,
    HTTPException,
    Depends,
    Header,
    WebSocket
)

from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import asyncio
import uuid

# ------------------------
# AUTH MODULE
# ------------------------

from auth import (
    hash_password,
    verify_password,
    create_token,
    decode_token
)

# ------------------------
# DB MODULE
# ------------------------

from db import (
    init_db,
    create_user,
    get_user_by_email,
    get_analysis_history,
    get_analysis_by_id,
    save_analysis
)

# ------------------------
# AZURE + AI MODULES
# ------------------------

from azure_scanner import (
    get_resource_groups,
    get_resources
)

from ai_analyzer import (
    analyze_resources
)

# ------------------------
# WEBSOCKET
# ------------------------

from websocket_manager import manager

# ------------------------
# APP INIT
# ------------------------

app = FastAPI(title="AI Cloud Cost Detective")

# ------------------------
# CORS
# ------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# ------------------------
# STARTUP
# ------------------------

@app.on_event("startup")
async def startup_event():
    await init_db()

# ------------------------
# MODELS
# ------------------------

class AuthRequest(BaseModel):
    email: str
    password: str


# ------------------------
# JWT DEPENDENCY
# ------------------------

async def get_current_user(
    authorization: str = Header(...)
):
    try:
        token = authorization.replace("Bearer ", "")
        return decode_token(token)

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )


# ------------------------
# ROOT
# ------------------------

@app.get("/")
def root():
    return {"status": "running"}


# ------------------------
# AUTH
# ------------------------

@app.post("/api/auth/signup")
async def signup(request: AuthRequest):

    existing = await get_user_by_email(request.email)

    if existing:
        raise HTTPException(
            status_code=400,
            detail="User already exists"
        )

    password_hash = hash_password(request.password)

    user = await create_user(
        request.email,
        password_hash
    )

    token = create_token(user["id"], user["email"])

    return {
        "token": token,
        "email": user["email"]
    }


@app.post("/api/auth/login")
async def login(request: AuthRequest):

    user = await get_user_by_email(request.email)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    if not verify_password(request.password, user["password_hash"]):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    token = create_token(user["id"], user["email"])

    return {
        "token": token,
        "email": user["email"]
    }


# ------------------------
# AZURE RESOURCE GROUPS
# ------------------------

@app.get("/api/resource-groups")
async def resource_groups(user=Depends(get_current_user)):

    groups = await asyncio.to_thread(get_resource_groups)

    return {
        "resource_groups": groups
    }


# ------------------------
# ANALYZE (CORE ENGINE)
# ------------------------

@app.post("/api/analyze")
async def analyze(
    request: dict,
    user=Depends(get_current_user)
):

    analysis_id = request.get("analysis_id") or str(uuid.uuid4())
    rg = request.get("resource_group")

    # Step 1
    await manager.send_progress(
        analysis_id,
        "Fetching Azure resources..."
    )

    # Step 2 - Azure CLI scan
    resources = await asyncio.to_thread(
        get_resources,
        rg
    )

    await manager.send_progress(
        analysis_id,
        "Analyzing with Llama 3.1..."
    )

    # Step 3 - AI analysis
    analysis = await asyncio.to_thread(
        analyze_resources,
        resources
    )

    await manager.send_progress(
        analysis_id,
        "Saving results..."
    )

    # Step 4 - Save DB
    await save_analysis(
        user_id=user["user_id"],
        resource_group=rg,
        resources_scanned=len(resources),
        analysis=analysis
    )

    await manager.send_progress(
        analysis_id,
        "Analysis complete"
    )

    return {
        "analysis_id": analysis_id,
        "resource_group": rg,
        "resources_scanned": len(resources),
        "analysis": analysis
    }


# ------------------------
# HISTORY
# ------------------------

@app.get("/api/history")
async def history(user=Depends(get_current_user)):
    return await get_analysis_history(user["user_id"])


@app.get("/api/history/{analysis_id}")
async def history_details(
    analysis_id: int,
    user=Depends(get_current_user)
):

    result = await get_analysis_by_id(
        analysis_id,
        user["user_id"]
    )

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Analysis not found"
        )

    return result


# ------------------------
# WEBSOCKET
# ------------------------

@app.websocket("/ws/progress/{analysis_id}")
async def websocket_progress(websocket: WebSocket, analysis_id: str):

    await manager.connect(websocket, analysis_id)

    try:
        while True:
            await websocket.receive_text()

    except Exception:
        manager.disconnect(websocket, analysis_id)


# ------------------------
# DEBUG ROUTE
# ------------------------

@app.get("/test")
def test():
    return {"ok": True}