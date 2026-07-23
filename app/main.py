from fastapi import FastAPI
from app.routers.predict import router as predict_router

app = FastAPI(title="tabFM API")

app.include_router(predict_router)

@app.get("/")
async def root():
    return {"message": "Welcome to tabFM!"}
