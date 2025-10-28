from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import (
    auth_router,
    agent_router,
    questions_router,
    evaluations_router,
    users_router,
    exams_router,
    sessions_router,
)

app = FastAPI(
    title="Ultimate MCQs Agent",
    version="2.0.0",
    description="AI Agent for generating and managing MCQs from text or audio."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def health():
    return {"status": "ok", "description": "Ultimate MCQ Agent is running"}

app.include_router(auth_router.router)
app.include_router(agent_router.router)
app.include_router(questions_router.router)
app.include_router(evaluations_router.router)
app.include_router(users_router.router)
app.include_router(exams_router.router)
app.include_router(sessions_router.router)