"""Testes de i18n: acusam texto sem tradução, na interface e nos dados.

Três frentes (todas em Python puro, sem navegador):

1. ``test_texto_interface_tem_ingles`` — todo literal passado por ``t()`` em ``web/src/*.js`` tem
   entrada no mapa ``EN`` de ``web/src/i18n.js`` (a tradução existe de fato);
2. ``test_texto_dado_tem_ingles`` — todo texto de dado (campos ``DATA_KEYS``) do
   ``web/data/analogs.json`` está no dicionário ``web/data/i18n-en.json``;
3. ``test_nenhum_texto_portugues_solto`` — nenhum texto em português aparece "solto" no código da
   interface: ele precisa estar dentro de ``t(...)`` no JavaScript ou num atributo ``data-pt`` /
   ``data-pt-aria-label`` / ``data-pt-title`` no ``index.html``.

A lista ``DATA_KEYS`` é a mesma de ``web/src/i18n.js``; ``test_lista_de_campos_eh_a_mesma`` confere
que as duas não divergiram.
"""

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"
SRC = WEB / "src"
I18N_JS = SRC / "i18n.js"

# Campos do analogs.json que têm texto traduzível (mesma lista de DATA_KEYS em web/src/i18n.js).
DATA_KEYS = {
    "name", "short_name", "full_name", "country", "description", "narrative", "clipping",
    "batch", "alt", "caption", "license", "author", "data_notes", "reading", "purpose", "condition",
    "criterion", "variable", "unit", "target_value", "dataset_earth", "dataset_target", "label",
    "text", "to_measure", "exploration_use", "observation", "value_note", "scale", "conclusions",
    "caveats",
}

# Arquivos da interface que podem conter texto visível (i18n.js fica de fora: é o dicionário).
UI_JS = sorted(p for p in SRC.glob("*.js") if p.name != "i18n.js")

# Literal em português permitido sem tradução: nome próprio, igual nos dois idiomas.
PROPRIOS = {"Rio de Janeiro"}

PT_CHARS = re.compile(r"[áàãâéêíóôõúçÁÀÃÂÉÊÍÓÔÕÚÇ]")
# Palavras que só existem em português (sem acento): pegam o texto esquecido sem t().
# As bordas aceitam "_" para não marcar enums como 'sem_faixas'.
PT_WORDS = re.compile(
    r"(?<![a-zà-ú_])(?:de|da|das|dos|para|com|não|uma|umas|uns|ainda|pelo|pela|pelos|pelas|"
    r"deste|desta|nesta|nestes|está|são|sem|como|quando|onde|mais|isso|este|esta|crase|"
    r"listado|locais|aderência|nota|fonte|foto)(?![a-zà-ú_])",
    re.IGNORECASE,
)

# Mensagens de console e de erro ficam em português: são para quem lê o código, não para a tela.
DEV_CALLS = (
    r"(?<![A-Za-z0-9_$])console\.(?:log|info|warn|error|debug)\(",
    r"(?<![A-Za-z0-9_$])new\s+Error\(",
)


def scan(source: str):
    """Percorre JavaScript devolvendo ``(texto, início, fim)`` de cada literal de string.

    Comentários são pulados (não viram literal) e não afetam os offsets. Só serve para os arquivos
    deste projeto: não trata regexp literais com aspas dentro.
    """
    literals = []
    i, n = 0, len(source)
    while i < n:
        two = source[i:i + 2]
        if two == "//":
            j = source.find("\n", i)
            i = n if j < 0 else j
        elif two == "/*":
            j = source.find("*/", i + 2)
            i = n if j < 0 else j + 2
        elif source[i] in "\"'`":
            quote = source[i]
            j = i + 1
            while j < n:
                if source[j] == "\\":
                    j += 2
                    continue
                if source[j] == quote:
                    break
                j += 1
            literals.append((source[i + 1:j], i + 1, j))
            i = j + 1
        else:
            i += 1
    return literals


def match_paren(source: str, opening: int) -> int | None:
    """Índice do ``)`` que fecha o ``(`` na posição ``opening`` (ou None se não fechar)."""
    depth, i, n = 0, opening, len(source)
    while i < n:
        two = source[i:i + 2]
        if two == "//":
            j = source.find("\n", i)
            if j < 0:
                return None
            i = j
        elif two == "/*":
            j = source.find("*/", i + 2)
            if j < 0:
                return None
            i = j + 2
        elif source[i] in "\"'`":
            quote = source[i]
            i += 1
            while i < n and source[i] != quote:
                i += 2 if source[i] == "\\" else 1
            i += 1
        elif source[i] == "(":
            depth += 1
            i += 1
        elif source[i] == ")":
            depth -= 1
            if depth == 0:
                return i
            i += 1
        else:
            i += 1
    return None


def last_call_opening(source: str, position: int, pattern: str) -> int | None:
    """Índice do ``(`` da última chamada cujo padrão termina em ``(`` e começa antes de ``position``."""
    found = None
    for m in re.finditer(pattern, source[:position]):
        found = m.end() - 1
    return found


def inside_call(source: str, start: int, end: int, pattern: str) -> bool:
    """O literal entre ``start`` e ``end`` está dentro de uma chamada que casa com ``pattern``?"""
    opening = last_call_opening(source, start, pattern)
    if opening is None:
        return False
    closing = match_paren(source, opening)
    return closing is not None and closing >= end


def inside_t(source: str, start: int, end: int) -> bool:
    """O literal está dentro de uma chamada ``t(...)``?"""
    return inside_call(source, start, end, r"(?<![A-Za-z0-9_$])t\(")


def t_keys(source: str):
    """Literais que são o primeiro argumento de ``t(...)``: as chaves de tradução da interface."""
    keys = []
    for m in re.finditer(r"(?<![A-Za-z0-9_$])t\(\s*", source):
        rest = source[m.end():]
        for text, offset, _ in scan(rest):
            # O literal precisa ser o primeiro argumento de t(): só espaço entre o ( e a aspa.
            if rest[:offset - 1].strip() == "":
                keys.append(text)
            break
    return keys


def english_map() -> dict:
    """Mapa ``EN`` de web/src/i18n.js: pares consecutivos de literais entre ``const EN = {`` e o fim."""
    source = I18N_JS.read_text(encoding="utf-8")
    start = source.index("const EN = {")
    end = source.index("\n};", start)
    strings = [text for text, _, _ in scan(source[start + len("const EN = "):end + 2])]
    assert len(strings) % 2 == 0, "mapa EN com número ímpar de literais"
    return dict(zip(strings[0::2], strings[1::2]))


def data_keys_of_i18n_js() -> set:
    source = I18N_JS.read_text(encoding="utf-8")
    begin = source.index("const DATA_KEYS = new Set([")
    end = source.index("]);", begin)
    return set(re.findall(r"'([^']+)'", source[begin:end]))


@pytest.fixture(scope="module")
def en():
    return english_map()


def test_lista_de_campos_eh_a_mesma(en):
    """A lista DATA_KEYS deste arquivo é a de web/src/i18n.js (a duplicação não divergiu)."""
    assert data_keys_of_i18n_js() == DATA_KEYS


def test_texto_interface_tem_ingles(en):
    """Todo texto passado por t() tem tradução: acusa a chave esquecida no mapa EN."""
    sem_traducao = {}
    for path in UI_JS:
        for key in t_keys(path.read_text(encoding="utf-8")):
            if key not in en:
                sem_traducao.setdefault(path.name, set()).add(key)
    assert not sem_traducao, (
        "texto de interface sem tradução em EN (falta entrada no mapa EN de web/src/i18n.js): "
        + "; ".join(f"{f}: {sorted(v)!r}" for f, v in sorted(sem_traducao.items()))
    )


def test_texto_dado_tem_ingles():
    """Todo texto de dado do analogs.json está no dicionário i18n-en.json (senão fica em português)."""
    analogs = WEB / "data" / "analogs.json"
    if not analogs.exists():
        pytest.skip("web/data/analogs.json ausente (gere com python -m etl build)")
    dicionario = json.loads((WEB / "data" / "i18n-en.json").read_text(encoding="utf-8"))

    valores = set()

    def walk(node, key=None):
        if isinstance(node, list):
            for item in node:
                if isinstance(item, str):
                    if key in DATA_KEYS:
                        valores.add(item)
                else:
                    walk(item, key)
        elif isinstance(node, dict):
            for k, value in node.items():
                if isinstance(value, str):
                    if k in DATA_KEYS:
                        valores.add(value)
                else:
                    walk(value, k)

    walk(json.loads(analogs.read_text(encoding="utf-8")))
    sem_traducao = sorted(v for v in valores if v not in dicionario)
    assert not sem_traducao, (
        f"{len(sem_traducao)} texto(s) de dado sem tradução em web/data/i18n-en.json: "
        + "; ".join(repr(v[:80]) for v in sem_traducao[:10])
    )


def test_nenhum_texto_portugues_solto():
    """Nenhum texto em português fora de t() (JS) ou de data-pt (HTML): acusa o t() esquecido."""
    achados = []
    for path in UI_JS:
        source = path.read_text(encoding="utf-8")
        for text, start, end in scan(source):
            if text in PROPRIOS:
                continue
            if not (PT_CHARS.search(text) or PT_WORDS.search(text)):
                continue
            if inside_t(source, start, end):
                continue
            if any(inside_call(source, start, end, p) for p in DEV_CALLS):
                continue
            achados.append(f"{path.name}: {text!r}")

    html = (WEB / "index.html").read_text(encoding="utf-8")
    sem_comentarios = re.sub(r"<!--.*?-->", "", html, flags=re.S)
    sem_data_pt = re.sub(r'data-pt(?:-aria-label|-title)?="[^"]*"', "", sem_comentarios)
    for text, _, _ in scan(sem_data_pt):
        if PT_CHARS.search(text) or PT_WORDS.search(text):
            achados.append(f"index.html: {text!r}")

    assert not achados, (
        "texto em português sem t() (JS) ou sem data-pt (HTML): " + "; ".join(achados)
    )
