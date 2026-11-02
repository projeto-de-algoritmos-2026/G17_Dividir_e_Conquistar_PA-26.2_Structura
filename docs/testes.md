# Testes

Resultados de 44 casos rodados nos dois modos, na versão atual do projeto.

- **Estrutural:** similaridade na forma de construir o texto. Olha só o formato, não o assunto.
- **Semântica:** suspeita de plágio. Olha as ideias.
- **Palavras idênticas:** quantas palavras do texto suspeito estão no original, ignorando palavras comuns como "o" e "de". Não entra na nota.

**O que os resultados mostram:**

- Cópias e reescritas têm suspeita alta na semântica, e textos sem relação dão 0%.
- Os modos discordam quando devem: uma paráfrase dá 86% na semântica e 24% na estrutural.
- Mudar a ordem das frases derruba a nota estrutural, mesmo em uma cópia. Nesses casos, vale olhar "Palavras idênticas" e a semântica.
- Redações autorais sobre o mesmo tema dão 85% na semântica: o modelo não separa paráfrase de autores que pensam parecido.
- Frases com sentido oposto seguem altas, e textos muito curtos seguem imprecisos.

## Cópias

| Caso | Estrutural | Semântica | Palavras idênticas |
|---|---|---|---|
| Cópia exata | 100% (alta) | 100% (alta) | 30 de 30 (100%) |
| Cópia em maiúsculas e sem acentos | 98% (alta) | 100% (alta) | 30 de 30 (100%) |
| Frases reordenadas | 10% (baixa) | 100% (alta) | 30 de 30 (100%) |
| Metades trocadas | 4% (baixa) | 100% (alta) | 30 de 30 (100%) |
| Uma frase copiada, duas novas | 34% (moderada) | 33% (moderada) | 8 de 21 (38%) |
| Texto longo com uma frase copiada | 17% (baixa) | 11% (baixa) | 7 de 95 (7%) |

## Reescritas

| Caso | Estrutural | Semântica | Palavras idênticas |
|---|---|---|---|
| Paráfrase completa | 24% (baixa) | 86% (alta) | 2 de 32 (6%) |
| Paráfrase reordenada | 4% (baixa) | 86% (alta) | 2 de 32 (6%) |
| Metade copiada, metade parafraseada | 59% (alta) | 92% (alta) | 16 de 30 (53%) |
| Exoplaneta: simples × técnico | 8% (baixa) | 69% (alta) | 2 de 57 (4%) |
| Médico: simples × técnico | 10% (baixa) | 64% (alta) | 0 de 35 (0%) |
| Tradução para inglês | 35% (moderada) | 96% (alta) | 1 de 7 (14%) |

## Frases curtas

| Caso | Estrutural | Semântica | Palavras idênticas |
|---|---|---|---|
| "O céu é azul" × "Azul é o ceu" | 70% (alta) | 100% (alta) | 2 de 2 (100%) |
| "Eu amo você." × "Eu te amo." | 71% (alta) | 86% (alta) | 1 de 1 (100%) |
| "Gosto de café." × "Adoro café." | 84% (alta) | 96% (alta) | 1 de 2 (50%) |
| "Vou embora amanhã." × "Amanhã vou embora." | 72% (alta) | 99% (alta) | 3 de 3 (100%) |
| "Ela ama ele." × "Ele é amado por ela." | 54% (alta) | 95% (alta) | 0 de 1 (0%) |
| "Está chovendo." × "Chove agora." | 30% (moderada) | 96% (alta) | 0 de 2 (0%) |
| "Oi" × "Oi" | 100% (alta) | 100% (alta) | 1 de 1 (100%) |

## Sentido diferente

| Caso | Estrutural | Semântica | Palavras idênticas |
|---|---|---|---|
| "Eu não amo você." × "Eu te amo." | 61% (alta) | 0% (baixa) | 1 de 1 (100%) |
| "Eu odeio você." × "Eu te amo." | 71% (alta) | 0% (baixa) | 0 de 1 (0%) |
| "Estou feliz." × "Estou triste." | 100% (alta) | 4% (baixa) | 1 de 2 (50%) |
| "O carro é azul." × "O carro é vermelho." | 78% (alta) | 72% (alta) | 1 de 2 (50%) |
| "eleva" × "reduz" o nível dos oceanos | 100% (alta) | 86% (alta) | 4 de 5 (80%) |
| Daniel chato × Daniel legal | 83% (alta) | 95% (alta) | 3 de 4 (75%) |
| Daniel salgado × Daniel doce | 52% (alta) | 87% (alta) | 2 de 4 (50%) |
| "Bom dia." × "Boa noite." | 63% (alta) | 78% (alta) | 0 de 2 (0%) |
| "Sim." × "Não." | 47% (alta) | 46% (moderada) | 0 de 0 (0%) |

## Sem relação

| Caso | Estrutural | Semântica | Palavras idênticas |
|---|---|---|---|
| Baleias × exoplaneta | 6% (baixa) | 0% (baixa) | 1 de 54 (2%) |
| Médico × futebol | 20% (baixa) | 0% (baixa) | 0 de 16 (0%) |
| Espaço × inflação | 3% (baixa) | 0% (baixa) | 0 de 15 (0%) |
| Revolução industrial × baleias | 20% (baixa) | 0% (baixa) | 1 de 16 (6%) |
| Poema × notícia | 9% (baixa) | 0% (baixa) | 0 de 13 (0%) |
| Lista de compras × notícia | 5% (baixa) | 0% (baixa) | 0 de 13 (0%) |
| Código × texto | 3% (baixa) | 0% (baixa) | 0 de 30 (0%) |

## Mesmo tema ou mesma construção

| Caso | Estrutural | Semântica | Palavras idênticas |
|---|---|---|---|
| Mesma construção, outro tema | 49% (alta) | 18% (baixa) | 0 de 30 (0%) |
| "O gato dorme no sofá." × "O cão late na rua." | 80% (alta) | 0% (baixa) | 0 de 3 (0%) |
| Médico × advogado, frases curtas | 53% (alta) | 0% (baixa) | 0 de 5 (0%) |
| Mesmo tema, texto próprio | 12% (baixa) | 26% (baixa) | 0 de 18 (0%) |
| Redações autorais do mesmo tema | 8% (baixa) | 85% (alta) | 13 de 40 (32%) |
| Mesmo contexto, outro tema | 13% (baixa) | 25% (baixa) | 6 de 34 (18%) |

## Citações e casos extremos

| Caso | Estrutural | Semântica | Palavras idênticas |
|---|---|---|---|
| Trecho inteiro entre aspas | 0% (baixa) | 0% (baixa) | 0 de 8 (0%) |
| Cópia só nas referências | 0% (baixa) | 0% (baixa) | 0 de 5 (0%) |
| Só pontuação | 0% (baixa) | 0% (baixa) | 0 de 0 (0%) |
