from fastapi import FastAPI

from app.api.documents import router as documents_router
from app.api.faces import router as faces_router

app = FastAPI(
    title="Identity Service",
    description="Servicio independiente para análisis de documentos e identidad.",
    version="0.1.0",
)

app.include_router(documents_router)
app.include_router(faces_router)

@app.get("/health", tags=["Health"])
def health():
    return {
        "status": "ok",
        "service": "identity-service",
    }