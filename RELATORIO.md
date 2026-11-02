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
- O desconto é proporcional ao tamanho, para funcionar em frases curtas.
- "Palavras idênticas" é uma métrica à parte, em número bruto e porcentagem.

**Modo semântico**

- Usa embeddings locais com `fastembed`.
- Hirschberg alinha as frases, e as inversões medem quanto a ordem das ideias mudou.
- Cada frase conta pela sua similaridade, reforçada pelas palavras de conteúdo em comum.
- A negação em só uma das frases anula esse reforço.
- A "Ideia geral" compara os textos inteiros e reconhece reescritas que fundem ou dividem frases.
- A tela lista as frases equivalentes com a nota de cada par.

**Dividir e conquistar**

- Hirschberg e Counting Significant Inversions são novos.
- O `ContadorInversoes` do Matheus segue em uso, sem alterações, na métrica "Inversões".

**Frontend**

- Visual com paleta rosa-terracota, Cormorant Garamond e Lato, sem framework nem build.
- Seletor de modos carregado da API, trechos destacados e destaque do par ao passar o mouse.
- Erros na página, layout para celular, botão de exemplo, contador de palavras e seção "Como funciona".

**Backend**

- Cada modo é uma entrada em `backend/core/analises/registro.py`, e a tela se ajusta sozinha.
- Citações entre aspas e a seção de referências ficam fora da análise.
- Cada texto é limitado a 20.000 caracteres.

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

## Mudanças no código do Matheus

`backend/core/algoritmos.py` não foi alterado.

| Arquivo | Mudança |
|---|---|
| `backend/main.py` | Serve o frontend; CORS removido |
| `backend/api/routes.py` | `/comparar` usa o registro de modos; nova rota `/analises` |
| `backend/schemas/models.py` | Novo campo `modo`; limite de tamanho |
| `backend/requirements.txt` | Adicionados `fastembed` e `numpy` |
| `frontend/` | Reescrito; `css/style.css` foi substituído por três arquivos |
| `README.md` | Nome, descrição e uso atualizados |
| `ProcessadorEstruturalLeve` | Criado por ele e ampliado de 3 para 5 tamanhos, mais classes gramaticais e pontuação |
| `resultado.js` | O destaque que ele tirou do modo estrutural voltou, só para palavras idênticas |

`/comparar` mudou de formato, e `AnalisadorSimilaridade` e `MapeadorPermutacao` não são mais usados.

## Verificação

- Hirschberg e inversões significativas bateram com a força bruta em 500 entradas aleatórias cada.
- Pior caso do modo estrutural, no limite de 20.000 caracteres: 7,6 segundos.
- Não há testes automatizados no repositório; as verificações usaram scripts temporários.
- As últimas mudanças da semântica foram testadas pelo backend, sem abrir a tela.
- O destaque ao passar o mouse nunca foi testado em navegador.

## Limitações conhecidas

- **Calibração:** faixas, limiar de frases e pesos vieram de poucos textos de teste.
- **Redações sobre o mesmo tema:** dão 85% na semântica, porque o modelo não separa paráfrase de autores que pensam parecido.
- **Sentido oposto:** "eleva" × "reduz" dá 86%. O modelo vê o mesmo assunto e não percebe a inversão.
- **Palavras em comum:** "O carro é azul." × "O carro é vermelho." dá 72%. O modo mede reaproveitamento, não igualdade exata de sentido.
- **Textos muito curtos:** "Bom dia." × "Boa noite." dá 78%, e "Sim." × "Não." dá 46%.
- **Cópias reordenadas:** dão nota baixa no estrutural, porque a construção mudou. A semântica e "Palavras idênticas" cobrem esse caso.
- **Primeira análise semântica:** baixa o modelo e precisa de internet.
