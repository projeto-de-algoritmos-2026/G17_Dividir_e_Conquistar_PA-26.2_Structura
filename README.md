<h1><font size="6"><b>Structura</b></font><br></h1>
<h3><b>Número da Lista:</b> 17<br></h3>
<h3><i>Conteúdo da disciplina:</i> Dividir e Conquistar<br></h3>
<h3>Alunos</h3>

| Matrícula | Aluno |
|-----------|----------------------------------|
| 251013660 | Matheus Moretti Soares           |
| 251019771 | Daniel Filipe Borges de Oliveira |

---

## Sobre
O **Structura** é uma ferramenta web que atua como **Detector de Similaridade** apontando indícios de plágio entre dois textos, em dois modos:

- **Estrutural:** as frases foram construídas do mesmo jeito? Olha a classe gramatical das palavras, não o assunto.
- **Semântica:** as ideias vêm do original? Reconhece cópias reescritas com outras palavras.

Os dois modos usam **Hirschberg** para alinhar as frases e **Counting Inversions (Merge Sort modificado)** para medir o quanto a ordem mudou. O resultado orienta uma revisão humana e não prova plágio.

## Screenshots

## Instalação

**Linguagens:** Python e JavaScript · **Framework:** FastAPI · **Pré-requisitos:** Python 3.12+ e Git

```bash
git clone https://github.com/projeto-de-algoritmos-2026/G17_Dividir_e_Conquistar_PA-26.2_Structura.git
cd G17_Dividir_e_Conquistar_PA-26.2_Structura

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r backend/requirements.txt
```

## Uso
```bash
uvicorn backend.main:app --reload
```

Acesse http://localhost:8000. O front é servido pelo backend, então abrir o `index.html` direto não funciona.

A primeira análise semântica baixa o modelo de linguagem e precisa de internet. As seguintes funcionam offline.

## Testes
```bash
pip install -r backend/requirements-dev.txt
python -m pytest
```

## Outros
- [Infraestrutura](docs/infraestrutura.md): arquitetura, algoritmos, fórmulas, limites e testes.
- [Guia da apresentação](docs/guia-apresentacao.md): roteiro, explicações e perguntas prováveis.
