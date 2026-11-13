"""Carrega a configuração e a tabela curada (sites.yaml) e extrai as features de cada local.

Cada local vira um `Site` com as 5 dimensões em forma comparável:

- temperatura: faixa (min, max) em °C, da tabela.
- gelo: nível ordinal 0..4 (config.yaml → ice_levels), da tabela.
- iluminacao: altura máxima do Sol ao meio-dia, calculada pela latitude e obliquidade do corpo
  (min(90, 90 - |lat| + obliquidade)), e fração do tempo iluminado (tabela ou default do config).
- regolito e relevo: listas de categorias, comparadas por matriz de similaridade do config.

Campo ausente na tabela = dimensão sem dado (fica de fora da comparação).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent


class SiteError(ValueError):
    """Erro de conteúdo na tabela curada; a mensagem lista todos os problemas encontrados."""


@dataclass
class Site:
    id: str
    body: str  # earth | moon | mars
    name: str
    lat: float
    lon: float
    description: str
    temperatura: tuple[float, float] | None = None
    gelo: int | None = None
    gelo_nota: str | None = None
    sol_max_elev: float = 0.0
    fracao_iluminada: float = 0.5
    regolito: list[str] | None = None
    relevo: list[str] | None = None
    uso: str | None = None
    fontes: list[dict] = field(default_factory=list)
    revisar: list[str] = field(default_factory=list)


def load_yaml(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_config(path: Path | str = ROOT / "pipeline" / "config.yaml") -> dict:
    return load_yaml(Path(path))


def normalize_lon(lon: float) -> float:
    """Converte longitude 0–360 leste para -180..180 leste."""
    lon = float(lon)
    if lon > 180:
        lon -= 360
    return lon


def sun_max_elevation(lat: float, obliquity: float) -> float:
    """Altura máxima do Sol ao meio-dia (graus) ao longo do ano, ignorando o relevo."""
    return max(0.0, min(90.0, 90.0 - abs(lat) + obliquity))


def _parse_site(raw: dict, body: str, config: dict, problems: list[str]) -> Site:
    sid = raw.get("id", "?")

    def bad(msg: str) -> None:
        problems.append(f"{sid}: {msg}")

    for key in ("id", "name", "lat", "lon", "description", "fontes"):
        if key not in raw:
            bad(f"campo obrigatório ausente: {key}")
    if body not in config["obliquity_deg"]:
        bad(f"corpo desconhecido: {body}")
        body = "earth"

    lat = float(raw.get("lat", 0))
    lon = normalize_lon(raw.get("lon", 0))
    if not -90 <= lat <= 90:
        bad(f"lat fora de -90..90: {lat}")
    if not -180 <= lon <= 180:
        bad(f"lon fora de -180..360: {raw.get('lon')}")

    temperatura = None
    if "temperatura_c" in raw:
        t = raw["temperatura_c"]
        if not (isinstance(t, list) and len(t) == 2 and t[0] <= t[1]):
            bad(f"temperatura_c deve ser [min, max] com min <= max: {t}")
        else:
            temperatura = (float(t[0]), float(t[1]))

    gelo = raw.get("gelo")
    if gelo is not None and gelo not in range(len(config["ice_levels"])):
        bad(f"gelo deve ser inteiro de 0 a {len(config['ice_levels']) - 1}: {gelo}")
        gelo = None

    fracao = float(raw.get("iluminacao_fracao", config["default_sunlit_fraction"]))
    if not 0 <= fracao <= 1:
        bad(f"iluminacao_fracao fora de 0..1: {fracao}")

    tags = {}
    for dim in ("regolito", "relevo"):
        values = raw.get(dim)
        if values is not None:
            unknown = [v for v in values if v not in config[dim]["labels"]]
            if unknown:
                bad(f"{dim} com categorias desconhecidas: {unknown}")
            if not values:
                bad(f"{dim} vazio (omita o campo se não houver dado)")
        tags[dim] = values

    for fonte in raw.get("fontes", []):
        if not fonte.get("label") or not str(fonte.get("url", "")).startswith("http"):
            bad(f"fonte inválida: {fonte}")
    if not raw.get("fontes"):
        bad("ao menos uma fonte é obrigatória")

    return Site(
        id=sid,
        body=body,
        name=raw.get("name", ""),
        lat=lat,
        lon=lon,
        description=" ".join(str(raw.get("description", "")).split()),
        temperatura=temperatura,
        gelo=gelo,
        gelo_nota=raw.get("gelo_nota"),
        sol_max_elev=sun_max_elevation(lat, config["obliquity_deg"].get(body, 0)),
        fracao_iluminada=fracao,
        regolito=tags["regolito"],
        relevo=tags["relevo"],
        uso=raw.get("uso"),
        fontes=list(raw.get("fontes", [])),
        revisar=list(raw.get("revisar", [])),
    )


def load_sites(config: dict, path: Path | str | None = None) -> tuple[list[Site], list[Site]]:
    """Retorna (alvos, análogos). Levanta SiteError com todos os problemas encontrados."""
    raw = load_yaml(Path(path) if path else ROOT / config["paths"]["sites"])
    problems: list[str] = []

    targets = []
    for t in raw.get("targets", []):
        body = t.get("body")
        if body not in ("moon", "mars"):
            problems.append(f"{t.get('id', '?')}: body deve ser moon ou mars")
        targets.append(_parse_site(t, body or "moon", config, problems))
    analogs = []
    for a in raw.get("analogs", []):
        site = _parse_site(a, "earth", config, problems)
        if not site.uso:
            problems.append(f"{site.id}: análogo sem `uso`")
        analogs.append(site)

    ids = [s.id for s in targets + analogs]
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    if dupes:
        problems.append(f"ids repetidos: {dupes}")

    if problems:
        raise SiteError("Problemas na tabela de locais:\n  - " + "\n  - ".join(problems))
    return targets, analogs
