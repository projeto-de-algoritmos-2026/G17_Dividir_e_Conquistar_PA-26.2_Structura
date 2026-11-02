import operator
import random
import re
from dataclasses import dataclass

from backend.core.analises.comum import (
    PALAVRA,
    RE_PALAVRA,
    Segmento,
    TextoGrandeDemais,
    agrupar_em_blocos,
    avisos_citacoes,
    calcular_ordem,
    classificar,
    comparar_segmentos,
    contar_palavras,
    eh_abreviacao,
    normalizar,
    ocultar_citacoes,
    parear,
    pontuar,
    sem_conteudo,
)
from backend.core.algoritmos import ContadorInversoes
from backend.core.analises.gramatica import classificar_palavra, classificar_tokens, tem_acentos
from backend.core.dividir_conquistar.hirschberg import hirschberg, tamanho_lcs

MIN_PARES = 3
MIN_BLOCO = 2
TOLERANCIA = 2 #trocas entre palavras vizinhas não contam como desordem
EMBARALHAMENTOS = 3
SEMENTE = 17 #fixa para o mesmo par de textos sempre receber a mesma nota
AMOSTRA_ACASO = 800 #a taxa de acaso se estabiliza cedo; o texto inteiro levaria dezenas de segundos
MAX_TOKENS = 6000 #o alinhamento é quadrático: 20.000 caracteres de tokens mínimos levavam 84 segundos
MIN_TOKENS_CONFIAVEL = 20 #medido em frases reais: abaixo disso, até 31% dos pares sem relação passam de "baixa"
MIN_TRECHO_LITERAL = 6 #tantas palavras de conteúdo seguidas raramente coincidem por acaso
LIMIAR_CONSTRUCAO = 0.75 #medido em frases reais: acima disso, duas frases independentes quase nunca chegam
EXIGENCIA_POR_TOKEN = 0.01 #frases curtas coincidem mais: p99 sem relação vai de 0,80 (10 tokens) a 0,70 (25)
TOKENS_LIMIAR_BASE = 20 #a partir daqui, o limiar para de subir
MAX_TOKENS_FRASE = 60 #sem pontuação, o texto inteiro viraria uma "frase", e a maioria dos tokens coincide por acaso
MIN_FRASES_CONTIDAS = 3 #com menos, "o texto menor inteiro está no maior" acontece por acaso
LIMIAR_CONTIDO = 0.9 #medido: entre dezenas de frases candidatas, alguma passa de 0,75 sem nenhuma relação
PONTUACAO = ".,;:!?"
FIM_DE_CONSTRUCAO = ".!?;:"
RE_TOKEN = re.compile(rf"\d+(?:[.,]\d+)*|{PALAVRA}|[{PONTUACAO}]")
RE_LINHA_EM_BRANCO = re.compile(r"\n[ \t]*\n")

STOPWORDS = set("""
a ao aos as com como da das de do dos e ela elas ele eles em entre era essa esse esta este
eu foi for ha isso isto ja la lhe mais mas me mesmo meu minha muito na nas nao nem no nos
nossa nosso num numa o os ou para pela pelas pelo pelos por qual quando que quem se sem ser
seu seus sua suas sao tambem te tem ter um uma uns umas voce
""".split())

@dataclass(frozen=True)
class Construcao:
    formas: tuple[str, ...]
    inicio: int
    fim: int

class ProcessadorEstruturalLeve:
    """Extração de estrutura pela classe gramatical de cada palavra (Pure Python)."""
    @staticmethod
    def classificar_token(token: str) -> str:
        return token if token in PONTUACAO else classificar_palavra(token)

    @staticmethod
    def extrair_construcoes(texto: str, respeitar_acentos: bool = True) -> list[Construcao]:
        #Pontuação e palavras de ligação ficam: elas mostram como o texto é construído.
        limpo = ocultar_citacoes(texto)
        achados = list(RE_TOKEN.finditer(limpo))
        tokens = [achado.group() for achado in achados]
        formas = classificar_tokens(tokens, PONTUACAO, respeitar_acentos)

        construcoes = []
        comeco = 0
        for k, achado in enumerate(achados):
            ultimo = k + 1 == len(achados)
            seguinte = tokens[k + 1] if not ultimo else ""
            pausa = tokens[k] in FIM_DE_CONSTRUCAO and seguinte not in PONTUACAO and not (k and eh_abreviacao(tokens[k - 1]))
            entre = limpo[achado.end():achados[k + 1].start()] if not ultimo else ""
            longa = k + 1 - comeco >= MAX_TOKENS_FRASE
            tem_palavra = any(token not in PONTUACAO for token in tokens[comeco:k + 1])
            if ultimo or (tem_palavra and (pausa or longa or RE_LINHA_EM_BRANCO.search(entre))):
                construcoes.append(Construcao(tuple(formas[comeco:k + 1]), achados[comeco].start(), achado.end()))
                comeco = k + 1
        return construcoes

    @staticmethod
    def extrair_estrutura(texto: str, respeitar_acentos: bool = True) -> list[str]:
        return [forma for c in ProcessadorEstruturalLeve.extrair_construcoes(texto, respeitar_acentos) for forma in c.formas]

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
    #Embaralhar um lado mantém as mesmas categorias, mas destrói a construção do texto.
    forma_a, forma_b = sorted((forma_a, forma_b)) #qual texto vem primeiro não pode mudar a nota
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
    acaso = medir_acaso(forma_a, forma_b)
    if acaso >= 1:
        return bruta, acaso
    return max(0.0, (bruta - acaso) / (1 - acaso)), acaso

def limiar_do_par(tamanho_a: int, tamanho_b: int) -> float:
    return LIMIAR_CONSTRUCAO + EXIGENCIA_POR_TOKEN * max(0, TOKENS_LIMIAR_BASE - (tamanho_a + tamanho_b) / 2)

def tabela_de_construcoes(formas_a: list[tuple], formas_b: list[tuple]) -> list[list[int]]:
    #Tokens em comum de cada par de frases; textos repetem formas, e cada forma distinta só é medida uma vez.
    distintas_a = list(dict.fromkeys(formas_a))
    distintas_b = list(dict.fromkeys(formas_b))
    medidas = {}
    for x in distintas_a:
        for y in distintas_b:
            #2 × menor / soma é o máximo que o par alcançaria: abaixo do limiar, o alinhamento é dispensável.
            alcancavel = 2 * min(len(x), len(y)) / (len(x) + len(y)) >= limiar_do_par(len(x), len(y))
            medidas[x, y] = tamanho_lcs(list(x), list(y), operator.eq) if alcancavel else 0
    return [[medidas[x, y] for y in formas_b] for x in formas_a]

def alinhar_construcoes(frases_a: list[Construcao], frases_b: list[Construcao]) -> dict:
    #Cada frase acha a sua par em qualquer posição: mudar a ordem não pode esconder a mesma construção.
    formas_a = [f.formas for f in frases_a]
    formas_b = [f.formas for f in frases_b]
    comuns = tabela_de_construcoes(formas_a, formas_b)
    similaridade = lambda i, j: 2 * comuns[i][j] / (len(formas_a[i]) + len(formas_b[j]))
    iguais = lambda i, j: similaridade(i, j) >= limiar_do_par(len(formas_a[i]), len(formas_b[j]))
    pares = parear(len(frases_a), len(frases_b), iguais, lambda i, j: float(comuns[i][j]))
    return {
        "pares": pares,
        "similaridade": similaridade,
        "tokens_em_comum": sum(comuns[i][j] for i, j in pares),
    }

def texto_contido(alinhamento: dict) -> bool:
    pares = alinhamento["pares"]
    if len(pares) < MIN_FRASES_CONTIDAS or alinhamento["tokens_em_comum"] < MIN_TOKENS_CONFIAVEL:
        return False
    return sum(alinhamento["similaridade"](i, j) for i, j in pares) / len(pares) >= LIMIAR_CONTIDO

def medir_frases(alinhamento: dict, total_a: int, total_b: int) -> dict:
    pares = alinhamento["pares"]
    comum = alinhamento["tokens_em_comum"]
    conjunta = 2 * comum / (total_a + total_b)
    #max em vez de um sentido fixo: mantém a nota simétrica e impede diluir a cópia com material novo.
    cobertura = max(comum / total_a, comum / total_b) if texto_contido(alinhamento) else conjunta
    blocos = agrupar_em_blocos(pares, 1)
    ordem = calcular_ordem(blocos, len(pares), 0) if pares else 0.0
    contador = ContadorInversoes()
    contador.ordenar_e_contar([i for i, _ in pares])
    return {
        "nota": pontuar(cobertura, ordem),
        "conjunta": conjunta,
        "cobertura": cobertura,
        "ordem": ordem,
        "inversoes": contador.inversoes,
    }

def explicar_nota(nota: float, medidas: dict) -> str:
    if medidas["cobertura"] > medidas["conjunta"] and medidas["nota"] >= nota:
        return f"{medidas['cobertura']:.0%} do texto menor segue a construção de frases do outro, que tem material a mais."
    return f"Os textos têm {nota:.0%} de semelhança na forma de construir as frases, sem considerar o assunto."

def analisar_estrutura(texto_a: str, texto_b: str) -> dict:
    respeitar_acentos = tem_acentos(texto_a) and tem_acentos(texto_b) #sem acento de um lado, "é" e "e" se confundem
    frases_a = ProcessadorEstruturalLeve.extrair_construcoes(texto_a, respeitar_acentos)
    frases_b = ProcessadorEstruturalLeve.extrair_construcoes(texto_b, respeitar_acentos)
    forma_a = [forma for frase in frases_a for forma in frase.formas]
    forma_b = [forma for frase in frases_b for forma in frase.formas]
    if not contar_palavras(ocultar_citacoes(texto_a)) or not contar_palavras(ocultar_citacoes(texto_b)):
        return sem_conteudo()
    if max(len(forma_a), len(forma_b)) > MAX_TOKENS:
        raise TextoGrandeDemais(f"Cada texto pode ter até {MAX_TOKENS:,} palavras e sinais de pontuação.".replace(",", "."))
    total = len(forma_a) + len(forma_b)

    #A comparação do texto inteiro cobre frases fundidas ou divididas, que não têm uma par exata.
    bruta = 2 * len(hirschberg(forma_a, forma_b, operator.eq)) / total
    continua, acaso = descontar_acaso(forma_a, forma_b, bruta)
    alinhamento = alinhar_construcoes(frases_a, frases_b)
    medidas = medir_frases(alinhamento, len(forma_a), len(forma_b))
    nota = max(medidas["nota"], continua)

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
    faixa = "inconclusiva" if curto else classificar(nota)
    pares = alinhamento["pares"]
    limpo_a, limpo_b = ocultar_citacoes(texto_a), ocultar_citacoes(texto_b)
    return {
        "nota": round(nota, 4),
        "faixa": faixa,
        "titulo": f"Similaridade estrutural {faixa}",
        "explicacao": explicar_nota(nota, medidas),
        "metricas": [
            {"rotulo": "Frases de mesma construção", "valor": f"{len(pares)} de {max(len(frases_a), len(frases_b))}"},
            {"rotulo": "Ordem das frases", "valor": f"{medidas['ordem']:.0%}" if pares else "—"},
            {"rotulo": "Inversões", "valor": str(medidas["inversoes"])},
            {"rotulo": "Formato em comum", "valor": f"{bruta:.0%}"},
            {"rotulo": "Esperado por acaso", "valor": f"{acaso:.0%}"},
            {"rotulo": "Palavras idênticas", "valor": f"{identicas} de {len(palavras_b)} ({proporcao:.0%})"},
            {"rotulo": "Maior trecho idêntico", "valor": f"{literal['maior_bloco']} palavras"},
            {"rotulo": "Trechos idênticos", "valor": str(literal["n_blocos"])},
        ],
        "legenda": "Em destaque: trechos com palavras idênticas.",
        "trechos": literal["trechos"],
        "titulo_pares": "Frases com a mesma construção",
        "pares": [
            {
                "texto_a": " ".join(limpo_a[frases_a[i].inicio:frases_a[i].fim].split()),
                "texto_b": " ".join(limpo_b[frases_b[j].inicio:frases_b[j].fim].split()),
                "nota": round(alinhamento["similaridade"](i, j), 2),
            }
            for i, j in pares
        ],
        "avisos": avisos,
    }
