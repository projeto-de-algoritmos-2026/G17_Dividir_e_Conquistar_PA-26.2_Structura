from backend.core.analises.estrutural import analisar_estrutura
from backend.core.analises.semantica import analisar_semantica

#Para criar um modo novo, basta adicionar uma entrada: a API e a tela se ajustam sozinhas.
ANALISES = {
    "estrutural": {
        "rotulo": "Estrutural",
        "descricao": "Mede se os textos são construídos do mesmo jeito, sem olhar o assunto.",
        "usa_limiar": False,
        "analisar": analisar_estrutura,
    },
    "semantica": {
        "rotulo": "Semântica",
        "descricao": "Procura plágio: ideias do original no texto suspeito, mesmo reescritas.",
        "usa_limiar": True,
        "analisar": analisar_semantica,
    },
}
