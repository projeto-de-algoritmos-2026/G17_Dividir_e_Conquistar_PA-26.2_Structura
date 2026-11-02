from backend.core.analises.estrutural import analisar_estrutura
from backend.core.analises.semantica import analisar_semantica

#Para criar um modo novo, basta adicionar uma entrada: a API e a tela se ajustam sozinhas.
ANALISES = {
    "estrutural": {
        "rotulo": "Estrutural",
        "descricao": "Procura cópia e reorganização de palavras.",
        "usa_limiar": False,
        "analisar": analisar_estrutura,
    },
    "semantica": {
        "rotulo": "Semântica",
        "descricao": "Procura ideias iguais escritas com outras palavras.",
        "usa_limiar": True,
        "analisar": analisar_semantica,
    },
}
