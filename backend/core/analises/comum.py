import re
import unicodedata
from dataclasses import dataclass

from backend.core.algoritmos import ContadorInversoes
from backend.core.dividir_conquistar.hirschberg import hirschberg, hirschberg_ponderado
from backend.core.dividir_conquistar.inversoes import contar_significativas

DISTANCIA_MAX_BLOCO = 2 #correspondências até essa distância pertencem ao mesmo bloco
FAIXAS = [(0.6, "alta"), (0.3, "moderada"), (0.0, "baixa")]
PESO_FIXO_ORDEM = 0.85 #reordenar não apaga a cópia: a ordem só tira até 15% da nota

MAX_PALAVRAS_CITACAO = 40 #além disso, aspas deixam de ser citação curta e viram esconderijo
MAX_PROPORCAO_CITACOES = 0.25 #citar demais não pode tirar o texto da análise
INICIO_MINIMO_REFERENCIAS = 0.5 #o título de referências só vale na segunda metade do texto
ABREVIACOES = {
    "dr", "dra", "sr", "sra", "srs", "sras", "prof", "profa", "art", "arts", "fig", "figs",
    "pag", "pags", "vol", "ed", "cap", "av", "tel", "num", "ex", "obs", "ltda", "cia",
}

INVISIVEIS = "­​-‏‪-‮⁠-⁤⁦-⁯﻿"
ACENTOS_SOLTOS = "̀-ͯ"
PALAVRA = rf"[{INVISIVEIS}{ACENTOS_SOLTOS}]*\w[\w{INVISIVEIS}{ACENTOS_SOLTOS}]*"
RE_PALAVRA = re.compile(PALAVRA)

#Letras de outros alfabetos que parecem latinas, já em minúsculas.
HOMOGLIFOS = str.maketrans("аеорсухіјѕһԁԛԝѵвнмткαοερτυνικ", "aeopcyxijshdqwvbhmtkaoeptuvik")

ASPAS = re.compile(r'(?<![\w"])"(?=\S)[^"]*(?<=\S)"(?!\w)|“[^”]*”|«[^»]*»')
TITULO_REFERENCIAS = re.compile(
    r"^[ \t]*(?:\d+[.)]?[ \t]*)?(?:refer[eê]ncias(?:[ \t]+bibliogr[aá]ficas)?|bibliografia)[ \t]*:?[ \t]*$",
    flags=re.IGNORECASE | re.MULTILINE,
)

class TextoGrandeDemais(Exception):
    """O texto passa do que a análise consegue processar em tempo razoável."""

@dataclass
class Segmento:
    texto: str
    inicio: int
    fim: int

def _trocar_homoglifos(achado: re.Match) -> str:
    #Só troca palavras inteiramente latinas depois da troca: russo e grego de verdade ficam intactos.
    trocada = achado.group().translate(HOMOGLIFOS)
    return trocada if trocada.isascii() else achado.group()

def normalizar(texto: str) -> str:
    decomposto = unicodedata.normalize("NFKD", texto.lower())
    limpo = "".join(c for c in decomposto if not unicodedata.combining(c) and unicodedata.category(c) != "Cf")
    return limpo if limpo.isascii() else re.sub(r"\w+", _trocar_homoglifos, limpo)

def eh_abreviacao(palavra: str) -> bool:
    #Ponto de abreviação ou de inicial ("Dr. Silva", "J. Silva") não termina a frase.
    return normalizar(palavra) in ABREVIACOES or (len(palavra) == 1 and palavra.isupper())

def contar_palavras(texto: str) -> int:
    return sum(1 for _ in RE_PALAVRA.finditer(texto))

def _inicio_referencias(texto: str) -> int:
    for titulo in TITULO_REFERENCIAS.finditer(texto):
        if titulo.start() >= len(texto) * INICIO_MINIMO_REFERENCIAS:
            return titulo.start()
    return len(texto)

def _separar_citacoes(corpo: str) -> tuple[list[re.Match], list[re.Match]]:
    #Devolve as citações aceitas e as recusadas, grandes demais para saírem da análise.
    achadas = list(ASPAS.finditer(corpo))
    curtas = [c for c in achadas if contar_palavras(c.group()) <= MAX_PALAVRAS_CITACAO]
    if sum(contar_palavras(c.group()) for c in curtas) > MAX_PROPORCAO_CITACOES * contar_palavras(corpo):
        return [], achadas
    return curtas, [c for c in achadas if c not in curtas]

def ocultar_citacoes(texto: str) -> str:
    #Troca por espaços, em vez de remover, para preservar as posições usadas no destaque.
    fim_corpo = _inicio_referencias(texto)
    corpo = texto[:fim_corpo]
    aceitas, _ = _separar_citacoes(corpo)
    pedacos = []
    posicao = 0
    for citacao in aceitas:
        pedacos += [corpo[posicao:citacao.start()], " " * len(citacao.group())]
        posicao = citacao.end()
    return "".join(pedacos) + corpo[posicao:] + " " * (len(texto) - fim_corpo)

def avisos_citacoes(texto_a: str, texto_b: str) -> list[str]:
    #A nota muda conforme o que sai da análise, então quem revisa precisa saber disso.
    avisos = []
    for nome, texto in (("original", texto_a), ("suspeito", texto_b)):
        total = contar_palavras(texto)
        ignoradas = total - contar_palavras(ocultar_citacoes(texto))
        if ignoradas:
            avisos.append(f"{ignoradas / total:.0%} do texto {nome} ficou fora da análise por estar em citações ou referências.")
        if _separar_citacoes(texto[:_inicio_referencias(texto)])[1]:
            avisos.append(f"O texto {nome} tem citações longas ou numerosas demais para serem ignoradas: elas foram analisadas.")
    return avisos

def sem_conteudo(titulo_texto: str = "Sem conteúdo para analisar") -> dict:
    #Nota vazia, e não 0%: nada analisado não pode parecer um texto sem indícios.
    return {
        "nota": None,
        "faixa": "indisponivel",
        "titulo": titulo_texto,
        "explicacao": "Depois de retirar citações, referências e pontuação, faltou texto em um dos lados.",
        "metricas": [],
        "legenda": "",
        "trechos": [],
        "titulo_pares": "",
        "pares": [],
        "avisos": [],
    }

def _recuperar_movidos(pares: list[tuple[int, int]], n_a: int, n_b: int, iguais, peso) -> None:
    usados_a = {i for i, _ in pares}
    usados_b = {j for _, j in pares}
    livres_a = [i for i in range(n_a) if i not in usados_a]
    livres_b = [j for j in range(n_b) if j not in usados_b]

    if peso:
        candidatos = [(i, j) for j in livres_b for i in livres_a if iguais(i, j)]
        for i, j in sorted(candidatos, key=lambda par: -peso(*par)):
            if i not in usados_a and j not in usados_b:
                pares.append((i, j))
                usados_a.add(i)
                usados_b.add(j)
        return

    for j in livres_b:
        for i in livres_a:
            if iguais(i, j):
                pares.append((i, j))
                livres_a.remove(i)
                break

def parear(n_a: int, n_b: int, iguais, peso=None, resgate=None) -> list[tuple[int, int]]:
    #A LCS acha o que está em ordem; a varredura seguinte recupera blocos movidos de lugar.
    indices_a, indices_b = list(range(n_a)), list(range(n_b))
    if peso:
        pares = hirschberg_ponderado(indices_a, indices_b, lambda i, j: peso(i, j) if iguais(i, j) else 0.0)
    else:
        pares = hirschberg(indices_a, indices_b, iguais)
    _recuperar_movidos(pares, n_a, n_b, iguais, peso)

    if resgate:
        #Vem depois do alinhamento para nunca disputar lugar com um par direto.
        #Uma frase dividida em duas, ou repetida, ainda vem da mesma frase do original.
        usados_b = {j for _, j in pares}
        for j in set(range(n_b)) - usados_b:
            melhor = max(range(n_a), key=lambda i: resgate(i, j))
            if resgate(melhor, j) > 0:
                pares.append((melhor, j))

    return sorted(pares, key=lambda par: par[1])

def agrupar_em_blocos(pares: list[tuple[int, int]], distancia: int = DISTANCIA_MAX_BLOCO) -> list[list[tuple[int, int]]]:
    blocos = []
    for i, j in pares:
        ultimo = blocos[-1][-1] if blocos else None
        continua = ultimo and 0 <= i - ultimo[0] <= distancia and j - ultimo[1] <= distancia
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

def classificar(nota: float, faixas: list[tuple[float, str]] = FAIXAS) -> str:
    return next(faixa for limite, faixa in faixas if nota >= limite)

def pontuar(cobertura: float, ordem: float) -> float:
    return cobertura * (PESO_FIXO_ORDEM + (1 - PESO_FIXO_ORDEM) * ordem)

def explicar(cobertura: float, ordem: float, unidade: str) -> str:
    if cobertura == 0:
        return f"Nenhuma das {unidade} do texto suspeito tem equivalente no original."
    if ordem >= 0.8:
        complemento = "praticamente na mesma ordem"
    elif ordem >= 0.4:
        complemento = "com parte da ordem alterada"
    else:
        complemento = "em ordem bastante diferente"
    return f"O texto suspeito tem {cobertura:.0%} de equivalência com o original, {complemento}."

def comparar_segmentos(seg_a: list[Segmento], seg_b: list[Segmento], iguais, unidade: str, min_pares: int, min_bloco: int, tolerancia: int, descrever_par=None, peso=None, distancia: int = DISTANCIA_MAX_BLOCO, resgate=None) -> dict:
    #Pipeline comum: cada modo só define como segmentar e o que conta como igual.
    pares = parear(len(seg_a), len(seg_b), iguais, peso, resgate)
    if len(pares) < min_pares:
        pares = []

    #Palavras soltas não contam: coincidem em qualquer texto sobre o mesmo tema.
    blocos = [bloco for bloco in agrupar_em_blocos(pares, distancia) if len(bloco) >= min_bloco]
    pares = [par for bloco in blocos for par in bloco]

    #Sem peso, cada par vale 1; com peso, vale o quanto os dois segmentos se parecem.
    valor = resgate or peso or (lambda i, j: 1.0)
    melhor_por_a = {}
    for i, j in pares:
        melhor_por_a[i] = max(melhor_por_a.get(i, 0.0), valor(i, j))
    cobertura = sum(valor(i, j) for i, j in pares) / len(seg_b) if seg_b else 0.0
    cobertura_original = sum(melhor_por_a.values()) / len(seg_a) if seg_a else 0.0
    ordem = calcular_ordem(blocos, len(pares), tolerancia) if pares else 0.0
    nota = pontuar(cobertura, ordem)

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
        "cobertura": cobertura,
        "cobertura_original": cobertura_original,
        "ordem": ordem,
        "n_blocos": len(blocos),
        "n_pares": len(pares),
        "n_inversoes": contador.inversoes,
        "n_segmentos_originais": len(melhor_por_a),
        "maior_bloco": max((len(bloco) for bloco in blocos), default=0),
        "trechos": trechos,
        "pares": [descrever_par(i, j) for i, j in pares] if descrever_par else [],
    }
