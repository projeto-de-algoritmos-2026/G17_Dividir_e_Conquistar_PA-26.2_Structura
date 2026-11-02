from pathlib import Path

import numpy as np
import pytest

from backend.core.analises import semantica
from backend.core.analises.comum import Segmento, TextoGrandeDemais
from backend.core.analises.semantica import (
    FOLGA_GERAL, LIMIAR_JANELA, MAX_FRASES, PASTA_MODELOS, PISO_JANELA, ModeloIndisponivel, analisar_semantica as S,
    conteudo_da_frase, contar_frases_literais, escalar_ideia_geral, juntar_notas, juntar_vizinhas, separar_frases,
    sobreposicao_palavras, somar_janelas,
)
from tests import corpus as C
from tests.conftest import metricas

def seg(texto):
    return Segmento(texto, 0, len(texto))

def resultado_frases(cobertura=0.0, original=0.0, ordem=1.0, pares=0, originais=0):
    return {"cobertura": cobertura, "cobertura_original": original, "ordem": ordem, "n_pares": pares, "n_segmentos_originais": originais, "explicacao": "x"}

# ---- partes puras, sem o modelo

@pytest.mark.parametrize("similaridade,nota", [(0.0, 0), (0.3, 0), (0.7, 0.7), (1.0, 1.0), (-0.5, 0), (0.5, 0.5)])
def test_escala_da_ideia_geral(similaridade, nota):
    assert escalar_ideia_geral(similaridade) == pytest.approx(nota)

@pytest.mark.parametrize("geral", [0.5, 0.6, 0.8, 0.85, 1.0])
def test_mesmo_tema_sem_frases_em_comum_fica_baixo(geral):
    assert juntar_notas(resultado_frases(), geral)[0] <= FOLGA_GERAL

def test_ideia_geral_so_reforca():
    nota, frases, _ = juntar_notas(resultado_frases(cobertura=0.5, pares=1, originais=1), 0.9)
    assert frases == 0.5 and nota == pytest.approx(0.5 + FOLGA_GERAL)

def test_ideia_geral_baixa_nao_derruba_as_frases():
    assert juntar_notas(resultado_frases(cobertura=0.8, pares=3, originais=3), 0.1)[0] == 0.8

@pytest.mark.parametrize("originais,conta", [(1, False), (2, False), (3, True), (10, True)])
def test_original_aproveitado_exige_frases_suficientes(originais, conta):
    nota = juntar_notas(resultado_frases(cobertura=0.1, original=1.0, pares=originais, originais=originais), 0.0)[0]
    assert (nota > 0.5) is conta

def test_ordem_invertida_tira_no_maximo_quinze_por_cento():
    assert juntar_notas(resultado_frases(cobertura=1.0, ordem=0.0, pares=3, originais=3), 0.0)[0] == 0.85

def test_janela_exige_limiar_e_piso():
    base = np.array([[0.5], [0.5]])
    assert somar_janelas(base, np.array([[LIMIAR_JANELA]])).tolist() == [[LIMIAR_JANELA], [LIMIAR_JANELA]]
    assert somar_janelas(base, np.array([[LIMIAR_JANELA - 0.01]])).tolist() == [[0.5], [0.5]]
    fraca = np.array([[PISO_JANELA - 0.01], [0.5]])
    assert somar_janelas(fraca, np.array([[0.9]])).tolist() == [[PISO_JANELA - 0.01], [0.9]]

def test_janela_nunca_reduz_similaridade():
    base = np.array([[0.9, 0.2], [0.4, 0.8], [0.1, 0.3]])
    assert (somar_janelas(base, np.full((2, 2), 0.75)) >= base).all()

def test_juntar_vizinhas():
    frases = [Segmento("a", 0, 1), Segmento("b", 2, 3), Segmento("c", 4, 5)]
    assert juntar_vizinhas(frases) == [Segmento("a b", 0, 3), Segmento("b c", 2, 5)]
    assert juntar_vizinhas(frases[:1]) == []

def test_dice_entre_frases():
    a, b = conteudo_da_frase(seg("gato preto")), conteudo_da_frase(seg("gato branco"))
    assert sobreposicao_palavras(a, a) == 1.0
    assert sobreposicao_palavras(a, b) == 0.5

def test_negacao_em_um_lado_anula_o_reforco():
    assert sobreposicao_palavras(conteudo_da_frase(seg("Eu não amo gatos.")), conteudo_da_frase(seg("Eu amo gatos."))) == 0.0

def test_negacao_nos_dois_lados_mantem_o_reforco():
    assert sobreposicao_palavras(conteudo_da_frase(seg("Não amo gatos.")), conteudo_da_frase(seg("Nunca amo gatos."))) > 0

def test_frases_literais_exigem_tamanho():
    curta, longa = "Bom dia a todos.", "A leitura desenvolve o pensamento crítico dos estudantes."
    assert contar_frases_literais([seg(curta)], [seg(curta)]) == 0
    assert contar_frases_literais([seg(longa)], [seg(longa.upper())]) == 1

def test_modelo_fica_fora_da_pasta_temporaria():
    assert PASTA_MODELOS == Path(__file__).resolve().parent.parent / ".cache" / "modelos"

def test_falha_ao_carregar_modelo_vira_erro_claro(monkeypatch):
    semantica.carregar_modelo.cache_clear()
    def falhar(*_, **__):
        raise OSError("sem rede")
    monkeypatch.setattr(semantica, "TextEmbedding", falhar)
    with pytest.raises(ModeloIndisponivel):
        semantica.carregar_modelo()
    semantica.carregar_modelo.cache_clear()

def test_frases_demais_sao_recusadas_sem_gastar_tempo_no_modelo(monkeypatch):
    monkeypatch.setattr(semantica, "vetorizar", lambda *_: pytest.fail("não deveria vetorizar"))
    with pytest.raises(TextoGrandeDemais):
        S("Frase. " * (MAX_FRASES + 1), "Texto curto.")

@pytest.mark.parametrize("a,b", [("", ""), ("texto", ""), ("", "texto"), ("...", "!!!"), ("😀", "😀")])
def test_sem_conteudo_nao_usa_modelo(a, b, monkeypatch):
    monkeypatch.setattr(semantica, "vetorizar", lambda *_: pytest.fail("não deveria vetorizar"))
    assert S(a, b)["nota"] is None

def test_quantas_frases_o_limite_cobre():
    assert len(separar_frases("Frase qualquer aqui. " * MAX_FRASES)) == MAX_FRASES

# ---- com o modelo

@pytest.mark.modelo
class TestComModelo:
    def test_hierarquia_das_notas(self):
        copia = S(C.CLIMA, C.CLIMA)["nota"]
        parafrase = S(C.CLIMA, C.CLIMA_PARAFRASE)["nota"]
        mesmo_tema = S(C.CLIMA, C.CLIMA_AUTOR_2)["nota"]
        outro_tema = S(C.CLIMA, C.BALEIAS)["nota"]
        assert copia > parafrase > mesmo_tema > outro_tema

    @pytest.mark.parametrize("a,b", [
        (C.CLIMA, C.CLIMA_AUTOR_2), (C.CLIMA, C.CLIMA_AUTOR_3), (C.CLIMA_AUTOR_2, C.CLIMA_AUTOR_3),
        (C.EDUCACAO_1, C.EDUCACAO_2), (C.EDUCACAO_1, C.EDUCACAO_3), (C.EDUCACAO_2, C.EDUCACAO_3), (C.REDES_1, C.REDES_2),
    ])
    def test_autores_independentes_ficam_longe_da_parafrase(self, a, b):
        assert S(C.CLIMA, C.CLIMA_PARAFRASE)["nota"] - S(a, b)["nota"] >= 0.35

    def test_mesmo_tema_sem_frases_avisa_que_pode_ser_so_o_tema(self):
        resultado = S(C.CLIMA, C.CLIMA_AUTOR_2)
        assert "mesmo tema" in resultado["explicacao"]

    def test_ordem_entra_na_medida_e_nao_derruba_a_copia(self):
        frases = [C.LEITURA_F1, C.LEITURA_F2, C.LEITURA_F3]
        em_ordem = S(C.LEITURA, " ".join(frases))
        invertida = S(C.LEITURA, " ".join(reversed(frases)))
        assert metricas(em_ordem)["Ordem"] == "100%" and metricas(invertida)["Ordem"] == "0%"
        assert metricas(invertida)["Cobertura do suspeito"] == "100%"
        assert invertida["nota"] >= 0.85

    def test_ordem_pesa_quando_a_ideia_geral_nao_decide(self):
        frases = [f.strip() + "." for f in C.LEITURA_PARAFRASE.split(".") if f.strip()]
        original = S(C.LEITURA, " ".join(frases))
        invertida = S(C.LEITURA, " ".join(reversed(frases)))
        assert metricas(invertida)["Ordem"] == "0%" and metricas(original)["Ordem"] == "100%"

    def test_nenhuma_frase_e_sacrificada_em_cópia_reordenada(self):
        resultado = S(C.LEITURA, f"{C.LEITURA_F3} {C.LEITURA_F1} {C.LEITURA_F2}")
        assert {p["nota"] for p in resultado["pares"]} == {1.0}

    def test_enchimento_nao_esconde_cópia(self):
        for vezes in (1, 2, 3, 5, 10):
            suspeito = f"{C.LEITURA} {' '.join(C.ENCHIMENTO * vezes)}"
            resultado = S(C.LEITURA, suspeito)
            assert resultado["faixa"] == "alta", vezes
            assert metricas(resultado)["Original aproveitado"] == "100%"
            assert "material novo" in resultado["explicacao"]

    def test_frase_literal_em_texto_longo_gera_aviso(self):
        resultado = S(C.LEITURA, f"{C.TEXTO_LONGO_NOVO} {C.LEITURA_F2}")
        assert resultado["faixa"] == "baixa"
        assert any("idênticas ao original" in aviso for aviso in resultado["avisos"])

    def test_texto_sem_copia_nao_tem_aviso_de_literal(self):
        assert not any("idênticas" in a for a in S(C.LEITURA, C.LEITURA_PARAFRASE)["avisos"])

    def test_destaque_nao_cobre_frase_sem_par(self):
        x, y, z = "A leitura desenvolve o pensamento crítico.", "O futebol movimenta bilhões de reais por ano.", "Bibliotecas públicas ampliam o acesso aos livros."
        novo = "A feijoada é servida com arroz e couve."
        suspeito = f"{x} {novo} {z}"
        resultado = S(f"{x} {y} {z}", suspeito)
        destacado = [suspeito[t["inicio_b"]:t["fim_b"]] for t in resultado["trechos"]]
        assert destacado == [x, z]

    def test_frase_exata_ganha_da_parecida(self):
        exata = "As bibliotecas públicas ampliam o acesso aos livros nas comunidades."
        parecida = "As bibliotecas públicas ampliam o acesso às obras em comunidades carentes."
        for original in (f"{exata} {parecida}", f"{parecida} {exata}"):
            resultado = S(original, exata)
            assert resultado["nota"] == 1.0 and resultado["pares"][0]["texto_a"] == exata

    def test_frase_repetida_vem_do_original(self):
        assert S(C.LEITURA_F1, " ".join([C.LEITURA_F1] * 3))["nota"] == 1.0

    def test_fim_de_frase_longa_conta(self):
        diferente = S(f"{C.INICIO_COMUM} {C.FIM_ECONOMIA}", f"{C.INICIO_COMUM} {C.FIM_XADREZ}")
        assert diferente["nota"] < 0.8
        assert S(f"{C.FIM_XADREZ} {C.INICIO_COMUM}", f"{C.FIM_ECONOMIA} {C.INICIO_COMUM}")["nota"] > 0.25

    def test_citacao_curta_nao_muda_a_nota_e_avisa(self):
        sem = S(C.LEITURA, C.BALEIAS)
        com = S(C.LEITURA, f'{C.BALEIAS} Segundo o autor, "{C.LEITURA_F2[:-1]}".')
        assert com["nota"] <= sem["nota"] + 0.05
        assert any("fora da análise" in aviso for aviso in com["avisos"])

    def test_nota_vem_com_metricas_completas(self):
        assert set(metricas(S(C.CLIMA, C.CLIMA))) == {"Ideia geral", "Cobertura do suspeito", "Original aproveitado", "Ordem", "Blocos", "Inversões", "Frases em comum"}

    def test_mesma_entrada_mesma_nota(self):
        assert S(C.CLIMA, C.CLIMA_PARAFRASE) == S(C.CLIMA, C.CLIMA_PARAFRASE)

    def test_vazio_de_um_lado_com_modelo_carregado(self):
        assert S("...", C.CLIMA)["nota"] is None
