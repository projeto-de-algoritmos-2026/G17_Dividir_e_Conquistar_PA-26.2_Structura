import random

import pytest

from backend.core.analises.comum import (
    Segmento, agrupar_em_blocos, calcular_ordem, classificar, comparar_segmentos, explicar, parear, pontuar, sem_conteudo,
)

def segmentos(n):
    return [Segmento(str(i), i * 2, i * 2 + 1) for i in range(n)]

def iguais_por_valor(a, b):
    return lambda i, j: a[i] == b[j]

def test_parear_mantem_um_para_um():
    a, b = [1, 2, 3, 4], [4, 3, 2, 1]
    pares = parear(4, 4, iguais_por_valor(a, b))
    assert sorted(i for i, _ in pares) == [0, 1, 2, 3] and sorted(j for _, j in pares) == [0, 1, 2, 3]

def test_parear_recupera_bloco_movido():
    a, b = [1, 2, 3, 4, 5, 6], [4, 5, 6, 1, 2, 3]
    assert len(parear(6, 6, iguais_por_valor(a, b))) == 6

def test_parear_sem_iguais():
    assert parear(3, 3, lambda i, j: False) == []

@pytest.mark.parametrize("semente", range(200))
def test_parear_nunca_repete_nem_inventa(semente):
    gerador = random.Random(semente)
    a = [gerador.randint(0, 6) for _ in range(gerador.randint(0, 30))]
    b = [gerador.randint(0, 6) for _ in range(gerador.randint(0, 30))]
    pares = parear(len(a), len(b), iguais_por_valor(a, b))
    assert all(a[i] == b[j] for i, j in pares)
    assert len({i for i, _ in pares}) == len(pares) == len({j for _, j in pares})
    assert [j for _, j in pares] == sorted(j for _, j in pares)
    comuns = sum(min(a.count(v), b.count(v)) for v in set(a))
    assert len(pares) == comuns

def test_parear_escolhe_o_par_mais_forte():
    pesos = [[0.6], [1.0]]
    assert parear(2, 1, lambda i, j: True, lambda i, j: pesos[i][j]) == [(1, 0)]

def test_varredura_de_movidos_prefere_o_mais_forte():
    #Em ordem só cabe um par; o melhor dos que sobram precisa vir da varredura.
    pesos = [[0.0, 0.9], [0.6, 0.0], [0.95, 0.0]]
    pares = parear(3, 2, lambda i, j: pesos[i][j] > 0, lambda i, j: pesos[i][j])
    assert sorted(pares) == [(0, 1), (2, 0)]

def test_resgate_nao_disputa_com_par_direto():
    #A frase 1 tem par direto: o crédito do resgate não pode tomar o lugar dele.
    direta = [[1.0, 0.0], [0.0, 1.0]]
    pares = parear(2, 2, lambda i, j: direta[i][j] > 0, lambda i, j: direta[i][j], lambda i, j: 0.9)
    assert pares == [(0, 0), (1, 1)]

def test_resgate_pode_repetir_a_frase_do_original():
    pares = parear(1, 3, lambda i, j: j == 0, lambda i, j: 1.0, lambda i, j: 0.8)
    assert pares == [(0, 0), (0, 1), (0, 2)]

def test_resgate_recusado_nao_pareia():
    assert parear(1, 2, lambda i, j: j == 0, lambda i, j: 1.0, lambda i, j: 0.0) == [(0, 0)]

@pytest.mark.parametrize("pares,distancia,n_blocos", [
    ([], 2, 0), ([(0, 0)], 2, 1), ([(0, 0), (1, 1), (2, 2)], 2, 1), ([(0, 0), (2, 2)], 2, 1),
    ([(0, 0), (2, 2)], 1, 2), ([(0, 0), (3, 3)], 2, 2), ([(5, 0), (0, 1)], 2, 2), ([(0, 0), (0, 1)], 1, 1),
])
def test_agrupar(pares, distancia, n_blocos):
    assert len(agrupar_em_blocos(pares, distancia)) == n_blocos

@pytest.mark.parametrize("blocos,n_pares,esperado", [
    ([], 0, 1.0), ([[(0, 0)]], 1, 1.0), ([[(0, 0)], [(5, 1)]], 2, 1.0), ([[(5, 0)], [(0, 1)]], 2, 0.0),
])
def test_ordem(blocos, n_pares, esperado):
    assert calcular_ordem(blocos, n_pares, 0) == esperado

@pytest.mark.parametrize("nota,faixa", [(0, "baixa"), (0.29, "baixa"), (0.3, "moderada"), (0.59, "moderada"), (0.6, "alta"), (1, "alta")])
def test_faixas(nota, faixa):
    assert classificar(nota) == faixa

@pytest.mark.parametrize("cobertura,ordem,nota", [(1, 1, 1), (1, 0, 0.85), (0, 1, 0), (0.5, 1, 0.5), (0.5, 0, 0.425)])
def test_ordem_pesa_pouco_na_nota(cobertura, ordem, nota):
    assert pontuar(cobertura, ordem) == pytest.approx(nota)

@pytest.mark.parametrize("cobertura,ordem,trecho", [
    (0, 0, "Nenhuma"), (0.5, 0.9, "mesma ordem"), (0.5, 0.5, "parte da ordem"), (0.5, 0.1, "bastante diferente"),
])
def test_explicacoes(cobertura, ordem, trecho):
    assert trecho in explicar(cobertura, ordem, "frases")

def test_nota_ausente_nao_parece_zero():
    resultado = sem_conteudo()
    assert resultado["nota"] is None and resultado["faixa"] == "indisponivel"

def test_cobertura_nos_dois_sentidos():
    a, b = [0, 1], [0, 1, 7, 8]
    resultado = comparar_segmentos(segmentos(2), segmentos(4), iguais_por_valor(a, b), "frases", 1, 1, 0)
    assert resultado["cobertura"] == 0.5 and resultado["cobertura_original"] == 1.0

def test_frase_repetida_conta_uma_vez_no_original():
    resultado = comparar_segmentos(
        segmentos(2), segmentos(2), lambda i, j: i == 0 and j == 0, "frases", 1, 1, 0,
        peso=lambda i, j: 1.0, distancia=1, resgate=lambda i, j: 1.0 if i == 0 else 0.0,
    )
    assert resultado["cobertura"] == 1.0 and resultado["cobertura_original"] == 0.5

def test_sem_lacuna_no_destaque_quando_distancia_e_um():
    a, b = [0, 1, 2], [0, 9, 2]
    resultado = comparar_segmentos(segmentos(3), segmentos(3), iguais_por_valor(a, b), "frases", 1, 1, 0, distancia=1)
    assert len(resultado["trechos"]) == 2

def test_minimo_de_pares():
    a, b = [0, 1], [0, 1]
    assert comparar_segmentos(segmentos(2), segmentos(2), iguais_por_valor(a, b), "palavras", 3, 1, 0)["n_pares"] == 0
