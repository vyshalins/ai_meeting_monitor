# app/services/groq_service.py (only the analyze_* parts changed)
from groq import Groq
from io import BytesIO
import json, re
from typing import Any, Dict, List, Tuple
import os
from dotenv import load_dotenv
import tempfile
from langdetect import detect, DetectorFactory

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

NAME_WORD = r"[A-Z][a-zA-Z]+"
ASSIGN_PATTERNS = [
    # "Rahul will finish the frontend by EOD."
    re.compile(rf"\b({NAME_WORD})\s+will\s+([^\.]+)", re.I),
    # "Assign Ram to handle backend with Flask."
    re.compile(rf"\bassign\s+({NAME_WORD})\s+to\s+([^\.]+)", re.I),
    # "Sakshin to do integration."
    re.compile(rf"\b({NAME_WORD})\s+to\s+([^\.]+)", re.I),
    # "({name}) is responsible for ..."
    re.compile(rf"\b({NAME_WORD})\s+is\s+responsible\s+for\s+([^\.]+)", re.I),
]

DetectorFactory.seed = 0

def transcribe_audio(file_path: str) -> Dict[str, Any]:
    """
    Automatically detects the spoken language and transcribes
    the given audio file into its native script.
    Uses Groq Whisper + langdetect fallback for language detection.
    """
    try:
        with open(file_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=audio_file
            )

        # Extract transcription text
        transcript_text = getattr(transcription, "text", "").strip()

        # Try to get language from Groq (if available)
        language_code = getattr(transcription, "language", None)

        # Fallback: detect language manually if not provided
        if not language_code or language_code == "unknown":
            try:
                language_code = detect(transcript_text)
            except Exception:
                language_code = "unknown"

        return {
            "language_code": language_code,
            "language_name": language_code.capitalize(),
            "transcript_native": transcript_text
        }

    except Exception as e:
        print(f"Transcription failed: {e}")
        return {"error": str(e)}

def translate_text(native_text: str, source_lang: str = "auto") -> str:
    """
    Translates text from its detected language into English using Groq's LLM.
    Returns the translated English text as a string.
    """
    try:
        # Explicit instruction for translation
        prompt = (
            f"You are a professional translator. The user will give you text in {source_lang}. "
            "Translate it into natural, fluent English. "
            "If the text is already in English, just return it as-is. "
            "Do not explain, comment, or repeat the source. "
            "Output only the English translation text.\n\n"
            f"Text:\n{native_text}"
        )

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a multilingual translation assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=600,
        )

        translated_text = response.choices[0].message.content.strip()

        # Optional: clean up potential "Translation:" prefixes
        if translated_text.lower().startswith("translation:"):
            translated_text = translated_text.split(":", 1)[1].strip()

        return translated_text

    except Exception as e:
        print(f"Translation failed: {e}")
        return ""

def summarize_text_en(text: str) -> dict:
    """
    Summarizes the given English text clearly and concisely.
    Returns a short meeting-style summary in English.
    """
    try:
        if not text.strip():
            return {"error": "Empty text for summarization."}

        prompt = (
            "You are a precise meeting summarizer. "
            "Summarize the following transcript into concise, clear English points. "
            "Focus on key discussion topics, decisions, and outcomes.\n\n"
            f"Transcript:\n{text}\n\n"
            "Summary:"
        )

        summary = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # ✅ updated model
            messages=[
                {"role": "system", "content": "You write clear, structured summaries."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=600
        )

        return {"summary_en": summary.choices[0].message.content.strip()}

    except Exception as e:
        print(f"Summarization failed: {e}")
        return {"error": str(e)}

def summarize_text_native(summary_en: str, target_lang: str) -> Dict[str, Any]:
    """
    Translates the English summary into the detected native language.
    Returns the summary in the original spoken language.
    """
    try:
        translated_text = translate_text(summary_en, target_lang)
        # translate_text() already returns a string, not a dict
        return {"summary_native": translated_text}
    except Exception as e:
        print(f"Native summary translation failed: {e}")
        return {"error": str(e)}
    
def moderate_text(text: str) -> Dict[str, Any]:
    """
    Detects offensive, hateful, sexual, violent, or self-harm related content.
    Returns a structured moderation result.
    """
    try:
        if not text.strip():
            return {"error": "Empty text for moderation."}

        prompt = (
            "You are a strict content moderation system. "
            "Analyze the following text and respond ONLY in valid JSON format with these keys:\n"
            "{"
            "\"is_flagged\": bool, "
            "\"categories\": {"
            "\"hate\": bool, "
            "\"violence\": bool, "
            "\"sexual\": bool, "
            "\"self_harm\": bool"
            "}, "
            "\"notes\": string"
            "}\n\n"
            f"Text:\n{text}\n\n"
            "Return JSON only, no extra words."
        )

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a JSON-only moderation classifier."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=300
        )

        raw = response.choices[0].message.content.strip()

        # Attempt to parse JSON safely
        import json
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = {"is_flagged": False, "categories": {}, "notes": "Invalid JSON response"}

        return parsed

    except Exception as e:
        print(f"Moderation failed: {e}")
        return {"error": str(e)}

def _strip_code_fences(text: str) -> str:
    m = re.search(r"```(?:json)?\s*(.+?)\s*```", text, re.S)
    return m.group(1).strip() if m else text.strip()

def _safe_json_loads(text: str) -> Dict[str, Any]:
    try:
        return json.loads(text)
    except Exception:
        text2 = re.sub(r'^\s*json\s*', '', text, flags=re.I).strip()
        try:
            return json.loads(text2)
        except Exception:
            return {}

def _fallback_actions_with_assignees(transcript: str) -> List[Dict[str, str]]:
    items: List[Dict[str, str]] = []
    # scan sentence by sentence
    sentences = re.split(r'(?<=[.!?])\s+', transcript)
    for s in sentences:
        s_clean = s.strip()
        if not s_clean:
            continue
        for pat in ASSIGN_PATTERNS:
            m = pat.search(s_clean)
            if m:
                assignee = m.group(1).strip().rstrip(",.")
                task = m.group(2).strip().rstrip(".")
                # tidy verbs like "to complete"/"complete"
                task = re.sub(r"^(to\s+)", "", task, flags=re.I)
                # cap length
                task = re.sub(r"\s+", " ", task)[:140]
                items.append({"assignee": assignee, "text": task})
                break

    # de-duplicate by assignee+text
    dedup: List[Dict[str, str]] = []
    seen: set[Tuple[str, str]] = set()
    for it in items:
        key = (it["assignee"].lower(), it["text"].lower())
        if key not in seen:
            seen.add(key)
            dedup.append(it)
    return dedup[:10]

class GroqClient:
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)

    def transcribe_bytes(self, audio_bytes: bytes, filename: str = "audio.wav") -> str:
        bio = BytesIO(audio_bytes); bio.name = filename
        tx = self.client.audio.transcriptions.create(
            file=bio, model="whisper-large-v3", response_format="json", temperature=0.0
        )
        return getattr(tx, "text", "") or (tx.get("text") if isinstance(tx, dict) else "")

    def analyze_transcript(self, transcript: str) -> Dict[str, Any]:
        system = (
            "You are an expert Meeting Analysis AI. "
            "Return ONLY valid JSON (no markdown). Schema:\n"
            "{"
            '"summary":"string",'
            '"actions":[{"assignee":"string","text":"string"}],'
            '"moderation":{"interruptions":0,"notes":["string",...]}'
            "}\n"
            "Rules: summary = 1–3 short sentences. "
            "actions = concrete, imperative, ≤120 chars each. "
            "If the assignee is obvious from the transcript, include their first name; otherwise use an empty string."
            "moderation.notes MUST include brief bullets for any toxic or harassing language (e.g., 'toxic: \"idiot\"'), hate, threats, sexual content, or PII (phone/email). If none, return an empty array."

        )
        user = f'Transcript:\n"""\n{transcript}\n"""\nReturn JSON only.'

        resp = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": system},
                      {"role": "user", "content": user}],
            temperature=0.1,
            max_tokens=700,
        )
        content = _strip_code_fences(resp.choices[0].message.content or "")
        data = _safe_json_loads(content)

        summary = (data.get("summary") or "").strip()
        actions = data.get("actions") or []
        moderation = data.get("moderation") or {}
        interruptions = int(moderation.get("interruptions") or 0)
        notes = moderation.get("notes") or []

        # Normalize actions to list of {assignee, text}
        norm_actions: List[Dict[str, str]] = []
        if isinstance(actions, list):
            for a in actions:
                if isinstance(a, dict):
                    norm_actions.append({
                        "assignee": (a.get("assignee") or "").strip(),
                        "text": (a.get("text") or "").strip(),
                    })
                elif isinstance(a, str):
                    # try to pull "Name: task" pattern
                    m = re.match(rf"^\s*({NAME_WORD})\s*[:\-]\s*(.+)$", a)
                    if m:
                        norm_actions.append({"assignee": m.group(1).strip(), "text": m.group(2).strip()})
                    else:
                        norm_actions.append({"assignee": "", "text": a.strip()})
        else:
            norm_actions = []

        # Fallback if model missed names/tasks
        if not norm_actions:
            norm_actions = _fallback_actions_with_assignees(transcript)

        # final trims
        for it in norm_actions:
            it["text"] = re.sub(r"\s+", " ", it["text"]).strip()[:120]
            it["assignee"] = it["assignee"].strip()

        if not summary:
            summary = "Key tasks were assigned with a target of EOD completion."

        return {
            "summary": summary,
            "actions": norm_actions,
            "moderation": {"interruptions": interruptions, "notes": notes if isinstance(notes, list) else [str(notes)]},
        }
