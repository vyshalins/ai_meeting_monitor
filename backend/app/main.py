# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.routes import router as api_router

app = FastAPI(
    title="AI Meeting Monitor",
    version="0.1.0",
    docs_url="/docs",       # ensure docs are ON
    redoc_url="/redoc",     # optional, nice to have
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

# mount v1 API
app.include_router(api_router, prefix="/api/v1")
