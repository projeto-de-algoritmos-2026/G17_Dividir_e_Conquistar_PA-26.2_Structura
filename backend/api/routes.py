from fastapi import APIRouter
from backend.schemas.models import TextoRequest
from backend.core.algoritmos import AnalisadorSimilaridade

#agrupa os endpoints
router = APIRouter()

analisador = AnalisadorSimilaridade()

@router.post("/comparar")
def comparar_textos(payload: TextoRequest):
    resultado = analisador.analisar(payload.texto_a, payload.texto_b)
    return resultado