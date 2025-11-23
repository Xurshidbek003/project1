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
        "http://127.0.0.1:5500/main.html",
        "http://127.0.0.1:5500/",
        "http://127.0.0.1:5500/token.html",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
