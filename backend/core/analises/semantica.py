import re
from functools import lru_cache

import numpy as np
from fastembed import TextEmbedding

from backend.core.analises.comum import Segmento, comparar_segmentos, normalizar, ocultar_citacoes

MODELO = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

@lru_cache
def carregar_modelo() -> TextEmbedding:
    #Carregado só no primeiro uso: a primeira execução baixa o modelo.
    return TextEmbedding(MODELO)

def extrair_frases(texto: str) -> list[Segmento]:
    frases = []
    for achado in re.finditer(r"[^.!?\n]+[.!?]*", ocultar_citacoes(texto)):
        if re.search(r"\w", achado.group()):
            inicio = achado.start() + len(achado.group()) - len(achado.group().lstrip())
            frases.append(Segmento(achado.group().strip(), inicio, achado.end()))
    return frases

def calcular_similaridades(frases_a: list[Segmento], frases_b: list[Segmento]) -> np.ndarray:
    #O modelo diferencia maiúsculas e acentos, o que derrubava cópias com grafia alterada.
    #Com vetores normalizados, o produto escalar é a similaridade de cosseno.
    vetores = np.array(list(carregar_modelo().embed([normalizar(f.texto) for f in frases_a + frases_b])))
    vetores /= np.linalg.norm(vetores, axis=1, keepdims=True)
    return vetores[:len(frases_a)] @ vetores[len(frases_a):].T

def rotular(resultado: dict) -> dict:
    return {
        **resultado,
        "titulo": f"Suspeita de plágio {resultado['faixa']}",
        "legenda": "Em destaque: frases com a mesma ideia.",
    }

def analisar_semantica(texto_a: str, texto_b: str, limiar: float) -> dict:
    frases_a = extrair_frases(texto_a)
    frases_b = extrair_frases(texto_b)
    if not frases_a or not frases_b:
        return rotular(comparar_segmentos([], [], None, "frases", 1, 1, 0))

    similaridades = calcular_similaridades(frases_a, frases_b)
    iguais = lambda i, j: similaridades[i, j] >= limiar
    descrever_par = lambda i, j: {
        "texto_a": frases_a[i].texto,
        "texto_b": frases_b[j].texto,
        "nota": round(float(similaridades[i, j]), 2),
    }
    return rotular(comparar_segmentos(frases_a, frases_b, iguais, "frases", 1, 1, 0, descrever_par))
