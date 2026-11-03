import pytest
from fastapi.testclient import TestClient

from backend.core.analises.estrutural import analisar_estrutura
from backend.core.analises.semantica import analisar_semantica
from backend.main import app

ANALISADORES = {"estrutural": analisar_estrutura, "semantica": analisar_semantica}

@pytest.fixture(scope="session")
def cliente():
    return TestClient(app, raise_server_exceptions=False)

def metricas(resultado: dict) -> dict:
    return {m["rotulo"]: m["valor"] for m in resultado["metricas"]}

def verificar_resposta(resultado: dict, texto_a: str, texto_b: str) -> None:
    #O que todo resultado precisa cumprir, seja qual for a entrada.
    nota = resultado["nota"]
    assert nota is None or 0 <= nota <= 1
    assert (nota is None) == (resultado["faixa"] == "indisponivel")
    assert resultado["titulo"] and resultado["explicacao"]
    assert isinstance(resultado["avisos"], list)
    for trecho in resultado["trechos"]:
        assert 0 <= trecho["inicio_a"] < trecho["fim_a"] <= len(texto_a)
        assert 0 <= trecho["inicio_b"] < trecho["fim_b"] <= len(texto_b)
    for par in resultado["pares"]:
        assert 0 <= par["nota"] <= 1 and par["texto_a"] and par["texto_b"]
