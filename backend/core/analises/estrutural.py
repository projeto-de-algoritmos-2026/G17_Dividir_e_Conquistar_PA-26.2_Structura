import re

from backend.core.analises.comum import Segmento, comparar_segmentos, normalizar, ocultar_citacoes

MIN_PARES = 3
MIN_BLOCO = 2
TOLERANCIA = 2 #trocas entre palavras vizinhas não contam como desordem

STOPWORDS = set("""
a ao aos as com como da das de do dos e ela elas ele eles em entre era essa esse esta este
eu foi for ha isso isto ja la lhe mais mas me mesmo meu minha muito na nas nao nem no nos
nossa nosso num numa o os ou para pela pelas pelo pelos por qual quando que quem se sem ser
seu seus sua suas sao tambem te tem ter um uma uns umas voce
""".split())

def extrair_palavras(texto: str) -> list[Segmento]:
    palavras = []
    for achado in re.finditer(r"\w+", ocultar_citacoes(texto)):
        palavra = normalizar(achado.group())
        if palavra not in STOPWORDS:
            palavras.append(Segmento(palavra, achado.start(), achado.end()))
    return palavras

def analisar_estrutura(texto_a: str, texto_b: str, limiar: float) -> dict:
    palavras_a = extrair_palavras(texto_a)
    palavras_b = extrair_palavras(texto_b)

    iguais = lambda i, j: ProcessadorEstruturalLeve.classificar_tamanho(palavras_a[i].texto) == \
                          ProcessadorEstruturalLeve.classificar_tamanho(palavras_b[j].texto)
    return comparar_segmentos(palavras_a, palavras_b, iguais, "palavras", MIN_PARES, MIN_BLOCO, TOLERANCIA)

class ProcessadorEstruturalLeve:
    """Extração de estrutura baseada em proxy de tamanho de palavras (Pure Python)."""
    #proxy de tamanho de palavras
    @staticmethod
    def classificar_tamanho(palavra: str) -> str:
        tamanho = len(palavra)
        if tamanho <= 3:
            return "CURTA"  #artigos preposições pronomes curtos
        elif tamanho <= 7:
            return "MEDIA"  #substantivos comuns e verbos
        else:
            return "LONGA"  #advérbios adjetivos complexos ou nomes compostos

    @staticmethod
    def extrair_estrutura(texto: str) -> list[str]:
        texto_limpo = re.sub(r'[^\w\s]', '', texto.lower())
        palavras = texto_limpo.split()
        
        estrutura = []
        for palavra in palavras:
            categoria = ProcessadorEstruturalLeve.classificar_tamanho(palavra)
            estrutura.append(categoria)
            
        return estrutura