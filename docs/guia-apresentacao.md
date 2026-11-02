# Guia da apresentação

Resumo do que o projeto faz, como calcula e o que cada número significa. A ordem da demonstração está em [apresentacao.md](apresentacao.md).

## O projeto em uma frase

Compara dois textos de duas formas: se foram **construídos do mesmo jeito** (estrutural) e se **as ideias vêm do original** (semântica). O resultado orienta uma revisão humana e não prova plágio.

| | Estrutural | Semântica |
|---|---|---|
| **Pergunta** | Os textos têm a mesma forma? | As ideias vêm do original? |
| **Unidade** | Formato de cada palavra | Frase |
| **Olha o assunto?** | Não | Sim |
| **Resultado** | Similaridade | Suspeita de plágio |
| **Faixas** | Baixa < 25% ≤ moderada < 45% ≤ alta | Baixa < 30% ≤ moderada < 60% ≤ alta |

## Algoritmos de dividir e conquistar

| Algoritmo | Para que serve | Como divide | Tempo | Espaço |
|---|---|---|---|---|
| **Hirschberg** | Acha a maior sequência em comum | Corta A ao meio, acha o melhor corte em B e resolve os dois lados | `O(nm)` | `O(n + m)` |
| **Hirschberg ponderado** | Escolhe os melhores pares de frases | A mesma divisão, somando similaridades em vez de contar pares | `O(nm)` | `O(n + m)` |
| **Counting Inversions** | Conta quantos pares estão fora de ordem | Merge sort: quando um elemento da direita passa à frente, inverte com todos os restantes da esquerda | `O(n log n)` | `O(n)` |
| **Inversões significativas** | Ignora trocas pequenas | Merge sort com contagem própria de pares `a[i] > a[j] + tolerância` | `O(n log n)` | `O(n)` |

**Recorrências:**

- Hirschberg: `T(n, m) = T(n/2, k) + T(n/2, m−k) + O(nm)`
- Inversões: `T(n) = 2T(n/2) + O(n)`

## Como cada nota é calculada

**Estrutural**

1. Cada palavra vira uma categoria: artigo, preposição, número, tamanho e assim por diante.
2. Hirschberg acha a maior sequência de categorias em comum.
3. O acaso é medido embaralhando o segundo texto, e esse valor é descontado.

```
formato = 2 × tamanho da sequência comum / total de tokens
nota    = (formato − acaso) / (1 − acaso)
```

**Semântica**

1. Cada frase vira um vetor de significado, gerado por um modelo local.
2. Duas frases contam como iguais se a similaridade, reforçada pelas palavras em comum, chega a 55%.
3. Hirschberg ponderado alinha as frases, e uma varredura recupera as que mudaram de lugar.
4. Frases ainda sem par são comparadas com a união de duas frases vizinhas, para reconhecer fusões e divisões.

```
frases = max(cobertura, original) × (0,85 + 0,15 × ordem)
nota   = max(frases, min(ideia geral, frases + 0,20))
```

**Por que a fórmula é assim:**

- A ordem tira no máximo 15%, porque reordenar não apaga a cópia.
- A ideia geral acrescenta no máximo 20 pontos, porque tratar do mesmo tema não é plágio.
- `original` impede esconder uma cópia no meio de muito texto novo.

## O que cada estatística diz

**Estrutural**

| Estatística | O que diz |
|---|---|
| Formato em comum | Quanto da sequência de categorias coincide, antes do desconto |
| Esperado por acaso | Quanto coincidiria em textos sem relação com as mesmas categorias |
| Palavras idênticas | Palavras de conteúdo do suspeito que existem no original; não entra na nota |
| Maior trecho idêntico | Maior sequência copiada, sem contar palavras comuns |
| Trechos idênticos | Quantos blocos de palavras iguais foram achados |
| Ordem dos trechos | Se esses blocos seguem a mesma ordem do original |
| Inversões | Pares de palavras em ordem trocada |

**Semântica**

| Estatística | O que diz |
|---|---|
| Ideia geral | Proximidade dos textos inteiros; indica tema próximo, não cópia |
| Cobertura do suspeito | Quanto do suspeito tem equivalente no original |
| Original aproveitado | Quanto do original aparece no suspeito |
| Ordem | Se as ideias seguem a mesma ordem; 100% é a ordem original |
| Blocos | Grupos de frases seguidas que correspondem |
| Inversões | Pares de frases em ordem trocada |
| Frases em comum | Quantas frases do suspeito têm par no original |

**Cobertura × Original aproveitado:** cobertura baixa com original alto indica uma cópia diluída em material novo.

## Funcionalidades

- **Trechos destacados:** mostram onde estão as correspondências. Passar o mouse acende o par nos dois textos.
- **Frases equivalentes:** lista cada par de frases com sua nota.
- **Avisos:** informam o que ficou fora da análise, frases idênticas e trechos copiados.
- **Citações e referências:** citações curtas e a seção final de referências são ignoradas, até 40 palavras por citação e 25% do texto.
- **Proteção contra burlas:** caracteres invisíveis e letras parecidas de outros alfabetos são normalizados.
- **Texto colado de PDF:** quebra de linha simples não termina frase.
- **Frases longas:** passam de 60 palavras e são divididas, porque o modelo corta o que excede seu limite.
- **Faixa inconclusiva:** no estrutural, textos com menos de 20 tokens não recebem faixa, porque o formato coincide com facilidade.
- **Sem conteúdo:** se nada sobrar para analisar, a tela mostra um traço em vez de 0%.
- **Limites:** 20.000 caracteres, 6.000 tokens no estrutural e 1.000 frases na semântica.

## Exemplos para citar

| Caso | Estrutural | Semântica | O que mostra |
|---|---|---|---|
| Cópia exata | 100% | 100% | Os dois modos concordam |
| Frases reordenadas | 26% | 100% | A forma muda, mas as ideias continuam |
| Paráfrase | 21% | 87% | Palavras diferentes, mesma ideia |
| Mesma construção, outro tema | 48% | 0% | Mesma forma, ideias diferentes |
| Cópia com 40 frases novas | 2% | 100% | O enchimento não esconde a cópia |

## Limitações

- O modelo não percebe inversão de sentido: "eleva" × "reduz" dá 88%.
- Textos muito curtos seguem imprecisos: "Bom dia." × "Boa noite." dá 78%.
- Limiares e faixas foram ajustados com textos escritos por nós, não com um conjunto real.
- Uma reescrita sem nenhuma frase correspondente fica limitada a 20%.

## Perguntas prováveis

- **Por que Hirschberg, e não a tabela completa?** Dá o mesmo resultado, gastando memória linear em vez de quadrática.
- **Por que dois modos?** Cada um enxerga o que o outro não vê: paráfrase na semântica, construção no estrutural.
- **Onde as inversões entram na nota?** Na semântica, pela Ordem. No estrutural, são só uma métrica à parte.
- **Como sabemos que funciona?** Os algoritmos batem com a força bruta em entradas aleatórias, e `python -m pytest` roda a bateria inteira, descrita em [testes.md](testes.md).
