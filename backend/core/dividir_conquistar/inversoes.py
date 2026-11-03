def _ordenar_e_contar(arr: list[int], tolerancia: int) -> tuple[list[int], int]:
    if len(arr) <= 1:
        return arr, 0

    meio = len(arr) // 2
    esquerda, contagem_esq = _ordenar_e_contar(arr[:meio], tolerancia)
    direita, contagem_dir = _ordenar_e_contar(arr[meio:], tolerancia)
    contagem = contagem_esq + contagem_dir

    #Conta antes de mesclar: a condição com tolerância difere da comparação do merge.
    p = 0
    for valor in direita:
        while p < len(esquerda) and esquerda[p] <= valor + tolerancia:
            p += 1
        contagem += len(esquerda) - p

    mesclado = []
    i = j = 0
    while i < len(esquerda) and j < len(direita):
        if esquerda[i] <= direita[j]:
            mesclado.append(esquerda[i])
            i += 1
        else:
            mesclado.append(direita[j])
            j += 1
    return mesclado + esquerda[i:] + direita[j:], contagem

def contar_significativas(arr: list[int], tolerancia: int = 0) -> int:
    #Pares i < j com arr[i] > arr[j] + tolerancia, em O(n log n).
    return _ordenar_e_contar(arr, tolerancia)[1]
