def _ultima_linha(a: list, b: list, iguais) -> list[int]:
    #Tamanho da LCS de a com cada prefixo de b, guardando apenas duas linhas da tabela.
    anterior = [0] * (len(b) + 1)
    for x in a:
        atual = [0] * (len(b) + 1)
        for j, y in enumerate(b, 1):
            atual[j] = anterior[j - 1] + 1 if iguais(x, y) else max(anterior[j], atual[j - 1])
        anterior = atual
    return anterior

def tamanho_lcs(a: list, b: list, iguais) -> int:
    return _ultima_linha(a, b, iguais)[-1]

def hirschberg(a: list, b: list, iguais) -> list[tuple]:
    #LCS por dividir e conquistar: O(nm) em tempo e O(n + m) em espaço.
    if not a or not b:
        return []
    if len(a) == 1:
        for y in b:
            if iguais(a[0], y):
                return [(a[0], y)]
        return []

    meio = len(a) // 2
    esquerda = _ultima_linha(a[:meio], b, iguais)
    direita = _ultima_linha(a[meio:][::-1], b[::-1], iguais)[::-1]
    corte = max(range(len(b) + 1), key=lambda j: esquerda[j] + direita[j])

    return hirschberg(a[:meio], b[:corte], iguais) + hirschberg(a[meio:], b[corte:], iguais)
