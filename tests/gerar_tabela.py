"""Refaz docs/testes.md a partir de tests/corpus.py: python -m tests.gerar_tabela"""
from pathlib import Path

from tests.conftest import ANALISADORES, metricas
from tests.corpus import CASOS, GRUPOS

DESTINO = Path(__file__).resolve().parent.parent / "docs" / "testes.md"

CABECALHO = """# Testes

Resultados de {total} casos rodados nos dois modos. Esta tabela é gerada por `python -m tests.gerar_tabela`, e os textos de cada caso estão em `tests/corpus.py`.

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
"""

def celula(resultado: dict) -> str:
    if resultado["nota"] is None:
        return "sem conteúdo"
    return f"{resultado['nota']:.0%} ({resultado['faixa']})"

def tabela_do_grupo(grupo: str) -> str:
    linhas = [f"## {GRUPOS[grupo]}\n", "| Caso | Estrutural | Semântica | Palavras idênticas |", "|---|---|---|---|"]
    for caso in (c for c in CASOS if c.grupo == grupo):
        estrutural = ANALISADORES["estrutural"](caso.a, caso.b)
        semantica = ANALISADORES["semantica"](caso.a, caso.b)
        identicas = metricas(estrutural).get("Palavras idênticas", "—")
        linhas.append(f"| {caso.nome} | {celula(estrutural)} | {celula(semantica)} | {identicas} |")
    return "\n".join(linhas)

def main() -> None:
    secoes = [CABECALHO.format(total=len(CASOS))] + [tabela_do_grupo(grupo) for grupo in GRUPOS]
    DESTINO.write_text("\n\n".join(secoes) + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()
