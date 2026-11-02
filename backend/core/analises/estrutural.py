import operator
import random
import re

from backend.core.analises.comum import Segmento, classificar, comparar_segmentos, normalizar, ocultar_citacoes, parear
from backend.core.dividir_conquistar.hirschberg import hirschberg, tamanho_lcs

MIN_PARES = 3
MIN_BLOCO = 2
TOLERANCIA = 2 #trocas entre palavras vizinhas não contam como desordem
EMBARALHAMENTOS = 3
TOKENS_ACASO_COMPLETO = 40 #em textos curtos, embaralhar quase não muda a sequência
SEMENTE = 17 #fixa para o mesmo par de textos sempre receber a mesma nota
AMOSTRA_ACASO = 800 #a taxa de acaso se estabiliza cedo; o texto inteiro levaria dezenas de segundos
FAIXAS = [(0.45, "alta"), (0.25, "moderada"), (0.0, "baixa")]

STOPWORDS = set("""
a ao aos as com como da das de do dos e ela elas ele eles em entre era essa esse esta este
eu foi for ha isso isto ja la lhe mais mas me mesmo meu minha muito na nas nao nem no nos
nossa nosso num numa o os ou para pela pelas pelo pelos por qual quando que quem se sem ser
seu seus sua suas sao tambem te tem ter um uma uns umas voce
""".split())

CLASSES_GRAMATICAIS = {
    "ARTIGO": "a o as os um uma uns umas",
    "PREPOSICAO": """de do da dos das em no na nos nas num numa por pelo pela pelos pelas
                     para com sem sobre entre ate ao aos desde contra""",
    "CONJUNCAO": "e ou mas porem pois porque que se como quando onde embora enquanto nem",
    "PRONOME": """eu tu ele ela nos eles elas voce me te lhe seu sua seus suas meu minha
                  este esta esse essa estes estas esses essas isso isto aquele aquela""",
    "NEGACAO": "nao nunca jamais",
}
CLASSE_DA_PALAVRA = {p: classe for classe, palavras in CLASSES_GRAMATICAIS.items() for p in palavras.split()}

class ProcessadorEstruturalLeve:
    """Extração de estrutura baseada em proxy de tamanho de palavras (Pure Python)."""
    #proxy de tamanho de palavras
    @staticmethod
    def classificar_tamanho(palavra: str) -> str:
        tamanho = len(palavra)
        if tamanho <= 4:
            return "MUITO_CURTA"
        elif tamanho <= 6:
            return "CURTA"
        elif tamanho <= 8:
            return "MEDIA"
        elif tamanho <= 10:
            return "LONGA"
        else:
            return "MUITO_LONGA"

    @staticmethod
    def classificar_token(token: str) -> str:
        if not token[0].isalnum():
            return token
        if token.isdigit():
            return "NUMERO"
        palavra = normalizar(token)
        return CLASSE_DA_PALAVRA.get(palavra) or ProcessadorEstruturalLeve.classificar_tamanho(palavra)

    @staticmethod
    def extrair_estrutura(texto: str) -> list[str]:
        #Pontuação e palavras de ligação ficam: elas mostram como o texto é construído.
        tokens = re.findall(r"\w+|[.,;:!?]", ocultar_citacoes(texto))
        return [ProcessadorEstruturalLeve.classificar_token(token) for token in tokens]

def extrair_palavras(texto: str) -> list[Segmento]:
    palavras = []
    for achado in re.finditer(r"\w+", ocultar_citacoes(texto)):
        palavra = normalizar(achado.group())
        if palavra not in STOPWORDS:
            palavras.append(Segmento(palavra, achado.start(), achado.end()))
    return palavras

def medir_acaso(forma_a: list[str], forma_b: list[str]) -> float:
    #Embaralhar B mantém as mesmas categorias, mas destrói a construção do texto.
    gerador = random.Random(SEMENTE)
    amostra_a = forma_a[:AMOSTRA_ACASO]
    embaralhada = list(forma_b)
    total = 0
    for _ in range(EMBARALHAMENTOS):
        gerador.shuffle(embaralhada)
        total += tamanho_lcs(amostra_a, embaralhada[:AMOSTRA_ACASO], operator.eq)
    return 2 * total / EMBARALHAMENTOS / (len(amostra_a) + min(len(forma_b), AMOSTRA_ACASO))

def analisar_estrutura(texto_a: str, texto_b: str) -> dict:
    forma_a = ProcessadorEstruturalLeve.extrair_estrutura(texto_a)
    forma_b = ProcessadorEstruturalLeve.extrair_estrutura(texto_b)
    total = len(forma_a) + len(forma_b)

    #Simétrica: similaridade é uma relação entre os dois textos, não uma origem.
    bruta = 2 * len(hirschberg(forma_a, forma_b, operator.eq)) / total if total else 0.0
    acaso = medir_acaso(forma_a, forma_b) * min(1, total / TOKENS_ACASO_COMPLETO) if total else 0.0
    nota = max(0.0, (bruta - acaso) / (1 - acaso))

    #Frases curtas têm poucas palavras, então os mínimos acompanham o tamanho do texto.
    palavras_a = extrair_palavras(texto_a)
    palavras_b = extrair_palavras(texto_b)
    iguais = lambda i, j: palavras_a[i].texto == palavras_b[j].texto
    min_pares = min(MIN_PARES, len(palavras_b))
    min_bloco = min(MIN_BLOCO, len(palavras_b))
    literal = comparar_segmentos(palavras_a, palavras_b, iguais, "palavras", min_pares, min_bloco, TOLERANCIA)
    _, ordem, trechos, inversoes, _ = [metrica["valor"] for metrica in literal["metricas"]]
    #Conta todas as palavras: "céu azul" e "azul céu" são idênticas, mesmo sem formar bloco.
    identicas = len(parear(len(palavras_a), len(palavras_b), iguais)) / len(palavras_b) if palavras_b else 0.0

    faixa = classificar(nota, FAIXAS)
    return {
        "nota": round(nota, 4),
        "faixa": faixa,
        "titulo": f"Similaridade estrutural {faixa}",
        "explicacao": f"Os textos têm {nota:.0%} de semelhança na forma de construir as frases, sem considerar o assunto.",
        "metricas": [
            {"rotulo": "Formato em comum", "valor": f"{bruta:.0%}"},
            {"rotulo": "Esperado por acaso", "valor": f"{acaso:.0%}"},
            {"rotulo": "Palavras idênticas", "valor": f"{identicas:.0%}"},
            {"rotulo": "Trechos idênticos", "valor": trechos},
            {"rotulo": "Ordem dos trechos", "valor": ordem},
            {"rotulo": "Inversões", "valor": inversoes},
        ],
        "legenda": "Em destaque: trechos com palavras idênticas.",
        "trechos": literal["trechos"],
        "pares": [],
    }
