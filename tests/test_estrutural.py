import pytest

from backend.core.analises.comum import TextoGrandeDemais
from backend.core.analises.estrutural import MAX_TOKENS, MIN_TOKENS_CONFIAVEL, ProcessadorEstruturalLeve, analisar_estrutura, extrair_palavras
from tests.conftest import metricas
from tests import corpus

NUMEROS = " ".join(map(str, range(25)))

@pytest.mark.parametrize("a,b,nota", [
    (NUMEROS, NUMEROS, 1.0),
    ("gato " * 25, "gato " * 25, 1.0),
    ("gato " * 25, "cama " * 25, 1.0),
    ("casa bola mesa pato rio sol " * 5, "lua mar flor cama copo " * 6, 1.0),
    ("1 " * 15, "2 " * 25, 0.75),
    ("1 " * 25, "2 " * 26, pytest.approx(0.98, abs=0.01)),
])
def test_categoria_unica_nao_quebra(a, b, nota):
    assert analisar_estrutura(a, b)["nota"] == nota

@pytest.mark.parametrize("n", [20, 21, 25, 50, 100, 500])
def test_listas_iguais_de_numeros_em_qualquer_tamanho(n):
    texto = " ".join(map(str, range(n)))
    assert analisar_estrutura(texto, texto)["nota"] == 1.0

def test_quase_categoria_unica_nao_quebra():
    #Duas categorias em que embaralhar quase nunca muda nada: o desconto chega perto de 1.
    a = "1 " * 39 + "casa"
    assert 0 <= analisar_estrutura(a, a)["nota"] <= 1

@pytest.mark.parametrize("a,b", [("Olá.", "Sim."), ("12", "99"), ("O rio secou.", "A lua brilha."), ("Socorro!", "Parabéns!")])
def test_frases_curtas_sao_inconclusivas(a, b):
    resultado = analisar_estrutura(a, b)
    assert resultado["faixa"] == "inconclusiva" and "inconclusiva" in resultado["titulo"]
    assert any("curto" in aviso for aviso in resultado["avisos"])

def test_limite_de_tamanho_confiavel():
    longo = "uma frase qualquer com palavras comuns e bastante extensa para passar do limite minimo de tokens agora aqui mesmo sem pressa"
    assert len(ProcessadorEstruturalLeve.extrair_estrutura(longo)) >= MIN_TOKENS_CONFIAVEL
    assert analisar_estrutura(longo, longo)["faixa"] == "alta"

@pytest.mark.parametrize("a,b", [("", ""), ("texto", ""), ("", "texto"), ("...", "!!!"), ("   ", "\n\n"), ("😀", "😀"), (". " * 25, "palavra")])
def test_sem_palavras_nao_vira_zero(a, b):
    assert analisar_estrutura(a, b)["nota"] is None

def test_tokens_demais_sao_recusados():
    texto = "a. " * (MAX_TOKENS // 2 + 1)
    with pytest.raises(TextoGrandeDemais):
        analisar_estrutura(texto, "texto curto")
    with pytest.raises(TextoGrandeDemais):
        analisar_estrutura("texto curto", texto)

def test_mesma_entrada_mesma_nota():
    assert analisar_estrutura(corpus.CLIMA, corpus.BALEIAS) == analisar_estrutura(corpus.CLIMA, corpus.BALEIAS)

def test_mesma_construcao_supera_construcao_diferente():
    parecidos = analisar_estrutura(corpus.CONSTRUCAO_A, corpus.CONSTRUCAO_B)["nota"]
    diferentes = analisar_estrutura(corpus.CONSTRUCAO_A, corpus.REDES_2)["nota"]
    assert parecidos > diferentes + 0.2

def test_palavras_identicas_ignoram_stopwords_e_grafia():
    assert metricas(analisar_estrutura("O Céu é Azul", "azul o CEU"))["Palavras idênticas"] == "2 de 2 (100%)"

def test_palavras_identicas_sao_medida_a_parte():
    resultado = metricas(analisar_estrutura(corpus.LEITURA, f"{corpus.LEITURA_F3} {corpus.LEITURA_F1} {corpus.LEITURA_F2}"))
    assert resultado["Palavras idênticas"].endswith("(100%)")

def test_trecho_literal_em_texto_longo_nao_passa_em_branco():
    resultado = analisar_estrutura(corpus.LEITURA, f"{corpus.TEXTO_LONGO_NOVO} {corpus.LEITURA_F2}")
    assert any("palavras idênticas seguidas" in aviso for aviso in resultado["avisos"])
    assert int(metricas(resultado)["Maior trecho idêntico"].split()[0]) >= 6

def test_sem_trecho_literal_nao_ha_aviso():
    assert not any("idênticas" in a for a in analisar_estrutura(corpus.CLIMA, corpus.BALEIAS)["avisos"])

def test_destaque_aponta_para_as_palavras():
    texto = corpus.LEITURA
    resultado = analisar_estrutura(texto, texto)
    trecho = resultado["trechos"][0]
    assert texto[trecho["inicio_a"]:trecho["fim_a"]].startswith("leitura")

def test_citacao_escondida_some_das_palavras():
    assert not [p for p in extrair_palavras('Texto livre e bem longo aqui mesmo "segredo" fim do texto.') if p.texto == "segredo"]
