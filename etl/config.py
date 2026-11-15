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
