import random

import pytest

from backend.core.algoritmos import ContadorInversoes
from backend.core.dividir_conquistar.inversoes import contar_significativas

def forca_bruta(arr, tolerancia=0):
    return sum(arr[i] > arr[j] + tolerancia for i in range(len(arr)) for j in range(i + 1, len(arr)))

@pytest.mark.parametrize("semente", range(500))
def test_significativas_igual_a_forca_bruta(semente):
    gerador = random.Random(semente)
    arr = [gerador.randint(-20, 20) for _ in range(gerador.randint(0, 60))]
    tolerancia = gerador.randint(0, 6)
    assert contar_significativas(arr, tolerancia) == forca_bruta(arr, tolerancia)

@pytest.mark.parametrize("semente", range(300))
def test_contador_do_matheus_igual_a_forca_bruta(semente):
    gerador = random.Random(semente)
    arr = [gerador.randint(0, 30) for _ in range(gerador.randint(0, 60))]
    contador = ContadorInversoes()
    assert contador.ordenar_e_contar(arr) == sorted(arr)
    assert contador.inversoes == forca_bruta(arr)

@pytest.mark.parametrize("arr,esperado", [([], 0), ([1], 0), ([1, 2, 3], 0), ([3, 2, 1], 3), ([2, 2, 2], 0), ([2, 1, 2, 1], 3)])
def test_inversoes_conhecidas(arr, esperado):
    assert contar_significativas(arr) == esperado

@pytest.mark.parametrize("n", [2, 5, 10, 100, 1000])
def test_lista_invertida_tem_o_maximo(n):
    assert contar_significativas(list(range(n, 0, -1))) == n * (n - 1) // 2

def test_tolerancia_ignora_trocas_pequenas():
    assert contar_significativas([2, 1, 4, 3], 1) == 0
    assert contar_significativas([2, 1, 4, 3], 0) == 2
