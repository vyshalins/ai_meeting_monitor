# app/api/v1/routes.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from uuid import uuid4
from app.config import get_settings
from app.services.groq_service import GroqClient, transcribe_audio
import tempfile, shutil, os
from app.services.groq_service import translate_text
from app.services.groq_service import summarize_text_en, summarize_text_native

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
@router.post("/translate")
async def translate_endpoint(file: UploadFile = File(...)):
    """
    Uploads an audio file → Transcribes (auto language detect + native script)
    → Translates to English → Returns both versions.
    """
    temp_path = None  # ✅ ensures variable exists even if try fails
    try:
        # 1️⃣ Save uploaded audio temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
            shutil.copyfileobj(file.file, temp_audio)
            temp_path = temp_audio.name

        # 2️⃣ Transcribe the audio
        result = transcribe_audio(temp_path)
        if "error" in result:
            return {"status": "error", "message": result["error"]}

        native = result["transcript_native"]
        lang = result["language_code"]
        lang_name = result["language_name"]

        # 3️⃣ Translate to English
        english = translate_text(native, lang)

        # 4️⃣ Return combined result
        return {
            "status": "success",
            "data": {
                "language_code": lang,
                "language_name": lang_name,
                "transcript_native": native,
                "transcript_english": english
            }
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}

    finally:
        # 5️⃣ Clean up temp file
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

@router.post("/summarize")
async def summarize_endpoint(payload: dict):
    text = payload.get("text", "")
    src_lang = payload.get("src_lang", "unknown")

    # Step 1: Summarize in English
    summary_en = summarize_text_en(text)
    if "error" in summary_en:
        return summary_en

    # Step 2: Translate summary to native language
    summary_native = summarize_text_native(summary_en["summary_en"], src_lang)

    return {
        "status": "success",
        "data": {
            "summary_en": summary_en["summary_en"],
            "summary_native": summary_native.get("summary_native", "")
        }
    }