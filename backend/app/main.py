from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.auth import router as auth_router
from app.api.routes.categories import router as categories_router
from app.api.routes.comments import router as comments_router
from app.api.routes.tickets import router as tickets_router
from app.core.config import settings

ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Ticket Portal API is running"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(auth_router)
app.include_router(categories_router)
app.include_router(tickets_router)
app.include_router(comments_router)