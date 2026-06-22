from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from backend.database.database import get_db
from backend.database.models import Conversation, Message, Setting
from backend.config.settings import settings
from backend.tools.registry import ToolRegistry
from backend.services.api_client import APIClient
from backend.tools.executor import ToolExecutor
from backend.services.ollama_service import OllamaService
from backend.agent.orchestrator import AgentOrchestrator

router = APIRouter()

# Dependency injections
tool_registry = ToolRegistry(settings.TOOLS_CONFIG_PATH)
api_client = APIClient(settings.APIS_CONFIG_PATH)
tool_executor = ToolExecutor(tool_registry, api_client)
ollama_service = OllamaService()
agent_orchestrator = AgentOrchestrator(ollama_service, tool_executor, tool_registry)

class ChatRequest(BaseModel):
    conversation_id: Optional[int] = None
    message: str

class SettingsUpdate(BaseModel):
    ollama_url: str
    model_name: str

@router.post("/chat")
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    # Get settings from DB
    ollama_url_setting = db.query(Setting).filter(Setting.key == "OLLAMA_URL").first()
    model_name_setting = db.query(Setting).filter(Setting.key == "DEFAULT_MODEL").first()
    
    ollama_url = ollama_url_setting.value if ollama_url_setting else settings.OLLAMA_URL
    model_name = model_name_setting.value if model_name_setting else settings.DEFAULT_MODEL

    # Create or get conversation
    if not request.conversation_id:
        conv = Conversation(title=request.message[:50])
        db.add(conv)
        db.commit()
        db.refresh(conv)
        conv_id = conv.id
    else:
        conv_id = request.conversation_id

    # Save user message
    user_msg = Message(conversation_id=conv_id, role="user", content=request.message)
    db.add(user_msg)
    db.commit()

    # Process via Orchestrator
    try:
        result = await agent_orchestrator.process_message(request.message, conv_id, db, ollama_url, model_name)
        
        # Save assistant message
        assistant_msg = Message(
            conversation_id=conv_id, 
            role="assistant", 
            content=result["answer"],
            tool_calls=result.get("tool_calls")
        )
        db.add(assistant_msg)
        db.commit()
        
        return {
            "conversation_id": conv_id,
            "answer": result["answer"],
            "tool_calls": result.get("tool_calls", []),
            "tool_results": result.get("tool_results", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversations")
def get_conversations(db: Session = Depends(get_db)):
    convs = db.query(Conversation).order_by(Conversation.created_at.desc()).all()
    return convs

@router.get("/conversations/{conv_id}/messages")
def get_messages(conv_id: int, db: Session = Depends(get_db)):
    msgs = db.query(Message).filter(Message.conversation_id == conv_id).order_by(Message.created_at.asc()).all()
    return msgs

@router.get("/status")
async def get_status(db: Session = Depends(get_db)):
    ollama_url_setting = db.query(Setting).filter(Setting.key == "OLLAMA_URL").first()
    ollama_url = ollama_url_setting.value if ollama_url_setting else settings.OLLAMA_URL

    ollama_health = await ollama_service.check_health(ollama_url)
    tool_count = len(tool_registry.list_tools())
    conv_count = db.query(Conversation).count()
    
    return {
        "ollama_status": "online" if ollama_health else "offline",
        "api_server_status": "online", # Self-reported
        "tool_count": tool_count,
        "recent_conversations": conv_count
    }

@router.get("/settings")
def get_settings(db: Session = Depends(get_db)):
    settings_db = {s.key: s.value for s in db.query(Setting).all()}
    return {
        "OLLAMA_URL": settings_db.get("OLLAMA_URL", settings.OLLAMA_URL),
        "DEFAULT_MODEL": settings_db.get("DEFAULT_MODEL", settings.DEFAULT_MODEL)
    }

@router.post("/settings")
def update_settings(updates: dict, db: Session = Depends(get_db)):
    for k, v in updates.items():
        setting = db.query(Setting).filter(Setting.key == k).first()
        if setting:
            setting.value = str(v)
        else:
            new_setting = Setting(key=k, value=str(v))
            db.add(new_setting)
    db.commit()
    return {"status": "success"}

# Mock API for tools to hit
@router.get("/mock-api/devices/{device_id}/status")
def mock_device_status(device_id: str):
    return {"device_id": device_id, "status": "healthy", "battery": "85%"}

@router.get("/mock-api/devices/{device_id}/latest")
def mock_device_latest(device_id: str):
    return {"device_id": device_id, "pm2_5": 12.5, "pm10": 20.1, "timestamp": "2023-10-25T10:00:00Z"}

@router.get("/mock-api/devices/calibration-needs")
def mock_calibration_needs():
    return {"devices_needing_calibration": ["AQ002", "AQ005"]}
