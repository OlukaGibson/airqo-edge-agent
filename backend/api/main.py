from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routers import router
from backend.database.database import engine, Base

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Air Quality Edge Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
