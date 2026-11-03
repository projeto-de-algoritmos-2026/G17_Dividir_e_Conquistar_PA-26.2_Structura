"""Entradas aleatórias e hostis: nenhuma pode virar erro 500 nem quebrar as regras da resposta."""
import random

import pytest

from tests.conftest import ANALISADORES, verificar_resposta

PEDACOS = [
    "casa", "rio", "de", "não", "O", "Dr.", "1.500", "3,14", "2024", "fim.", "ok!", "será?", ",", ";", ":", ".", "...", "!!!",
    '"', "“", "”", "«", "»", "'", "(", ")", "[", "]", "\n", "\n\n", "\t", "  ", "\r\n", "😀", "👨‍👩‍👧", "🇧🇷", "á", "́", "​",
    "﻿", "‮", "­", " ", "　", "日本語", "العربية", "русский", "ελληνικά", "ß", "İ", "ﬁ", "½", "²", "_", "__x__",
    "Referências", "Referências\n", "\nReferências\n", "Bibliografia", "<script>alert(1)</script>", "&amp;", "\\", "\\n", "%s", "{}", "$(x)", "\x00", "\x7f", "퟿",
    "а", "о", "е", "Α", "nao", "NUNCA", "a" * 50, "palavra " * 70,
]

def gerar(gerador: random.Random) -> str:
    return " ".join(gerador.choice(PEDACOS) for _ in range(gerador.randint(0, 60)))

@pytest.mark.parametrize("semente", range(1500))
def test_estrutural_aguenta_qualquer_texto(semente):
    gerador = random.Random(semente)
    a, b = gerar(gerador), gerar(gerador)
    verificar_resposta(ANALISADORES["estrutural"](a, b), a, b)

@pytest.mark.modelo
@pytest.mark.parametrize("semente", range(300))
def test_semantica_aguenta_qualquer_texto(semente):
    gerador = random.Random(semente)
    a, b = gerar(gerador), gerar(gerador)
    verificar_resposta(ANALISADORES["semantica"](a, b), a, b)

@pytest.mark.modelo
@pytest.mark.parametrize("modo", ["estrutural", "semantica"])
@pytest.mark.parametrize("semente", range(100))
def test_mesma_entrada_mesmo_resultado(modo, semente):
    gerador = random.Random(semente)
    a, b = gerar(gerador), gerar(gerador)
    assert ANALISADORES[modo](a, b) == ANALISADORES[modo](a, b)

@pytest.mark.parametrize("semente", range(300))
def test_texto_comparado_consigo_mesmo_da_nota_maxima_no_estrutural(semente):
    gerador = random.Random(semente)
    a = gerar(gerador)
    nota = ANALISADORES["estrutural"](a, a)["nota"]
    assert nota is None or nota == 1.0

@pytest.mark.modelo
@pytest.mark.parametrize("semente", range(100))
def test_texto_comparado_consigo_mesmo_da_nota_maxima_na_semantica(semente):
    gerador = random.Random(semente)
    a = gerar(gerador)
    nota = ANALISADORES["semantica"](a, a)["nota"]
    assert nota is None or nota >= 0.99

@pytest.mark.parametrize("semente", range(200))
def test_api_nunca_responde_500(cliente, semente):
    gerador = random.Random(semente)
    corpo = {"texto_a": gerar(gerador), "texto_b": gerar(gerador), "modo": "estrutural"}
    assert cliente.post("/api/comparar", json=corpo).status_code == 200
