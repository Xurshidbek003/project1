from fastapi import FastAPI
from database import Base, engine
from routers.users import router as auth_router

app = FastAPI(
    title="Kindergarten",
    description="API for kindergarten management",
    version="0.0.1",
    docs_url="/",
)

Base.metadata.create_all(bind=engine)

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
