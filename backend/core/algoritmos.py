import re #biblioteca de expressoes regulares(busca, validação substituição e padrão em texto)

class ProcessadorTexto:
    @staticmethod
    def limpar_e_extrair(texto: str) -> list[str]:
        texto_limpo = re.sub(r'[^\w\s]', '', texto.lower())
        return texto_limpo.split()

class MapeadorPermutacao: #HashMap conta frequência
    @staticmethod
    def criar_permutacao(palavras_a: list[str], palavras_b: list[str]) -> list[int]:
        mapa_ordem = {}
        for i, palavra in enumerate(palavras_a):
            if palavra not in mapa_ordem:
                mapa_ordem[palavra] = i
        
        permutacao = []
        for palavra in palavras_b:
            if palavra in mapa_ordem:
                permutacao.append(mapa_ordem[palavra])
                
        return permutacao

class ContadorInversoes:
    #Algoritmo Counting Inversions (Merge Sort modificado).
    def __init__(self):
        self.inversoes = 0

    def ordenar_e_contar(self, arr: list[int]) -> list[int]:
        if len(arr) <= 1:
            return arr
        
        meio = len(arr) // 2
        esquerda = self.ordenar_e_contar(arr[:meio])
        direita = self.ordenar_e_contar(arr[meio:])
        
        return self.mesclar_e_contar(esquerda, direita)

    def mesclar_e_contar(self, esquerda: list[int], direita: list[int]) -> list[int]:
        mesclado = []
        i = j = 0
        
        while i < len(esquerda) and j < len(direita):
            if esquerda[i] <= direita[j]:
                mesclado.append(esquerda[i])
                i += 1
            else:
                mesclado.append(direita[j])
                self.inversoes += (len(esquerda) - i)
                j += 1
                
        mesclado.extend(esquerda[i:])
        mesclado.extend(direita[j:])
        return mesclado

class AnalisadorSimilaridade:
    def analisar(self, texto_a: str, texto_b: str) -> dict:
        palavras_a = ProcessadorTexto.limpar_e_extrair(texto_a)
        palavras_b = ProcessadorTexto.limpar_e_extrair(texto_b)
        
        permutacao = MapeadorPermutacao.criar_permutacao(palavras_a, palavras_b)
        
        n = len(permutacao)
        if n <= 1:
            return {"similaridade": 1.0, "inversoes": 0, "n_palavras": n}
            
        contador = ContadorInversoes()
        contador.ordenar_e_contar(permutacao)
        
        max_inversoes = (n * (n - 1)) / 2
        similaridade = 1 - (contador.inversoes / max_inversoes) if max_inversoes > 0 else 1.0
        
        return {
            "similaridade": round(similaridade, 4),
            "inversoes": contador.inversoes,
            "n_palavras": n
        }