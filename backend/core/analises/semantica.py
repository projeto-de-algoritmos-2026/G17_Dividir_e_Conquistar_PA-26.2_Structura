import re
from functools import lru_cache

import numpy as np
from fastembed import TextEmbedding

from backend.core.analises.comum import Segmento, classificar, comparar_segmentos, normalizar, ocultar_citacoes
from backend.core.analises.estrutural import extrair_palavras

MODELO = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
LIMIAR_FRASE = 0.55 #abaixo disso, duas frases não contam como a mesma ideia
PESO_PALAVRAS = 0.65 #quanto as palavras em comum aproximam a nota de 1
NEGACOES = {"nao", "nunca", "jamais"}
SIMILARIDADE_NULA = 0.3 #textos sem relação ficam abaixo disso
SIMILARIDADE_TOTAL = 0.7 #reescritas completas costumam ficar perto disso

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

def vetorizar(frases: list[Segmento]) -> np.ndarray:
    #O modelo diferencia maiúsculas e acentos, o que derrubava cópias com grafia alterada.
    vetores = np.array(list(carregar_modelo().embed([normalizar(f.texto) for f in frases])))
    return vetores / np.linalg.norm(vetores, axis=1, keepdims=True)

def tem_negacao(frase: Segmento) -> bool:
    return not NEGACOES.isdisjoint(normalizar(frase.texto).split())

def sobreposicao_palavras(frase_a: Segmento, frase_b: Segmento) -> float:
    #Coeficiente de Dice entre as palavras de conteúdo das duas frases.
    if tem_negacao(frase_a) != tem_negacao(frase_b):
        return 0.0
    palavras_a = {p.texto for p in extrair_palavras(frase_a.texto)}
    palavras_b = {p.texto for p in extrair_palavras(frase_b.texto)}
    total = len(palavras_a) + len(palavras_b)
    return 2 * len(palavras_a & palavras_b) / total if total else 0.0

def reforcar_com_palavras(similaridades: np.ndarray, frases_a: list[Segmento], frases_b: list[Segmento]) -> np.ndarray:
    #Em frases curtas o modelo é impreciso: palavras em comum são uma evidência a mais.
    sobreposicao = np.array([[sobreposicao_palavras(a, b) for b in frases_b] for a in frases_a])
    return similaridades + (1 - similaridades) * PESO_PALAVRAS * sobreposicao

def comparar_textos_inteiros(vetores_a: np.ndarray, vetores_b: np.ndarray) -> float:
    #A média captura a ideia geral, mesmo quando uma frase não corresponde a outra.
    media_a, media_b = vetores_a.mean(axis=0), vetores_b.mean(axis=0)
    similaridade = media_a @ media_b / (np.linalg.norm(media_a) * np.linalg.norm(media_b))
    return float(similaridade)

def rotular(resultado: dict) -> dict:
    return {
        **resultado,
        "titulo": f"Suspeita de plágio {resultado['faixa']}",
        "legenda": "Em destaque: frases com a mesma ideia.",
    }

def analisar_semantica(texto_a: str, texto_b: str) -> dict:
    frases_a = extrair_frases(texto_a)
    frases_b = extrair_frases(texto_b)
    if not frases_a or not frases_b:
        return rotular(comparar_segmentos([], [], None, "frases", 1, 1, 0))

    vetores_a = vetorizar(frases_a)
    vetores_b = vetorizar(frases_b)
    similaridades = reforcar_com_palavras(vetores_a @ vetores_b.T, frases_a, frases_b)
    iguais = lambda i, j: similaridades[i, j] >= LIMIAR_FRASE
    descrever_par = lambda i, j: {
        "texto_a": frases_a[i].texto,
        "texto_b": frases_b[j].texto,
        "nota": round(float(similaridades[i, j]), 2),
    }
    peso = lambda i, j: min(1.0, float(similaridades[i, j]))
    resultado = comparar_segmentos(frases_a, frases_b, iguais, "frases", 1, 1, 0, descrever_par, peso)

    #Reescritas podem fundir ou dividir frases: vale o maior sinal entre as duas visões.
    geral = comparar_textos_inteiros(vetores_a, vetores_b)
    #A escala realça reescritas, mas nunca passa da similaridade medida de verdade.
    escalada = (geral - SIMILARIDADE_NULA) / (SIMILARIDADE_TOTAL - SIMILARIDADE_NULA)
    nota_geral = max(0.0, min(escalada, geral, 1.0))
    resultado["metricas"].insert(0, {"rotulo": "Ideia geral", "valor": f"{nota_geral:.0%}"})

    if nota_geral > resultado["nota"]:
        resultado["nota"] = round(nota_geral, 4)
        resultado["faixa"] = classificar(nota_geral)
        resultado["explicacao"] = f"No conjunto, os textos têm {nota_geral:.0%} de proximidade de ideias, mesmo sem frases correspondentes uma a uma."
    return rotular(resultado)
