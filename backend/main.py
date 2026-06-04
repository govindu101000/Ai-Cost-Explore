import os
import traceback
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio

from backend.azure_scanner import (
    list_resource_groups,
    scan_resource_group,
    AzNotInstalled,
    AzNotLoggedIn,
    ResourceGroupNotFound,
    AzureCLIError,
)
from backend.ai_analyzer import analyze_with_ai, OpenAIError
from backend import db
from backend.auth import router as auth_router, get_current_user


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/auth")


class AnalyzeRequest(BaseModel):
    resource_group: str


ws_connections = {}


@app.on_event("startup")
async def startup_event():
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, db.init_db)


@app.get("/api/resource-groups")
def get_resource_groups(current_user: dict = Depends(get_current_user)):
    try:
        groups = list_resource_groups()
        return {"resource_groups": groups}
    except AzNotInstalled:
        raise HTTPException(status_code=500, detail="Azure CLI not installed")
    except AzNotLoggedIn:
        raise HTTPException(status_code=401, detail="Azure CLI not logged in. Run 'az login'.")
    except AzureCLIError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze")
async def analyze(req: AnalyzeRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]

    try:
        # create initial DB row (status running)
        analysis_id = await asyncio.get_running_loop().run_in_executor(
            None, db.save_analysis, user_id, req.resource_group
        )

        async def background_work(aid: int, rg: str, uid: int):
            async def send_progress(msg: str):
                ws = ws_connections.get(str(aid))
                if ws:
                    try:
                        await ws.send_text(msg)
                    except Exception:
                        pass

            try:
                await send_progress("Fetching resource groups...")

                resources = await asyncio.get_running_loop().run_in_executor(None, scan_resource_group, rg)

                await send_progress(f"Scanning resources in {rg}...")
                await send_progress("Analyzing costs with AI...")

                analysis = await asyncio.get_running_loop().run_in_executor(None, analyze_with_ai, resources)

                await send_progress("Storing results...")

                resources_scanned = len(resources)
                issues_found = 0
                estimated_savings = None
                if isinstance(analysis, dict):
                    issues = analysis.get("issues") or []
                    issues_found = len(issues)
                    estimated_savings = str(analysis.get("estimated_savings"))

                await asyncio.get_running_loop().run_in_executor(
                    None,
                    db.update_analysis_if_running,
                    aid,
                    **{
                        "resources_scanned": resources_scanned,
                        "issues_found": issues_found,
                        "estimated_savings": estimated_savings,
                        "analysis_result": analysis,
                        "status": "complete",
                    },
                )

                await send_progress("Analysis complete")
            except ResourceGroupNotFound:
                await send_progress("Resource group not found")
                await asyncio.get_running_loop().run_in_executor(
                    None,
                    db.update_analysis_if_running,
                    aid,
                    status="failed",
                    analysis_result={"error": "Resource group not found"},
                )
            except OpenAIError as e:
                await send_progress(f"AI analysis failed: {str(e)}")
                await asyncio.get_running_loop().run_in_executor(
                    None,
                    db.update_analysis_if_running,
                    aid,
                    status="failed",
                    analysis_result={"error": str(e)},
                )
            except AzureCLIError as e:
                await send_progress(f"Azure CLI error: {str(e)}")
                await asyncio.get_running_loop().run_in_executor(
                    None,
                    db.update_analysis_if_running,
                    aid,
                    status="failed",
                    analysis_result={"error": str(e)},
                )
            except Exception as e:
                await send_progress(f"Unexpected error: {str(e)}")
                traceback.print_exc()
                await asyncio.get_running_loop().run_in_executor(
                    None,
                    db.update_analysis_if_running,
                    aid,
                    status="failed",
                    analysis_result={"error": str(e)},
                )

        # schedule background work and return analysis_id immediately
        asyncio.create_task(background_work(analysis_id, req.resource_group, user_id))

        return {"analysis_id": analysis_id}
    except AzNotInstalled:
        raise HTTPException(status_code=500, detail="Azure CLI not installed")
    except AzNotLoggedIn:
        raise HTTPException(status_code=401, detail="Azure CLI not logged in. Run 'az login'.")
    except AzureCLIError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/history")
def get_history(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    try:
        rows = db.get_analyses_for_user(user_id)
        return {"history": rows}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws/progress/{analysis_id}")
async def websocket_progress(websocket: WebSocket, analysis_id: str):
    await websocket.accept()
    ws_connections[str(analysis_id)] = websocket
    try:
        while True:
            try:
                await websocket.receive_text()
            except WebSocketDisconnect:
                break
            except Exception:
                await asyncio.sleep(0.5)
    finally:
        ws_connections.pop(str(analysis_id), None)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
