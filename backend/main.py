from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from backend.api.routes import router as api_router

PASTA_FRONTEND = Path(__file__).parent.parent / "frontend"

app = FastAPI(title="Detector de Similaridade Estrutural", version="1.0")

app.include_router(api_router, prefix="/api")

@app.get("/api/status")
def health_check():
    return {"status": "ok", "mensagem": "Servidor rodando"}

#Fica por último para não capturar as rotas da API.
app.mount("/", StaticFiles(directory=PASTA_FRONTEND, html=True), name="frontend")
