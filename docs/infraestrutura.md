# Infraestrutura

## Arquitetura

API FastAPI sem estado: recebe dois textos, compara, responde e descarta. O mesmo servidor entrega o front, em HTML, CSS e JS puros, sem build.

```
backend/
├── main.py                  sobe a API e serve o frontend
├── api/routes.py            rotas
├── schemas/models.py        validação da entrada
└── core/
    ├── algoritmos.py        ContadorInversoes (código original do projeto)
    ├── dividir_conquistar/  hirschberg.py, inversoes.py
    └── analises/            registro.py, comum.py, gramatica.py, estrutural.py, semantica.py
frontend/                    index.html, css/, js/ (api.js, app.js, resultado.js)
tests/                       pytest e Node
```

| Rota | Função |
|---|---|
| `GET /api/analises` | Lista os modos e o limite de caracteres |
| `POST /api/comparar` | Recebe `texto_a`, `texto_b` e `modo`; devolve nota, faixa, métricas, trechos, pares e avisos |
| `GET /api/status` | Verifica se o servidor está no ar |

Erros: `422` para texto grande demais ou modo desconhecido, `503` se o modelo não puder ser carregado. Para criar um modo, basta adicionar uma entrada em `registro.py`: a API e a tela se ajustam sozinhas.

**Dependências principais:** `fastapi`, `uvicorn`, `fastembed` e `numpy`. O modelo fica em `.cache/modelos`, fora do Git.

## Algoritmos de dividir e conquistar

| Algoritmo | Pergunta | Recorrência | Tempo | Espaço |
|---|---|---|---|---|
| Hirschberg | Qual é a maior sequência em comum? | `T(n, m) = T(n/2, k) + T(n/2, m−k) + O(nm)` | `O(nm)` | `O(n + m)` |
| Hirschberg ponderado | Quais pares de frases somam mais? | A mesma | `O(nm)` | `O(n + m)` |
| Counting Inversions | Quanto a ordem mudou? | `T(n) = 2T(n/2) + O(n)` | `O(n log n)` | `O(n)` |
| Inversões significativas | Essa troca é relevante? | `T(n) = 2T(n/2) + O(n)` | `O(n log n)` | `O(n)` |

- **Hirschberg:** corta `A` ao meio, calcula a última linha da LCS de cada metade contra `B` (a direita, invertida) e acha o corte `k` de `B` que maximiza a soma. Resolve os dois lados recursivamente. A versão ponderada maximiza a soma dos pesos, e não a quantidade de pares.
- **Recuperação de movidos:** a LCS só acha o que está em ordem. `parear` faz depois uma varredura para recuperar o que mudou de lugar.
- **Inversões significativas:** contam pares `i < j` com `a[i] > a[j] + tolerância`, em uma varredura própria antes do merge. São aplicadas ao início de cada bloco, então mover um parágrafo inteiro conta como um movimento. A tolerância é 0 entre frases e 2 entre palavras idênticas.

## Modo estrutural

`estrutural.py` e `gramatica.py`. Pipeline: classificar palavras → separar frases → alinhar frases → medir a ordem → comparar o texto inteiro → nota.

**Classes:** artigo, preposição, conjunção, pronome, negação, verbo, advérbio, substantivo, adjetivo, número e pontuação. Vêm de um léxico, dos sufixos do português e do contexto, em Python puro. Acentos separam "é" de "e" quando os dois textos os têm. Maiúsculas não são usadas.

```
comum(i, j) = LCS das classes das frases i e j
similar     = 2 × comum / (tamanho i + tamanho j)
limiar      = 0,75 + 0,01 × max(0, 20 − tamanho médio do par)
conjunta    = 2 × tokens em comum / (tokens A + tokens B)
cobertura   = max(em comum / tokens A, em comum / tokens B), se o menor estiver contido; senão, conjunta
por frases  = cobertura × (0,85 + 0,15 × ordem)
formato     = 2 × LCS(texto A, texto B) / (tokens A + tokens B)
acaso       = a mesma conta com um texto embaralhado (3 vezes, em amostra de 800 tokens)
contínua    = (formato − acaso) / (1 − acaso), nunca abaixo de 0
nota        = max(por frases, contínua)
```

| Regra | Motivo |
|---|---|
| Comparar frase a frase | A LCS do texto inteiro não enxerga frases movidas nem cópias diluídas |
| Limiar maior em frases curtas | Sem relação, o percentil 99 da similaridade cai de 0,80 (10 tokens) para 0,70 (25) |
| Comparar também o texto inteiro | Reconhece frases fundidas ou divididas |
| Contido exige 3 frases, 20 tokens e média 0,90 | Entre dezenas de candidatas, alguma coincide por acaso |
| Dividir a cada 60 tokens sem pontuação | Senão, o texto inteiro viraria uma "frase" |
| Menos de 20 tokens: faixa inconclusiva | De 14% a 31% dos pares sem relação passam de "baixa" |

A nota é simétrica: trocar os textos de lugar não a muda. **Palavras idênticas** é uma medida à parte, sem stopwords, que não entra na nota e define os destaques na tela.

## Modo semântico

`semantica.py`, com o modelo `paraphrase-multilingual-MiniLM-L12-v2` via `fastembed`. Pipeline: separar frases → gerar vetores → alinhar frases → resgatar fusões → agrupar em blocos → medir a ordem → nota.

```
par       = s + (1 − s) × 0,65 × dice das palavras de conteúdo (sem reforço se só uma frase tiver negação)
cobertura = soma das similaridades das frases em comum / frases do suspeito
original  = a mesma soma / frases do original (vale com 3 frases ou mais)
frases    = max(cobertura, original) × (0,85 + 0,15 × ordem)
geral     = (s − 0,30) / 0,40, entre 0 e o menor valor entre 1 e s, com s = similaridade dos textos inteiros
nota      = max(frases, min(geral, frases + 0,20))
```

- Duas frases contam como iguais a partir de 0,55.
- Frases sem par são comparadas com a união de duas vizinhas, nos dois sentidos, para reconhecer fusões e divisões: a união precisa de 0,70, e cada parte, de 0,35.
- `original` impede esconder uma cópia no meio de texto novo.
- A ideia geral só reforça a nota, porque tratar do mesmo tema não é plágio.
- Frases com mais de 60 palavras são divididas, porque o modelo corta o excedente.

**Faixas dos dois modos:** baixa abaixo de 30%, moderada de 30% a 59%, alta a partir de 60%.

## Limites e proteções

| Regra | Valor |
|---|---|
| Caracteres por texto | 20.000 |
| Tokens no estrutural | 6.000 |
| Frases na semântica | 1.000 |
| Citação ignorada | Até 40 palavras entre aspas |
| Total de citações ignoradas | Até 25% do texto; se passar, todas são analisadas |
| Referências ignoradas | Título sozinho na linha, na segunda metade do texto |

Caracteres invisíveis e letras de outros alfabetos que imitam as latinas são normalizados. Quebra de linha simples não termina frase, o que permite colar texto de PDF. Tudo que sai da análise gera um aviso na tela, e sem conteúdo a nota fica vazia, em vez de 0%.

## Testes

`python -m pytest` roda toda a bateria, e `node --test tests/frontend.test.mjs` testa o front.

| Arquivo | O que verifica |
|---|---|
| `corpus.py`, `test_casos.py` | 85 casos reais de uso, nos dois modos, contra a faixa esperada |
| `test_hirschberg.py`, `test_inversoes.py` | Algoritmos contra a tabela completa e a força bruta, em 500 entradas aleatórias |
| `test_estrutural.py`, `test_gramatica.py` | Notas, simetria, frases e classes gramaticais |
| `test_semantica.py`, `test_comum.py` | Notas, avisos, pareamento, blocos e ordem |
| `test_citacoes.py`, `test_frases.py`, `test_normalizacao.py` | Citações, abreviações, invisíveis e letras parecidas |
| `test_aleatorio.py` | Texto hostil não pode virar erro |
| `test_api.py`, `test_desempenho.py` | Rotas, erros e pior caso abaixo de 30 segundos (cerca de 9 segundos hoje) |
| `frontend.test.mjs` | Destaque com emoji e mensagens de erro |

**Validação do modo estrutural:** 48 artigos da Wikipédia, 24 para calibrar e 24 usados só no fim. Trocar as palavras de conteúdo por outras da mesma classe mantém a sintaxe, e frases de artigos diferentes são independentes, então o rótulo de cada par vem da forma como ele foi gerado.

| Cenário (825 pares) | Antes | Depois |
|---|---|---|
| Mesma construção, outro vocabulário | 75% | 100% |
| Mesma construção, fora de ordem | 4% | 100% |
| Mesma construção, 10% das palavras removidas | 41% | 100% |
| Cópia reordenada | 14% | 99% |
| Cópia com o triplo de texto novo | 0% | 98% |
| Metade da mesma construção | 40% | 100% |
| Sem relação | 100% | 100% |
| **Total** | **53,8%** | **99,6%** |

O classificador concorda com o spaCy em 91% das palavras, sem contar artigos e palavras de ligação, em que os dois adotam convenções diferentes. O spaCy e os artigos foram usados só para medir e não fazem parte do projeto.

## Limitações

- O modo estrutural foi validado com pares gerados por programa, e não com textos de alunos. No semântico, os limiares vêm de textos escritos por nós.
- A semântica não percebe inversão de sentido: "eleva" × "reduz" dá 88%, e "O carro é azul." × "O carro é vermelho." dá 72%.
- Uma reescrita sem nenhuma frase correspondente fica limitada a 20%.
- Textos muito curtos são imprecisos: "Bom dia." × "Boa noite." dá 78% na semântica.
- Textos que repetem o molde e várias palavras, mudando só o tema, dão suspeita alta.
- Maiúscula isolada antes do ponto ("Clark Y.") é lida como inicial, e duas frases se fundem.
- Voz ativa e passiva contam como construções diferentes.
- Palavras hifenizadas em PDF continuam partidas, e citações com mais de 40 palavras sobem a nota, com aviso.

## Fora do escopo

| Item | Motivo |
|---|---|
| Mediana das medianas, Skyline, árvore de Merkle | Não respondem a nenhuma pergunta que o alinhamento já não cubra |
| spaCy na análise | Dependência pesada, com ganho pequeno sobre o classificador próprio |
| Bigramas de classes | Testado: não separa melhor que a LCS e piora com pequenas edições |
| Modelo de 1 GB | Testado, sem ganho sobre o atual |

`AnalisadorSimilaridade` e `MapeadorPermutacao`, em `algoritmos.py`, não são mais usados; só `ContadorInversoes` segue ativo.

**Escala:** um banco de dados tornaria a API stateful e permitiria comparar um texto contra milhares de documentos já processados, de 1 para N, guardando o histórico.
