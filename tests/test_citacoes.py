import pytest

from backend.core.analises.comum import MAX_PALAVRAS_CITACAO, avisos_citacoes, contar_palavras, ocultar_citacoes

TEXTO = " ".join(f"palavra{i}" for i in range(100))

def citar(trecho, aspas='"{}"'):
    return f"{TEXTO} {aspas.format(trecho)} {TEXTO}"

@pytest.mark.parametrize("aspas", ['"{}"', "“{}”", "«{}»"])
def test_citacao_curta_sai_da_analise(aspas):
    assert "segredo" not in ocultar_citacoes(citar("trecho segredo citado", aspas))

@pytest.mark.parametrize("texto", [TEXTO, citar("curta"), citar("x" * 10), "", "   ", "😀" * 5, 'a "b" c', "linha\n\noutra"])
def test_posicoes_preservadas(texto):
    assert len(ocultar_citacoes(texto)) == len(texto)

def test_citacao_no_limite_de_palavras():
    limite = " ".join(["segredo"] * MAX_PALAVRAS_CITACAO)
    assert "segredo" not in ocultar_citacoes(citar(limite))
    assert "segredo" in ocultar_citacoes(citar(limite + " segredo"))

@pytest.mark.parametrize("aspas", ['"{}"', "“{}”", "«{}»"])
def test_texto_inteiro_entre_aspas_continua_na_analise(aspas):
    texto = aspas.format("uma cópia integral de outro texto com várias palavras")
    assert "cópia" in ocultar_citacoes(texto)

def test_muitas_citacoes_curtas_nao_escondem_o_texto():
    texto = " ".join(f'"frase copiada numero {i}" a' for i in range(40))
    assert "copiada" in ocultar_citacoes(texto)

def test_ate_um_quarto_do_texto_pode_ser_citacao():
    assert "citado" not in ocultar_citacoes('"citado aqui" ' + " ".join(["livre"] * 6))
    assert "citado" in ocultar_citacoes('"citado aqui" ' + " ".join(["livre"] * 5))

@pytest.mark.parametrize("texto", [
    'A tela tem 5" de largura. Todo este trecho segue. O monitor de 7" é maior.',
    'Mede 5" e o resto do texto continua normalmente até o fim.',
    'Sem fechamento: "este trecho não termina',
    "Aspa isolada \" no meio do trecho",
])
def test_aspas_soltas_nao_apagam_texto(texto):
    assert ocultar_citacoes(texto) == texto

TITULOS = ["Referências", "REFERÊNCIAS", "Referencias", "Referências:", "  Referências  ", "Referências bibliográficas", "REFERÊNCIAS BIBLIOGRÁFICAS", "Bibliografia", "7. Referências", "7 Referências"]

@pytest.mark.parametrize("titulo", TITULOS)
def test_secao_de_referencias_no_fim_sai(titulo):
    resultado = ocultar_citacoes(f"{TEXTO}\n{titulo}\nSILVA, Segredo. Livro. 2020.")
    assert "Segredo" not in resultado and "palavra99" in resultado

@pytest.mark.parametrize("titulo", TITULOS)
def test_titulo_na_primeira_metade_nao_apaga_o_resto(titulo):
    assert ocultar_citacoes(f"{titulo}\n{TEXTO}") == f"{titulo}\n{TEXTO}"

@pytest.mark.parametrize("linha", [
    "Referências culturais moldam a identidade de um povo.",
    "Referências importantes sobre o tema.",
    "Referências aparecem em toda parte",
    "Bibliografia comentada do autor",
])
def test_frase_comum_nao_e_titulo(linha):
    texto = f"{TEXTO}\n{linha}\n{TEXTO}"
    assert ocultar_citacoes(texto) == texto

def test_citacao_dentro_das_referencias_nao_conta_no_limite():
    assert "citado" not in ocultar_citacoes(f'{TEXTO} "citado aqui" fim\nReferências\n"Livro um" e "Livro dois" e "Livro três".')

def test_aviso_informa_quanto_foi_ignorado():
    avisos = avisos_citacoes(TEXTO, citar("trecho citado curto"))
    assert len(avisos) == 1 and "suspeito" in avisos[0] and "%" in avisos[0]

def test_aviso_nos_dois_textos():
    assert len(avisos_citacoes(citar("citado"), citar("citado"))) == 2

def test_sem_citacoes_nao_ha_aviso():
    assert avisos_citacoes(TEXTO, TEXTO) == []

def test_aviso_de_citacao_recusada():
    avisos = avisos_citacoes(TEXTO, '"' + " ".join(["x"] * 100) + '"')
    assert any("foram analisadas" in aviso for aviso in avisos)

def test_palavras_ocultas_batem_com_a_contagem():
    texto = citar("um dois tres")
    assert contar_palavras(texto) - contar_palavras(ocultar_citacoes(texto)) == 3
