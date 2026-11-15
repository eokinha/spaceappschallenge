"""Configuração do ETL: caminhos, ids estáveis, aliases e decisões de modelagem.

Tudo o que é "decisão humana" (e não dado das planilhas) fica aqui, num lugar só, para ficar fácil de
revisar. O resto do código só lê planilhas e aplica estas regras.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
SITE_JSON = ROOT / "web" / "data" / "analogs.json"
SITE_SCHEMA = Path(__file__).resolve().parent / "analogs.schema.json"
SCHEMA_DOC = Path(__file__).resolve().parent / "SCHEMA.md"

# Layout comum das abas: linha 9 = descrição, 10 = data, 12 = cabeçalho, dados a partir da 13.
ROW_DESCRICAO = 9
ROW_DATA = 10
ROW_HEADER = 12
ROW_FIRST_DATA = 13

# Planilhas usadas. `conjunto` é o conjunto de critérios que os locais da planilha usam:
# Lote 2 e Lote 3 têm os 48 critérios idênticos, então compartilham `lotes-v1-1`
# (o extract confere isso e falha se um dia deixarem de ser iguais).
PLANILHAS = {
    "base-v1-1": {"arquivo": "Base_referencia_v1.1.xlsx", "rotulo": "Base v1.1", "conjunto": "base-v1-1", "fonte_prefixo": "F"},
    "lote-2": {"arquivo": "Lote2_7_locais.xlsx", "rotulo": "Lote 2", "conjunto": "lotes-v1-1", "fonte_prefixo": "G"},
    "lote-3": {"arquivo": "Lote3_locais_brasileiros.xlsx", "rotulo": "Lote 3", "conjunto": "lotes-v1-1", "fonte_prefixo": "H"},
    "rede": {"arquivo": "Rede_de_analogos.xlsx", "rotulo": "Rede", "conjunto": None, "fonte_prefixo": "R"},
}
LOTES = ["base-v1-1", "lote-2", "lote-3"]  # planilhas que trazem locais e notas

# Ids estáveis dos 14 locais, na ordem das colunas da aba Notas da rede (a ordem importa:
# "Melhor local (primeiro)" no Excel é o primeiro da esquerda para a direita).
# Os aliases são todos os nomes com que o local aparece nas abas.
LOCAIS = {
    "atacama": ["Atacama", "Atacama (Yungay)", "Atacama – Yungay"],
    "haughton": ["Haughton"],
    "vale-da-morte": ["Vale da Morte", "Vale da Morte – Badwater e Ubehebe"],
    "cinder-lake": ["Cinder Lake", "Cinder Lake Crater Field"],
    "meteor-crater": ["Meteor Crater"],
    "holuhraun": ["Holuhraun", "Holuhraun (Islândia)"],
    "mauna-kea": ["Mauna Kea"],
    "mcmurdo": ["McMurdo", "McMurdo Dry Valleys"],
    "rio-tinto": ["Rio Tinto"],
    "askja": ["Askja", "Askja (Islândia)"],
    "vargeao": ["Vargeão"],
    "araguainha": ["Araguainha"],
    "lencois-maranhenses": ["Lençóis Maranhenses"],
    "toca-da-boa-vista": ["Toca da Boa Vista"],
}

ALVOS = {
    "lua": {"aliases": ["Lua", "Lua – polo sul", "Lua – polo sul (Shackleton)"], "corpo": "moon",
            "local_referencia": "Shackleton"},
    "marte": {"aliases": ["Marte", "Marte – Jezero"], "corpo": "mars", "local_referencia": "Jezero"},
}

# Vale da Morte está "a confirmar" na aba Locais da base. Usamos a célula climática da fonte F33
# (36,25 N; −116,75) e marcamos a coordenada como aproximada.
COORDENADAS_OVERRIDE = {
    "vale-da-morte": {"lat": 36.25, "lon": -116.75,
                      "motivo": "Aba Locais da base diz 'a confirmar'; usada a célula 36,25 N, −116,75 da fonte F33."},
}

# Categoria que não entra na aderência (U15 – radiação: nenhum lugar da Terra reproduz).
CATEGORIAS_FORA_DA_ADERENCIA = {"limitacoes-universais"}

# Variáveis com nomes diferentes entre a base e os lotes, ou que precisam ser divididas.
# Chave: (nome normalizado na planilha, alvo ou None) -> id canônico.
# Na base, "Dose de radiação como % da do alvo" tem um valor por alvo (0,5 na Lua, 1 em Marte),
# então vira duas variáveis canônicas, as mesmas dos lotes.
VARIAVEIS_OVERRIDE = {
    ("dose de radiação como % da do alvo", "lua"): "dose-radiacao-pct-lua",
    ("dose de radiação como % da do alvo", "marte"): "dose-radiacao-pct-marte",
    ("dose de radiação como % da lunar", None): "dose-radiacao-pct-lua",
    ("dose de radiação como % da marciana", None): "dose-radiacao-pct-marte",
}
# Unidade canônica quando base e lotes discordam (decisão aprovada: rugosidade em metros).
UNIDADE_OVERRIDE = {
    "rugosidade-do-terreno": ("m", "A base v1.1 usa 'índice'; os lotes usam 'm'. Adotado 'm'. Não há dado em nenhum local."),
}

# Textos que significam "sem valor ainda" (viram null; o texto original vai para status_texto).
TEXTOS_SEM_VALOR = ("a extrair", "a medir", "a verificar", "a confirmar", "—", "-", "")

# Limiares usados nos textos do site (pontos fortes / onde a analogia falha), na escala 0–3.
# São os mesmos da aba Validação da base: "Alta (≥ 2)" e "Baixa (≤ 1)".
LIMIAR_FORTE = 2.0
LIMIAR_FRACO = 1.0

# Duas aderências que diferem menos que isto contam como empate no rank. O rank continua sendo uma
# posição única (desempate pela ordem da rede); o empate só é sinalizado (`rank_empatado` / `rank_tied`).
TOLERANCIA_EMPATE = 1e-9

# Foto de cada local, mostrada no topo do card do site. Não vem das planilhas: foi escolhida pela equipe
# na Wikimedia Commons (licenças livres) e baixada para web/images/analogs/<local_id>.jpg (máx. 1200 px).
# `tipo`: "foto" (de campo) ou "satelite". `licenca_url` é None em domínio público.
# O ETL confere que todo local tem uma entrada e que o arquivo existe; vira `analogs[].image` no JSON.
IMAGENS_DIR = ROOT / "web" / "images" / "analogs"
IMAGENS_URL = "images/analogs"  # caminho relativo a web/, como o front usa
_COMMONS = "https://commons.wikimedia.org/wiki/File:"
_BY_SA_2, _BY_SA_3, _BY_SA_4 = (f"https://creativecommons.org/licenses/by-sa/{v}/" for v in ("2.0", "3.0", "4.0"))
_BY_3, _BY_4 = (f"https://creativecommons.org/licenses/by/{v}/" for v in ("3.0", "4.0"))
IMAGENS = {
    "atacama": {
        "tipo": "foto", "legenda": "Chão pedregoso e sem vegetação no núcleo hiperárido do Atacama",
        "alt": "Planície de cascalho escuro sem vegetação até o horizonte, sob céu azul",
        "autor": "Chris Hunkeler", "licenca": "CC BY-SA 2.0", "licenca_url": _BY_SA_2,
        "fonte": _COMMONS + "Desert_Ground_(32097822997).jpg"},
    "haughton": {
        "tipo": "foto", "legenda": "Borda da cratera de impacto de Haughton, ilha Devon",
        "alt": "Encosta coberta de fragmentos de rocha clara, com planalto árido ao fundo",
        "autor": "Haughton-Mars Project", "licenca": "Domínio público", "licenca_url": None,
        "fonte": _COMMONS + "Edge_of_Haughton_Crater_(2672692755).jpg"},
    "vale-da-morte": {
        "tipo": "foto", "legenda": "Salina de Badwater, o ponto mais baixo da América do Norte",
        "alt": "Crosta de sal branca com poças rasas e montanhas ao fundo",
        "autor": "King of Hearts", "licenca": "CC BY-SA 3.0", "licenca_url": _BY_SA_3,
        "fonte": _COMMONS + "Badwater_Basin_Death_Valley_December_2013_001.jpg"},
    "cinder-lake": {
        "tipo": "foto", "legenda": "Criação do campo de crateras de Cinder Lake pelo USGS para treinar os astronautas da Apollo",
        "alt": "Foto em preto e branco de uma explosão levantando cinza vulcânica num campo plano, com montanhas ao fundo",
        "autor": "U.S. Geological Survey", "licenca": "Domínio público", "licenca_url": None,
        "fonte": _COMMONS + "Cinder_Lake_Crater_Field.jpg"},
    "meteor-crater": {
        "tipo": "foto", "legenda": "Meteor Crater (cratera Barringer), Arizona",
        "alt": "Cratera de impacto circular com paredes de rocha avermelhada no deserto",
        "autor": "Librarybell", "licenca": "CC0", "licenca_url": "https://creativecommons.org/publicdomain/zero/1.0/",
        "fonte": _COMMONS + "Meteor_crater_site_in_Arizona_2019.jpg"},
    "holuhraun": {
        "tipo": "foto", "legenda": "Erupção de Holuhraun em 2014, vista do alto",
        "alt": "Vista aérea de um campo de lava escuro com lava incandescente e uma coluna de vapor",
        "autor": "Milan Nykodym", "licenca": "CC BY-SA 2.0", "licenca_url": _BY_SA_2,
        "fonte": _COMMONS + "Bárðarbunga_V_-_Holuhraun_(14971316014).jpg"},
    "mauna-kea": {
        "tipo": "foto", "legenda": "Cones de cinza (pu'u) no cume do Mauna Kea",
        "alt": "Cones vulcânicos avermelhados sobre terreno árido, acima das nuvens",
        "autor": "S P Schmidt", "licenca": "CC BY 4.0", "licenca_url": _BY_4,
        "fonte": _COMMONS + "Pu'u_on_Mauna_Kea.jpg"},
    "mcmurdo": {
        "tipo": "foto", "legenda": "Gargoyle Ridge, nos vales secos de McMurdo",
        "alt": "Rochas escuras e esculpidas pelo vento em primeiro plano, vale seco e montanhas com gelo ao fundo",
        "autor": "U.S. Department of State", "licenca": "Domínio público", "licenca_url": None,
        "fonte": _COMMONS + "Gargoyle_Ridge_in_the_McMurdo_Dry_Valleys_in_Antarctica_(30877661786).jpg"},
    "rio-tinto": {
        "tipo": "foto", "legenda": "Margens do Rio Tinto, de água ácida e rica em ferro",
        "alt": "Rio de água alaranjada entre margens de rocha clara e pinheiros",
        "autor": "David Mata Verdejo", "licenca": "CC BY-SA 4.0", "licenca_url": _BY_SA_4,
        "fonte": _COMMONS + "P71012-115351_ribera_Rio_Tinto_(Huelva-Andalucía._Spain).jpg"},
    "askja": {
        "tipo": "foto", "legenda": "Caldeira do Askja: lago Öskjuvatn e a cratera Víti",
        "alt": "Vista aérea de um grande lago numa caldeira vulcânica e de uma cratera menor com água azul-clara",
        "autor": "Areuland", "licenca": "CC BY 4.0", "licenca_url": _BY_4,
        "fonte": _COMMONS + "Öskjuvatn_und_Viti.jpg"},
    "vargeao": {
        "tipo": "satelite", "legenda": "Domo de Vargeão visto pelo Landsat: o anel da estrutura de impacto",
        "alt": "Imagem de satélite de uma estrutura circular de cerca de 12 km entre plantações e mata",
        "autor": "USGS/NASA Landsat (recorte: Szczureq)", "licenca": "Domínio público", "licenca_url": None,
        "fonte": _COMMONS + "Vargeao_Dome_-_Landsat_OLI_222.jpg"},
    "araguainha": {
        "tipo": "foto", "legenda": "Rochas deformadas no domo de Araguainha, a maior cratera de impacto da América do Sul",
        "alt": "Afloramento de camadas de rocha inclinadas e fraturadas",
        "autor": "Geraldo C F Valadare…", "licenca": "CC BY 3.0", "licenca_url": _BY_3,
        "fonte": _COMMONS + "Araguainha_-_State_of_Mato_Grosso,_Brazil_-_panoramio_(801).jpg"},
    "lencois-maranhenses": {
        "tipo": "foto", "legenda": "Dunas dos Lençóis Maranhenses",
        "alt": "Campo de dunas de areia clara até o horizonte, com uma pessoa caminhando",
        "autor": "Joao lara mesquita", "licenca": "CC BY-SA 4.0", "licenca_url": _BY_SA_4,
        "fonte": _COMMONS + "Os_lencois.jpg"},
    "toca-da-boa-vista": {
        "tipo": "foto",
        # Não há foto livre da Toca da Boa Vista na Commons; usamos a caverna vizinha, do mesmo sistema.
        "legenda": "Toca da Barriguda, caverna vizinha do mesmo sistema (Campo Formoso, BA)",
        "alt": "Salão de caverna com paredes de rocha clara esculpidas e uma pessoa pequena na entrada de uma galeria",
        "autor": "Diego de Medeiros Bento", "licenca": "CC BY-SA 4.0", "licenca_url": _BY_SA_4,
        "fonte": _COMMONS + "Área_de_Proteção_Ambiental_do_Boqueirão_da_Onça_Diego_Bento_(01).jpg"},
}

# Nível semântico de uma nota 0–3 (cor e rótulo no site). Usa os mesmos limiares de pontos fortes e
# fracos, para nenhum ponto "parcial" aparecer em "onde a analogia falha": ≥ 2 forte, ≤ 1 fraco.
def nivel(nota):
    """'high' (≥ LIMIAR_FORTE), 'low' (≤ LIMIAR_FRACO), 'moderate' (entre os dois) ou None (a medir)."""
    if nota is None:
        return None
    if nota >= LIMIAR_FORTE:
        return "high"
    if nota <= LIMIAR_FRACO:
        return "low"
    return "moderate"


# Variável de pontuação -> variável descritiva do Catálogo da base. Serve para achar, para cada valor
# usado numa nota, as fontes citadas no Catálogo (os locais da base não têm fonte na aba Critérios) e o
# dataset de referência por corpo ("Terra: MODIS LST | Lua: Diviner | Marte: MEDA").
# None = a variável não tem linha correspondente no Catálogo.
VARIAVEL_CATALOGO = {
    "temperatura-media": "temperatura-media-do-ar",
    "temperatura-minima-registrada": "extremos-de-temperatura-do-ar",
    "temperatura-maxima-do-solo": "extremos-de-temperatura-do-ar",
    "amplitude-termica-diaria-do-solo": "amplitude-termica-diaria-solo",
    "nivel-de-uv-0-3": "radiacao-solar-uv",
    "indice-uv-medio-anual": "radiacao-solar-uv",
    "perclorato-maximo-no-solo": "perclorato-no-solo",
    "precipitacao-anual": "precipitacao-anual",
    "gelo-no-subsolo-0-3": "gelo-no-subsolo-permafrost",
    "teor-de-gelo-no-solo": "gelo-no-subsolo-permafrost",
    "teste-de-sistema-de-pouso-documentado-0-3": "uso-documentado-como-analogo",
    "declividade-media": "declividade-e-rugosidade",
    "declividade-maxima": "declividade-e-rugosidade",
    "rugosidade-do-terreno": "declividade-e-rugosidade",
    "historico-como-analogo-tripulado-0-3": "uso-documentado-como-analogo",
    "isolamento-e-logistica-remota-0-3": "uso-documentado-como-analogo",
    "origem-por-impacto-0-3": "feicao-alvo-e-escala",
    "sedimentos-de-lago-evaporitos-expostos-0-3": "mineralogia-dominante",
    "poeira-fina-sem-vento-0-3": "vento-e-poeira",
    "rajadas-de-vento-maximas": "vento-e-poeira",
    "latitude-modulo": None,
    "dose-radiacao-pct-lua": "dose-de-radiacao-na-superficie",
    "dose-radiacao-pct-marte": "dose-de-radiacao-na-superficie",
    "vulcanismo-basaltico-0-3": "mineralogia-dominante",
    "agua-acida-e-minerais-de-fe-s-0-3": "mineralogia-dominante",
    "cavidade-subterranea-acessivel-0-3": "feicao-alvo-e-escala",
    "alteracao-hidrotermal-documentada-0-3": "mineralogia-dominante",
}

# Nas observações da aba Valores dos lotes, um mesmo texto fala de vários locais
# ("McMurdo: ... Mauna Kea: ..."). Para mostrar só o trecho de cada local, os prefixos são comparados com
# os aliases de LOCAIS e com estes apelidos usados nas planilhas.
APELIDOS_OBSERVACAO = {
    "askja": ["Islândia", "islandês", "Askja"],
    "holuhraun": ["Islândia", "islandês", "Holuhraun"],
    "toca-da-boa-vista": ["Toca"],
    "lencois-maranhenses": ["Lençóis"],
    "cinder-lake": ["Cinder"],
    "meteor-crater": ["Meteor"],
}

# Texto de "Por que é análogo" no site. Não vem pronto das planilhas: foi escrito a partir do dossiê
# (docs/referencia-analogos-pitch.md) e conferido, frase por frase, com as planilhas (recorte e
# justificativa da aba Locais, observações da aba Valores, referências F/G/H). Fica só o que as
# planilhas sustentam, e todo número é o da planilha. Afirmações do dossiê sem respaldo nas planilhas ou
# em desacordo com elas foram retiradas (ex.: Toca com 120 km, idade de Vargeão, Apollo 11 a 17).
# Local sem entrada usa a justificativa da planilha.
NARRATIVAS = {
    "atacama": (
        "O recorte é o núcleo hiperárido do Atacama, perto da antiga mina de nitrato de Yungay, o ponto mais "
        "estudado do deserto, com séries de clima e de solo publicadas. Chove em média cerca de 0,6 mm por ano, e "
        "o solo, salino e oxidante, acumula perclorato em níveis comparáveis aos medidos pela sonda Phoenix em "
        "Marte. Com um dos UV mais altos da Terra e vida rara e em manchas, virou campo de prova de instrumentos "
        "e rovers que procuram moléculas orgânicas e sinais de vida. A semelhança é de aridez e de química do "
        "solo: a pressão é cerca de 125 vezes a de Jezero, o ar tem oxigênio e a superfície é muito mais quente."),
    "haughton": (
        "Haughton é uma cratera de impacto inteira, de 23 km, na ilha Devon, no Ártico canadense, e a única "
        "conhecida num deserto polar. Formada há 31 a 32 milhões de anos, tem permafrost contínuo, polígonos de "
        "gelo e ravinas de degelo parecidos com os das altas latitudes de Marte, e guarda os restos de um "
        "sistema hidrotermal gerado pelo impacto. Sedia o Haughton-Mars Project e a estação FMARS, onde se "
        "ensaiam operações humanas com trajes e rovers e o uso de radar para achar gelo. Mesmo assim, é cerca "
        "de 40 °C mais quente que Jezero e tem a pressão e a proteção contra radiação da Terra."),
    "vale-da-morte": (
        "No Vale da Morte, dois processos diferentes ficam lado a lado: o salar de Badwater é o que restou de um "
        "lago que evaporou, como os lagos antigos de Marte, e a cratera Ubehebe é um maar, aberto por explosões "
        "de magma em contato com água. O ar extremamente seco, com umidade que pode cair abaixo de 1%, e o "
        "terreno sem vegetação serviram para testar o rover Marsokhod (1992) e o sistema de visão de pouso do "
        "Perseverance (2019). Para a Lua, vale como banco de calor: o solo passa de 90 °C, como ao meio-dia "
        "lunar perto do equador. É, porém, muito mais quente que Marte, tem chuva ocasional e tem vida."),
    "mcmurdo": (
        "O Vale Wright, nos vales secos de McMurdo, é um deserto frio e seco: média anual de cerca de −20 °C, "
        "mínimas abaixo de −50 °C na região e permafrost seco sobre solo cimentado por gelo a menos de 1 m de "
        "profundidade, o mesmo arranjo do sítio de pouso da Phoenix em Marte. Por isso serve para estudar e "
        "prospectar gelo raso num solo parecido com o marciano, a partir de uma estação de pesquisa ocupada o "
        "ano todo. O solo tem perclorato, mas em teores muito menores que os do Phoenix, e a analogia falha na "
        "pressão do ar e na radiação, que continuam sendo as da Terra."),
    "rio-tinto": (
        "Na nascente do Rio Tinto, perto de Minas de Riotinto e Nerva, a água é ácida (pH ~2,3) e rica em "
        "ferro, e deposita jarosita e hematita, a mesma assinatura mineral encontrada em Meridiani Planum, em "
        "Marte. Os projetos MARTE, da NASA com o Centro de Astrobiologia da Espanha, e IPBSL perfuraram o "
        "subsolo da região para estudar a vida ligada a essa química e testar tecnologia de busca de vida em "
        "Marte. O clima, porém, é mediterrâneo, com cerca de 450 mm de chuva por ano e um rio correndo, nada "
        "parecido com o Marte de hoje."),
    "askja": (
        "A caldeira de Askja, no planalto central da Islândia, reúne vulcanismo, gelo e água no mesmo lugar: "
        "terrenos vulcânicos, uma área geotermal ativa, o lago da caldeira e uma geleira vizinha, a "
        "Dyngjujökull. Seus campos de lava foram usados no treino de geologia de campo dos astronautas do "
        "programa Apollo em 1965 e 1967, e hoje ajudam a estudar como vulcanismo, calor e água interagem. A "
        "analogia falha no clima: neve, chuva e ciclos de congelamento e degelo desgastam as rochas de um jeito "
        "que não existe na Lua, e o acesso ao planalto é só sazonal."),
    "vargeao": (
        "O Domo de Vargeão, em Santa Catarina, é uma cratera de impacto de cerca de 12 km aberta nos derrames de "
        "basalto da Formação Serra Geral, na Bacia do Paraná. É uma das duas únicas crateras da Terra em basalto "
        "bem exposto, a mesma rocha de boa parte da crosta de Marte e dos mares da Lua. O impacto reativou um "
        "sistema hidrotermal que alterou as brechas de basalto e formou óxidos de ferro, um ambiente que "
        "interessa à busca por habitats antigos em Marte. O clima subtropical úmido, com cerca de 1.750 mm de "
        "chuva por ano, porém, erode a estrutura, e não há uso como análogo tripulado."),
    "araguainha": (
        "O Domo de Araguainha, na divisa entre Mato Grosso e Goiás, é a maior e mais bem exposta estrutura de "
        "impacto da América do Sul, com cerca de 40 km. É uma cratera complexa, com anel de pico, brechas e "
        "rochas fundidas pelo impacto, o tipo de cratera que domina a superfície da Lua e de Marte; por isso "
        "serve para estudar geologia de impacto e treinar a coleta de amostras. Tem ainda uma caverna em "
        "arenito. O clima tropical, com cerca de 1.360 mm de chuva por ano, altera e erode as rochas, e a "
        "alteração hidrotermal ainda precisa ser verificada."),
    "lencois-maranhenses": (
        "Os Lençóis Maranhenses formam um grande campo de dunas barcanas e barcanoides, de até 30 m, o mesmo "
        "tipo de duna em meia-lua que cobre áreas de Marte; modelos de como o vento move as barcanas valem "
        "tanto para os Lençóis quanto para as dunas marcianas. As lagoas de água doce que se formam entre as "
        "dunas na estação chuvosa lembram um Marte com água intermitente no passado. A semelhança é de forma e "
        "de processo eólico: aqui chove cerca de 1.400 mm por ano, ao contrário do Marte atual, e o modelo "
        "ainda não mede as dunas."),
    "toca-da-boa-vista": (
        "A Toca da Boa Vista, em Campo Formoso (BA), é a maior caverna do Brasil e da América do Sul, com cerca "
        "de 114 km de galerias mapeadas em calcário e dolomito. Cavernas são candidatas a abrigar bases na Lua e "
        "em Marte, porque o teto de rocha protege da radiação, dos micrometeoritos e das grandes variações de "
        "temperatura; a Toca serve para treinar operação, navegação e mapeamento debaixo da terra, com acesso "
        "controlado. A diferença está na origem: é uma caverna hipogênica, escavada por fluidos que subiram das "
        "profundezas e dissolveram a rocha, enquanto as cavernas da Lua e de Marte são tubos de lava."),
}
