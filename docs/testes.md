# Testes

Resultados de 85 casos rodados nos dois modos. Esta tabela é gerada por `python -m tests.gerar_tabela`, e os textos de cada caso estão em `tests/corpus.py`.

Para rodar a bateria inteira:

```bash
pip install -r backend/requirements-dev.txt
python -m pytest
```

| Arquivo | O que verifica |
|---|---|
| `test_casos.py` | Cada caso desta página, nos dois modos, contra a faixa de nota esperada |
| `test_hirschberg.py`, `test_inversoes.py` | Algoritmos contra a resposta da tabela completa e da força bruta, em entradas aleatórias |
| `test_aleatorio.py` | Texto aleatório e hostil (Unicode, controle, HTML): nada pode virar erro nem quebrar as regras da resposta |
| `test_citacoes.py`, `test_frases.py`, `test_normalizacao.py` | Citações, referências, frases, abreviações, caracteres invisíveis e letras parecidas |
| `test_comum.py`, `test_estrutural.py`, `test_semantica.py` | Pareamento, blocos, ordem, notas e avisos de cada modo |
| `test_gramatica.py` | Classe gramatical de cada palavra, com acento, sufixo e contexto |
| `test_api.py` | Rotas, limites, erros e arquivos servidos |
| `test_desempenho.py` | Pior caso aceito pela API abaixo de 30 segundos |
| `frontend.test.mjs` | Destaque com emoji e mensagens de erro, em Node |

**Como ler as colunas:**

- **Estrutural:** similaridade na forma de construir as frases. Olha a classe gramatical das palavras, não o assunto. Com menos de 20 tokens, a faixa é "inconclusiva", porque construções coincidem com facilidade.
- **Semântica:** suspeita de plágio. Olha as ideias.
- **Palavras idênticas:** quantas palavras do texto suspeito estão no original, ignorando palavras comuns como "o" e "de". Não entra na nota.

**O que os resultados mostram:**

- Cópias e reescritas têm suspeita alta na semântica, e textos sem relação dão 0%.
- Textos independentes sobre o mesmo tema ficam bem abaixo das paráfrases, porque a ideia geral sozinha não basta para subir a nota.
- Os modos discordam quando devem: uma paráfrase tem suspeita alta e similaridade estrutural baixa, e a mesma construção sobre outro assunto tem o contrário.
- Mudar a ordem das frases custa no máximo 15% da nota estrutural: as frases continuam construídas do mesmo jeito.
- As tentativas de burla (aspas, enchimento, caracteres invisíveis e letras parecidas) não escondem mais a cópia.
- Frases com sentido oposto seguem altas quando só uma palavra muda, e textos muito curtos seguem imprecisos.

**Validação com texto real:** a análise estrutural foi calibrada e validada com 48 artigos da Wikipédia em português, divididos em 24 de calibração e 24 usados uma única vez, no fim. Os pares têm o rótulo garantido pela forma como são gerados: trocar as palavras de conteúdo por outras da mesma classe mantém a sintaxe, e frases de artigos diferentes são independentes.

| Cenário (825 pares nunca usados na calibração) | Acerto antes | Acerto depois |
|---|---|---|
| Mesmo molde, outro vocabulário | 75% | 100% |
| Mesmo molde, frases fora de ordem | 4% | 100% |
| Mesmo molde, 10% das palavras removidas | 41% | 100% |
| Cópia reordenada | 14% | 99% |
| Cópia com o triplo de material novo | 0% | 98% |
| Metade do molde | 40% | 100% |
| Sem relação (artigos diferentes, mesmo artigo, pequeno × grande) | 100% | 100% |
| **Total** | **53,8%** | **99,6%** |

Esse conjunto foi gerado por programa e não substitui textos reais de alunos. O classificador gramatical concorda com o spaCy em 91% das palavras desses artigos, sem contar artigos e palavras de ligação, em que os dois adotam convenções diferentes. O script e os artigos não fazem parte do repositório.


## Cópias

| Caso | Estrutural | Semântica | Palavras idênticas |
|---|---|---|---|
| Cópia exata | 100% (alta) | 100% (alta) | 25 de 25 (100%) |
| Cópia em maiúsculas e sem acentos | 100% (alta) | 100% (alta) | 25 de 25 (100%) |
| Frases reordenadas | 92% (alta) | 100% (alta) | 25 de 25 (100%) |
| Metades trocadas | 92% (alta) | 100% (alta) | 25 de 25 (100%) |
| Uma frase copiada, duas novas | 51% (moderada) | 33% (moderada) | 10 de 19 (53%) |
| Texto longo com uma frase copiada | 16% (baixa) | 8% (baixa) | 8 de 59 (14%) |

## Reescritas

| Caso | Estrutural | Semântica | Palavras idênticas |
|---|---|---|---|
| Paráfrase completa | 36% (moderada) | 87% (alta) | 3 de 29 (10%) |
| Paráfrase de outro tema | 26% (baixa) | 86% (alta) | 3 de 22 (14%) |
| Paráfrase reordenada | 26% (baixa) | 87% (alta) | 3 de 29 (10%) |
| Metade copiada, metade parafraseada | 78% (alta) | 98% (alta) | 18 de 27 (67%) |
| Frases fundidas | 58% (moderada) | 97% (alta) | 17 de 20 (85%) |
| Frases divididas | 51% (moderada) | 96% (alta) | 16 de 27 (59%) |
| Exoplaneta: simples × técnico | 14% (baixa) | 64% (alta) | 1 de 26 (4%) |
| Médico: simples × técnico | 42% (inconclusiva) | 79% (alta) | 3 de 13 (23%) |
| Tradução para inglês | 7% (baixa) | 98% (alta) | 0 de 35 (0%) |

## Frases curtas

| Caso | Estrutural | Semântica | Palavras idênticas |
|---|---|---|---|
| "O céu é azul" × "Azul é o ceu" | 0% (inconclusiva) | 100% (alta) | 2 de 2 (100%) |
| "Eu amo você." × "Eu te amo." | 0% (inconclusiva) | 86% (alta) | 1 de 1 (100%) |
| "Gosto de café." × "Adoro café." | 40% (inconclusiva) | 96% (alta) | 1 de 2 (50%) |
| "Vou embora amanhã." × "Amanhã vou embora." | 0% (inconclusiva) | 99% (alta) | 3 de 3 (100%) |
| "Ela ama ele." × "Ele é amado por ela." | 57% (inconclusiva) | 95% (alta) | 0 de 1 (0%) |
| "Está chovendo." × "Chove agora." | 0% (inconclusiva) | 96% (alta) | 0 de 2 (0%) |
| "Oi" × "Oi" | 100% (inconclusiva) | 100% (alta) | 1 de 1 (100%) |

## Sentido diferente

| Caso | Estrutural | Semântica | Palavras idênticas |
|---|---|---|---|
| "Eu não amo você." × "Eu te amo." | 0% (inconclusiva) | 0% (baixa) | 1 de 1 (100%) |
| "Eu odeio você." × "Eu te amo." | 0% (inconclusiva) | 0% (baixa) | 0 de 1 (0%) |
| "Estou feliz." × "Estou triste." | 100% (inconclusiva) | 4% (baixa) | 1 de 2 (50%) |
| "O carro é azul." × "O carro é vermelho." | 100% (inconclusiva) | 72% (alta) | 1 de 2 (50%) |
| "eleva" × "reduz" o nível dos oceanos | 100% (inconclusiva) | 88% (alta) | 4 de 5 (80%) |
| Daniel chato × Daniel legal | 100% (inconclusiva) | 86% (alta) | 2 de 3 (67%) |
| Daniel salgado × Daniel doce | 47% (inconclusiva) | 69% (alta) | 1 de 4 (25%) |
| "Bom dia." × "Boa noite." | 100% (inconclusiva) | 78% (alta) | 0 de 2 (0%) |
| "Sim." × "Não." | 0% (inconclusiva) | 20% (baixa) | 0 de 0 (0%) |

## Sem relação

| Caso | Estrutural | Semântica | Palavras idênticas |
|---|---|---|---|
| Baleias × exoplaneta | 15% (baixa) | 0% (baixa) | 0 de 26 (0%) |
| Médico × futebol | 24% (baixa) | 0% (baixa) | 0 de 15 (0%) |
| Espaço × inflação | 19% (inconclusiva) | 0% (baixa) | 0 de 11 (0%) |
| Revolução industrial × baleias | 5% (baixa) | 0% (baixa) | 0 de 20 (0%) |
| Poema × notícia | 32% (inconclusiva) | 0% (baixa) | 0 de 10 (0%) |
| Lista de compras × notícia | 3% (inconclusiva) | 0% (baixa) | 0 de 10 (0%) |
| Código × texto | 3% (baixa) | 0% (baixa) | 0 de 25 (0%) |
| Clima × educação | 16% (baixa) | 0% (baixa) | 0 de 17 (0%) |
| Feijoada × futebol | 20% (baixa) | 0% (baixa) | 0 de 15 (0%) |
| Redes sociais × clima | 10% (baixa) | 0% (baixa) | 0 de 20 (0%) |

## Mesmo tema ou mesma construção

| Caso | Estrutural | Semântica | Palavras idênticas |
|---|---|---|---|
| Mesma construção, outro tema | 100% (alta) | 0% (baixa) | 2 de 18 (11%) |
| "O gato dorme no sofá." × "O cão late na rua." | 100% (inconclusiva) | 0% (baixa) | 0 de 3 (0%) |
| Médico × advogado, frases curtas | 49% (inconclusiva) | 2% (baixa) | 3 de 10 (30%) |
| Clima: autores 1 e 2 | 14% (baixa) | 20% (baixa) | 0 de 18 (0%) |
| Clima: autores 1 e 3 | 13% (baixa) | 20% (baixa) | 0 de 20 (0%) |
| Clima: autores 2 e 3 | 15% (baixa) | 9% (baixa) | 0 de 20 (0%) |
| Educação: autores 1 e 2 | 14% (baixa) | 20% (baixa) | 0 de 16 (0%) |
| Educação: autores 1 e 3 | 9% (baixa) | 44% (moderada) | 1 de 19 (5%) |
| Educação: autores 2 e 3 | 12% (baixa) | 20% (baixa) | 0 de 19 (0%) |
| Redes sociais: autores 1 e 2 | 22% (baixa) | 18% (baixa) | 0 de 19 (0%) |
| Mesmo molde de frases, outro tema | 91% (alta) | 74% (alta) | 5 de 14 (36%) |

## Construção igual ou diferente

| Caso | Estrutural | Semântica | Palavras idênticas |
|---|---|---|---|
| Notícia policial × esportiva | 100% (alta) | 0% (baixa) | 0 de 16 (0%) |
| Jurídico × escolar | 97% (alta) | 20% (baixa) | 1 de 16 (6%) |
| Ciência × economia | 100% (alta) | 41% (moderada) | 3 de 20 (15%) |
| Palavras curtas × palavras longas | 100% (alta) | 38% (moderada) | 2 de 14 (14%) |
| Narrativas em pessoas diferentes | 74% (alta) | 20% (baixa) | 1 de 15 (7%) |
| Perguntas com o mesmo molde | 96% (alta) | 39% (moderada) | 2 de 13 (15%) |
| Molde igual, frases fora de ordem | 85% (alta) | 0% (baixa) | 0 de 16 (0%) |
| Moldes intercalados de dois textos | 95% (alta) | 11% (baixa) | 1 de 32 (3%) |
| Metade do molde, metade própria | 49% (moderada) | 0% (baixa) | 0 de 15 (0%) |
| Telegráfico × subordinado | 3% (baixa) | 0% (baixa) | 0 de 27 (0%) |
| Receita × texto acadêmico | 15% (baixa) | 0% (baixa) | 0 de 20 (0%) |
| Diálogo × texto acadêmico | 1% (baixa) | 0% (baixa) | 0 de 20 (0%) |
| Lista × subordinado | 6% (baixa) | 0% (baixa) | 0 de 27 (0%) |
| Diálogo × notícia | 0% (baixa) | 0% (baixa) | 0 de 16 (0%) |
| Voz ativa × voz passiva | 29% (baixa) | 99% (alta) | 10 de 13 (77%) |

## Citações e casos extremos

| Caso | Estrutural | Semântica | Palavras idênticas |
|---|---|---|---|
| Citação curta ao lado de texto próprio | 11% (baixa) | 0% (baixa) | 1 de 52 (2%) |
| Cópia só nas referências | 24% (baixa) | 0% (baixa) | 1 de 35 (3%) |
| Só pontuação | sem conteúdo | sem conteúdo | — |

## Tentativas de burla

| Caso | Estrutural | Semântica | Palavras idênticas |
|---|---|---|---|
| Trecho inteiro entre aspas | 100% (alta) | 100% (alta) | 25 de 25 (100%) |
| Trecho inteiro em aspas curvas | 100% (alta) | 100% (alta) | 25 de 25 (100%) |
| Linha 'Referências' antes da cópia | 100% (alta) | 99% (alta) | 25 de 26 (96%) |
| Parágrafo que começa com 'Referências' | 100% (alta) | 100% (alta) | 25 de 29 (86%) |
| Aspas soltas de polegada | 100% (alta) | 100% (alta) | 25 de 31 (81%) |
| Cópia integral com 8 frases novas | 100% (alta) | 100% (alta) | 25 de 58 (43%) |
| Cópia integral com 40 frases novas | 100% (alta) | 100% (alta) | 25 de 190 (13%) |
| Enchimento antes da cópia | 100% (alta) | 100% (alta) | 25 de 190 (13%) |
| Letras cirílicas parecidas | 100% (alta) | 100% (alta) | 25 de 25 (100%) |
| Caracteres invisíveis nas palavras | 100% (alta) | 100% (alta) | 25 de 25 (100%) |
| Pontos trocados por ponto e vírgula | 95% (alta) | 97% (alta) | 25 de 25 (100%) |
| Texto colado de PDF | 100% (alta) | 100% (alta) | 76 de 76 (100%) |
| Original colado de PDF | 100% (alta) | 100% (alta) | 76 de 76 (100%) |
| Só o início em comum, sem pontuação | 40% (moderada) | 50% (moderada) | 90 de 220 (41%) |
| Só o fim em comum, sem pontuação | 43% (moderada) | 56% (moderada) | 90 de 196 (46%) |
