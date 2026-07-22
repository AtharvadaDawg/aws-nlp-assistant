from fastapi import FastAPI, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import json
import os
from aws_client_factory import aws_credentials_context

load_dotenv()

from typing import List, Optional

from intent_classifier import classify_intent
from aws_skills import run_skill
from action_engine import build_proposal, execute_action

app = FastAPI(title="AWS NLP Assistant")

allowed_origins_env = os.getenv("ALLOWED_ORIGINS")
if allowed_origins_env:
    origins = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]
else:
    origins = ["http://localhost:5173", "http://localhost:5174", "http://localhost:5175"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Pending action store (file-based so it survives reloads) ──────────────────

PENDING_FILE = os.path.join(os.path.dirname(__file__), "pending_actions.json")

def load_pending():
    if not os.path.exists(PENDING_FILE):
        return {}
    try:
        with open(PENDING_FILE) as f:
            return json.load(f)
    except Exception:
        return {}

def save_pending(data):
    with open(PENDING_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_pending(session_id: str):
    return load_pending().get(session_id)

def set_pending(session_id: str, action: dict):
    data = load_pending()
    data[session_id] = action
    save_pending(data)
    print(f"[DEBUG] Saved pending action for session '{session_id}' to {PENDING_FILE}")

def clear_pending(session_id: str):
    data = load_pending()
    data.pop(session_id, None)
    save_pending(data)

# ── Models ────────────────────────────────────────────────────────────────────

class HistoryMessage(BaseModel):
    role: str
    content: str

class ChatMessage(BaseModel):
    message: str
    session_id: str = "default"
    history: List[HistoryMessage] = []

class ConfirmAction(BaseModel):
    session_id: str = "default"
    confirmed: bool = True
    use_real_aws: bool = False

# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {"status": "ok", "message": "AWS NLP Assistant backend running"}

@app.get("/api/skills")
def list_skills():
    return {
        "skills": [
            {"id": "system_health",     "label": "System Health",    "example": "Is everything running okay?"},
            {"id": "recent_errors",     "label": "Recent Errors",    "example": "What broke recently?"},
            {"id": "cloud_cost",        "label": "Cloud Costs",      "example": "How much did we spend this month?"},
            {"id": "recent_changes",    "label": "Recent Changes",   "example": "What changed in our infrastructure?"},
            {"id": "service_metrics",   "label": "Service Metrics",  "example": "How is the payment service performing?"},
            {"id": "action_restart",    "label": "Restart Service",  "example": "Restart the payment service"},
            {"id": "action_stop",       "label": "Stop Service",     "example": "Stop the inventory service"},
            {"id": "action_scale",      "label": "Scale Up",         "example": "Scale up the order service"},
            {"id": "action_alarm",      "label": "Create Alarm",     "example": "Alert me when CPU exceeds 80%"},
            {"id": "action_postmortem", "label": "Run Postmortem",   "example": "Generate a postmortem for this incident"},
        ]
    }

async def get_aws_credentials(
    x_aws_access_key_id: Optional[str] = Header(None),
    x_aws_secret_access_key: Optional[str] = Header(None),
    x_aws_region: Optional[str] = Header(None),
):
    ctx = {
        "access_key_id": x_aws_access_key_id,
        "secret_access_key": x_aws_secret_access_key,
        "region": x_aws_region
    }
    token = aws_credentials_context.set(ctx)
    try:
        yield ctx
    finally:
        aws_credentials_context.reset(token)

@app.post("/api/chat")
def chat(body: ChatMessage, creds: dict = Depends(get_aws_credentials)):
    history = [{"role": m.role, "content": m.content} for m in body.history]
    intent    = classify_intent(body.message, history)
    skill     = intent.get("skill", "unknown")
    extracted = intent.get("extracted", {})

    if intent.get("is_action"):
        proposal = build_proposal(skill, extracted)
        set_pending(body.session_id, {
            "skill":    skill,
            "extracted": extracted,
            "proposal": proposal
        })
        return {
            "type": "action_proposal",
            "question": body.message,
            "thinking": intent.get("thinking", ""),
            "skill_used": skill,
            "proposal": proposal,
            "answer": "I can do that. Here's what I'm about to do — please confirm before I proceed.",
            "requires_confirmation": True,
            "data_type": None,
            "data": {}
        }

    result = run_skill(skill=skill, question=body.message, extracted=extracted, history=history)
    return {
        "type": "read_response",
        "question": body.message,
        "thinking": intent.get("thinking", ""),
        "skill_used": result["skill_used"],
        "answer": result["answer"],
        "requires_confirmation": False,
        "data_type": result.get("data_type"),
        "data": result.get("data", {}),
        "confidence": intent.get("confidence", 0)
    }

@app.post("/api/confirm")
def confirm(body: ConfirmAction, creds: dict = Depends(get_aws_credentials)):
    print(f"[DEBUG] Confirm called for session '{body.session_id}'")
    print(f"[DEBUG] Pending file exists: {os.path.exists(PENDING_FILE)}")
    print(f"[DEBUG] Current pending: {load_pending()}")

    pending = get_pending(body.session_id)
    if not pending:
        return {"success": False, "message": "No pending action found."}

    if not body.confirmed:
        clear_pending(body.session_id)
        return {
            "success": False,
            "cancelled": True,
            "message": "Action cancelled. Nothing was changed."
        }

    result = execute_action(
        skill=pending["skill"],
        extracted=pending["extracted"],
        use_real_aws=body.use_real_aws
    )
    clear_pending(body.session_id)
    return {**result, "type": "action_result"}

@app.get("/api/suggestions")
def suggestions():
    return {
        "suggestions": [
            "Is our system running fine right now?",
            "What errors happened today?",
            "How much did we spend on cloud this month?",
            "Restart the payment service",
            "Scale up the order service",
            "Create an alarm for high CPU on the database",
        ]
    }

# ── Serve Frontend Static Files ──────────────────────────────────────────────

frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "../frontend/dist"))
if os.path.exists(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

    @app.get("/{fallback_path:path}")
    def serve_frontend(fallback_path: str):
        index_file = os.path.join(frontend_dist, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {"error": "Frontend build files not found"}