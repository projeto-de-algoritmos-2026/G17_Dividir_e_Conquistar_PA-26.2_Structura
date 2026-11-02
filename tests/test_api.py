import pytest

from backend.core.analises import semantica
from backend.core.analises.estrutural import MAX_TOKENS
from backend.schemas.models import MAX_CARACTERES

def comparar(cliente, a, b, modo="estrutural"):
    return cliente.post("/api/comparar", json={"texto_a": a, "texto_b": b, "modo": modo})

def test_status(cliente):
    assert cliente.get("/api/status").json()["status"] == "ok"

def test_lista_de_modos(cliente):
    dados = cliente.get("/api/analises").json()
    assert [m["id"] for m in dados["modos"]] == ["estrutural", "semantica"]
    assert dados["max_caracteres"] == MAX_CARACTERES
    assert all(m["rotulo"] and m["descricao"] and "analisar" not in m for m in dados["modos"])

@pytest.mark.parametrize("caminho,tipo", [("/", "text/html"), ("/js/app.js", "javascript"), ("/js/api.js", "javascript"), ("/js/resultado.js", "javascript"), ("/css/tokens.css", "css"), ("/css/base.css", "css"), ("/css/componentes.css", "css")])
def test_frontend_servido(cliente, caminho, tipo):
    resposta = cliente.get(caminho)
    assert resposta.status_code == 200 and tipo in resposta.headers["content-type"]

@pytest.mark.parametrize("caminho", ["/../backend/main.py", "/..%2f..%2fetc/passwd", "/.env", "/backend/main.py"])
def test_fora_do_frontend_nao_sai(cliente, caminho):
    assert cliente.get(caminho).status_code == 404

def test_modo_desconhecido(cliente):
    resposta = comparar(cliente, "a", "b", "inexistente")
    assert resposta.status_code == 422 and resposta.json()["detail"] == "Modo de análise desconhecido."

def test_modo_padrao_e_estrutural(cliente):
    assert cliente.post("/api/comparar", json={"texto_a": "oi", "texto_b": "oi"}).json()["modo"] == "estrutural"

@pytest.mark.parametrize("corpo", [{}, {"texto_a": "a"}, {"texto_b": "a"}, {"texto_a": 1, "texto_b": 2}, {"texto_a": None, "texto_b": "a"}, {"texto_a": ["a"], "texto_b": "b"}])
def test_corpo_invalido(cliente, corpo):
    assert cliente.post("/api/comparar", json=corpo).status_code == 422

def test_json_quebrado(cliente):
    assert cliente.post("/api/comparar", content="{", headers={"content-type": "application/json"}).status_code == 422

@pytest.mark.parametrize("modo", ["estrutural", "semantica"])
def test_limite_exato_de_caracteres(cliente, modo):
    texto = "x" * MAX_CARACTERES
    assert comparar(cliente, texto, texto, modo).status_code == 200
    assert comparar(cliente, texto + "x", "a", modo).status_code == 422
    assert comparar(cliente, "a", texto + "x", modo).status_code == 422

def test_emoji_conta_um_caractere(cliente):
    assert comparar(cliente, "😀" * MAX_CARACTERES, "a").status_code == 200

@pytest.mark.parametrize("modo", ["estrutural", "semantica"])
@pytest.mark.parametrize("a,b", [("", ""), ("   ", "  "), ("...", "..."), ("a", ""), ("", "a")])
def test_entradas_vazias_respondem_sem_nota(cliente, modo, a, b):
    resposta = comparar(cliente, a, b, modo)
    assert resposta.status_code == 200 and resposta.json()["nota"] is None

def test_lista_de_numeros_nao_derruba_o_servidor(cliente):
    texto = " ".join(map(str, range(25)))
    resposta = comparar(cliente, texto, texto)
    assert resposta.status_code == 200 and resposta.json()["nota"] == 1.0

def test_texto_fragmentado_demais_explica_o_motivo(cliente):
    texto = "a. " * (MAX_TOKENS // 2 + 1)
    resposta = comparar(cliente, texto, "oi")
    assert resposta.status_code == 422 and "até 6.000" in resposta.json()["detail"]

def test_frases_demais_explicam_o_motivo(cliente):
    resposta = comparar(cliente, "Oi. " * 1001, "oi", "semantica")
    assert resposta.status_code == 422 and "1000 frases" in resposta.json()["detail"]

def test_modelo_indisponivel_responde_503(cliente, monkeypatch):
    def falhar(_):
        raise semantica.ModeloIndisponivel("Sem modelo.")
    monkeypatch.setattr(semantica, "vetorizar", falhar)
    resposta = comparar(cliente, "Oi.", "Oi.", "semantica")
    assert resposta.status_code == 503 and resposta.json()["detail"] == "Sem modelo."

@pytest.mark.parametrize("modo", ["estrutural", "semantica"])
def test_formato_da_resposta(cliente, modo):
    dados = comparar(cliente, "O rato roeu a roupa.", "O rato roeu a roupa.", modo).json()
    assert set(dados) == {"modo", "nota", "faixa", "titulo", "explicacao", "metricas", "legenda", "trechos", "pares", "avisos"}
    assert dados["modo"] == modo
