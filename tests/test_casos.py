import pytest

from tests.conftest import ANALISADORES, verificar_resposta
from tests.corpus import CASOS

PARES = [(modo, caso) for caso in CASOS for modo in ("estrutural", "semantica")]

@pytest.mark.modelo
@pytest.mark.parametrize("modo,caso", PARES, ids=[f"{m}-{c.nome}" for m, c in PARES])
def test_caso(modo, caso):
    resultado = ANALISADORES[modo](caso.a, caso.b)
    verificar_resposta(resultado, caso.a, caso.b)
    faixa = getattr(caso, modo)
    if faixa:
        assert faixa[0] - 1e-9 <= resultado["nota"] <= faixa[1] + 1e-9, f"nota {resultado['nota']}, esperado {faixa}"
