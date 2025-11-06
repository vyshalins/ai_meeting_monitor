# app/api/v1/routes.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from uuid import uuid4
from app.config import get_settings
from app.services.groq_service import GroqClient, transcribe_audio
import tempfile, shutil

router = APIRouter()

@router.get("/health")
def v1_health():
    return {"status": "ok", "version": "v1"}

# In-memory store for MVP
_MEETINGS = {}
_LAST_AUDIO: bytes | None = None
_LAST_AUDIO_NAME: str = "audio.wav"

@router.get("/meetings")
def list_meetings():
    return list(_MEETINGS.values())

@router.post("/meetings")
def create_meeting(title: str = "Untitled", meeting_type: str = "upload"):
    mid = str(uuid4())
    item = {"id": mid, "title": title, "meeting_type": meeting_type}
    _MEETINGS[mid] = item
    return item

@router.post("/meetings/upload")
async def upload_audio(file: UploadFile = File(...)):
    global _LAST_AUDIO, _LAST_AUDIO_NAME
    if file.content_type not in {"audio/mpeg","audio/wav","audio/x-m4a","audio/mp4","audio/aac"}:
        raise HTTPException(status_code=400, detail="Unsupported audio type")
    _LAST_AUDIO = await file.read()
    _LAST_AUDIO_NAME = file.filename or "audio.wav"
    return {"status": "received", "filename": _LAST_AUDIO_NAME, "size": len(_LAST_AUDIO)}

@router.post("/meetings/transcribe")
def transcribe_stub():
    if _LAST_AUDIO is None:
        raise HTTPException(status_code=400, detail="No audio uploaded yet")
    settings = get_settings()
    if not settings.GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not set")
    groq = GroqClient(api_key=settings.GROQ_API_KEY)
    text = groq.transcribe_bytes(_LAST_AUDIO, filename=_LAST_AUDIO_NAME)
    return {"text": text}

@router.post("/meetings/process")
def process_stub(payload: dict):
    transcript = payload.get("transcript", "")
    if not transcript:
        raise HTTPException(status_code=400, detail="transcript is required")
    settings = get_settings()
    if not settings.GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not set")
    groq = GroqClient(api_key=settings.GROQ_API_KEY)
    analysis = groq.analyze_transcript(transcript)
    return analysis

@router.post("/transcribe")
async def transcribe_audio_endpoint(file: UploadFile = File(...)):
    # Save file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
        shutil.copyfileobj(file.file, temp_audio)
        temp_path = temp_audio.name

    # Process audio
    result = transcribe_audio(temp_path)

    return {
        "status": "success",
        "data": result
    }
