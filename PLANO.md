# Plano do projeto: Detector de Similaridade

**Como usar:** apague o que não quiser. O que sobrar é o que será feito.
Nas decisões, deixe só uma opção. Cada item tem um código (ex.: `DC3`) para facilitar a conversa.

**Legenda:** ⭐ recomendado · 🟢 simples · 🟡 médio · 🔴 trabalhoso · ⚠️ mexe em código do Matheus

---

## 1. Diagnóstico

### Estado atual

- Backend em FastAPI com uma rota (`POST /api/comparar`) e frontend em HTML, CSS e JS puros.
- Único algoritmo de D&C: Counting Inversions com merge sort. **A implementação está correta.**
- Sem testes, sem linter, sem `CLAUDE.md` e com README incompleto (`Nome Projeto`, screenshots vazios).

### Atenção: todo o código atual é do Matheus

O autor `Boynic3` dos commits usa o e-mail `matheusmorettisoares@gmail.com`. Assim, os 8 arquivos de código
são dele, e **qualquer mudança neles depende da sua autorização** (seção 2).

### Problemas confirmados rodando o código atual

| Caso testado                                                | Resultado atual        | Esperado    |
|-------------------------------------------------------------|------------------------|-------------|
| Textos sem nenhuma palavra em comum                         | **100%**               | 0%          |
| Só 1 palavra em comum                                       | **100%**               | ~0%         |
| Texto B com apenas 2 palavras de A                          | **100%**               | baixo       |
| B = "gato gato gato gato gato"                              | **100%**               | baixo       |
| Textos **idênticos** com palavras repetidas (`a b a b a b`) | **80%**                | 100%        |
| Texto com as duas metades trocadas (cópia integral)         | 46,67%                 | alto        |
| Texto de 4 palavras contra um de 9                          | 100% nos dois sentidos | diferenciar |

**Três causas:**

1. **O sistema só mede ordem, não quantidade.** Ele ignora quanto do texto é comum, e por isso poucas palavras em
   ordem já resultam em 100%. O retorno fixo de `1.0` quando há 0 ou 1 palavra em comum agrava o problema.
2. **Palavras repetidas apontam para a primeira ocorrência** (`mapa_ordem` guarda só o primeiro índice), o que gera
   empates e inversões falsas.
3. **Mover um bloco inteiro é punido como desordem total**, embora seja uma técnica comum de plágio.

### Problemas menores

- Texto de tamanho ilimitado na API.
- URL do backend fixa no JS.
- `allow_origins=["*"]` junto com `allow_credentials=True`.
- `.idea/` fora do `.gitignore`.
- `opentelemetry-api` no `requirements.txt` sem uso aparente.
- Comentário "HashMap conta frequência" incorreto: o mapa guarda posição, não frequência.

---

## 2. Permissões sobre o código do Matheus

Apague as linhas que **não** autoriza. O item removido segue a alternativa indicada.

| ID    | Arquivo                                       | Mudança                                                                       | Se não autorizar                                                              |
|-------|-----------------------------------------------|-------------------------------------------------------------------------------|-------------------------------------------------------------------------------|
| P1 ⚠️ | `backend/core/algoritmos.py`                  | Nada. Os itens novos ficam em arquivos novos e reutilizam `ContadorInversoes` | Já é o padrão ⭐                                                               |
| P2 ⚠️ | `backend/core/algoritmos.py`                  | Corrigir ali os bugs de `MapeadorPermutacao` e `AnalisadorSimilaridade`       | Correções em arquivo novo; o antigo fica sem uso                              |
| P3 ⚠️ | `backend/schemas/models.py`                   | Adicionar o campo `modo`                                                      | Novo arquivo de schemas                                                       |
| P4 ⚠️ | `backend/api/routes.py`                       | Encaminhar `/comparar` para o modo escolhido                                  | Rota nova; `/comparar` continua com bugs                                      |
| P5 ⚠️ | `backend/main.py`                             | Registrar rotas novas, servir o frontend e ajustar CORS                       | Sem isso, nenhuma rota nova funciona: **precisamos ao menos de 1 linha aqui** |
| P6 ⚠️ | `frontend/*`                                  | Reescrever o visual nos próprios arquivos                                     | Front novo em outra pasta e o antigo mantido                                  |
| P7 ⚠️ | `README.md`, `.gitignore`, `requirements.txt` | Completar e corrigir                                                          | Ficam como estão                                                              |

**Recomendação:** não tocar em `algoritmos.py` (P1) e autorizar P3, P4, P5, P6 e P7.

---

## 3. Decisões gerais

**D1. Nome do produto**
- [ ] Manter "Detector de Similaridade Estrutural"

**D2. O que a nota principal mede**

- [ ] ⭐ Nota com dois componentes visíveis, **cobertura** (quanto é comum) e **ordem** (quão preservada)

**D3. Fórmula da nota final**

- [ ] ⭐ `cobertura × (0,5 + 0,5 × ordem)`: sem cobertura a nota é zero; texto reordenado ainda pontua


**D4. Direção da comparação**

- [ ] ⭐ Assimétrica: "quanto do **suspeito** vem do original". É o sentido natural de plágio

**D5. Tom do resultado**

- [ ] ⭐ Falar em "indício", com faixas baixa/moderada/alta, nunca "é plágio"


**D6. Idioma**

- [ ] ⭐ Só português no início, com stopwords e radicalização próprias

**D7. Estilo de código**

- [ ] ⭐ Nomes em português, como já está no projeto
- [ ] ⭐ Funções puras para algoritmos novos; classes só onde houver estado
- [ ] ⭐ Comentários só no porquê e na complexidade de cada algoritmo

**D8. Git**
- [ ] ⭐ Commits como os atuais (`feat: adiciona ...`)
- [ ] Commits diretos na `develop`

---

## 4. Análise estrutural aprimorada

Pipeline proposto, comum aos dois modos:

```
Segmentar → Comparar → Alinhar (D&C) → Medir ordem (D&C) → Localizar trechos (D&C) → Pontuar
```

- [ ] **E1** ⭐🟢 **Cobertura na nota.** Corrige os falsos 100%.
- [ ] **E2** ⭐🟢 **Tratar casos sem base de comparação.** 0 ou 1 palavra em comum deixa de valer 100%.
- [ ] **E3** ⭐🟢 **k-ésima ocorrência ↔ k-ésima ocorrência.** Gera uma permutação real e corrige o caso dos idênticos em 80%.
- [ ] **E4** ⭐🟢 **Remover stopwords** ("de", "a", "que"), que inflam a coincidência.
- [ ] **E5** ⭐🟢 **Normalizar acentos e maiúsculas.**
- [ ] **E6** 🟢 **Radicalização** (RSLP): "correu" e "correndo" contam como a mesma palavra.
- [ ] **E7** ⭐🟡 **Inversões por blocos**, para que trocar duas metades conte como pouca desordem. Depende de `DC1`.
- [ ] **E8** ⭐🟡 **Inversões significativas**, que ignoram trocas locais pequenas. Ver `DC2`.
- [ ] **E10** 🟢 **n-gramas** (pares ou trios de palavras) como unidade de comparação.
- [ ] **E12** 🟢 **Comparação em múltiplos níveis**: palavra, frase e parágrafo, com nota para cada um.

---

## 5. Mais dividir e conquistar

Cada algoritmo deve responder a uma pergunta real do produto, para o D&C não virar enfeite.

### Núcleo recomendado

- [ ] **DC1** ⭐🟡 **Hirschberg (LCS com espaço linear).** *"Quais palavras correspondem a quais?"*
  Divide A ao meio, acha o ponto de corte ótimo em B e recursa. `O(nm)` em tempo e `O(n+m)` em espaço.
  **É a peça central:** gera o alinhamento usado por `E7`, pelo destaque colorido e pelo modo semântico.
  Medido em Python puro: 500 palavras em 0,03s, 2.000 em 0,5s e 5.000 em 3,3s.
- [ ] **DC2** ⭐🟢 **Counting Significant Inversions.** *"Essa troca é relevante?"*
  Conta pares com `a[i] > a[j] + d`, com ponteiros extras no merge. `O(n log n)`.
  Exercício clássico do Kleinberg-Tardos e extensão direta do código do Matheus.


### Boas extensões

- [ ] **DC5** 🟡 **mediana das medianas.** *"Quais são as k frases mais parecidas?"* `O(n)`, sem ordenar tudo.
- [ ] **DC6** 🟡 **Árvore de Merkle do documento.** *"Quais seções são idênticas?"* Hash recursivo por seção; compara o topo e só desce onde difere.
- [ ] **DC8** 🟢 **Skyline.** *"Como unir trechos sobrepostos?"* Une, por D&C, os intervalos achados pelos outros algoritmos em um perfil de cobertura.


---

## 6. Análise semântica

O modo estrutural pergunta **"copiou e reorganizou?"**; o semântico pergunta **"disse o mesmo com outras palavras?"**

**Ideia central:** os dois modos usam o **mesmo pipeline D&C**. Mudam a unidade (palavra ou frase) e o comparador
(igualdade ou similaridade de significado). Hirschberg alinha frases, e o Counting Inversions mede a ordem das ideias.
Assim, o modo semântico também fica dentro do tema da disciplina.

**D9. Como medir significado**

- [ ] ⭐🟡 **S1. Embeddings locais** (`fastembed` com modelo multilíngue): capta paráfrases de verdade, roda offline após baixar o modelo e dispensa PyTorch.
  Risco: a compatibilidade com o seu Python 3.14 **ainda não foi testada**; será o primeiro passo.
-
**Melhorias**

- [ ] **S6** ⭐🟢 Mostrar **pares de frases correspondentes** lado a lado, com a nota de cada par.
- [ ] **S7** ⭐🟢 **Limiar ajustável** do que conta como frase equivalente (padrão a calibrar com `Q3`).
---

## 7. Frontend

### Direção visual

Papel, tinta e vermelho envelhecido, como um manuscrito revisado à mão: elegante e pouco saturado, sem cara de painel genérico.

**D10. Paleta**

- [ ] ⭐ **Rosa-terracota** (contrastes abaixo já calculados; todos passam no AA, de 4,5:1):

| Token           | Cor       | Uso                | Contraste              |
|-----------------|-----------|--------------------|------------------------|
| `--papel`       | `#FBF6F2` | Fundo              |                        |
| `--tinta`       | `#3B2A2B` | Texto              | 12,6:1 sobre papel     |
| `--tinta-suave` | `#6F5A5A` | Texto secundário   | 5,9:1 sobre papel      |
| `--vermelho`    | `#9C4A4F` | Botões e destaques | 6,0:1 com texto branco |
| `--rosa`        | `#F3DAD6` | Trechos marcados   | 10,2:1 com `--tinta`   |
| `--vinho`       | `#7A3338` | Texto sobre rosa   | 6,7:1                  |


**D11. Fontes** (Google Fonts)

- [ ] **Cormorant Garamond** e **Lato**: mais clássico

**D12. Tema**

- [ ] Só claro

**D13. Forma**

- [ ] ⭐ Cantos pouco arredondados, linhas finas e quase sem sombra


### Layout proposto

```
 Cotejo                                                  ☾
 Compare dois textos e veja o que foi copiado.

 ┌ Tipo de análise ───────────────────────────────┐
 │ [ Estrutural ]   Semântica                     │
 │ Procura cópia e reorganização de palavras.     │
 └────────────────────────────────────────────────┘

 ┌ Texto original ──────┐  ┌ Texto suspeito ──────┐
 │                      │  │                      │
 └──────────────────────┘  └──────────────────────┘
                                  [ Analisar textos ]

 72%   Indício moderado
 Cobertura 81%  ·  Ordem 64%  ·  3 blocos  ·  124 palavras

 ┌ Original ─────────────┐  ┌ Suspeito ────────────┐
 │ texto com trechos     │  │ texto com trechos    │
 │ destacados            │  │ destacados           │
 └───────────────────────┘  └──────────────────────┘
```

### Botão de escolha

- [ ] **U1** ⭐🟢 **Controle segmentado Estrutural/Semântica**, com uma frase explicando o modo escolhido. Acessível por teclado.

### Fácil de escalar

- [ ] **U4** ⭐🟢 **Sem framework e sem build:** HTML, CSS e módulos JS puros.

```js
export const ANALISES = [
  { id: "estrutural", rotulo: "Estrutural", descricao: "Procura cópia e reorganização de palavras." },
  { id: "semantica", rotulo: "Semântica", descricao: "Procura ideias iguais com outras palavras." },
];
```

- [ ] **U7** ⭐🟢 **Resultado genérico:** a API devolve nota, métricas e trechos, e a tela apenas desenha. Assim, métrica nova não exige mudar o front.
- [ ] **U8** ⭐🟢 **Arquivos curtos:** `api.js`, `analises.js`, `resultado.js`, `app.js`.

```
frontend/
├── index.html
├── css/  tokens.css  base.css  componentes.css
└── js/   app.js  api.js  analises.js  resultado.js
```

### Experiência

- [ ] **U9** ⭐🟢 Erros na própria página, no lugar de `alert()`.
- [ ] **U10** ⭐🟢 Layout responsivo para celular.
- [ ] **U11** ⭐🟢 Botão "usar exemplo" com textos prontos, útil na apresentação.
- [ ] **U12** 🟢 Contador de palavras nos campos de texto.
- [ ] **U13** ⭐🟢 Passar o mouse em um trecho destaca o correspondente no outro texto.
- [ ] **U14** 🟢 Nota animada ao aparecer.
- [ ] **U16** 🟢 Página "Como funciona", explicando os algoritmos.

---

## 8. Backend e arquitetura

- [ ] **B1** ⭐🟢 **Registro de análises:** um dicionário com um arquivo por análise.

```python
ANALISES = {"estrutural": analisar_estrutura, "semantica": analisar_semantica}
```

- [ ] **B2** ⭐🟢 **Formato único de resposta:**

```json
{
  "modo": "estrutural",
  "nota": 0.72,
  "faixa": "moderada",
  "metricas": [{ "rotulo": "Cobertura", "valor": 0.81 }],
  "trechos": [{ "inicio_a": 10, "fim_a": 42, "inicio_b": 3, "fim_b": 35 }]
}
```

- [ ] **B3** ⭐🟢 **Algoritmos isolados**, sem FastAPI, para testar e reaproveitar.

```
backend/core/
├── algoritmos.py            (Matheus, intacto)
├── dividir_conquistar/      hirschberg.py  fft.py  subarray.py  inversoes.py
└── analises/                registro.py  estrutural.py  semantica.py
```

- [ ] **B4** ⭐🟢 **Limite de tamanho do texto**, com mensagem clara (valor a definir pelos benchmarks).
- [ ] **B5** ⭐🟢 **Servir o frontend pelo FastAPI:** um comando sobe tudo em uma só porta, e a URL fixa no JS some.
- [ ] **B6** ⭐🟢 **CORS restrito** (fica desnecessário para o uso local com `B5`).
- [ ] **B7** 🟢 **Rota `GET /api/analises`**, para o front descobrir os modos disponíveis sozinho.
- [ ] **B8** 🟢 **Ajustar o `requirements.txt`**, removendo o que não é usado.

---

## 9. Novas funcionalidades


- [ ] **F5** ⭐🟢 **Explicação da nota em linguagem simples** ("81% das palavras vêm do original, mas em outra ordem").
- [ ] **F12** 🟢 **Ignorar citações** entre aspas e referências bibliográficas, reduzindo falsos positivos.

---

## 10. Qualidade, documentação e entrega

- [ ] **Q9** ⭐🟢 **Roteiro da apresentação**, com um exemplo por algoritmo.
- [ ] **Q10** 🟢 **`docs/algoritmos.md`** explicando cada algoritmo e sua recorrência (ex.: `T(n) = 2T(n/2) + O(n)`).

---

## 11. Ordem de execução

Cada fase fica utilizável sozinha. Se o tempo acabar, o que já foi feito continua funcionando.

| Fase | Entrega | Itens |
|---|---|---|
| **0. Preparação** | Permissões resolvidas e casos de teste escritos | Seção 2, `Q1`, `Q7`, `Q8` |
| **1. Base correta** | Notas confiáveis no modo estrutural | `B1`–`B3`, `E1`–`E5` |
| **2. Frontend novo** | Visual final com seletor de modos | `U1`, `U4`–`U11`, `B5` |
| **3. D&C central** | Alinhamento e trechos destacados | `DC1`–`DC3`, `E7`, `E8`, `F1`, `F4`, `F5`, `Q2` |
| **4. Semântica** | Segundo modo funcionando | D9, `S6`, `S7` |
| **5. Visualizações** | Recursos de impacto | `DC4`, `F2`, `F3`, `DC12`, `DC13`, `U13` |
| **6. Calibração** | Notas ajustadas e limites definidos | `Q3`, `Q4`, `B4` |
| **7. Entrega** | Projeto documentado | `Q6`, `Q9`, `Q10` |

**Prazo:** informe a data da entrega para eu definir onde cortar. As fases 0 a 4 são o mínimo para cumprir o que você pediu.

---

## 12. Espaço para seus comentários

**Data de entrega:**

**Algo que o Matheus precisa ver antes:**

**Outras preferências:**
