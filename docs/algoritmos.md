# Algoritmos

Cada modo responde a uma pergunta diferente.

| | Estrutural | Semântica |
|---|---|---|
| **Pergunta** | Os textos são construídos do mesmo jeito? | As ideias vêm do original? |
| **Resultado** | Similaridade | Suspeita de plágio |
| **Olha o assunto?** | Não | Sim |
| **Direção** | Simétrica | Do suspeito para o original |
| **Unidade** | Classe gramatical de cada palavra, agrupada em frases | Frase |

```
Estrutural: Classificar palavras → Separar frases → Alinhar frases (Hirschberg ponderado) → Medir ordem (inversões) → Comparar o texto inteiro (Hirschberg) → Nota
Semântica:  Separar frases → Alinhar (Hirschberg ponderado) → Resgatar fusões → Agrupar em blocos → Medir ordem (inversões) → Nota
```

| Algoritmo | Pergunta que responde | Recorrência | Tempo | Espaço |
|---|---|---|---|---|
| Hirschberg | Quais trechos correspondem? | `T(n, m) = T(n/2, k) + T(n/2, m−k) + O(nm)` | `O(nm)` | `O(n + m)` |
| Hirschberg ponderado | Qual é o melhor conjunto de frases correspondentes? | A mesma | `O(nm)` | `O(n + m)` |
| Counting Inversions | Quanto a ordem mudou? | `T(n) = 2T(n/2) + O(n)` | `O(n log n)` | `O(n)` |
| Inversões significativas | Essa troca é relevante? | `T(n) = 2T(n/2) + O(n)` | `O(n log n)` | `O(n)` |

## Hirschberg

`backend/core/dividir_conquistar/hirschberg.py`

Acha a maior subsequência comum (LCS) sem guardar a tabela inteira da programação dinâmica.

- **Dividir:** corta `A` ao meio. Calcula a última linha da LCS da metade esquerda com `B`, e da metade direita invertida com `B` invertido.
- **Combinar:** o ponto `k` de `B` que maximiza a soma das duas linhas é onde o alinhamento ótimo cruza o meio de `A`.
- **Conquistar:** resolve `A[:meio]` com `B[:k]` e `A[meio:]` com `B[k:]`.

A LCS só encontra o que está na mesma ordem. Depois dela, `parear` faz uma varredura nas unidades restantes para recuperar blocos movidos de lugar.

A versão ponderada usa a mesma divisão, mas maximiza a soma dos pesos, e não a quantidade de pares. Sem isso, uma frase copiada poderia ser pareada com uma apenas parecida, porque as duas passam do limiar.

## Counting Inversions

`ContadorInversoes`, em `backend/core/algoritmos.py`, é a implementação original do projeto, reaproveitada sem alterações.

Durante o merge, quando um elemento da direita passa à frente, ele forma inversão com todos os elementos restantes da esquerda. Isso permite somar vários pares de uma vez, sem compará-los um a um. O valor aparece na tela como **Inversões**.

Nos dois modos, a ordem das frases entra na nota pelas inversões significativas.

## Inversões significativas

`backend/core/dividir_conquistar/inversoes.py`

Conta pares `i < j` com `a[i] > a[j] + tolerância`. A condição difere da comparação usada no merge, então a contagem é feita em uma varredura própria com dois ponteiros, antes de mesclar.

É aplicada ao início de cada bloco, e isso define a **Ordem**. Com isso, trocar duas metades do texto conta como um movimento, e não como centenas de inversões entre palavras. A ordem tira no máximo 15% da nota das frases, porque reordenar não apaga a cópia nem muda como cada frase foi construída.

| Modo | Tolerância | Motivo |
|---|---|---|
| Frases, nos dois modos | 0 | Mover uma frase já é uma mudança real |
| Palavras idênticas | 2 posições | Trocar palavras vizinhas não muda o trecho |

## Modo estrutural

`backend/core/analises/estrutural.py`

`backend/core/analises/gramatica.py` classifica as palavras.

Cada token vira uma classe gramatical: artigo, preposição, conjunção, pronome, negação, verbo, advérbio, substantivo, adjetivo ou número, além da pontuação. Assim, "O gato dorme no sofá." e "O cão late na rua." têm a mesma forma, sem nenhuma palavra em comum. Antes, as palavras de conteúdo eram classificadas pelo tamanho: "menino" e "ministro" caíam em categorias diferentes, e "bola" e "lei" na mesma de "nova".

A classe vem de três fontes, em Python puro, sem dependências:

1. **Léxico:** palavras de ligação, verbos irregulares, numerais e adjetivos comuns. O acento é usado quando os dois textos têm acentos, para separar "é" de "e" e "está" de "esta".
2. **Sufixos do português:** `-mente` para advérbio, `-aram` e `-ando` para verbo, `-ção` e `-dade` para substantivo, `-oso` e `-ável` para adjetivo.
3. **Contexto:** "o jantar" é nome e "vai jantar" é verbo; "a lei foi assinada" é verbo e "a lei assinada" é adjetivo.

Maiúsculas não são usadas, para a nota não mudar com a caixa em que o texto foi colado. Em textos da Wikipédia, esse classificador concorda com o spaCy, um etiquetador estatístico treinado, em 91% das palavras, sem contar artigos e palavras de ligação como "que" e "se", em que os dois adotam convenções diferentes.

```
comum(i, j)  = LCS das classes da frase i com as da frase j
similar(i,j) = 2 × comum / (tamanho i + tamanho j)
limiar       = 0,75 + 0,01 × max(0, 20 − tamanho médio do par)
frases       = Hirschberg ponderado sobre os pares acima do limiar, somando comum(i, j)
conjunta     = 2 × tokens em comum / (tokens A + tokens B)
cobertura    = max(tokens em comum / tokens A, tokens em comum / tokens B), se o texto menor estiver contido
             = conjunta, nos demais casos
por frases   = cobertura × (0,85 + 0,15 × ordem)
contínua     = (formato − acaso) / (1 − acaso), nunca abaixo de 0
nota         = max(por frases, contínua)
```

**Por que comparar frase a frase:** uma LCS do texto inteiro só enxerga o que está na mesma ordem. Trocar duas frases de lugar, ou colocar material novo antes da cópia, derrubava a nota, embora cada frase continuasse construída do mesmo jeito. Agora cada frase procura sua par em qualquer posição: Hirschberg ponderado acha as que estão em ordem, e `parear` recupera as que mudaram de lugar.

**Por que o limiar muda com o tamanho:** com 10 classes, frases curtas coincidem com facilidade. Em frases reais sem relação, o percentil 99 da similaridade cai de 0,80, em 10 tokens, para 0,70, em 25 tokens, enquanto frases de mesma sintaxe ficam acima de 0,82.

**Por que o texto inteiro continua sendo comparado:** frases fundidas ou divididas não têm uma par exata, e a comparação contínua as reconhece.

```
formato = 2 × LCS(classes A, classes B) / (tamanho A + tamanho B)
acaso   = a mesma conta com um dos textos embaralhado (3 vezes, em amostra de 800 tokens)
          (quando tudo é da mesma categoria, nota = formato: embaralhar não mudaria nada)
```

**Quando o texto menor está contido no maior:** exige ao menos 3 frases em comum, 20 tokens e similaridade média de 0,90. Sem isso, entre dezenas de frases candidatas, alguma coincidiria por acaso. Usar o maior dos dois sentidos mantém a nota simétrica: trocar os textos de lugar nunca muda o resultado.

Trechos sem pontuação são divididos a cada 60 tokens; do contrário, o texto inteiro viraria uma "frase".

**Palavras idênticas** é uma medida à parte, que não entra na nota: compara as palavras sem stopwords, com Hirschberg, blocos e inversões. É ela que define os trechos destacados na tela.

| Nota | Faixa |
|---|---|
| Abaixo de 30% | Baixa |
| De 30% a 59% | Moderada |
| 60% ou mais | Alta |

Com menos de 20 tokens em um dos textos, a faixa é **inconclusiva**: em frases reais sem relação, de 14% a 31% dos pares abaixo desse tamanho passam de "baixa".

## Nota do modo semântico

```
cobertura = soma das similaridades das frases equivalentes / total de frases do suspeito
original  = a mesma soma / total de frases do original (vale com 3 frases ou mais em comum)
ordem     = 1 − inversões entre blocos / max(C(blocos, 2), frases em comum − 1)
frases    = max(cobertura, original) × (0,85 + 0,15 × ordem)
s         = similaridade da média dos vetores dos dois textos
geral     = (s − 0,30) / (0,70 − 0,30), entre 0 e o menor valor entre 1 e s
nota      = max(frases, min(geral, frases + 0,20))
```

A visão geral só reforça o alinhamento. Sozinha, ela chegaria a 85% em redações independentes sobre o mesmo tema, que não têm nenhuma frase correspondente. Ela também ignora a ordem das frases, e por isso não pode decidir a nota.

`original` existe porque encher o suspeito de material novo diluía a cobertura: uma cópia integral somada a 40 frases novas dava 13%.

| Nota | Faixa |
|---|---|
| Abaixo de 30% | Baixa |
| De 30% a 59% | Moderada |
| 60% ou mais | Alta |

As faixas do modo semântico foram conferidas em `tests/corpus.py`, mas não em um conjunto real de textos. As do modo estrutural foram validadas em artigos reais da Wikipédia, com os resultados em [testes.md](testes.md).

## Modo semântico

`backend/core/analises/semantica.py`

Cada frase é normalizada (minúsculas, sem acentos) e vira um vetor no modelo multilíngue `paraphrase-multilingual-MiniLM-L12-v2`. A similaridade de cada par de frases é reforçada pelas palavras de conteúdo em comum: `s + (1 − s) × 0,65 × dice`. O reforço é anulado quando só uma das frases tem negação. Duas frases contam como iguais quando esse valor atinge 0,55. A partir daí, Hirschberg alinha as frases e as inversões medem quanto a ordem das ideias mudou.

Depois do alinhamento, frases do suspeito sem par são comparadas com a união de duas frases vizinhas, nos dois sentidos, para reconhecer fusões e divisões. A união precisa atingir 0,70, e cada parte, 0,35. Essa etapa vem depois porque a similaridade de uma união é alta com facilidade: dentro do alinhamento, ela tomava o lugar de pares verdadeiros.

Frases com mais de 60 palavras são divididas, porque o modelo corta o que passa do seu limite e ignoraria o restante. Quebra de linha simples não termina frase, para que textos colados de PDF funcionem.

## Limites de tamanho e citações

| Regra | Valor | Motivo |
|---|---|---|
| Caracteres por texto | 20.000 | Limite geral da API |
| Tokens no estrutural | 6.000 | O alinhamento é quadrático; sem esse limite, o pior caso levava 84 segundos |
| Frases na semântica | 1.000 | Sem esse limite, o pior caso levava 164 segundos |
| Citação ignorada | Até 40 palavras | Aspas longas seriam um esconderijo |
| Total de citações ignoradas | Até 25% do texto | Se passar disso, todas são analisadas |
| Título de referências | Sozinho na linha, na segunda metade do texto | Um parágrafo que começa com "Referências" apagava o resto do texto |

Tudo que sai da análise aparece em um aviso na tela. Quando nada sobra para analisar, a resposta não tem nota, em vez de mostrar 0%.
