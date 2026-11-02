"""Classe gramatical aproximada de cada palavra, sem dependências: léxico, sufixos e contexto."""
import unicodedata

from backend.core.analises.comum import normalizar

ARTIGO = "ARTIGO"
PREPOSICAO = "PREPOSICAO"
CONJUNCAO = "CONJUNCAO"
PRONOME = "PRONOME"
NEGACAO = "NEGACAO"
VERBO = "VERBO"
ADVERBIO = "ADVERBIO"
SUBSTANTIVO = "SUBSTANTIVO"
ADJETIVO = "ADJETIVO"
NUMERO = "NUMERO"

#O acento desfaz ambiguidades que somem na forma normalizada: "é" × "e", "está" × "esta".
ACENTUADAS = {
    "é": VERBO, "está": VERBO, "estás": VERBO, "há": VERBO, "têm": VERBO, "vêm": VERBO,
    "dá": VERBO, "dê": VERBO, "pôr": VERBO, "pôde": VERBO, "às": PREPOSICAO, "à": PREPOSICAO,
    "nós": PRONOME, "só": ADVERBIO, "será": VERBO, "serão": VERBO, "estará": VERBO,
}

LEXICO = {
    ARTIGO: "a o as os um uma uns umas",
    PREPOSICAO: """de do da dos das em no na nos nas num numa nuns numas por pelo pela pelos pelas
        para pra com sem sobre sob entre ate ao aos desde contra apos ante perante durante mediante
        dum duma dele dela deles delas nele nela neles nelas deste desta destes destas desse dessa
        desses dessas neste nesta nestes nestas nesse nessa nesses nessas daquele daquela daqueles
        daquelas naquele naquela naqueles naquelas disso disto daquilo nisso nisto naquilo daqui dali
        conforme""",
    CONJUNCAO: """e ou mas porem pois porque que se como quando onde embora enquanto contudo
        todavia entretanto portanto logo caso conquanto nem tampouco""",
    PRONOME: """eu tu ele ela eles elas voce voces me te lhe lhes mim ti si comigo conosco consigo
        seu sua seus suas meu minha meus minhas teu tua teus tuas nosso nossa nossos nossas
        este esta estes estas esse essa esses essas aquele aquela aqueles aquelas isso isto aquilo
        todo toda todos todas cada outro outra outros outras muitos muitas varios varias algum
        alguma alguns algumas nenhum nenhuma mesmo mesma mesmos mesmas tal tais qual quais quem
        cujo cuja cujos cujas ambos ambas poucos poucas tantos tantas alguem ninguem tudo nada
        qualquer quaisquer certos certas diversos diversas demais""",
    NEGACAO: "nao nunca jamais",
    VERBO: """sao foi foram era eram seja sejam fosse fossem sendo sido ser sou somos fui
        estao estava estavam estive esteve estiveram esteja estar estando
        tem tinha tinham teve tiveram tenha tenham tendo ter tenho temos ha havia houve haja haver
        vai vao ia iam ir vou vamos indo pode podem podia podiam pude pudesse puderam poder podendo
        deve devem devia deviam dever faz fazem fez fizeram fazer fazendo fazia faziam diz dizem
        disse disseram dizer dizia dao deu deram dar dando ve veem viu viram ver vendo vem veio
        vieram vir sabe sabem soube saber quer querem quis quiseram querer fica ficam ficou ficaram
        ficar parece parecem passa passam leva levam traz trazem trouxe permite permitem existe
        existem precisa precisam consiste consistem inclui incluem possui possuem apresenta
        apresentam torna tornam move vive vivem ocorre ocorrem surge surgem cresce crescem
        muda mudam usa usam ajuda ajudam mostra mostram representa representam acontece acontecem
        significa significam varia variam seria seriam sera serao podera poderia poderiam deveria
        deveriam teria teriam haveria faria fariam iria feito dito visto posto aberto escrito
        conhecido conhecida conhecidos conhecidas chamado chamada chamados chamadas""",
    NUMERO: """zero dois duas tres quatro cinco seis sete oito nove dez onze doze treze catorze
        quatorze quinze dezesseis dezessete dezoito dezenove vinte trinta quarenta cinquenta
        sessenta setenta oitenta noventa cem cento duzentos trezentos quinhentos mil milhao milhoes
        bilhao bilhoes trilhao trilhoes""",
    ADVERBIO: """muito mais menos bem mal ja ainda sempre aqui ali la ca hoje ontem amanha agora
        depois antes tambem so apenas quase tao bastante assim entao talvez alem aproximadamente
        cerca acima abaixo atras adiante pouco tanto sim dentro fora perto longe devido apesar
        atraves junto quanto bem mal cedo depressa devagar""",
    ADJETIVO: """novo nova novos novas velho velha velhos velhas grande grandes pequeno pequena
        pequenos pequenas bom boa bons boas mau ma maus mas melhor melhores pior piores maior
        maiores menor menores alto alta altos altas baixo baixa baixos baixas forte fortes fraco
        fraca fracos fracas longo longa longos longas curto curta curtos curtas belo bela belos
        belas bonito bonita bonitos bonitas feio feia feios feias rico rica ricos ricas pobre pobres
        jovem jovens antigo antiga antigos antigas moderno moderna modernos modernas simples dificil
        dificeis facil faceis importante importantes principal principais primeiro primeira
        primeiros primeiras segundo segunda segundos segundas terceiro terceira ultimo ultima
        ultimos ultimas proximo proxima proximos proximas diferente diferentes igual iguais
        azul azuis verde verdes vermelho vermelha vermelhos vermelhas branco branca brancos brancas
        preto preta pretos pretas amarelo amarela amarelos amarelas cinza quente quentes frio fria
        frios frias feliz felizes triste tristes legal legais chato chata chatos chatas doce doces
        lindo linda lindos lindas forte largo larga largos largas pesado pesada leve leves rapido
        rapida rapidos rapidas lento lenta lentos lentas livre livres vivo viva vivos vivas morto
        morta mortos mortas certo certa errado errada verdadeiro verdadeira falso falsa puro pura
        seguinte seguintes nacional nacionais internacional internacionais social sociais
        unico unica unicos unicas comum comuns terrestre terrestres direto direta diretos diretas
        geral gerais natural naturais humano humana humanos humanas politico
        brasileiro brasileira brasileiros brasileiras europeu europeia europeus europeias
        portugues portuguesa americano americana americanos americanas""",
}

#Palavras que os sufixos de verbo e de adjetivo classificariam errado.
SUBSTANTIVOS = set("""
lugar mulher mulheres colher mar bar ar par jantar altar pilar acucar radar nectar polegar
carater cancer poder dever prazer ser homem homens viagem imagem ordem
origem margem garagem linguagem passagem vantagem mensagem personagem paisagem bagagem nuvem
museu trofeu pneu chapeu ceu reu estado lado mercado soldado resultado significado cuidado
mandado passado deputado senado vida partida comida saida ida bebida medida unidade cidade
partido sentido ruido tecido animal jornal hospital capital canal sinal metal material local
final total musica fisica republica tecnica politica critica fabrica clinica pratica informatica
matematica quimica economia familia historia dia via tia mania ideia energia tecnologia
biologia engenharia secretaria categoria maioria teoria companhia agua lingua sistema problema
tema programa clima planeta terra estudante presidente gente parte arte morte noite tarde
tipo modo caso fato ano anos tempo mundo corpo grupo povo paulo pedro maria joao brasil
trem armazem refem forma vez vezes semente mente aluno alunos professor autor ator doutor senhor
senhora setor motor valor cor dor amor sabor calor flor favor governo trabalho exemplo produto projeto objeto sujeito direito
""".split())

SUFIXOS_VERBO = (
    "aram", "eram", "iram", "avam", "ariam", "eriam", "iriam", "assem", "essem", "issem",
    "aremos", "eremos", "iremos", "amos", "emos", "imos", "ando", "endo", "indo", "ava",
)
SUFIXOS_ADJETIVO = (
    "oso", "osa", "osos", "osas", "avel", "aveis", "ivel", "iveis", "ico", "ica", "icos", "icas",
    "ivo", "iva", "ivos", "ivas", "ario", "aria", "arios", "arias", "ense", "enses", "ano", "ana",
    "anos", "anas", "ante", "antes", "ente", "entes", "al", "ais", "ar", "ares",
)
SUFIXOS_PARTICIPIO = ("ado", "ada", "ados", "adas", "ido", "ida", "idos", "idas")
SUFIXOS_SUBSTANTIVO = (
    "cao", "coes", "sao", "soes", "dade", "dades", "mento", "mentos", "ismo", "ismos", "ista",
    "istas", "agem", "agens", "igem", "ugem", "eza", "ezas", "ura", "uras", "ncia", "ncias",
    "eiro", "eira", "eiros", "eiras", "tor", "tores", "dor", "dores",
)

CLASSE_DA_PALAVRA = {p: classe for classe, palavras in LEXICO.items() for p in palavras.split()}
#Ambiguidades de léxico: quando a forma aparece em duas listas, vale a função mais frequente.
CLASSE_DA_PALAVRA.update({
    "ate": PREPOSICAO, "nos": PREPOSICAO, "mas": CONJUNCAO, "ma": ADJETIVO, "nada": PRONOME,
    "demais": PRONOME, "logo": ADVERBIO, "bem": ADVERBIO,
})

#Formas que abrem um sintagma nominal: o que vem depois delas é nome, não verbo.
DETERMINANTES = set("""
o os um uma uns umas do da dos das no na nos nas ao aos pelo pela pelos pelas num numa este esta
estes estas esse essa esses essas aquele aquela seu sua seus suas meu minha nosso nossa cada
""".split())
PRONOMES_A = {"a", "as"} #também são preposição: "a comer"
AUXILIARES = set("""
e sao foi foram era eram seja sejam fosse fossem sendo sido ser esta estao estava estavam estar
tem tinha tinham teve tiveram ter ha havia houve
""".split())
MODAIS = set("vai vao ia iam vou pode podem podia podiam deve devem devia deviam quer querem precisa precisam".split())
SUJEITOS = {"eu", "tu", "ele", "ela", "eles", "elas", "voce", "voces", "nao", "se", "me", "te", "lhe"}

def _termina_em(palavra: str, sufixos: tuple[str, ...], minimo: int = 3) -> bool:
    return any(palavra.endswith(s) and len(palavra) - len(s) >= minimo for s in sufixos)

def _classe_por_forma(palavra: str) -> str:
    #Sufixos do mais específico para o mais ambíguo; o padrão é substantivo, a classe mais comum.
    if palavra in SUBSTANTIVOS:
        return SUBSTANTIVO
    if palavra.endswith("mente") and len(palavra) > 6:
        return ADVERBIO
    if _termina_em(palavra, SUFIXOS_SUBSTANTIVO, 2):
        return SUBSTANTIVO
    if _termina_em(palavra, SUFIXOS_VERBO, 2):
        return VERBO
    if palavra.endswith("am") and len(palavra) > 3:
        return VERBO
    if palavra.endswith(("ou", "iu", "eu", "em", "ei")) and len(palavra) > 4:
        return VERBO
    if _termina_em(palavra, SUFIXOS_PARTICIPIO, 2):
        return ADJETIVO
    if palavra.endswith(("ar", "er", "ir")) and len(palavra) > 4 and not _termina_em(palavra, ("lar", "nar", "ular"), 2):
        return VERBO
    if _termina_em(palavra, SUFIXOS_ADJETIVO, 2):
        return ADJETIVO
    return SUBSTANTIVO

def classificar_palavra(token: str, respeitar_acentos: bool = True) -> str:
    #Sem contexto: serve de primeira passada e para consultar uma palavra isolada.
    if respeitar_acentos:
        classe = ACENTUADAS.get(normalizar_mantendo_acentos(token))
        if classe:
            return classe
    palavra = normalizar(token)
    if palavra[:1].isdigit():
        return NUMERO
    return CLASSE_DA_PALAVRA.get(palavra) or _classe_por_forma(palavra)

def normalizar_mantendo_acentos(token: str) -> str:
    #Mesma limpeza de normalizar(), que aqui não pode tirar o acento.
    return unicodedata.normalize("NFC", "".join(c for c in token.lower() if unicodedata.category(c) != "Cf"))

def tem_acentos(texto: str) -> bool:
    return any(unicodedata.combining(c) for c in unicodedata.normalize("NFD", texto))

def classificar_tokens(tokens: list[str], pontuacao: str, respeitar_acentos: bool = True) -> list[str]:
    #Maiúsculas ficam de fora: a nota não pode mudar com a caixa em que o texto foi colado.
    classes = [t if t in pontuacao else classificar_palavra(t, respeitar_acentos) for t in tokens]
    _aplicar_contexto(classes, [normalizar(t) for t in tokens])
    return classes

def _aplicar_contexto(classes: list[str], palavras: list[str]) -> None:
    #A forma isolada é ambígua: "o jantar" é nome, "vai jantar" é verbo; a palavra vizinha decide.
    for k, palavra in enumerate(palavras):
        atual = classes[k]
        anterior = palavras[k - 1] if k else ""
        classe_anterior = classes[k - 1] if k else None
        proxima = classes[k + 1] if k + 1 < len(classes) else None
        do_lexico = palavra in CLASSE_DA_PALAVRA and atual != VERBO

        if atual == VERBO and (anterior in DETERMINANTES or (anterior in PRONOMES_A and not _eh_infinitivo(palavra))):
            classes[k] = SUBSTANTIVO
        elif anterior in MODAIS and _eh_infinitivo(palavra):
            classes[k] = VERBO
        elif do_lexico or palavra in SUBSTANTIVOS:
            continue
        elif atual == ADJETIVO and anterior in AUXILIARES and _termina_em(palavra, SUFIXOS_PARTICIPIO, 2):
            classes[k] = VERBO
        elif atual == ADJETIVO and anterior in DETERMINANTES | PRONOMES_A:
            if proxima != SUBSTANTIVO:
                classes[k] = SUBSTANTIVO
        elif atual == ADJETIVO and classe_anterior not in (SUBSTANTIVO, ADJETIVO, ADVERBIO, CONJUNCAO) and anterior not in AUXILIARES:
            #Sem nome à esquerda para qualificar, é o próprio nome: "de animais", "Técnicas modernas".
            classes[k] = SUBSTANTIVO
        elif atual == SUBSTANTIVO and anterior in SUJEITOS:
            classes[k] = VERBO
        elif atual == SUBSTANTIVO and classe_anterior == SUBSTANTIVO:
            if palavra.endswith(("eiro", "eira", "eiros", "eiras", "ano", "ana", "anos", "anas")):
                classes[k] = ADJETIVO
            elif proxima in (PREPOSICAO, ARTIGO, PRONOME):
                classes[k] = VERBO

def _eh_infinitivo(palavra: str) -> bool:
    return palavra.endswith(("ar", "er", "ir")) and len(palavra) > 3
