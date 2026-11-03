import operator
import random

import pytest

from backend.core.dividir_conquistar.hirschberg import hirschberg, hirschberg_ponderado, tamanho_lcs, valor_alinhamento

def lcs_tabela(a, b):
    tabela = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i, x in enumerate(a, 1):
        for j, y in enumerate(b, 1):
            tabela[i][j] = tabela[i - 1][j - 1] + 1 if x == y else max(tabela[i - 1][j], tabela[i][j - 1])
    return tabela[-1][-1]

def alinhamento_tabela(n, m, peso):
    tabela = [[0.0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            tabela[i][j] = max(tabela[i - 1][j], tabela[i][j - 1], tabela[i - 1][j - 1] + peso(i - 1, j - 1))
    return tabela[-1][-1]

@pytest.mark.parametrize("semente", range(500))
def test_lcs_igual_a_tabela_completa(semente):
    gerador = random.Random(semente)
    alfabeto = "abcdef"[:gerador.randint(1, 6)]
    a = [gerador.choice(alfabeto) for _ in range(gerador.randint(0, 40))]
    b = [gerador.choice(alfabeto) for _ in range(gerador.randint(0, 40))]
    indices = hirschberg(list(range(len(a))), list(range(len(b))), lambda i, j: a[i] == b[j])
    assert len(indices) == lcs_tabela(a, b) == tamanho_lcs(a, b, operator.eq)
    assert all(a[i] == b[j] for i, j in indices)
    assert all(p[0] < q[0] and p[1] < q[1] for p, q in zip(indices, indices[1:]))

@pytest.mark.parametrize("semente", range(500))
def test_ponderado_igual_a_tabela_completa(semente):
    gerador = random.Random(semente)
    n, m = gerador.randint(0, 25), gerador.randint(0, 25)
    pesos = [[gerador.choice([0.0, 0.0, gerador.random()]) for _ in range(m)] for _ in range(n)]
    peso = lambda i, j: pesos[i][j]
    pares = hirschberg_ponderado(list(range(n)), list(range(m)), peso)
    esperado = alinhamento_tabela(n, m, peso)
    assert sum(peso(i, j) for i, j in pares) == pytest.approx(esperado)
    assert valor_alinhamento(list(range(n)), list(range(m)), peso) == pytest.approx(esperado)
    assert all(peso(i, j) > 0 for i, j in pares)
    assert all(p[0] < q[0] and p[1] < q[1] for p, q in zip(pares, pares[1:]))

@pytest.mark.parametrize("a,b,tamanho", [
    ([], [], 0), ([], [1], 0), ([1], [], 0), ([1], [1], 1), ([1], [2], 0),
    ([1, 2, 3], [1, 2, 3], 3), ([1, 2, 3], [3, 2, 1], 1), ([1, 1, 1], [1, 1], 2),
    ([1, 2], [3, 4], 0), (list(range(100)), list(range(100)), 100),
])
def test_lcs_casos_conhecidos(a, b, tamanho):
    assert len(hirschberg(a, b, operator.eq)) == tamanho

def test_ponderado_prefere_o_par_mais_forte_e_nao_o_primeiro():
    pesos = {(0, 0): 0.6, (1, 0): 1.0}
    assert hirschberg_ponderado([0, 1], [0], lambda i, j: pesos.get((i, j), 0.0)) == [(1, 0)]

def test_ponderado_troca_quantidade_por_qualidade():
    #Dois pares fracos valem menos que um forte que cruza com eles.
    pesos = {(0, 1): 0.3, (1, 2): 0.3, (0, 2): 0.0, (1, 0): 0.0, (2, 0): 0.0, (1, 1): 1.0}
    pares = hirschberg_ponderado([0, 1], [0, 1, 2], lambda i, j: pesos.get((i, j), 0.0))
    assert pares == [(1, 1)]

def test_ponderado_sem_pesos_nao_pareia():
    assert hirschberg_ponderado([0, 1, 2], [0, 1], lambda i, j: 0.0) == []
