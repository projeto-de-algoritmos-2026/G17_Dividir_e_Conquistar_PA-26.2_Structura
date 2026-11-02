import pytest

from backend.core.analises.estrutural import ProcessadorEstruturalLeve
from backend.core.analises.gramatica import classificar_palavra, tem_acentos

def classe_em(frase: str, palavra: str) -> str:
    tokens = frase.split()
    formas = ProcessadorEstruturalLeve.extrair_estrutura(frase.replace(".", ""))
    return formas[tokens.index(palavra)]

@pytest.mark.parametrize("palavra,classe", [
    ("é", "VERBO"), ("e", "CONJUNCAO"), ("está", "VERBO"), ("esta", "PRONOME"), ("à", "PREPOSICAO"),
    ("às", "PREPOSICAO"), ("a", "ARTIGO"), ("as", "ARTIGO"), ("nós", "PRONOME"), ("nos", "PREPOSICAO"),
    ("pôr", "VERBO"), ("por", "PREPOSICAO"), ("há", "VERBO"), ("só", "ADVERBIO"), ("dá", "VERBO"), ("da", "PREPOSICAO"),
])
def test_acento_desfaz_ambiguidade(palavra, classe):
    assert classificar_palavra(palavra) == classe

@pytest.mark.parametrize("palavra", ["é", "está", "às", "nós", "pôr", "há"])
def test_sem_respeitar_acentos_vale_a_forma_sem_acento(palavra):
    assert classificar_palavra(palavra, False) == classificar_palavra(palavra.replace("é", "e").replace("á", "a").replace("à", "a").replace("ó", "o").replace("ô", "o"), False)

@pytest.mark.parametrize("palavra,classe", [
    ("comprou", "VERBO"), ("assinou", "VERBO"), ("vendeu", "VERBO"), ("partiu", "VERBO"), ("falaram", "VERBO"),
    ("correram", "VERBO"), ("partiram", "VERBO"), ("falavam", "VERBO"), ("falando", "VERBO"), ("correndo", "VERBO"),
    ("partindo", "VERBO"), ("comem", "VERBO"), ("cantam", "VERBO"), ("cantava", "VERBO"), ("cantarei", "VERBO"),
    ("falassem", "VERBO"), ("cantamos", "VERBO"), ("foi", "VERBO"), ("são", "VERBO"), ("tinha", "VERBO"),
    ("pode", "VERBO"), ("deve", "VERBO"), ("fazer", "VERBO"), ("seria", "VERBO"),
])
def test_verbos(palavra, classe):
    assert classificar_palavra(palavra) == classe

@pytest.mark.parametrize("palavra", [
    "mesa", "bola", "lei", "fábrica", "ministro", "menino", "cachorro", "construção", "liberdade",
    "pensamento", "racismo", "jornalista", "coragem", "beleza", "cultura", "ciência", "padeiro",
    "homem", "mulher", "lugar", "museu", "céu", "viagem", "trem", "nordeste", "semente",
])
def test_substantivos(palavra):
    assert classificar_palavra(palavra) == "SUBSTANTIVO"

@pytest.mark.parametrize("palavra", [
    "nova", "velha", "grande", "pequeno", "feliz", "azul", "famoso", "amável", "possível", "elétrico",
    "ativo", "nacional", "brasileira",
])
def test_adjetivos(palavra):
    assert classificar_palavra(palavra) == "ADJETIVO"

@pytest.mark.parametrize("palavra,classe", [
    ("rapidamente", "ADVERBIO"), ("hoje", "ADVERBIO"), ("muito", "ADVERBIO"), ("nunca", "NEGACAO"), ("não", "NEGACAO"),
    ("dois", "NUMERO"), ("mil", "NUMERO"), ("2026", "NUMERO"), ("3,14", "NUMERO"), ("1.500,75", "NUMERO"),
    ("todos", "PRONOME"), ("cada", "PRONOME"), ("que", "CONJUNCAO"), ("embora", "CONJUNCAO"), ("durante", "PREPOSICAO"),
])
def test_demais_classes(palavra, classe):
    assert classificar_palavra(palavra) == classe

@pytest.mark.parametrize("frase,palavra,classe", [
    ("o jantar acabou", "jantar", "SUBSTANTIVO"),
    ("vai jantar agora", "jantar", "VERBO"),
    ("o poder cresceu", "poder", "SUBSTANTIVO"),
    ("ele pode poder", "pode", "VERBO"),
    ("a comer bem", "comer", "VERBO"),
    ("uma ajuda boa", "ajuda", "SUBSTANTIVO"),
    ("ele ajuda muito", "ajuda", "VERBO"),
    ("o estudante chegou", "estudante", "SUBSTANTIVO"),
    ("a lei foi assinada", "assinada", "VERBO"),
    ("a lei assinada caiu", "assinada", "ADJETIVO"),
    ("o resultado saiu", "resultado", "SUBSTANTIVO"),
    ("ela dorme cedo", "dorme", "VERBO"),
    ("não corre aqui", "corre", "VERBO"),
    ("se move lentamente", "move", "VERBO"),
    ("de animais grandes", "animais", "SUBSTANTIVO"),
    ("o animal doente", "animal", "SUBSTANTIVO"),
    ("o gato dorme no sofá", "dorme", "VERBO"),
    ("a população brasileira cresceu", "brasileira", "ADJETIVO"),
    ("a economia nacional cresceu", "economia", "SUBSTANTIVO"),
])
def test_contexto_decide_a_classe(frase, palavra, classe):
    assert classe_em(frase, palavra) == classe

@pytest.mark.parametrize("texto,resposta", [("água", True), ("agua", False), ("é", True), ("e", False), ("", False), ("😀", False)])
def test_tem_acentos(texto, resposta):
    assert tem_acentos(texto) is resposta
