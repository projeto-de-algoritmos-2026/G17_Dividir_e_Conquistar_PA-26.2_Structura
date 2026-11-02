import re
import unicodedata
from dataclasses import dataclass

from backend.core.algoritmos import ContadorInversoes
from backend.core.dividir_conquistar.hirschberg import hirschberg
from backend.core.dividir_conquistar.inversoes import contar_significativas

DISTANCIA_MAX_BLOCO = 2 #correspondências até essa distância pertencem ao mesmo bloco
FAIXAS = [(0.6, "alta"), (0.3, "moderada"), (0.0, "baixa")]

@dataclass
class Segmento:
    texto: str
    inicio: int
    fim: int

def normalizar(texto: str) -> str:
    sem_acento = unicodedata.normalize("NFKD", texto.lower())
    return "".join(c for c in sem_acento if not unicodedata.combining(c))

def ocultar_citacoes(texto: str) -> str:
    #Troca por espaços, em vez de remover, para preservar as posições usadas no destaque.
    apagar = lambda trecho: " " * len(trecho.group())
    texto = re.sub(r'"[^"]*"|“[^”]*”', apagar, texto)
    return re.sub(r'^\s*refer[eê]ncias\b.*', apagar, texto, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL)

def parear(n_a: int, n_b: int, iguais) -> list[tuple[int, int]]:
    #A LCS acha o que está em ordem; a varredura seguinte recupera blocos movidos de lugar.
    pares = hirschberg(list(range(n_a)), list(range(n_b)), iguais)
    usados_a = {i for i, _ in pares}
    usados_b = {j for _, j in pares}
    livres_a = [i for i in range(n_a) if i not in usados_a]

    for j in range(n_b):
        if j in usados_b:
            continue
        for i in livres_a:
            if iguais(i, j):
                pares.append((i, j))
                livres_a.remove(i)
                break

    return sorted(pares, key=lambda par: par[1])

def agrupar_em_blocos(pares: list[tuple[int, int]]) -> list[list[tuple[int, int]]]:
    blocos = []
    for i, j in pares:
        ultimo = blocos[-1][-1] if blocos else None
        continua = ultimo and 0 < i - ultimo[0] <= DISTANCIA_MAX_BLOCO and j - ultimo[1] <= DISTANCIA_MAX_BLOCO
        if continua:
            blocos[-1].append((i, j))
        else:
            blocos.append([(i, j)])
    return blocos

def calcular_ordem(blocos: list[list[tuple[int, int]]], n_pares: int, tolerancia: int) -> float:
    #Mede a desordem entre blocos: mover um parágrafo inteiro é uma única inversão.
    inicios = [bloco[0][0] for bloco in blocos]
    n_blocos = len(blocos)
    maximo = max(n_blocos * (n_blocos - 1) // 2, n_pares - 1)
    if maximo == 0:
        return 1.0
    return 1 - contar_significativas(inicios, tolerancia) / maximo

def classificar(nota: float) -> str:
    return next(faixa for limite, faixa in FAIXAS if nota >= limite)

def explicar(cobertura: float, ordem: float, unidade: str) -> str:
    if cobertura == 0:
        return f"Não há {unidade} suficientes em comum para indicar semelhança."
    if ordem >= 0.8:
        complemento = "praticamente na mesma ordem"
    elif ordem >= 0.4:
        complemento = "com parte da ordem alterada"
    else:
        complemento = "em ordem bastante diferente"
    return f"{cobertura:.0%} das {unidade} do texto suspeito aparecem no original, {complemento}."

def comparar_segmentos(seg_a: list[Segmento], seg_b: list[Segmento], iguais, unidade: str, min_pares: int, min_bloco: int, tolerancia: int, descrever_par=None) -> dict:
    #Pipeline comum: cada modo só define como segmentar e o que conta como igual.
    pares = parear(len(seg_a), len(seg_b), iguais)
    if len(pares) < min_pares:
        pares = []

    #Palavras soltas não contam: coincidem em qualquer texto sobre o mesmo tema.
    blocos = [bloco for bloco in agrupar_em_blocos(pares) if len(bloco) >= min_bloco]
    pares = [par for bloco in blocos for par in bloco]

    cobertura = len(pares) / len(seg_b) if seg_b else 0.0
    ordem = calcular_ordem(blocos, len(pares), tolerancia) if pares else 0.0
    nota = cobertura * (0.5 + 0.5 * ordem)

    contador = ContadorInversoes()
    contador.ordenar_e_contar([i for i, _ in pares])

    trechos = [
        {
            "inicio_a": seg_a[bloco[0][0]].inicio,
            "fim_a": seg_a[bloco[-1][0]].fim,
            "inicio_b": seg_b[bloco[0][1]].inicio,
            "fim_b": seg_b[bloco[-1][1]].fim,
        }
        for bloco in blocos
    ]

    return {
        "nota": round(nota, 4),
        "faixa": classificar(nota),
        "explicacao": explicar(cobertura, ordem, unidade),
        "metricas": [
            {"rotulo": "Cobertura", "valor": f"{cobertura:.0%}"},
            {"rotulo": "Ordem", "valor": f"{ordem:.0%}"},
            {"rotulo": "Blocos", "valor": str(len(blocos))},
            {"rotulo": "Inversões", "valor": str(contador.inversoes)},
            {"rotulo": unidade.capitalize() + " em comum", "valor": str(len(pares))},
        ],
        "trechos": trechos,
        "pares": [descrever_par(i, j) for i, j in pares] if descrever_par else [],
    }
