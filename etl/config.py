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
