import random
import time

import pytest

from backend.core.analises.estrutural import MAX_TOKENS
from backend.core.analises.semantica import MAX_FRASES
from backend.schemas.models import MAX_CARACTERES
from tests.conftest import ANALISADORES

LIMITE_SEGUNDOS = 30 #acima disso, quem usa a tela acha que travou
PALAVRAS = "casa rio livro mesa ponte festa verde corrida janela música cidade trabalho governo escola floresta".split()

def cronometrar(modo, a, b):
    inicio = time.perf_counter()
    resultado = ANALISADORES[modo](a, b)
    return time.perf_counter() - inicio, resultado

def prosa(gerador, caracteres):
    frases, total = [], 0
    while total < caracteres:
        frase = " ".join(gerador.choice(PALAVRAS) for _ in range(14)).capitalize() + ". "
        frases.append(frase)
        total += len(frase)
    return "".join(frases)[:caracteres]

@pytest.mark.lento
def test_pior_caso_estrutural_aceito():
    gerador = random.Random(1)
    texto = "".join(gerador.choice("abcdefgh") + gerador.choice(".,") for _ in range(MAX_TOKENS // 2))
    tempo, resultado = cronometrar("estrutural", texto, texto)
    assert resultado["nota"] == 1.0 and tempo < LIMITE_SEGUNDOS

@pytest.mark.lento
@pytest.mark.modelo
def test_pior_caso_semantico_aceito():
    gerador = random.Random(2)
    texto = "".join(f"{gerador.choice(PALAVRAS)[:3]}. " for _ in range(MAX_FRASES))
    tempo, _ = cronometrar("semantica", texto, texto)
    assert tempo < LIMITE_SEGUNDOS

@pytest.mark.lento
@pytest.mark.modelo
@pytest.mark.parametrize("modo", ["estrutural", "semantica"])
def test_prosa_no_limite_de_caracteres(modo):
    gerador = random.Random(3)
    tempo, _ = cronometrar(modo, prosa(gerador, MAX_CARACTERES), prosa(gerador, MAX_CARACTERES))
    assert tempo < LIMITE_SEGUNDOS

@pytest.mark.parametrize("modo", ["estrutural", "semantica"])
def test_recusa_e_imediata(cliente, modo):
    texto = "a. " * (MAX_CARACTERES // 3)
    inicio = time.perf_counter()
    assert cliente.post("/api/comparar", json={"texto_a": texto, "texto_b": texto, "modo": modo}).status_code == 422
    assert time.perf_counter() - inicio < 1
