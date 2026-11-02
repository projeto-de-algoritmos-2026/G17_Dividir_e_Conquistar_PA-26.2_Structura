# Relatório do que foi feito

## Como rodar

```bash
source venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload
```

Acesse http://localhost:8000. O front agora é servido pelo backend, então não precisa mais de Live Server.

## Feito

**Análise estrutural**

- A nota agora combina cobertura e ordem: `cobertura × (0,5 + 0,5 × ordem)`, medindo quanto do suspeito vem do original (`E1`, `D2`–`D4`).
- Menos de 3 palavras em comum dá nota 0 (`E2`), e palavras soltas, fora de blocos de 2 ou mais, não contam na cobertura.
- Palavras repetidas são pareadas corretamente (`E3`, resolvido pelo alinhamento mais uma varredura).
- Stopwords são removidas, e acentos e maiúsculas são normalizados (`E4`, `E5`).
- Mover um bloco conta como pouca desordem, e trocas entre vizinhas são ignoradas (`E7`, `E8`).
- Citações entre aspas e a seção de referências ficam de fora (`F12`).

**Dividir e conquistar**

- Hirschberg (`DC1`).
- Counting Significant Inversions (`DC2`).
- O `ContadorInversoes` do Matheus continua em uso, sem alterações, na métrica "Inversões".

**Análise semântica**

- Embeddings locais com `fastembed`, usando o mesmo pipeline do modo estrutural (`S1`).
- Lista de frases equivalentes com a nota de cada par (`S6`).
- Controle de exigência na tela (`S7`).

**Frontend**

- Visual novo com a paleta rosa-terracota, Cormorant Garamond e Lato, tema claro e linhas finas.
- Seletor Estrutural/Semântica (`U1`), sem framework ou build (`U4`) e em arquivos curtos (`U8`).
- A tela desenha o que a API devolve (`U7`) e descobre os modos sozinha (`B7`).
- Erros na página (`U9`), layout para celular (`U10`), botão de exemplo (`U11`) e contador de palavras (`U12`).
- Passar o mouse destaca o trecho correspondente (`U13`), a nota é animada (`U14`) e há a seção "Como funciona" (`U16`).

**Backend**

- Registro de análises (`B1`), resposta única (`B2`) e algoritmos isolados do FastAPI (`B3`).
- Limite de 30.000 caracteres por texto (`B4`), front servido pelo FastAPI (`B5`) e CORS removido, por não ser mais necessário (`B6`).
- Explicação da nota em frase simples (`F5`).

**Documentação**

- README atualizado.
- `docs/algoritmos.md` (`Q10`) e `docs/apresentacao.md` (`Q9`).

**Tamanho:** 934 linhas no total, contando CSS e HTML, acima da estimativa inicial de 650.

## Cortado de propósito

| Item | Motivo |
|---|---|
| `DC5` Mediana das medianas | Com poucas frases, um `sorted` resolve; seria enfeite |
| `DC6` Árvore de Merkle | Só acha seções idênticas e alinhadas, o que o alinhamento já cobre |
| `DC8` Skyline | Os blocos não se sobrepõem, então não há o que unir |
| `E6` Radicalização | Exige dependência ou um radicalizador próprio |
| `E10` n-gramas | Duplicaria o que os blocos já fazem |
| `E12` Múltiplos níveis | Três notas confundiriam mais do que ajudariam |
| `analises.js` | Com `B7`, a API já informa os modos |
| `fft.py`, `subarray.py` | Você removeu `DC3` e `DC4` do plano |
| `B8` (parte) | `opentelemetry-api` **fica**: é dependência do FastAPI, ao contrário do que escrevi no plano |

## Mudanças no código do Matheus

Todas autorizadas na seção 2 do plano. **`backend/core/algoritmos.py` não foi alterado**, embora `P2` também tenha ficado no plano.

| Arquivo | Mudança |
|---|---|
| `backend/main.py` | Serve o frontend; CORS removido |
| `backend/api/routes.py` | `/comparar` usa o registro de modos; nova rota `/analises` |
| `backend/schemas/models.py` | Novos campos `modo` e `limiar`; limite de tamanho |
| `backend/requirements.txt` | Adicionados `fastembed` e `numpy` |
| `frontend/` | Reescrito; `css/style.css` foi substituído por três arquivos |
| `README.md` | Nome, descrição e uso atualizados |

**Mostre ao Matheus:**

- `/comparar` mudou de formato: agora devolve `nota`, `metricas` e `trechos`.
- `AnalisadorSimilaridade` e `MapeadorPermutacao` continuam no arquivo, mas não são mais usados.

## Resultados dos testes

| Caso | Antes | Agora |
|---|---|---|
| Sem palavras em comum | 100% | 0% |
| 1 palavra em comum | 100% | 0% |
| B com apenas 2 palavras de A | 100% | 0% |
| B = "gato gato gato gato gato" | 100% | 0% |
| Idênticos com repetição | 80% | 100% |
| Duas metades trocadas | 46,67% | 96,15% |
| Texto invertido | 0% | 0% (sem blocos em comum) |

- Hirschberg e inversões significativas bateram com a força bruta em 500 entradas aleatórias cada.
- Pior caso no limite de 30.000 caracteres, modo estrutural: cerca de 4 segundos.
- As telas de desktop e do modo semântico foram conferidas no Firefox headless. No celular, o layout foi conferido antes da última correção visual.
- Não há testes no repositório, pois `Q1` saiu do plano. As verificações foram feitas com scripts temporários.

## Limitações conhecidas

- **As faixas não foram calibradas.** Os cortes de 30% e 60%, o limiar de 70% e os mínimos de palavras são pontos de partida, pois `Q3` saiu do plano.
- **Redações autorais sobre o mesmo tema ainda pontuam no modo semântico:** 40% no teste, contra 18% no estrutural. Nenhum limiar separa isso totalmente de uma paráfrase.
- **O modo semântico não entende inversão de sentido:** "João ama Maria" e "Maria ama João" contam como equivalentes. Por isso vale olhar os dois modos juntos.
- **Palavras em ordem invertida, uma a uma, dão nota 0** no modo estrutural, porque não formam blocos.
- **Textos muito curtos no modo semântico são punidos com rigor na ordem:** trocar duas frases de um texto de duas frases dá nota 50%, porque a ordem cai a 0%.
- **A primeira análise semântica baixa o modelo** e precisa de internet; as seguintes funcionam offline.
- **A seção de referências** só é reconhecida quando uma linha começa com "Referências".
- **O hover do `U13` não foi exercitado** em navegador; só o desenho dos trechos foi conferido.
