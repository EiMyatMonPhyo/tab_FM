from fastapi import FastAPI
from app.routers.predict import router as predict_router
from app.routers.fit import router as fit_router
from app.routers.predict_proba import router as predict_proba_router

app = FastAPI(title="tabFM API")

app.include_router(fit_router)
app.include_router(predict_router)
app.include_router(predict_proba_router)

@app.get("/")
async def root():
    return {"message": "Welcome to tabFM!"}
