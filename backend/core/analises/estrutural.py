import operator
import random
import re

from backend.core.analises.comum import (
    PALAVRA,
    RE_PALAVRA,
    Segmento,
    TextoGrandeDemais,
    avisos_citacoes,
    classificar,
    comparar_segmentos,
    contar_palavras,
    normalizar,
    ocultar_citacoes,
    parear,
    sem_conteudo,
)
from backend.core.dividir_conquistar.hirschberg import hirschberg, tamanho_lcs

MIN_PARES = 3
MIN_BLOCO = 2
TOLERANCIA = 2 #trocas entre palavras vizinhas não contam como desordem
EMBARALHAMENTOS = 3
TOKENS_ACASO_COMPLETO = 40 #em textos curtos, embaralhar quase não muda a sequência
SEMENTE = 17 #fixa para o mesmo par de textos sempre receber a mesma nota
AMOSTRA_ACASO = 800 #a taxa de acaso se estabiliza cedo; o texto inteiro levaria dezenas de segundos
MAX_TOKENS = 6000 #o alinhamento é quadrático: 20.000 caracteres de tokens mínimos levavam 84 segundos
MIN_TOKENS_CONFIAVEL = 20 #medido: abaixo disso, até 46% dos pares sem relação passam de "baixa"; acima, 3%
MIN_TRECHO_LITERAL = 6 #tantas palavras de conteúdo seguidas raramente coincidem por acaso
FAIXAS = [(0.45, "alta"), (0.25, "moderada"), (0.0, "baixa")]
PONTUACAO = ".,;:!?"

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
        if token in PONTUACAO:
            return token
        palavra = normalizar(token)
        if palavra.isdigit():
            return "NUMERO"
        return CLASSE_DA_PALAVRA.get(palavra) or ProcessadorEstruturalLeve.classificar_tamanho(palavra)

    @staticmethod
    def extrair_estrutura(texto: str) -> list[str]:
        #Pontuação e palavras de ligação ficam: elas mostram como o texto é construído.
        tokens = re.findall(rf"{PALAVRA}|[{PONTUACAO}]", ocultar_citacoes(texto))
        return [ProcessadorEstruturalLeve.classificar_token(token) for token in tokens]

def listar_palavras(texto: str) -> list[Segmento]:
    palavras = []
    for achado in RE_PALAVRA.finditer(texto):
        palavra = normalizar(achado.group())
        if palavra not in STOPWORDS:
            palavras.append(Segmento(palavra, achado.start(), achado.end()))
    return palavras

def extrair_palavras(texto: str) -> list[Segmento]:
    return listar_palavras(ocultar_citacoes(texto))

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

def descontar_acaso(forma_a: list[str], forma_b: list[str], bruta: float) -> tuple[float, float]:
    #Com uma categoria só, embaralhar não muda nada: o desconto não teria o que medir.
    if len(set(forma_a + forma_b)) <= 1:
        return bruta, 0.0
    total = len(forma_a) + len(forma_b)
    acaso = medir_acaso(forma_a, forma_b) * min(1, total / TOKENS_ACASO_COMPLETO)
    if acaso >= 1:
        return bruta, acaso
    return max(0.0, (bruta - acaso) / (1 - acaso)), acaso

def analisar_estrutura(texto_a: str, texto_b: str) -> dict:
    forma_a = ProcessadorEstruturalLeve.extrair_estrutura(texto_a)
    forma_b = ProcessadorEstruturalLeve.extrair_estrutura(texto_b)
    if not contar_palavras(ocultar_citacoes(texto_a)) or not contar_palavras(ocultar_citacoes(texto_b)):
        return sem_conteudo()
    if max(len(forma_a), len(forma_b)) > MAX_TOKENS:
        raise TextoGrandeDemais(f"Cada texto pode ter até {MAX_TOKENS:,} palavras e sinais de pontuação.".replace(",", "."))
    total = len(forma_a) + len(forma_b)

    #Simétrica: similaridade é uma relação entre os dois textos, não uma origem.
    bruta = 2 * len(hirschberg(forma_a, forma_b, operator.eq)) / total
    nota, acaso = descontar_acaso(forma_a, forma_b, bruta)

    #Frases curtas têm poucas palavras, então os mínimos acompanham o tamanho do texto.
    palavras_a = extrair_palavras(texto_a)
    palavras_b = extrair_palavras(texto_b)
    iguais = lambda i, j: palavras_a[i].texto == palavras_b[j].texto
    min_pares = min(MIN_PARES, len(palavras_b))
    min_bloco = min(MIN_BLOCO, len(palavras_b))
    literal = comparar_segmentos(palavras_a, palavras_b, iguais, "palavras", min_pares, min_bloco, TOLERANCIA)
    #Conta todas as palavras: "céu azul" e "azul céu" são idênticas, mesmo sem formar bloco.
    identicas = len(parear(len(palavras_a), len(palavras_b), iguais))
    proporcao = identicas / len(palavras_b) if palavras_b else 0.0

    avisos = avisos_citacoes(texto_a, texto_b)
    if literal["maior_bloco"] >= MIN_TRECHO_LITERAL:
        avisos.append(f"Há um trecho com {literal['maior_bloco']} palavras idênticas seguidas.")

    curto = min(len(forma_a), len(forma_b)) < MIN_TOKENS_CONFIAVEL
    if curto:
        avisos.append("Texto curto: coincidir no formato é fácil, e a nota não indica semelhança real.")
    faixa = "inconclusiva" if curto else classificar(nota, FAIXAS)
    return {
        "nota": round(nota, 4),
        "faixa": faixa,
        "titulo": f"Similaridade estrutural {faixa}",
        "explicacao": f"Os textos têm {nota:.0%} de semelhança na forma de construir as frases, sem considerar o assunto.",
        "metricas": [
            {"rotulo": "Formato em comum", "valor": f"{bruta:.0%}"},
            {"rotulo": "Esperado por acaso", "valor": f"{acaso:.0%}"},
            {"rotulo": "Palavras idênticas", "valor": f"{identicas} de {len(palavras_b)} ({proporcao:.0%})"},
            {"rotulo": "Maior trecho idêntico", "valor": f"{literal['maior_bloco']} palavras"},
            {"rotulo": "Trechos idênticos", "valor": str(literal["n_blocos"])},
            {"rotulo": "Ordem dos trechos", "valor": f"{literal['ordem']:.0%}"},
            {"rotulo": "Inversões", "valor": str(literal["n_inversoes"])},
        ],
        "legenda": "Em destaque: trechos com palavras idênticas.",
        "trechos": literal["trechos"],
        "pares": [],
        "avisos": avisos,
    }
