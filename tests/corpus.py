"""Textos de todos os casos: é daqui que saem os testes e a tabela de docs/testes.md."""
from dataclasses import dataclass

LEITURA = (
    "A leitura desenvolve o pensamento crítico dos estudantes porque apresenta pontos de vista diferentes. "
    "Bibliotecas públicas ampliam o acesso aos livros nas comunidades mais pobres. "
    "Sem políticas de incentivo, muitos jovens terminam a escola sem o hábito de ler."
)
LEITURA_F1, LEITURA_F2, LEITURA_F3 = [f.strip() + "." for f in LEITURA.split(".") if f.strip()]
LEITURA_PARAFRASE = (
    "Quem lê aprende a pensar de forma crítica, pois entra em contato com opiniões variadas. "
    "O acesso a obras literárias nas regiões carentes cresce graças às bibliotecas do governo. "
    "Na falta de programas de estímulo, grande parte dos adolescentes conclui os estudos sem gostar de ler."
)
LEITURA_INGLES = (
    "Reading develops students' critical thinking because it presents different points of view. "
    "Public libraries expand access to books in the poorest communities. "
    "Without incentive policies, many young people finish school without the habit of reading."
)
LEITURA_MISTA = f"{LEITURA_F1} {LEITURA_F2} Na falta de programas de estímulo, grande parte dos adolescentes conclui os estudos sem gostar de ler."

CLIMA = (
    "O aquecimento global é causado principalmente pela queima de combustíveis fósseis. "
    "As emissões de gás carbônico cresceram muito desde a industrialização. "
    "Governos precisam investir em energia limpa para frear esse processo."
)
CLIMA_PARAFRASE = (
    "A combustão de petróleo e carvão é a principal origem do aquecimento do planeta. "
    "Desde a Revolução Industrial, a liberação de CO2 aumentou bastante. "
    "É necessário que os governos apliquem recursos em fontes renováveis para conter esse fenômeno."
)
CLIMA_FUNDIDO = (
    "O aquecimento do planeta vem da queima de combustíveis fósseis, cujas emissões de gás carbônico cresceram desde a industrialização. "
    "Por isso os governos precisam investir em energia limpa para frear esse processo."
)
CLIMA_DIVIDIDO = (
    "O aquecimento global tem uma causa principal. "
    "Essa causa é a queima de combustíveis fósseis. "
    "As emissões de gás carbônico aumentaram bastante. "
    "Esse aumento começou com a industrialização. "
    "Governos precisam investir em energia limpa. "
    "Só assim será possível frear esse processo."
)
CLIMA_AUTOR_2 = (
    "Eu acredito que o maior desafio do século é ambiental. "
    "Na minha cidade, as enchentes ficaram mais frequentes nos últimos anos. "
    "Precisamos mudar hábitos de consumo e cobrar empresas poluidoras."
)
CLIMA_AUTOR_3 = (
    "Temperaturas recordes têm sido registradas em vários continentes. "
    "Geleiras derretem e o mar avança sobre cidades costeiras. "
    "Acordos internacionais tentam limitar esse aumento, com resultados modestos."
)
EDUCACAO_1 = (
    "A educação básica brasileira enfrenta problemas de financiamento. "
    "Professores recebem salários baixos e as escolas carecem de estrutura. "
    "Isso compromete a aprendizagem dos alunos mais pobres."
)
EDUCACAO_2 = (
    "Minha experiência como docente mostra que motivar crianças é difícil. "
    "Salas lotadas dificultam a atenção individual. "
    "Valorizar o magistério deveria ser prioridade nacional."
)
EDUCACAO_3 = (
    "Estudantes de escolas públicas têm desempenho inferior nas avaliações nacionais. "
    "A desigualdade começa cedo, antes mesmo da alfabetização. "
    "Políticas de creche e tempo integral podem reduzir essa diferença."
)
REDES_1 = (
    "Redes sociais mudaram a forma como as pessoas se informam. "
    "Algoritmos escolhem o que cada usuário vê. "
    "Isso favorece bolhas e a desinformação."
)
REDES_2 = (
    "Passo horas no celular todos os dias e percebo que isso me deixa ansioso. "
    "Comparar a própria vida com a dos outros faz mal. "
    "Tenho tentado reduzir o tempo de tela."
)
FEIJOADA = (
    "A feijoada é um prato tradicional do Brasil. "
    "Seu preparo leva feijão preto e carnes variadas. "
    "Costuma ser servida com arroz, couve e laranja."
)
FUTEBOL = (
    "O futebol movimenta bilhões de reais por ano. "
    "Clubes vendem jogadores jovens para a Europa. "
    "A torcida acompanha cada transferência com paixão."
)
BALEIAS = (
    "As baleias jubarte migram milhares de quilômetros todos os anos. "
    "Elas se alimentam em águas frias e se reproduzem em mares tropicais. "
    "Os machos cantam melodias longas durante a temporada de acasalamento."
)
EXOPLANETA_SIMPLES = (
    "Cientistas acharam um planeta parecido com a Terra perto de outra estrela. "
    "Ele pode ter água líquida. "
    "Isso nos faz pensar que pode existir vida lá."
)
EXOPLANETA_TECNICO = (
    "Astrônomos detectaram um exoplaneta rochoso na zona habitável de uma anã vermelha, por meio do método de trânsito. "
    "As condições de temperatura na superfície permitiriam a presença de água em estado líquido. "
    "A descoberta reforça a hipótese de habitabilidade em sistemas estelares distantes."
)
MEDICO_SIMPLES = (
    "O paciente estava com dor no peito e falta de ar. "
    "O médico pediu exames e passou um remédio para o coração."
)
MEDICO_TECNICO = (
    "O paciente apresentou quadro de dor torácica e dispneia. "
    "Foram solicitados exames complementares e prescrito tratamento cardiológico."
)
ADVOGADO = "O réu apresentou recurso ao tribunal. Foram solicitados novos documentos e marcada a audiência."
ESPACO = "A sonda espacial entrou na órbita de Júpiter após cinco anos de viagem pelo sistema solar."
INFLACAO = "A inflação acumulada em doze meses subiu, e o banco central elevou a taxa básica de juros."
REVOLUCAO = (
    "A Revolução Industrial começou na Inglaterra no século dezoito. "
    "Máquinas a vapor transformaram a produção de tecidos e o transporte."
)
POEMA = "Minha alma canta ao vento da tarde, e o mar responde em silêncio às estrelas distantes."
NOTICIA = "A prefeitura anunciou ontem a reforma de três escolas municipais, com obras previstas para março."
COMPRAS = "Arroz, feijão, leite, ovos, tomate, cebola, sabão, papel e café."
CODIGO = "def somar(a, b):\n    return a + b\n\nfor i in range(10):\n    print(somar(i, 1))"

CONSTRUCAO_A = (
    "O menino comprou uma bola nova na loja do bairro. "
    "A menina levou uma boneca velha para a casa da avó. "
    "O cachorro achou um osso grande no quintal do vizinho."
)
CONSTRUCAO_B = (
    "O ministro assinou uma lei nova no palácio da capital. "
    "A empresa vendeu uma fábrica velha para o grupo da China. "
    "O técnico montou um time forte no clube do interior."
)
CONTEXTO_A = (
    "A pandemia alterou a rotina das escolas brasileiras. "
    "Aulas remotas exigiram computadores e internet que muitos alunos não tinham."
)
CONTEXTO_B = (
    "A pandemia alterou a rotina dos hospitais brasileiros. "
    "Leitos de terapia intensiva exigiram equipamentos e profissionais que muitas cidades não tinham."
)
ENCHIMENTO = [
    "A feijoada é um prato tradicional do Brasil.",
    "O futebol movimenta bilhões de reais por ano.",
    "Marte tem duas luas pequenas.",
    "O violino exige muitos anos de prática.",
    "As abelhas produzem mel nas colmeias.",
    "Tubarões vivem em todos os oceanos.",
    "O metrô da cidade foi ampliado.",
    "A pintura impressionista surgiu na França.",
]
TEXTO_LONGO_NOVO = " ".join(ENCHIMENTO + [
    "O trem chegou atrasado à estação central.",
    "Cozinheiros franceses valorizam a manteiga fresca.",
    "O vulcão entrou em erupção durante a madrugada.",
    "A ponte foi construída por engenheiros alemães.",
])
SEM_RELACAO_LONGO = " ".join([BALEIAS, EXOPLANETA_SIMPLES, FUTEBOL])

def _trocar_homoglifos(texto: str) -> str:
    return texto.replace("a", "а").replace("o", "о").replace("e", "е")

def _invisiveis(texto: str) -> str:
    return " ".join("​".join(p[i:i + 3] for i in range(0, len(p), 3)) for p in texto.split())

def _quebrar_linhas(texto: str, largura: int = 60) -> str:
    import textwrap
    return "\n".join(textwrap.wrap(texto, largura))

LEITURA_LONGA = " ".join([LEITURA, CLIMA, EDUCACAO_1, REDES_1])

#Frases sem nenhuma pontuação: o modelo só enxerga o começo de cada frase longa.
_PESQUISA = "os pesquisadores analisaram amostras coletadas no litoral norte durante varios meses de campo e compararam os resultados com dados historicos da regiao".split()
_ECONOMIA = "a economia regional cresceu com o turismo de inverno e com novos investimentos em portos e estradas".split()
_XADREZ = "o campeonato de xadrez reuniu jovens talentos em torneios rapidos transmitidos ao vivo para o mundo todo".split()
INICIO_COMUM = " ".join((_PESQUISA * 6)[:160])
FIM_ECONOMIA = " ".join((_ECONOMIA * 20)[:200])
FIM_XADREZ = " ".join((_XADREZ * 20)[:200])

@dataclass(frozen=True)
class Caso:
    grupo: str
    nome: str
    a: str
    b: str
    estrutural: tuple[float, float] | None = None  #faixa aceita para a nota
    semantica: tuple[float, float] | None = None

GRUPOS = {
    "copias": "Cópias",
    "reescritas": "Reescritas",
    "curtas": "Frases curtas",
    "sentido": "Sentido diferente",
    "sem_relacao": "Sem relação",
    "mesmo_tema": "Mesmo tema ou mesma construção",
    "extremos": "Citações e casos extremos",
    "burlas": "Tentativas de burla",
}

CASOS = [
    #Cópias
    Caso("copias", "Cópia exata", LEITURA, LEITURA, (1, 1), (1, 1)),
    Caso("copias", "Cópia em maiúsculas e sem acentos", LEITURA, "A LEITURA DESENVOLVE O PENSAMENTO CRITICO DOS ESTUDANTES PORQUE APRESENTA PONTOS DE VISTA DIFERENTES. BIBLIOTECAS PUBLICAS AMPLIAM O ACESSO AOS LIVROS NAS COMUNIDADES MAIS POBRES. SEM POLITICAS DE INCENTIVO, MUITOS JOVENS TERMINAM A ESCOLA SEM O HABITO DE LER.", (0.95, 1), (0.95, 1)),
    Caso("copias", "Frases reordenadas", LEITURA, f"{LEITURA_F3} {LEITURA_F1} {LEITURA_F2}", (0, 0.6), (0.85, 1)),
    Caso("copias", "Metades trocadas", LEITURA, f"{LEITURA_F2} {LEITURA_F3} {LEITURA_F1}", (0, 0.6), (0.85, 1)),
    Caso("copias", "Uma frase copiada, duas novas", LEITURA, f"{LEITURA_F1} {ENCHIMENTO[0]} {ENCHIMENTO[1]}", (0, 0.6), (0.25, 0.55)),
    Caso("copias", "Texto longo com uma frase copiada", LEITURA, f"{TEXTO_LONGO_NOVO} {LEITURA_F2}", (0, 0.4), (0, 0.3)),
    #Reescritas
    Caso("reescritas", "Paráfrase completa", LEITURA, LEITURA_PARAFRASE, (0, 0.6), (0.6, 1)),
    Caso("reescritas", "Paráfrase de outro tema", CLIMA, CLIMA_PARAFRASE, (0, 0.6), (0.6, 1)),
    Caso("reescritas", "Paráfrase reordenada", LEITURA, " ".join(reversed([f.strip() + "." for f in LEITURA_PARAFRASE.split(".") if f.strip()])), (0, 0.6), (0.55, 1)),
    Caso("reescritas", "Metade copiada, metade parafraseada", LEITURA, LEITURA_MISTA, (0.2, 1), (0.7, 1)),
    Caso("reescritas", "Frases fundidas", CLIMA, CLIMA_FUNDIDO, (0, 0.8), (0.6, 1)),
    Caso("reescritas", "Frases divididas", CLIMA, CLIMA_DIVIDIDO, (0, 0.8), (0.6, 1)),
    Caso("reescritas", "Exoplaneta: simples × técnico", EXOPLANETA_SIMPLES, EXOPLANETA_TECNICO, (0, 0.6), (0.2, 1)),
    Caso("reescritas", "Médico: simples × técnico", MEDICO_SIMPLES, MEDICO_TECNICO, (0, 0.6), (0.2, 1)),
    Caso("reescritas", "Tradução para inglês", LEITURA, LEITURA_INGLES, (0, 0.6), (0.6, 1)),
    #Frases curtas
    Caso("curtas", '"O céu é azul" × "Azul é o ceu"', "O céu é azul", "Azul é o ceu", None, (0.6, 1)),
    Caso("curtas", '"Eu amo você." × "Eu te amo."', "Eu amo você.", "Eu te amo.", None, (0.6, 1)),
    Caso("curtas", '"Gosto de café." × "Adoro café."', "Gosto de café.", "Adoro café.", None, (0.6, 1)),
    Caso("curtas", '"Vou embora amanhã." × "Amanhã vou embora."', "Vou embora amanhã.", "Amanhã vou embora.", None, (0.6, 1)),
    Caso("curtas", '"Ela ama ele." × "Ele é amado por ela."', "Ela ama ele.", "Ele é amado por ela.", None, (0.6, 1)),
    Caso("curtas", '"Está chovendo." × "Chove agora."', "Está chovendo.", "Chove agora.", None, (0.6, 1)),
    Caso("curtas", '"Oi" × "Oi"', "Oi", "Oi", (1, 1), (1, 1)),
    #Sentido diferente
    Caso("sentido", '"Eu não amo você." × "Eu te amo."', "Eu não amo você.", "Eu te amo.", None, (0, 0.3)),
    Caso("sentido", '"Eu odeio você." × "Eu te amo."', "Eu odeio você.", "Eu te amo.", None, (0, 0.3)),
    Caso("sentido", '"Estou feliz." × "Estou triste."', "Estou feliz.", "Estou triste.", None, (0, 0.3)),
    Caso("sentido", '"O carro é azul." × "O carro é vermelho."', "O carro é azul.", "O carro é vermelho."),
    Caso("sentido", '"eleva" × "reduz" o nível dos oceanos', "O derretimento das geleiras eleva o nível dos oceanos.", "O derretimento das geleiras reduz o nível dos oceanos."),
    Caso("sentido", "Daniel chato × Daniel legal", "O Daniel é um rapaz muito chato.", "O Daniel é um rapaz muito legal."),
    Caso("sentido", "Daniel salgado × Daniel doce", "O Daniel gosta de comida salgada.", "O Daniel prefere comer doces."),
    Caso("sentido", '"Bom dia." × "Boa noite."', "Bom dia.", "Boa noite."),
    Caso("sentido", '"Sim." × "Não."', "Sim.", "Não."),
    #Sem relação
    Caso("sem_relacao", "Baleias × exoplaneta", BALEIAS, EXOPLANETA_TECNICO, (0, 0.25), (0, 0.15)),
    Caso("sem_relacao", "Médico × futebol", MEDICO_SIMPLES, FUTEBOL, (0, 0.25), (0, 0.15)),
    Caso("sem_relacao", "Espaço × inflação", ESPACO, INFLACAO, (0, 0.3), (0, 0.15)),
    Caso("sem_relacao", "Revolução industrial × baleias", REVOLUCAO, BALEIAS, (0, 0.25), (0, 0.15)),
    Caso("sem_relacao", "Poema × notícia", POEMA, NOTICIA, (0, 0.25), (0, 0.15)),
    Caso("sem_relacao", "Lista de compras × notícia", COMPRAS, NOTICIA, (0, 0.25), (0, 0.15)),
    Caso("sem_relacao", "Código × texto", CODIGO, LEITURA, (0, 0.25), (0, 0.15)),
    Caso("sem_relacao", "Clima × educação", CLIMA, EDUCACAO_1, (0, 0.25), (0, 0.15)),
    Caso("sem_relacao", "Feijoada × futebol", FEIJOADA, FUTEBOL, (0, 0.25), (0, 0.15)),
    Caso("sem_relacao", "Redes sociais × clima", REDES_1, CLIMA, (0, 0.25), (0, 0.15)),
    #Mesmo tema ou mesma construção
    Caso("mesmo_tema", "Mesma construção, outro tema", CONSTRUCAO_A, CONSTRUCAO_B, (0.45, 1), (0, 0.3)),
    Caso("mesmo_tema", '"O gato dorme no sofá." × "O cão late na rua."', "O gato dorme no sofá.", "O cão late na rua.", None, (0, 0.3)),
    Caso("mesmo_tema", "Médico × advogado, frases curtas", MEDICO_TECNICO, ADVOGADO, (0.2, 1), (0, 0.3)),
    Caso("mesmo_tema", "Clima: autores 1 e 2", CLIMA, CLIMA_AUTOR_2, (0, 0.45), (0, 0.3)),
    Caso("mesmo_tema", "Clima: autores 1 e 3", CLIMA, CLIMA_AUTOR_3, (0, 0.45), (0, 0.3)),
    Caso("mesmo_tema", "Clima: autores 2 e 3", CLIMA_AUTOR_2, CLIMA_AUTOR_3, (0, 0.45), (0, 0.3)),
    Caso("mesmo_tema", "Educação: autores 1 e 2", EDUCACAO_1, EDUCACAO_2, (0, 0.45), (0, 0.3)),
    Caso("mesmo_tema", "Educação: autores 1 e 3", EDUCACAO_1, EDUCACAO_3, (0, 0.45), (0, 0.45)),
    Caso("mesmo_tema", "Educação: autores 2 e 3", EDUCACAO_2, EDUCACAO_3, (0, 0.45), (0, 0.3)),
    Caso("mesmo_tema", "Redes sociais: autores 1 e 2", REDES_1, REDES_2, (0, 0.45), (0, 0.3)),
    Caso("mesmo_tema", "Mesmo molde de frases, outro tema", CONTEXTO_A, CONTEXTO_B, (0.45, 1)),
    #Citações e casos extremos
    Caso("extremos", "Citação curta ao lado de texto próprio", LEITURA, f'{BALEIAS} {FEIJOADA} {FUTEBOL} Como disse o autor, "{LEITURA_F2[:-1]}".', (0, 0.4), (0, 0.15)),
    Caso("extremos", "Cópia só nas referências", LEITURA, f"{BALEIAS} {FUTEBOL}\n\nReferências\n{LEITURA}", (0, 0.25), (0, 0.15)),
    Caso("extremos", "Só pontuação", "... !!! ???", "... !!! ???"),
    #Tentativas de burla
    Caso("burlas", "Trecho inteiro entre aspas", LEITURA, f'"{LEITURA}"', (0.9, 1), (0.9, 1)),
    Caso("burlas", "Trecho inteiro em aspas curvas", LEITURA, f"“{LEITURA}”", (0.9, 1), (0.9, 1)),
    Caso("burlas", "Linha 'Referências' antes da cópia", LEITURA, f"Referências\n{LEITURA}", (0.8, 1), (0.9, 1)),
    Caso("burlas", "Parágrafo que começa com 'Referências'", LEITURA, f"Referências importantes sobre o tema. {LEITURA}", (0.7, 1), (0.7, 1)),
    Caso("burlas", "Aspas soltas de polegada", LEITURA, f'A tela tem 5" de largura. {LEITURA} O monitor de 7" é maior.', None, (0.55, 1)),
    Caso("burlas", "Cópia integral com 8 frases novas", LEITURA, f"{LEITURA} {' '.join(ENCHIMENTO)}", None, (0.85, 1)),
    Caso("burlas", "Cópia integral com 40 frases novas", LEITURA, f"{LEITURA} {' '.join(ENCHIMENTO * 5)}", None, (0.85, 1)),
    Caso("burlas", "Enchimento antes da cópia", LEITURA, f"{' '.join(ENCHIMENTO * 5)} {LEITURA}", None, (0.85, 1)),
    Caso("burlas", "Letras cirílicas parecidas", LEITURA, _trocar_homoglifos(LEITURA), (0.95, 1), (0.95, 1)),
    Caso("burlas", "Caracteres invisíveis nas palavras", LEITURA, _invisiveis(LEITURA), (0.95, 1), (0.95, 1)),
    Caso("burlas", "Pontos trocados por ponto e vírgula", LEITURA, LEITURA.replace(". ", "; "), None, (0.6, 1)),
    Caso("burlas", "Texto colado de PDF", LEITURA_LONGA, _quebrar_linhas(LEITURA_LONGA), (0.95, 1), (0.9, 1)),
    Caso("burlas", "Original colado de PDF", _quebrar_linhas(LEITURA_LONGA), LEITURA_LONGA, (0.95, 1), (0.9, 1)),
    Caso("burlas", "Só o início em comum, sem pontuação", f"{INICIO_COMUM} {FIM_ECONOMIA}", f"{INICIO_COMUM} {FIM_XADREZ}", None, (0.25, 0.7)),
    Caso("burlas", "Só o fim em comum, sem pontuação", f"{FIM_XADREZ} {INICIO_COMUM}", f"{FIM_ECONOMIA} {INICIO_COMUM}", None, (0.25, 0.7)),
]
