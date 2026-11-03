import pytest

from backend.core.analises.comum import TextoGrandeDemais
import random
import unicodedata

from backend.core.analises.estrutural import (
    LIMIAR_CONSTRUCAO,
    MAX_TOKENS,
    MAX_TOKENS_FRASE,
    MIN_TOKENS_CONFIAVEL,
    ProcessadorEstruturalLeve,
    analisar_estrutura,
    extrair_palavras,
    limiar_do_par,
)
from tests.conftest import metricas
from tests import corpus

NUMEROS = " ".join(map(str, range(25)))

@pytest.mark.parametrize("a,b,nota", [
    (NUMEROS, NUMEROS, 1.0),
    ("gato " * 25, "gato " * 25, 1.0),
    ("gato " * 25, "cama " * 25, 1.0),
    ("casa bola mesa pato rio sol " * 5, "lua mar flor cama copo " * 6, 1.0),
    ("1 " * 15, "2 " * 25, 0.75),
    ("1 " * 25, "2 " * 26, pytest.approx(0.98, abs=0.01)),
])
def test_categoria_unica_nao_quebra(a, b, nota):
    assert analisar_estrutura(a, b)["nota"] == nota

@pytest.mark.parametrize("n", [20, 21, 25, 50, 100, 500])
def test_listas_iguais_de_numeros_em_qualquer_tamanho(n):
    texto = " ".join(map(str, range(n)))
    assert analisar_estrutura(texto, texto)["nota"] == 1.0

def test_quase_categoria_unica_nao_quebra():
    #Duas categorias em que embaralhar quase nunca muda nada: o desconto chega perto de 1.
    a = "1 " * 39 + "casa"
    assert 0 <= analisar_estrutura(a, a)["nota"] <= 1

@pytest.mark.parametrize("a,b", [("Olá.", "Sim."), ("12", "99"), ("O rio secou.", "A lua brilha."), ("Socorro!", "Parabéns!")])
def test_frases_curtas_sao_inconclusivas(a, b):
    resultado = analisar_estrutura(a, b)
    assert resultado["faixa"] == "inconclusiva" and "inconclusiva" in resultado["titulo"]
    assert any("curto" in aviso for aviso in resultado["avisos"])

def test_limite_de_tamanho_confiavel():
    longo = "uma frase qualquer com palavras comuns e bastante extensa para passar do limite minimo de tokens agora aqui mesmo sem pressa"
    assert len(ProcessadorEstruturalLeve.extrair_estrutura(longo)) >= MIN_TOKENS_CONFIAVEL
    assert analisar_estrutura(longo, longo)["faixa"] == "alta"

@pytest.mark.parametrize("a,b", [("", ""), ("texto", ""), ("", "texto"), ("...", "!!!"), ("   ", "\n\n"), ("😀", "😀"), (". " * 25, "palavra")])
def test_sem_palavras_nao_vira_zero(a, b):
    assert analisar_estrutura(a, b)["nota"] is None

def test_tokens_demais_sao_recusados():
    texto = "a. " * (MAX_TOKENS // 2 + 1)
    with pytest.raises(TextoGrandeDemais):
        analisar_estrutura(texto, "texto curto")
    with pytest.raises(TextoGrandeDemais):
        analisar_estrutura("texto curto", texto)

F = ProcessadorEstruturalLeve

def nota(a, b):
    return analisar_estrutura(a, b)["nota"]

def tirar_acentos(texto):
    return "".join(c for c in unicodedata.normalize("NFD", texto) if not unicodedata.combining(c))

TEXTOS = [
    corpus.LEITURA, corpus.CLIMA, corpus.BALEIAS, corpus.REDES_2, corpus.MOLDE_POLICIA,
    corpus.MOLDE_CIENCIA, corpus.ESTILO_SUBORDINADO, corpus.ESTILO_DIALOGO, corpus.ESTILO_RECEITA,
]
PARES_DE_TEXTOS = [(a, b) for k, a in enumerate(TEXTOS) for b in TEXTOS[k + 1:]]

@pytest.mark.parametrize("a,b", PARES_DE_TEXTOS)
def test_nota_nao_depende_de_qual_texto_vem_primeiro(a, b):
    assert nota(a, b) == nota(b, a)

@pytest.mark.parametrize("texto", TEXTOS)
@pytest.mark.parametrize("transformar", [str.lower, str.upper, str.title, tirar_acentos], ids=["minusculas", "maiusculas", "titulo", "sem_acentos"])
def test_caixa_e_acento_nao_mudam_a_nota(texto, transformar):
    assert nota(texto, transformar(texto)) == 1.0

@pytest.mark.parametrize("texto", TEXTOS)
def test_quebra_de_linha_e_espacos_nao_mudam_a_nota(texto):
    assert nota(texto, texto.replace(" ", "  ").replace(". ", ".\n")) == 1.0

@pytest.mark.parametrize("a,b", [
    ("O menino comprou uma bola nova na loja.", "O ministro assinou uma lei nova no palácio."),
    ("O rei viu um rio.", "O imperador contemplou um desfiladeiro."),
    ("A casa é bonita.", "A universidade é extraordinária."),
    ("O sol nasceu cedo.", "O relâmpago apareceu rapidamente."),
])
def test_tamanho_da_palavra_nao_e_estrutura(a, b):
    assert nota(a, b) >= 0.9

def test_e_verbo_nao_equivale_a_e_conjuncao():
    assert F.extrair_estrutura("Ele é alto") != F.extrair_estrutura("Ele e alto")

def test_esta_verbo_nao_equivale_a_esta_pronome():
    assert F.extrair_estrutura("Ela está aqui") != F.extrair_estrutura("Ela esta aqui")

@pytest.mark.parametrize("k", [1, 2, 3, 4, 5])
def test_rotacionar_as_frases_mantem_a_construcao(k):
    frases = [corpus.MOLDE_POLICIA, corpus.MOLDE_JURIDICO, corpus.MOLDE_CIENCIA, corpus.MOLDE_NARRATIVA_1, corpus.LEITURA, corpus.CLIMA]
    assert nota(" ".join(frases), " ".join(frases[k:] + frases[:k])) >= 0.85

def test_reordenar_custa_pouco_mas_custa():
    original = f"{corpus.LEITURA_F1} {corpus.LEITURA_F2} {corpus.LEITURA_F3}"
    invertido = f"{corpus.LEITURA_F3} {corpus.LEITURA_F2} {corpus.LEITURA_F1}"
    assert 0.85 <= nota(original, invertido) < nota(original, original)

def test_inversoes_das_frases_aparecem_nas_metricas():
    invertido = f"{corpus.LEITURA_F3} {corpus.LEITURA_F2} {corpus.LEITURA_F1}"
    resultado = metricas(analisar_estrutura(corpus.LEITURA, invertido))
    assert resultado["Inversões"] == "3" and resultado["Ordem das frases"] != "100%"

def test_sem_frases_em_comum_a_ordem_nao_vira_zero():
    assert metricas(analisar_estrutura(corpus.ESTILO_LISTA, corpus.ESTILO_SUBORDINADO))["Ordem das frases"] == "—"

@pytest.mark.parametrize("n", [1, 3, 8, 20, 40])
def test_material_novo_nao_esconde_a_copia(n):
    assert nota(corpus.LEITURA, f"{corpus.LEITURA} {' '.join((corpus.ENCHIMENTO * 5)[:n])}") >= 0.9

@pytest.mark.parametrize("n", [1, 3, 8, 20, 40])
def test_material_novo_antes_da_copia_tambem_nao_esconde(n):
    assert nota(corpus.LEITURA, f"{' '.join((corpus.ENCHIMENTO * 5)[:n])} {corpus.LEITURA}") >= 0.9

def test_duas_frases_contidas_nao_bastam():
    #Com poucas frases, achar par em um texto grande acontece por acaso.
    a = f"{corpus.LEITURA_F1} {corpus.LEITURA_F2}"
    assert nota(a, f"{a} {corpus.SEM_RELACAO_LONGO} {corpus.CLIMA} {corpus.EDUCACAO_1}") < 0.6

def test_texto_pequeno_sem_relacao_com_texto_grande_fica_baixo():
    assert nota(corpus.FEIJOADA, " ".join([corpus.SEM_RELACAO_LONGO, corpus.CLIMA, corpus.EDUCACAO_2, corpus.REDES_2])) < 0.3

SINTAXE_PROPRIA = [
    "Mas quem, afinal, teria coragem de repetir aquilo tudo?",
    "Se você quiser, eu posso te ajudar com isso amanhã bem cedo.",
    "Chuva forte, ruas alagadas, trânsito parado, escolas fechadas, tudo igual!",
]

@pytest.mark.parametrize("n,minimo,maximo", [(0, 0, 0.1), (1, 0.2, 0.45), (2, 0.5, 0.75), (3, 0.95, 1)])
def test_nota_acompanha_a_parte_com_o_mesmo_molde(n, minimo, maximo):
    proprias = SINTAXE_PROPRIA
    assert minimo <= nota(corpus.MOLDE_POLICIA, " ".join(corpus._ESPORTE[:n] + proprias[n:])) <= maximo

def test_mais_frases_do_mesmo_molde_nunca_baixam_a_nota():
    proprias = SINTAXE_PROPRIA
    notas = [nota(corpus.MOLDE_POLICIA, " ".join(corpus._ESPORTE[:n] + proprias[n:])) for n in range(4)]
    assert notas == sorted(notas)

@pytest.mark.parametrize("a,b", [
    (corpus.ESTILO_TELEGRAFICO, corpus.ESTILO_SUBORDINADO),
    (corpus.ESTILO_DIALOGO, corpus.ESTILO_ACADEMICO),
    (corpus.ESTILO_LISTA, corpus.ESTILO_ACADEMICO),
    (corpus.ESTILO_RECEITA, corpus.ESTILO_SUBORDINADO),
    (corpus.CODIGO, corpus.ESTILO_ACADEMICO),
])
def test_estilos_diferentes_ficam_na_faixa_baixa(a, b):
    assert analisar_estrutura(a, b)["faixa"] in ("baixa", "inconclusiva") and nota(a, b) < 0.3

def test_frases_equivalentes_listam_a_construcao():
    resultado = analisar_estrutura(corpus.CONSTRUCAO_A, corpus.CONSTRUCAO_B)
    assert resultado["titulo_pares"] == "Frases com a mesma construção" and len(resultado["pares"]) == 3
    assert resultado["pares"][0]["texto_a"].startswith("O menino") and resultado["pares"][0]["texto_b"].startswith("O ministro")

def test_par_nunca_pede_acima_do_limite():
    assert all(limiar_do_par(n, n) < 1 for n in range(1, 8))

@pytest.mark.parametrize("menor,maior", [(5, 10), (10, 15), (15, 20)])
def test_frase_curta_exige_mais(menor, maior):
    assert limiar_do_par(menor, menor) > limiar_do_par(maior, maior)

@pytest.mark.parametrize("n", [20, 30, 100])
def test_frase_longa_usa_o_limiar_base(n):
    assert limiar_do_par(n, n) == LIMIAR_CONSTRUCAO

@pytest.mark.parametrize("texto,frases", [
    ("O dia acabou. A noite chegou.", 2),
    ("O dia acabou; a noite chegou: tudo mudou.", 3),
    ("O dia acabou... A noite chegou.", 2),
    ("O dia acabou?! A noite chegou.", 2),
    ("O dr. Silva chegou. Ela saiu.", 2),
    ("A nota é 7.5 hoje. Ela subiu.", 2),
    ("Título\n\nO texto começa aqui.", 2),
    ("linha um\nlinha dois", 1),
    ("... O dia acabou.", 1),
    ("sem pontuação nenhuma aqui", 1),
])
def test_divisao_em_construcoes(texto, frases):
    assert len(F.extrair_construcoes(texto)) == frases

def test_numero_com_separadores_e_um_token_so():
    assert F.extrair_estrutura("1.500,75") == ["NUMERO"]

def test_trecho_longo_sem_pontuacao_e_dividido():
    construcoes = F.extrair_construcoes(" ".join(["casa"] * (MAX_TOKENS_FRASE * 3 + 1)))
    assert len(construcoes) == 4 and all(len(c.formas) <= MAX_TOKENS_FRASE for c in construcoes)

def test_posicoes_das_construcoes_apontam_para_o_texto():
    texto = "O dia acabou. A noite chegou."
    assert [texto[c.inicio:c.fim] for c in F.extrair_construcoes(texto)] == ["O dia acabou.", "A noite chegou."]

@pytest.mark.parametrize("semente", range(20))
def test_trocar_palavras_por_outras_da_mesma_classe_preserva_a_nota(semente):
    gerador = random.Random(semente)
    nomes, verbos = ["casa", "rio", "ponte", "mesa", "festa"], ["comprou", "vendeu", "achou", "levou", "partiu"]
    gerar = lambda: " ".join(f"O {gerador.choice(nomes)} {gerador.choice(verbos)} a {gerador.choice(nomes)} do {gerador.choice(nomes)}." for _ in range(5))
    assert nota(gerar(), gerar()) == 1.0

def test_mesma_entrada_mesma_nota():
    assert analisar_estrutura(corpus.CLIMA, corpus.BALEIAS) == analisar_estrutura(corpus.CLIMA, corpus.BALEIAS)

def test_mesma_construcao_supera_construcao_diferente():
    parecidos = analisar_estrutura(corpus.CONSTRUCAO_A, corpus.CONSTRUCAO_B)["nota"]
    diferentes = analisar_estrutura(corpus.CONSTRUCAO_A, corpus.REDES_2)["nota"]
    assert parecidos > diferentes + 0.2

def test_palavras_identicas_ignoram_stopwords_e_grafia():
    assert metricas(analisar_estrutura("O Céu é Azul", "azul o CEU"))["Palavras idênticas"] == "2 de 2 (100%)"

def test_palavras_identicas_sao_medida_a_parte():
    resultado = metricas(analisar_estrutura(corpus.LEITURA, f"{corpus.LEITURA_F3} {corpus.LEITURA_F1} {corpus.LEITURA_F2}"))
    assert resultado["Palavras idênticas"].endswith("(100%)")

def test_trecho_literal_em_texto_longo_nao_passa_em_branco():
    resultado = analisar_estrutura(corpus.LEITURA, f"{corpus.TEXTO_LONGO_NOVO} {corpus.LEITURA_F2}")
    assert any("palavras idênticas seguidas" in aviso for aviso in resultado["avisos"])
    assert int(metricas(resultado)["Maior trecho idêntico"].split()[0]) >= 6

def test_sem_trecho_literal_nao_ha_aviso():
    assert not any("idênticas" in a for a in analisar_estrutura(corpus.CLIMA, corpus.BALEIAS)["avisos"])

def test_destaque_aponta_para_as_palavras():
    texto = corpus.LEITURA
    resultado = analisar_estrutura(texto, texto)
    trecho = resultado["trechos"][0]
    assert texto[trecho["inicio_a"]:trecho["fim_a"]].startswith("leitura")

def test_citacao_escondida_some_das_palavras():
    assert not [p for p in extrair_palavras('Texto livre e bem longo aqui mesmo "segredo" fim do texto.') if p.texto == "segredo"]
