import re
from functools import lru_cache
from pathlib import Path

import numpy as np
from fastembed import TextEmbedding

from backend.core.analises.comum import (
    RE_PALAVRA,
    Segmento,
    TextoGrandeDemais,
    avisos_citacoes,
    classificar,
    comparar_segmentos,
    eh_abreviacao,
    normalizar,
    ocultar_citacoes,
    pontuar,
    sem_conteudo,
)
from backend.core.analises.estrutural import listar_palavras

MODELO = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
#O padrão do fastembed é a pasta temporária, que o sistema apaga ao reiniciar.
PASTA_MODELOS = Path(__file__).resolve().parents[3] / ".cache" / "modelos"

LIMIAR_FRASE = 0.55 #abaixo disso, duas frases não contam como a mesma ideia
LIMIAR_JANELA = 0.70 #frases vizinhas somadas dão similaridades altas com mais facilidade
PISO_JANELA = 0.35 #cada parte de uma fusão precisa ter relação própria com a outra frase
PESO_PALAVRAS = 0.65 #quanto as palavras em comum aproximam a nota de 1
NEGACOES = {"nao", "nunca", "jamais", "nem", "ninguem", "nenhum", "nenhuma", "nada"}
SIMILARIDADE_NULA = 0.3 #textos sem relação ficam abaixo disso
SIMILARIDADE_TOTAL = 0.7 #reescritas completas costumam ficar perto disso
FOLGA_GERAL = 0.2 #mesmo tema sem frases correspondentes não pode passar disso
MIN_FRASES_ORIGINAL = 3 #com menos, "todo o original foi usado" acontece por acaso
MIN_PALAVRAS_LITERAL = 5 #frases menores coincidem sem ser cópia
MAX_PALAVRAS_FRASE = 60 #o modelo corta frases longas e ignoraria o resto delas
MAX_FRASES = 1000 #a comparação é quadrática no número de frases
FIM_DE_FRASE = re.compile(r"[.!?]+(?=[\s\"'”»)\]]|$)|\n[ \t]*\n")

class ModeloIndisponivel(Exception):
    """O modelo não está no cache e não pôde ser baixado."""

@lru_cache
def carregar_modelo() -> TextEmbedding:
    #Carregado só no primeiro uso: a primeira execução baixa o modelo.
    try:
        return TextEmbedding(MODELO, cache_dir=str(PASTA_MODELOS))
    except Exception as falha:
        raise ModeloIndisponivel("Não foi possível carregar o modelo de linguagem. Na primeira análise semântica é preciso ter internet.") from falha

def termina_frase(texto: str, achado: re.Match) -> bool:
    if achado.group() != ".":
        return True
    anterior = re.search(r"\w+$", texto[max(0, achado.start() - 12):achado.start()])
    return not anterior or not eh_abreviacao(anterior.group())

def dividir_frase_longa(texto: str, inicio: int, fim: int) -> list[Segmento]:
    palavras = [(p.start(), p.end()) for p in RE_PALAVRA.finditer(texto, inicio, fim)]
    if len(palavras) <= MAX_PALAVRAS_FRASE:
        return [Segmento(" ".join(texto[inicio:fim].split()), inicio, fim)]
    grupos = [palavras[k:k + MAX_PALAVRAS_FRASE] for k in range(0, len(palavras), MAX_PALAVRAS_FRASE)]
    trechos = [(grupo[0][0], grupo[-1][1]) for grupo in grupos]
    return [Segmento(" ".join(texto[a:b].split()), a, b) for a, b in trechos]

def separar_frases(texto: str) -> list[Segmento]:
    #Quebra de linha simples não termina frase: é assim que textos colados de PDF chegam.
    frases = []
    inicio = 0
    limites = [achado.end() for achado in FIM_DE_FRASE.finditer(texto) if termina_frase(texto, achado)]
    for fim in limites + [len(texto)]:
        bruto = texto[inicio:fim]
        if RE_PALAVRA.search(bruto):
            comeco = inicio + len(bruto) - len(bruto.lstrip())
            final = inicio + len(bruto.rstrip())
            frases += dividir_frase_longa(texto, comeco, final)
        inicio = fim
    return frases

def extrair_frases(texto: str) -> list[Segmento]:
    return separar_frases(ocultar_citacoes(texto))

def vetorizar(frases: list[Segmento]) -> np.ndarray:
    #O modelo diferencia maiúsculas e acentos, o que derrubava cópias com grafia alterada.
    vetores = np.array(list(carregar_modelo().embed([normalizar(f.texto) for f in frases])))
    return vetores / np.linalg.norm(vetores, axis=1, keepdims=True)

def tem_negacao(frase: Segmento) -> bool:
    return not NEGACOES.isdisjoint(RE_PALAVRA.findall(normalizar(frase.texto)))

def conteudo_da_frase(frase: Segmento) -> tuple[frozenset, bool]:
    return frozenset(p.texto for p in listar_palavras(frase.texto)), tem_negacao(frase)

def sobreposicao_palavras(conteudo_a: tuple[frozenset, bool], conteudo_b: tuple[frozenset, bool]) -> float:
    #Coeficiente de Dice entre as palavras de conteúdo das duas frases.
    palavras_a, negacao_a = conteudo_a
    palavras_b, negacao_b = conteudo_b
    total = len(palavras_a) + len(palavras_b)
    if negacao_a != negacao_b or not total:
        return 0.0
    return 2 * len(palavras_a & palavras_b) / total

def reforcar_com_palavras(similaridades: np.ndarray, frases_a: list[Segmento], frases_b: list[Segmento]) -> np.ndarray:
    #Em frases curtas o modelo é impreciso: palavras em comum são uma evidência a mais.
    #O conteúdo é calculado uma vez por frase: refazer isso a cada par dominava o tempo total.
    conteudos_a = [conteudo_da_frase(f) for f in frases_a]
    conteudos_b = [conteudo_da_frase(f) for f in frases_b]
    sobreposicao = np.array([[sobreposicao_palavras(a, b) for b in conteudos_b] for a in conteudos_a])
    return similaridades + (1 - similaridades) * PESO_PALAVRAS * sobreposicao

def juntar_vizinhas(frases: list[Segmento]) -> list[Segmento]:
    return [Segmento(f"{a.texto} {b.texto}", a.inicio, b.fim) for a, b in zip(frases, frases[1:])]

def somar_janelas(base: np.ndarray, janelas: np.ndarray) -> np.ndarray:
    #Credita às duas frases da janela (linhas) a similaridade da união com a frase da coluna.
    aceitas = np.where(janelas >= LIMIAR_JANELA, janelas, 0.0)
    resultado = base.copy()
    resultado[:-1] = np.maximum(resultado[:-1], np.where(base[:-1] >= PISO_JANELA, aceitas, 0.0))
    resultado[1:] = np.maximum(resultado[1:], np.where(base[1:] >= PISO_JANELA, aceitas, 0.0))
    return resultado

def considerar_fusoes(base: np.ndarray, frases_a: list[Segmento], frases_b: list[Segmento], vetores_a: np.ndarray, vetores_b: np.ndarray) -> np.ndarray:
    #Reescritas fundem e dividem frases: duas vizinhas de um lado podem equivaler a uma do outro.
    resultado = base
    if len(frases_a) > 1:
        resultado = somar_janelas(resultado, vetorizar(juntar_vizinhas(frases_a)) @ vetores_b.T)
    if len(frases_b) > 1:
        resultado = somar_janelas(resultado.T, vetorizar(juntar_vizinhas(frases_b)) @ vetores_a.T).T
    return resultado

def comparar_textos_inteiros(vetores_a: np.ndarray, vetores_b: np.ndarray) -> float:
    #A média captura a ideia geral, mesmo quando uma frase não corresponde a outra.
    media_a, media_b = vetores_a.mean(axis=0), vetores_b.mean(axis=0)
    similaridade = media_a @ media_b / (np.linalg.norm(media_a) * np.linalg.norm(media_b))
    return float(similaridade)

def escalar_ideia_geral(similaridade: float) -> float:
    #A escala realça reescritas, mas nunca passa da similaridade medida de verdade.
    escalada = (similaridade - SIMILARIDADE_NULA) / (SIMILARIDADE_TOTAL - SIMILARIDADE_NULA)
    return max(0.0, min(escalada, similaridade, 1.0))

def contar_frases_literais(frases_a: list[Segmento], frases_b: list[Segmento]) -> int:
    originais = {normalizar(f.texto) for f in frases_a}
    return sum(
        1 for f in frases_b
        if normalizar(f.texto) in originais and len(RE_PALAVRA.findall(f.texto)) >= MIN_PALAVRAS_LITERAL
    )

def juntar_notas(resultado: dict, nota_geral: float) -> tuple[float, float, str]:
    #Conta o maior aproveitamento: frases do suspeito que vêm do original, ou o original que foi parar no suspeito.
    #O segundo sentido impede esconder uma cópia integral no meio de material novo.
    cobertura = resultado["cobertura"]
    if resultado["n_segmentos_originais"] >= MIN_FRASES_ORIGINAL:
        cobertura = max(cobertura, resultado["cobertura_original"])
    nota_frases = pontuar(cobertura, resultado["ordem"])
    #A ideia geral reforça o alinhamento, mas não o substitui: tratar do mesmo tema não é plágio.
    return max(nota_frases, min(nota_geral, nota_frases + FOLGA_GERAL)), nota_frases, cobertura

def explicar_nota(resultado: dict, nota: float, nota_frases: float, cobertura: float, nota_geral: float) -> str:
    if cobertura > resultado["cobertura"]:
        return f"{cobertura:.0%} das ideias do original aparecem no texto suspeito, junto com material novo."
    if nota > nota_frases and resultado["n_pares"] == 0:
        return f"Nenhuma frase tem equivalente direto, mas os textos têm {nota_geral:.0%} de proximidade geral: pode ser só o mesmo tema."
    return resultado["explicacao"]

def montar_avisos(texto_a: str, texto_b: str, frases_a: list[Segmento], frases_b: list[Segmento]) -> list[str]:
    avisos = avisos_citacoes(texto_a, texto_b)
    literais = contar_frases_literais(frases_a, frases_b)
    if literais:
        avisos.append(f"{literais} frase(s) do suspeito são idênticas ao original.")
    return avisos

def analisar_semantica(texto_a: str, texto_b: str) -> dict:
    frases_a = extrair_frases(texto_a)
    frases_b = extrair_frases(texto_b)
    if not frases_a or not frases_b:
        return sem_conteudo()
    if max(len(frases_a), len(frases_b)) > MAX_FRASES:
        raise TextoGrandeDemais(f"Cada texto pode ter até {MAX_FRASES} frases na análise semântica.")

    vetores_a = vetorizar(frases_a)
    vetores_b = vetorizar(frases_b)
    base = reforcar_com_palavras(vetores_a @ vetores_b.T, frases_a, frases_b)
    fusoes = considerar_fusoes(base, frases_a, frases_b, vetores_a, vetores_b).tolist()

    #Listas de Python: o alinhamento lê a matriz milhões de vezes, e índices numpy são lentos.
    diretas = base.tolist()
    iguais = lambda i, j: diretas[i][j] >= LIMIAR_FRASE
    peso = lambda i, j: min(1.0, diretas[i][j])
    resgate = lambda i, j: min(1.0, fusoes[i][j]) if fusoes[i][j] >= LIMIAR_FRASE else 0.0
    descrever_par = lambda i, j: {
        "texto_a": frases_a[i].texto,
        "texto_b": frases_b[j].texto,
        "nota": round(resgate(i, j), 2),
    }
    resultado = comparar_segmentos(
        frases_a, frases_b, iguais, "frases", 1, 1, 0, descrever_par, peso,
        distancia=1, resgate=resgate,
    )

    nota_geral = escalar_ideia_geral(comparar_textos_inteiros(vetores_a, vetores_b))
    nota, nota_frases, cobertura = juntar_notas(resultado, nota_geral)
    faixa = classificar(nota)
    return {
        "nota": round(nota, 4),
        "faixa": faixa,
        "titulo": f"Suspeita de plágio {faixa}",
        "explicacao": explicar_nota(resultado, nota, nota_frases, cobertura, nota_geral),
        "metricas": [
            {"rotulo": "Ideia geral", "valor": f"{nota_geral:.0%}"},
            {"rotulo": "Cobertura do suspeito", "valor": f"{resultado['cobertura']:.0%}"},
            {"rotulo": "Original aproveitado", "valor": f"{resultado['cobertura_original']:.0%}"},
            {"rotulo": "Ordem", "valor": f"{resultado['ordem']:.0%}"},
            {"rotulo": "Blocos", "valor": str(resultado["n_blocos"])},
            {"rotulo": "Inversões", "valor": str(resultado["n_inversoes"])},
            {"rotulo": "Frases em comum", "valor": str(resultado["n_pares"])},
        ],
        "legenda": "Em destaque: frases com a mesma ideia.",
        "trechos": resultado["trechos"],
        "titulo_pares": "Frases equivalentes",
        "pares": resultado["pares"],
        "avisos": montar_avisos(texto_a, texto_b, frases_a, frases_b),
    }
