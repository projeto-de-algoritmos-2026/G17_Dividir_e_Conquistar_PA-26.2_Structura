# Testes

Resultados de 70 casos rodados nos dois modos. Esta tabela é gerada por `python -m tests.gerar_tabela`, e os textos de cada caso estão em `tests/corpus.py`.

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
| `test_api.py` | Rotas, limites, erros e arquivos servidos |
| `test_desempenho.py` | Pior caso aceito pela API abaixo de 30 segundos |
| `frontend.test.mjs` | Destaque com emoji e mensagens de erro, em Node |

**Como ler as colunas:**

- **Estrutural:** similaridade na forma de construir o texto. Olha só o formato, não o assunto. Com menos de 20 tokens, a faixa é "inconclusiva", porque formatos coincidem com facilidade.
- **Semântica:** suspeita de plágio. Olha as ideias.
- **Palavras idênticas:** quantas palavras do texto suspeito estão no original, ignorando palavras comuns como "o" e "de". Não entra na nota.

**O que os resultados mostram:**

- Cópias e reescritas têm suspeita alta na semântica, e textos sem relação dão 0%.
- Textos independentes sobre o mesmo tema ficam bem abaixo das paráfrases, porque a ideia geral sozinha não basta para subir a nota.
- Os modos discordam quando devem: uma paráfrase tem suspeita alta e similaridade estrutural baixa.
- Mudar a ordem das frases derruba a nota estrutural, mesmo em uma cópia. Nesses casos, vale olhar "Palavras idênticas" e a semântica.
- As tentativas de burla (aspas, enchimento, caracteres invisíveis e letras parecidas) não escondem mais a cópia.
- Frases com sentido oposto seguem altas quando só uma palavra muda, e textos muito curtos seguem imprecisos.


## Cópias

| Caso | Estrutural | Semântica | Palavras idênticas |
|---|---|---|---|
| Cópia exata | 100% (alta) | 100% (alta) | 25 de 25 (100%) |
| Cópia em maiúsculas e sem acentos | 100% (alta) | 100% (alta) | 25 de 25 (100%) |
| Frases reordenadas | 26% (moderada) | 100% (alta) | 25 de 25 (100%) |
| Metades trocadas | 27% (moderada) | 100% (alta) | 25 de 25 (100%) |
| Uma frase copiada, duas novas | 52% (alta) | 33% (moderada) | 10 de 19 (53%) |
| Texto longo com uma frase copiada | 12% (baixa) | 8% (baixa) | 8 de 59 (14%) |

## Reescritas

| Caso | Estrutural | Semântica | Palavras idênticas |
|---|---|---|---|
| Paráfrase completa | 21% (baixa) | 87% (alta) | 3 de 29 (10%) |
| Paráfrase de outro tema | 31% (moderada) | 86% (alta) | 3 de 22 (14%) |
| Paráfrase reordenada | 5% (baixa) | 87% (alta) | 3 de 29 (10%) |
| Metade copiada, metade parafraseada | 79% (alta) | 98% (alta) | 18 de 27 (67%) |
| Frases fundidas | 64% (alta) | 97% (alta) | 17 de 20 (85%) |
| Frases divididas | 46% (alta) | 96% (alta) | 16 de 27 (59%) |
| Exoplaneta: simples × técnico | 4% (baixa) | 64% (alta) | 1 de 26 (4%) |
| Médico: simples × técnico | 18% (inconclusiva) | 79% (alta) | 3 de 13 (23%) |
| Tradução para inglês | 8% (baixa) | 98% (alta) | 0 de 35 (0%) |

## Frases curtas

| Caso | Estrutural | Semântica | Palavras idênticas |
|---|---|---|---|
| "O céu é azul" × "Azul é o ceu" | 70% (inconclusiva) | 100% (alta) | 2 de 2 (100%) |
| "Eu amo você." × "Eu te amo." | 71% (inconclusiva) | 86% (alta) | 1 de 1 (100%) |
| "Gosto de café." × "Adoro café." | 84% (inconclusiva) | 96% (alta) | 1 de 2 (50%) |
| "Vou embora amanhã." × "Amanhã vou embora." | 72% (inconclusiva) | 99% (alta) | 3 de 3 (100%) |
| "Ela ama ele." × "Ele é amado por ela." | 54% (inconclusiva) | 95% (alta) | 0 de 1 (0%) |
| "Está chovendo." × "Chove agora." | 30% (inconclusiva) | 96% (alta) | 0 de 2 (0%) |
| "Oi" × "Oi" | 100% (inconclusiva) | 100% (alta) | 1 de 1 (100%) |

## Sentido diferente

| Caso | Estrutural | Semântica | Palavras idênticas |
|---|---|---|---|
| "Eu não amo você." × "Eu te amo." | 61% (inconclusiva) | 0% (baixa) | 1 de 1 (100%) |
| "Eu odeio você." × "Eu te amo." | 71% (inconclusiva) | 0% (baixa) | 0 de 1 (0%) |
| "Estou feliz." × "Estou triste." | 100% (inconclusiva) | 4% (baixa) | 1 de 2 (50%) |
| "O carro é azul." × "O carro é vermelho." | 78% (inconclusiva) | 72% (alta) | 1 de 2 (50%) |
| "eleva" × "reduz" o nível dos oceanos | 100% (inconclusiva) | 88% (alta) | 4 de 5 (80%) |
| Daniel chato × Daniel legal | 100% (inconclusiva) | 86% (alta) | 2 de 3 (67%) |
| Daniel salgado × Daniel doce | 71% (inconclusiva) | 69% (alta) | 1 de 4 (25%) |
| "Bom dia." × "Boa noite." | 63% (inconclusiva) | 78% (alta) | 0 de 2 (0%) |
| "Sim." × "Não." | 47% (inconclusiva) | 20% (baixa) | 0 de 0 (0%) |

## Sem relação

| Caso | Estrutural | Semântica | Palavras idênticas |
|---|---|---|---|
| Baleias × exoplaneta | 14% (baixa) | 0% (baixa) | 0 de 26 (0%) |
| Médico × futebol | 20% (baixa) | 0% (baixa) | 0 de 15 (0%) |
| Espaço × inflação | 27% (inconclusiva) | 0% (baixa) | 0 de 11 (0%) |
| Revolução industrial × baleias | 12% (baixa) | 0% (baixa) | 0 de 20 (0%) |
| Poema × notícia | 3% (inconclusiva) | 0% (baixa) | 0 de 10 (0%) |
| Lista de compras × notícia | 10% (inconclusiva) | 0% (baixa) | 0 de 10 (0%) |
| Código × texto | 0% (baixa) | 0% (baixa) | 0 de 25 (0%) |
| Clima × educação | 12% (baixa) | 0% (baixa) | 0 de 17 (0%) |
| Feijoada × futebol | 14% (baixa) | 0% (baixa) | 0 de 15 (0%) |
| Redes sociais × clima | 0% (baixa) | 0% (baixa) | 0 de 20 (0%) |

## Mesmo tema ou mesma construção

| Caso | Estrutural | Semântica | Palavras idênticas |
|---|---|---|---|
| Mesma construção, outro tema | 48% (alta) | 0% (baixa) | 2 de 18 (11%) |
| "O gato dorme no sofá." × "O cão late na rua." | 80% (inconclusiva) | 0% (baixa) | 0 de 3 (0%) |
| Médico × advogado, frases curtas | 36% (inconclusiva) | 2% (baixa) | 3 de 10 (30%) |
| Clima: autores 1 e 2 | 13% (baixa) | 20% (baixa) | 0 de 18 (0%) |
| Clima: autores 1 e 3 | 12% (baixa) | 20% (baixa) | 0 de 20 (0%) |
| Clima: autores 2 e 3 | 0% (baixa) | 9% (baixa) | 0 de 20 (0%) |
| Educação: autores 1 e 2 | 15% (baixa) | 20% (baixa) | 0 de 16 (0%) |
| Educação: autores 1 e 3 | 7% (baixa) | 44% (moderada) | 1 de 19 (5%) |
| Educação: autores 2 e 3 | 0% (baixa) | 20% (baixa) | 0 de 19 (0%) |
| Redes sociais: autores 1 e 2 | 16% (baixa) | 18% (baixa) | 0 de 19 (0%) |
| Mesmo molde de frases, outro tema | 68% (alta) | 74% (alta) | 5 de 14 (36%) |

## Citações e casos extremos

| Caso | Estrutural | Semântica | Palavras idênticas |
|---|---|---|---|
| Citação curta ao lado de texto próprio | 7% (baixa) | 0% (baixa) | 1 de 52 (2%) |
| Cópia só nas referências | 10% (baixa) | 0% (baixa) | 1 de 35 (3%) |
| Só pontuação | sem conteúdo | sem conteúdo | — |

## Tentativas de burla

| Caso | Estrutural | Semântica | Palavras idênticas |
|---|---|---|---|
| Trecho inteiro entre aspas | 100% (alta) | 100% (alta) | 25 de 25 (100%) |
| Trecho inteiro em aspas curvas | 100% (alta) | 100% (alta) | 25 de 25 (100%) |
| Linha 'Referências' antes da cópia | 98% (alta) | 99% (alta) | 25 de 26 (96%) |
| Parágrafo que começa com 'Referências' | 87% (alta) | 100% (alta) | 25 de 29 (86%) |
| Aspas soltas de polegada | 73% (alta) | 100% (alta) | 25 de 31 (81%) |
| Cópia integral com 8 frases novas | 27% (moderada) | 100% (alta) | 25 de 58 (43%) |
| Cópia integral com 40 frases novas | 2% (baixa) | 100% (alta) | 25 de 190 (13%) |
| Enchimento antes da cópia | 2% (baixa) | 100% (alta) | 25 de 190 (13%) |
| Letras cirílicas parecidas | 100% (alta) | 100% (alta) | 25 de 25 (100%) |
| Caracteres invisíveis nas palavras | 100% (alta) | 100% (alta) | 25 de 25 (100%) |
| Pontos trocados por ponto e vírgula | 91% (alta) | 97% (alta) | 25 de 25 (100%) |
| Texto colado de PDF | 100% (alta) | 100% (alta) | 76 de 76 (100%) |
| Original colado de PDF | 100% (alta) | 100% (alta) | 76 de 76 (100%) |
| Só o início em comum, sem pontuação | 34% (moderada) | 50% (moderada) | 90 de 220 (41%) |
| Só o fim em comum, sem pontuação | 32% (moderada) | 56% (moderada) | 90 de 196 (46%) |
