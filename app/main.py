from fastapi import FastAPI
from slowapi import Limiter, _rate_limit_exceeded_handler 
from slowapi.util import get_remote_address 
from slowapi.errors import RateLimitExceeded
from fastapi.middleware.cors import CORSMiddleware
from .routers import (
    auth_router,
    agent_router,
    questions_router,
    evaluations_router,
    users_router,
    exams_router,
    sessions_router,
    export_router,
    lti_router,
)

limiter = Limiter(key_func=get_remote_address, default_limits=["10/second"])

app = FastAPI(
    title="Ultimate MCQs Agent",
    version="2.0.0",
    description="AI Agent for generating and managing MCQs from text or audio."
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
<<<<<<< HEAD
    allow_origins=["https://bnson.id.vn"],
=======
    allow_origins=[
        "https://bnson.id.vn",                 # <-- THÊM MỚI: Frontend của bạn
        "https://ultimatemcqsagent.moodlecloud.com" # <-- THÊM MỚI: Moodle
    ],
>>>>>>> 5b1e416 (lms 2)
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
app.include_router(export_router.router, tags=["Export"])
app.include_router(lti_router.router)