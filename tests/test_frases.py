import random
import re

import pytest

from backend.core.analises.semantica import MAX_PALAVRAS_FRASE, extrair_frases, tem_negacao
from backend.core.analises.comum import Segmento, contar_palavras

def textos(entrada):
    return [f.texto for f in extrair_frases(entrada)]

@pytest.mark.parametrize("entrada,saida", [
    ("Uma frase.", ["Uma frase."]),
    ("Sem ponto final", ["Sem ponto final"]),
    ("Uma. Duas. Três.", ["Uma.", "Duas.", "Três."]),
    ("Pergunta? Exclamação! Fim.", ["Pergunta?", "Exclamação!", "Fim."]),
    ("Reticências... e continua.", ["Reticências...", "e continua."]),
    ("O quê?! Sério.", ["O quê?!", "Sério."]),
    ("", []), ("   ", []), ("...", []), ("!?.", []),
])
def test_separacao_basica(entrada, saida):
    assert textos(entrada) == saida

@pytest.mark.parametrize("entrada", [
    "O Dr. Silva chegou cedo.", "A Dra. Costa falou.", "O Sr. Lima e a Sra. Reis saíram.",
    "Veja o art. 5 da lei.", "Na fig. 3 aparece isso.", "O Prof. Souza explicou.",
    "J. Silva escreveu o livro.", "O pagamento de R$ 1.500,50 saiu.", "Em 3.2.2024 tudo mudou.",
    "O valor de pi é 3.14 aproximadamente.", "Visite o site exemplo.com hoje.", "A Av. Paulista lotou.",
])
def test_abreviacoes_e_numeros_nao_partem_a_frase(entrada):
    assert textos(entrada) == [entrada]

def test_ponto_antes_de_aspas_termina_a_frase():
    assert len(textos('Ele saiu." Depois voltou.')) == 2

def test_quebra_de_linha_simples_nao_termina_frase():
    assert textos("Uma frase que foi\nquebrada ao meio.") == ["Uma frase que foi quebrada ao meio."]

def test_linha_em_branco_termina_frase():
    assert textos("Título sem ponto\n\nPrimeira frase.") == ["Título sem ponto", "Primeira frase."]

@pytest.mark.parametrize("largura", [20, 40, 60, 80])
def test_quebrar_linhas_nao_muda_as_frases(largura):
    import textwrap
    original = "A primeira frase tem várias palavras comuns. A segunda frase também tem. A terceira encerra o parágrafo com calma."
    assert textos("\n".join(textwrap.wrap(original, largura))) == textos(original)

def test_frase_com_citacao_fica_sem_buracos():
    longo = " ".join(["palavra"] * 30)
    frase = textos(f'{longo} disse "algo" ontem.')[0]
    assert "  " not in frase and "algo" not in frase

@pytest.mark.parametrize("n", [1, 59, 60, 61, 120, 121, 500, 2000])
def test_frase_longa_vira_janelas(n):
    frases = extrair_frases(" ".join(f"p{i}" for i in range(n)))
    assert all(contar_palavras(f.texto) <= MAX_PALAVRAS_FRASE for f in frases)
    assert sum(contar_palavras(f.texto) for f in frases) == n

@pytest.mark.parametrize("semente", range(100))
def test_posicoes_das_frases_batem_com_o_texto(semente):
    gerador = random.Random(semente)
    blocos = ["casa", "rio", "Dr.", "1.500", "fim.", "ok!", "será?", "\n", "\n\n", "  ", "😀", "a​b", " ".join(["p"] * 70)]
    texto = " ".join(gerador.choice(blocos) for _ in range(gerador.randint(0, 80)))
    anterior = 0
    for frase in extrair_frases(texto):
        assert anterior <= frase.inicio < frase.fim <= len(texto)
        assert " ".join(texto[frase.inicio:frase.fim].split()) == frase.texto
        anterior = frase.fim

@pytest.mark.parametrize("frase,negada", [
    ("Eu não amo você.", True), ("Não, eu amo você.", True), ("Eu amo você, não.", True), ("NÃO aceito.", True),
    ("Nunca mais volto.", True), ("Jamais diria isso.", True), ("Ninguém ama você.", True), ("Nem pensar.", True),
    ("Nenhum aluno veio.", True), ("Nada mudou.", True), ("Eu amo você.", False), ("A nação cresceu.", False),
    ("Nadar faz bem.", False), ("O nanico saiu.", False),
])
def test_negacao(frase, negada):
    assert tem_negacao(Segmento(frase, 0, len(frase))) is negada
