"""Notas de semelhança (0 a 1) por dimensão e nota geral.

Fórmulas:

- temperatura: sobreposição das faixas, interseção / união (Jaccard de intervalos). Faixas que não se
  tocam valem 0.
- gelo: 1 - |nível_a - nível_b| / nível_máximo, na escala ordinal do config.
- iluminacao: média de duas partes:
    altura do Sol:   1 - |elev_a - elev_b| / 90
    tempo iluminado: max(0, 1 - |fração_a - fração_b| / 0,5)
- regolito e relevo: casamento de categorias. Para cada categoria de um local, pega a maior similaridade
  com as categorias do outro (matriz do config; iguais = 1). A nota é a média dos dois sentidos, para
  ser simétrica.
- nota geral: média ponderada (pesos do config) só das dimensões com dado nos dois locais.
"""
from __future__ import annotations

from .features import Site


def interval_overlap(a: tuple[float, float], b: tuple[float, float]) -> float:
    inter = min(a[1], b[1]) - max(a[0], b[0])
    union = max(a[1], b[1]) - min(a[0], b[0])
    if union <= 0:  # duas faixas de um ponto só, iguais
        return 1.0 if a == b else 0.0
    return max(0.0, inter) / union


def ordinal_score(a: int, b: int, max_level: int) -> float:
    return 1 - abs(a - b) / max_level


def illumination_score(elev_a: float, frac_a: float, elev_b: float, frac_b: float) -> float:
    elev = 1 - abs(elev_a - elev_b) / 90
    frac = max(0.0, 1 - abs(frac_a - frac_b) / 0.5)
    return (elev + frac) / 2


def build_matrix(pairs: list[list]) -> dict[frozenset, float]:
    return {frozenset((a, b)): float(s) for a, b, s in pairs}


def tag_similarity(x: str, y: str, matrix: dict[frozenset, float]) -> float:
    if x == y:
        return 1.0
    return matrix.get(frozenset((x, y)), 0.0)


def tag_set_score(a: list[str], b: list[str], matrix: dict[frozenset, float]) -> float:
    def one_way(src, dst):
        return sum(max(tag_similarity(s, d, matrix) for d in dst) for s in src) / len(src)

    return (one_way(a, b) + one_way(b, a)) / 2


# ------------------------------------------------------------------ textos exibidos no painel

def _fmt_temp(t: tuple[float, float]) -> str:
    return f"{t[0]:.0f} a {t[1]:.0f} °C"


def _fmt_ice(site: Site, config: dict) -> str:
    return site.gelo_nota or config["ice_levels"][site.gelo]


def _fmt_light(site: Site) -> str:
    return f"Sol até {site.sol_max_elev:.0f}° de altura, iluminado ~{site.fracao_iluminada * 100:.0f}% do tempo"


def _fmt_tags(tags: list[str], labels: dict) -> str:
    return ", ".join(labels[t] for t in tags)


NOTES = {
    "temperatura": "Sobreposição das faixas de temperatura (interseção ÷ união).",
    "gelo": "Distância na escala de gelo de 0 (sem gelo) a 4 (gelo maciço).",
    "iluminacao": "Média entre a diferença na altura máxima do Sol e no tempo iluminado.",
    "regolito": "Casamento entre os tipos de material dos dois locais.",
    "relevo": "Casamento entre os tipos de relevo dos dois locais.",
}


def compare(analog: Site, target: Site, config: dict, matrices: dict) -> dict[str, dict]:
    """Compara um análogo com um alvo. Retorna só as dimensões com dado nos dois."""
    dims: dict[str, dict] = {}

    def put(dim: str, score: float, earth: str, tgt: str) -> None:
        dims[dim] = {"score": round(score, 2), "earth": earth, "target": tgt, "note": NOTES[dim]}

    if analog.gelo is not None and target.gelo is not None:
        put("gelo", ordinal_score(analog.gelo, target.gelo, len(config["ice_levels"]) - 1),
            _fmt_ice(analog, config), _fmt_ice(target, config))
    if analog.temperatura and target.temperatura:
        put("temperatura", interval_overlap(analog.temperatura, target.temperatura),
            _fmt_temp(analog.temperatura), _fmt_temp(target.temperatura))
    if analog.regolito and target.regolito:
        labels = config["regolito"]["labels"]
        put("regolito", tag_set_score(analog.regolito, target.regolito, matrices["regolito"]),
            _fmt_tags(analog.regolito, labels), _fmt_tags(target.regolito, labels))
    put("iluminacao",
        illumination_score(analog.sol_max_elev, analog.fracao_iluminada,
                           target.sol_max_elev, target.fracao_iluminada),
        _fmt_light(analog), _fmt_light(target))
    if analog.relevo and target.relevo:
        labels = config["relevo"]["labels"]
        put("relevo", tag_set_score(analog.relevo, target.relevo, matrices["relevo"]),
            _fmt_tags(analog.relevo, labels), _fmt_tags(target.relevo, labels))

    order = [d["id"] for d in config["dimensions"]]
    return {k: dims[k] for k in order if k in dims}


def overall_score(dims: dict[str, dict], weights: dict[str, float]) -> float:
    total = sum(weights[d] for d in dims)
    if total == 0:
        return 0.0
    return round(sum(weights[d] * v["score"] for d, v in dims.items()) / total, 2)
