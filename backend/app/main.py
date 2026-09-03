from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router

app = FastAPI(
    title="GCP Data Infrastructure Calculator",
    description=(
        "Calculadora de custos para projetos de dados no Google Cloud, "
        "baseada em precos oficiais publicados pelo Google Cloud."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def root() -> dict[str, str]:
    return {
        "service": "GCP Data Infrastructure Calculator API",
        "message": "Esta é apenas a API. A interface web roda em http://localhost:3000.",
        "docs": "/docs",
        "services": "/api/services",
    }
