# Relatório do projeto

Estado atual do que foi feito. Os resultados de cada caso estão em [docs/testes.md](docs/testes.md), e as fórmulas, em [docs/algoritmos.md](docs/algoritmos.md).

## Como rodar

```bash
source venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload
```

Acesse http://localhost:8000. O front é servido pelo backend, então abrir o `index.html` direto ou pelo Live Server não funciona.

## Os dois modos

| | Estrutural | Semântica |
|---|---|---|
| **Pergunta** | Os textos são construídos do mesmo jeito? | As ideias vêm do original? |
| **Na tela** | Similaridade estrutural | Suspeita de plágio |
| **Compara** | Formato de cada palavra | Significado das frases e do texto inteiro |
| **Destaque** | Trechos com palavras idênticas | Frases com a mesma ideia |

## O que foi feito

**Modo estrutural**

- Cada palavra vira uma categoria: classe gramatical, tamanho, número ou pontuação.
- Hirschberg acha a maior sequência de formatos em comum, e a nota desconta o que coincidiria por acaso.
- O desconto é proporcional ao tamanho, e textos com menos de 20 tokens recebem a faixa "inconclusiva".
- "Palavras idênticas" é uma métrica à parte, em número bruto e porcentagem.
- "Maior trecho idêntico" mostra a maior sequência copiada, e 6 palavras de conteúdo seguidas geram um aviso.

**Modo semântico**

- Usa embeddings locais com `fastembed`.
- Hirschberg ponderado alinha as frases, e as inversões medem quanto a ordem das ideias mudou.
- Cada frase conta pela sua similaridade, reforçada pelas palavras de conteúdo em comum.
- A negação em só uma das frases anula esse reforço.
- Frases vizinhas somadas resgatam reescritas que fundem ou dividem frases.
- A nota considera o que veio do original e quanto do original foi aproveitado, o que impede esconder a cópia com enchimento.
- A "Ideia geral" compara os textos inteiros, mas só reforça a nota.
- A tela lista as frases equivalentes com a nota de cada par e avisa sobre frases idênticas.

**Dividir e conquistar**

- Hirschberg, Hirschberg ponderado e Counting Significant Inversions são novos.
- O `ContadorInversoes` original segue em uso, sem alterações, na métrica "Inversões".

**Frontend**

- Visual com paleta rosa-terracota, Cormorant Garamond e Lato, sem framework nem build.
- Seletor de modos carregado da API, trechos destacados e destaque do par ao passar o mouse.
- Erros na página, layout para celular, botão de exemplo, contador de palavras e seção "Como funciona".

**Backend**

- Cada modo é uma entrada em `backend/core/analises/registro.py`, e a tela se ajusta sozinha.
- Citações curtas e a seção de referências ficam fora da análise, com limites e aviso na tela.
- Caracteres invisíveis e letras de outros alfabetos que imitam as latinas não escondem mais as palavras.
- Cada texto é limitado a 20.000 caracteres, 6.000 tokens e 1.000 frases, com mensagem de erro clara.
- O modelo fica em `.cache/modelos`, dentro do projeto, e não some ao reiniciar o computador.

## Cortado de propósito

| Item | Motivo |
|---|---|
| Mediana das medianas | Com poucas frases, um `sorted` resolve |
| Árvore de Merkle | Só acha seções idênticas e alinhadas, o que o alinhamento já cobre |
| Skyline | Os blocos não se sobrepõem |
| Radicalização | Exige dependência ou um radicalizador próprio |
| n-gramas e múltiplos níveis | Duplicariam o que blocos e modo semântico já fazem |
| Controle de exigência | Removido a pedido; o limiar agora é fixo |
| Modelo de 1 GB | Testado, sem ganho sobre o atual |

## Mudanças no código original

`backend/core/algoritmos.py` não foi alterado.

| Arquivo | Mudança |
|---|---|
| `backend/main.py` | Serve o frontend; CORS removido; título atualizado |
| `backend/api/routes.py` | `/comparar` usa o registro de modos e devolve erros claros; nova rota `/analises` |
| `backend/schemas/models.py` | Novo campo `modo`; limite de tamanho |
| `backend/requirements.txt` | Adicionados `fastembed` e `numpy`; todas as dependências com versão fixa |
| `frontend/` | Reescrito; `css/style.css` foi substituído por três arquivos |
| `README.md` | Nome, descrição, uso e versão do Python atualizados |
| `ProcessadorEstruturalLeve` | Ampliado de 3 para 5 tamanhos, mais classes gramaticais e pontuação |
| `resultado.js` | O destaque do modo estrutural voltou, só para palavras idênticas |

`/comparar` mudou de formato, e `AnalisadorSimilaridade` e `MapeadorPermutacao` não são mais usados.

## Verificação

- `python -m pytest` roda a bateria inteira; `docs/testes.md` explica o que cada arquivo cobre.
- Hirschberg, a versão ponderada e as inversões batem com a tabela completa e a força bruta em 500 entradas aleatórias cada.
- Pior caso aceito pela API: cerca de 7 segundos em cada modo. Antes dos limites, eram 84 segundos no estrutural e 164 na semântica.
- A tela foi testada no Firefox, inclusive o destaque ao passar o mouse, o layout de celular e as mensagens de erro. Esse teste usou um script temporário, fora do repositório.
- A análise semântica foi rodada com a rede desligada, usando o modelo em `.cache/modelos`.

## Limitações conhecidas

- **Calibração:** faixas, limiares e pesos vieram dos textos de `tests/corpus.py`, escritos por nós, e não de um conjunto real.
- **Mesmo tema:** textos independentes ficaram entre 9% e 44% na semântica nos pares testados, mas textos com frases parecidas por acaso ainda podem chegar à faixa moderada.
- **Reescritas muito livres:** como a ideia geral não decide mais sozinha, uma reescrita sem nenhuma frase correspondente fica limitada a 20%.
- **Mesmo molde de frases:** textos que repetem a estrutura e várias palavras, mudando só o tema, dão suspeita alta.
- **Sentido oposto:** "eleva" × "reduz" dá 88%. O modelo vê o mesmo assunto e não percebe a inversão.
- **Palavras em comum:** "O carro é azul." × "O carro é vermelho." dá 72%. O modo mede reaproveitamento, não igualdade exata de sentido.
- **Textos muito curtos:** "Bom dia." × "Boa noite." dá 78% na semântica.
- **Palavras hifenizadas em PDF:** "desenvol-\nvimento" continua partida em duas palavras.
- **Citação longa legítima:** uma citação com mais de 40 palavras entra na análise e sobe a nota; um aviso informa isso.
- **Cópias reordenadas:** dão nota baixa no estrutural, porque a construção mudou. A semântica e "Palavras idênticas" cobrem esse caso.
- **Primeira análise semântica:** baixa o modelo e precisa de internet. Sem rede, a tela mostra uma mensagem clara.
