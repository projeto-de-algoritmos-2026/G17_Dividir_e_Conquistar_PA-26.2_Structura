import unicodedata

import pytest

from backend.core.analises.comum import contar_palavras, normalizar
from backend.core.analises.estrutural import ProcessadorEstruturalLeve, extrair_palavras

@pytest.mark.parametrize("entrada,saida", [
    ("Coração", "coracao"), ("ÁGUA", "agua"), ("não", "nao"), ("ÉÇÃÕÜ", "ecaou"), ("", ""),
    ("ﬁm", "fim"), ("Ａｂｃ", "abc"), ("1º", "1o"),
    ("pa​lavra", "palavra"), ("pa­lavra", "palavra"), ("pa‌lavra", "palavra"),
    ("pa‍lavra", "palavra"), ("pa⁠lavra", "palavra"), ("﻿palavra", "palavra"),
    ("pa‮lavra", "palavra"),
    ("а leitura", "a leitura"), ("lеiturа", "leitura"), ("pаlаvrа", "palavra"), ("сорo", "copo"),
    ("ΑΓΑΠΗ".lower()[:0] + "cοpο", "copo"),
])
def test_normalizar(entrada, saida):
    assert normalizar(entrada) == saida

def test_texto_decomposto_vale_o_mesmo_que_composto():
    composto = "A água é vital para o coração."
    decomposto = unicodedata.normalize("NFD", composto)
    assert composto != decomposto
    assert normalizar(composto) == normalizar(decomposto)

@pytest.mark.parametrize("palavra", ["только", "привет", "мир", "друг", "λόγος"[:0] + "λογος", "γλωσσα"])
def test_russo_e_grego_de_verdade_ficam_intactos(palavra):
    assert normalizar(palavra) == palavra.replace("й", "и")

def test_palavra_latina_com_acento_nao_vira_outra():
    assert normalizar("maçã") == "maca"

@pytest.mark.parametrize("texto,total", [
    ("", 0), ("   ", 0), ("...", 0), ("uma", 1), ("duas palavras", 2), ("a-b", 2), ("3,14", 2),
    ("pa​lavra", 1), ("café quente", 2), ("água", 1), ("😀", 0), ("_", 1),
])
def test_contar_palavras(texto, total):
    assert contar_palavras(texto) == total

def test_palavra_decomposta_nao_se_parte_no_acento():
    assert [p.texto for p in extrair_palavras("água limpa")] == ["agua", "limpa"]

def test_posicoes_apontam_para_o_texto_original():
    texto = "água pa​lavra final"
    for palavra in extrair_palavras(texto):
        assert normalizar(texto[palavra.inicio:palavra.fim]) == palavra.texto

@pytest.mark.parametrize("token,categoria", [
    (".", "."), (",", ","), ("?", "?"), ("123", "NUMERO"), ("de", "PREPOSICAO"), ("não", "NEGACAO"),
    ("o", "ARTIGO"), ("porque", "CONJUNCAO"), ("você", "PRONOME"), ("sol", "MUITO_CURTA"), ("mundo", "CURTA"),
    ("janelas", "MEDIA"), ("biblioteca", "LONGA"), ("extraordinariamente", "MUITO_LONGA"),
    ("_x", "MUITO_CURTA"), ("​de", "PREPOSICAO"), ("d​e", "PREPOSICAO"),
])
def test_classificar_token(token, categoria):
    assert ProcessadorEstruturalLeve.classificar_token(token) == categoria

def test_estrutura_nao_vaza_a_palavra_original():
    categorias = ProcessadorEstruturalLeve.extrair_estrutura("_segredo 123 casa, _outra.")
    assert "_segredo" not in categorias and "_outra" not in categorias
