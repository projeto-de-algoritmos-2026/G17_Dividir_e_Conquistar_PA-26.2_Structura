# Algoritmos

Cada modo responde a uma pergunta diferente.

| | Estrutural | Semântica |
|---|---|---|
| **Pergunta** | Os textos são construídos do mesmo jeito? | As ideias vêm do original? |
| **Resultado** | Similaridade | Suspeita de plágio |
| **Olha o assunto?** | Não | Sim |
| **Direção** | Simétrica | Do suspeito para o original |
| **Unidade** | Formato de cada palavra | Frase |

```
Estrutural: Extrair formatos → Alinhar (Hirschberg) → Descontar o acaso → Nota
Semântica:  Separar frases → Alinhar (Hirschberg) → Agrupar em blocos → Medir ordem (inversões) → Nota
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

## Modo estrutural

`backend/core/analises/estrutural.py`

Cada token vira uma categoria: pontuação, número, classe gramatical (artigo, preposição, conjunção, pronome, negação) ou um de cinco tamanhos de palavra. Assim, "O gato dorme no sofá." e "O cão late na rua." têm formatos parecidos, mesmo sem nenhuma palavra em comum. A ideia de classificar por tamanho é do `ProcessadorEstruturalLeve`, do Matheus.

```
formato = 2 × LCS(formato A, formato B) / (tamanho A + tamanho B)
acaso   = a mesma conta com B embaralhado (3 vezes, em amostra de 800 tokens)
          × min(1, tokens dos dois textos / 40)
nota    = (formato − acaso) / (1 − acaso), nunca abaixo de 0
```

Sem o desconto, dois textos quaisquer em português já pareceriam bastante similares, porque usam as mesmas categorias. Embaralhar mantém as categorias, mas destrói a construção, o que mede justamente essa parte devida ao acaso. Em textos curtos, embaralhar quase não muda a sequência, por isso o desconto é proporcional ao tamanho.

**Palavras idênticas** é uma medida à parte, que não entra na nota: compara as palavras sem stopwords, com Hirschberg, blocos e inversões. É ela que define os trechos destacados na tela.

| Nota | Faixa |
|---|---|
| Abaixo de 25% | Baixa |
| De 25% a 44% | Moderada |
| 45% ou mais | Alta |

## Nota do modo semântico

```
frases    = cobertura × (0,5 + 0,5 × ordem)
geral     = (similaridade da média dos vetores − 0,30) / (0,70 − 0,30), entre 0 e 1
nota      = max(frases, geral)
cobertura = frases do suspeito com equivalente no original / total de frases do suspeito
ordem     = 1 − inversões entre blocos / max(C(blocos, 2), frases em comum − 1)
```

A visão geral existe porque reescritas podem fundir ou dividir frases, e aí a comparação uma a uma falha.

| Nota | Faixa |
|---|---|
| Abaixo de 30% | Baixa |
| De 30% a 59% | Moderada |
| 60% ou mais | Alta |

As faixas dos dois modos são pontos de partida: ainda não foram calibradas com um conjunto real de textos.

## Modo semântico

`backend/core/analises/semantica.py`

Cada frase é normalizada (minúsculas, sem acentos) e vira um vetor no modelo multilíngue `paraphrase-multilingual-MiniLM-L12-v2`. Duas frases contam como iguais quando a similaridade de cosseno atinge 0,55. A partir daí, Hirschberg alinha as frases e as inversões medem quanto a ordem das ideias mudou.
