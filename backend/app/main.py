from fastapi import FastAPI
from app.api.routes import router
from app.db.database import engine, Base
from app.db import models

app = FastAPI(title="Resume-JD Matcher")

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

app.include_router(router)
