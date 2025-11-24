from fastapi import FastAPI
from database import Base, engine
from fastapi.middleware.cors import CORSMiddleware
from routers.users import router as auth_router

app = FastAPI(
    title="Kindergarten",
    description="API for kindergarten management",
    version="0.0.1",
    docs_url="/",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173/register",
        "https://forkindergarten.netlify.app/",
        "http://localhost:5173/"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
