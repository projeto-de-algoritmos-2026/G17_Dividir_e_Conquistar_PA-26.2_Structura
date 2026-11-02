from fastapi import APIRouter, HTTPException
from backend.schemas.models import MAX_CARACTERES, TextoRequest
from backend.core.analises.registro import ANALISES

#agrupa os endpoints
router = APIRouter()

@router.get("/analises")
def listar_analises():
    modos = [
        {"id": id_modo, "rotulo": a["rotulo"], "descricao": a["descricao"]}
        for id_modo, a in ANALISES.items()
    ]
    return {"modos": modos, "max_caracteres": MAX_CARACTERES}

@router.post("/comparar")
def comparar_textos(payload: TextoRequest):
    if payload.modo not in ANALISES:
        raise HTTPException(status_code=422, detail="Modo de análise desconhecido.")

    resultado = ANALISES[payload.modo]["analisar"](payload.texto_a, payload.texto_b)
    return {"modo": payload.modo, **resultado}
