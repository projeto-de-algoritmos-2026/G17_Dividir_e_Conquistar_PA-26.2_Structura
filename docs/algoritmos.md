# Algoritmos

Os dois modos seguem o mesmo pipeline. Muda apenas a unidade comparada (palavra ou frase) e o critério de igualdade.

```
Segmentar → Alinhar (Hirschberg) → Agrupar em blocos → Medir ordem (inversões) → Pontuar
```

| Algoritmo | Pergunta que responde | Recorrência | Tempo | Espaço |
|---|---|---|---|---|
| Hirschberg | Quais trechos correspondem? | `T(n, m) = T(n/2, k) + T(n/2, m−k) + O(nm)` | `O(nm)` | `O(n + m)` |
| Counting Inversions | Quanto a ordem mudou? | `T(n) = 2T(n/2) + O(n)` | `O(n log n)` | `O(n)` |
| Inversões significativas | Essa troca é relevante? | `T(n) = 2T(n/2) + O(n)` | `O(n log n)` | `O(n)` |

## Hirschberg

`backend/core/dividir_conquistar/hirschberg.py`

Acha a maior subsequência comum (LCS) sem guardar a tabela inteira da programação dinâmica.

- **Dividir:** corta `A` ao meio. Calcula a última linha da LCS da metade esquerda com `B`, e da metade direita invertida com `B` invertido.
- **Combinar:** o ponto `k` de `B` que maximiza a soma das duas linhas é onde o alinhamento ótimo cruza o meio de `A`.
- **Conquistar:** resolve `A[:meio]` com `B[:k]` e `A[meio:]` com `B[k:]`.

A LCS só encontra o que está na mesma ordem. Depois dela, `parear` faz uma varredura nas unidades restantes para recuperar blocos movidos de lugar.

## Counting Inversions

`ContadorInversoes`, em `backend/core/algoritmos.py`, escrito pelo Matheus e reaproveitado sem alterações.

Durante o merge, quando um elemento da direita passa à frente, ele forma inversão com todos os elementos restantes da esquerda. Isso permite somar vários pares de uma vez, sem compará-los um a um. O valor aparece na tela como **Inversões**.

## Inversões significativas

`backend/core/dividir_conquistar/inversoes.py`

Conta pares `i < j` com `a[i] > a[j] + tolerância`. A condição difere da comparação usada no merge, então a contagem é feita em uma varredura própria com dois ponteiros, antes de mesclar.

É aplicada ao início de cada bloco, e isso define a **Ordem**. Com isso, trocar duas metades do texto conta como um movimento, e não como centenas de inversões entre palavras.

| Modo | Tolerância | Motivo |
|---|---|---|
| Estrutural | 2 posições | Trocar palavras vizinhas não muda a estrutura |
| Semântica | 0 | Mover uma frase já é uma mudança real |

## Nota

```
cobertura = unidades do suspeito dentro de blocos / total de unidades do suspeito
ordem     = 1 − inversões entre blocos / max(C(blocos, 2), unidades em comum − 1)
nota      = cobertura × (0,5 + 0,5 × ordem)
```

| Nota | Faixa |
|---|---|
| Abaixo de 30% | Baixa |
| De 30% a 59% | Moderada |
| 60% ou mais | Alta |

No modo estrutural, um bloco precisa de ao menos 2 palavras: palavras soltas coincidem em qualquer texto sobre o mesmo tema. Abaixo de 3 palavras em comum, a nota é 0.

As faixas são pontos de partida: ainda não foram calibradas com um conjunto real de textos.

## Modo semântico

`backend/core/analises/semantica.py`

Cada frase é normalizada (minúsculas, sem acentos) e vira um vetor no modelo multilíngue `paraphrase-multilingual-MiniLM-L12-v2`. Duas frases contam como iguais quando a similaridade de cosseno atinge o limiar escolhido na tela (70% por padrão). A partir daí, Hirschberg e inversões funcionam exatamente como no modo estrutural.
