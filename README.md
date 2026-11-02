<h1><font size="6"><b>Detector de Similaridade</b></font><br></h1>
<h3><b>Número da Lista:</b> 17<br></h3>
<h3><i>Conteúdo da disciplina:</i> Dividir e Conquistar<br></h3>
<h3>Alunos</h3>

| Matrícula | Aluno |
|-----------|----------------------------------|
| 251013660 | Matheus Moretti Soares           |
| 251019771 | Daniel Filipe Borges de Oliveira |

---

## Sobre
O **Detector de Similaridade** é uma ferramenta web que aponta indícios de plágio entre dois textos, em dois modos:

- **Estrutural:** mede se os textos são construídos do mesmo jeito, sem olhar o assunto. O resultado é uma similaridade.
- **Semântica:** procura ideias do original no texto suspeito, mesmo reescritas. O resultado é uma suspeita de plágio.

Os dois modos usam dividir e conquistar: **Hirschberg** para alinhar as sequências e **Counting Inversions (Merge Sort modificado)** para medir o quanto a ordem mudou, o que entra na nota do modo semântico e aparece como métrica no estrutural. Detalhes em [docs/algoritmos.md](docs/algoritmos.md), e resultados em [docs/testes.md](docs/testes.md).

## Screenshots

## Instalação

Linguagem: Python e JavaScript
Framework: FastAPI

<font size = "5">**Pré-requisitos:** </font>
- Python 3.12 ou superior instalado
- Git instalado

<font size = "5"> **Comandos necessários:**</font>

**1. Clone este repositório:**
```bash
git clone https://github.com/projeto-de-algoritmos-2026/G17_Dividir_e_Conquistar_PA-26.2.git

cd G17_Dividir_e_Conquistar_PA-26.2
```
**2. Crie e ative o ambiente virtual:**
```bash
python -m venv venv

# Ativar no Windows:
venv\Scripts\activate

# Ativar no Linux/Mac:
source venv/bin/activate
```

**3. Instale as dependências do backend:**
```bash
pip install -r backend/requirements.txt
```

## Uso
Com as dependências instaladas e o ambiente virtual ativo, inicie o servidor local executando:

```bash
uvicorn backend.main:app --reload
```

Após o servidor iniciar, acesse http://localhost:8000 no navegador.

A primeira análise semântica baixa o modelo de linguagem para `.cache/modelos` e, por isso, precisa de internet e demora mais. As seguintes funcionam offline.

## Testes
```bash
pip install -r backend/requirements-dev.txt
python -m pytest
```

Os resultados de cada caso e o que cada arquivo de teste verifica estão em [docs/testes.md](docs/testes.md).

## Outros
**Análise Algorítmica:** O núcleo matemático do projeto evita a contagem de força bruta $O(N^2)$ ao implementar o algoritmo de Merge Sort para a contagem de inversões. Isso reduz a contagem de inversões para $O(N \log N)$. O alinhamento de Hirschberg custa $O(NM)$ em tempo e $O(N+M)$ em espaço, por isso cada texto é limitado a 20.000 caracteres, 6.000 tokens no modo estrutural e 1.000 frases no semântico.

**Arquitetura e Escalabilidade:**
Em um detector de plágio em escala real, a integração de um Banco de Dados não visa criar "inteligência" (no sentido de Machine Learning), mas atuar como um Repositório de Base (Corpus) e um Otimizador de Performance.

O escopo atual do projeto opera como uma API stateless (sem estado): ela recebe o Texto A e o Texto B, compara os dois simultaneamente, devolve o resultado e descarta os dados. Com a adição de um banco de dados, a arquitetura se tornaria stateful (com estado), permitindo comparações de 1 para N. Dessa forma, um único texto suspeito seria contrastado contra milhares de documentos pré-processados e em cache, viabilizando o armazenamento do histórico de plágios.