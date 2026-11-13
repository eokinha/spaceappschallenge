"""Gera web/data/analogs.json a partir da tabela curada.

Uso:
    python -m pipeline.export            # gera e valida o JSON
    python -m pipeline.export --check    # só valida, sem escrever

Passos:
1. Carrega config.yaml e sites.yaml (features.py).
2. Compara todo análogo com todo alvo (similarity.py).
3. Para cada alvo, mantém os N análogos de maior nota (config → links).
4. Monta pontos fortes e limitações a partir das notas por dimensão e das limitações físicas do corpo.
5. Valida contra schema.json e confere os ids das ligações. Se falhar, sai com código 1 sem escrever.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import jsonschema

from .features import ROOT, Site, SiteError, load_config, load_sites
from .similarity import build_matrix, compare, overall_score


class ExportError(ValueError):
    pass


def _strengths_and_limits(dims: dict, target: Site, config: dict) -> tuple[list[str], list[str]]:
    labels = {d["id"]: d["label"] for d in config["dimensions"]}
    th = config["thresholds"]
    strengths, limits = [], []
    for dim, v in sorted(dims.items(), key=lambda kv: -kv[1]["score"]):
        if v["score"] >= th["strength"]:
            strengths.append(f"{labels[dim]} parecida: {v['earth']} × {v['target']}")
    for dim, v in sorted(dims.items(), key=lambda kv: kv[1]["score"]):
        if v["score"] <= th["limit"]:
            limits.append(f"{labels[dim]} diferente: {v['earth']} na Terra × {v['target']} no alvo")
    limits.extend(config["body_limits"][target.body])
    return strengths, limits


def _sources(analog: Site, target: Site) -> list[dict]:
    seen, out = set(), []
    for f in target.fontes + analog.fontes:
        if f["url"] not in seen:
            seen.add(f["url"])
            out.append({"label": f["label"], "url": f["url"]})
    return out


def build_links(targets: list[Site], analogs: list[Site], config: dict) -> list[dict]:
    matrices = {dim: build_matrix(config[dim]["similar"]) for dim in ("regolito", "relevo")}
    rules = config["links"]
    links = []
    for target in targets:
        candidates = []
        for analog in analogs:
            dims = compare(analog, target, config, matrices)
            if len(dims) < rules["min_dimensions"]:
                continue
            score = overall_score(dims, config["weights"])
            if score >= rules["min_score"]:
                candidates.append((score, analog, dims))
        candidates.sort(key=lambda c: (-c[0], c[1].id))
        for score, analog, dims in candidates[: rules["top_n_per_target"]]:
            strengths, limits = _strengths_and_limits(dims, target, config)
            links.append({
                "analog": analog.id,
                "target": target.id,
                "score": score,
                "dimensions": dims,
                "strengths": strengths,
                "limits": limits,
                "exploration_use": analog.uso,
                "sources": _sources(analog, target),
            })
    return links


def _site_json(site: Site, with_body: bool) -> dict:
    out = {"id": site.id}
    if with_body:
        out["body"] = site.body
    out.update({"name": site.name, "lat": round(site.lat, 4), "lon": round(site.lon, 4),
                "description": site.description})
    return out


def build_document(config: dict, targets: list[Site], analogs: list[Site]) -> dict:
    links = build_links(targets, analogs, config)
    used = {l["analog"] for l in links}
    return {
        "version": 1,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "dimensions": [{"id": d["id"], "label": d["label"]} for d in config["dimensions"]],
        "targets": [_site_json(t, True) for t in targets],
        # Só os análogos que têm pelo menos uma ligação aparecem no globo.
        "analogs": [_site_json(a, False) for a in analogs if a.id in used],
        "links": links,
    }


def validate_document(doc: dict, schema: dict) -> None:
    """Valida contra o schema e confere os ids. Levanta ExportError com todos os problemas."""
    validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
    problems = [f"{'/'.join(map(str, e.absolute_path)) or '(raiz)'}: {e.message}"
                for e in validator.iter_errors(doc)]
    target_ids = {t["id"] for t in doc.get("targets", [])}
    analog_ids = {a["id"] for a in doc.get("analogs", [])}
    for i, link in enumerate(doc.get("links", [])):
        if link.get("target") not in target_ids:
            problems.append(f"links/{i}: alvo inexistente {link.get('target')!r}")
        if link.get("analog") not in analog_ids:
            problems.append(f"links/{i}: análogo inexistente {link.get('analog')!r}")
    if problems:
        raise ExportError("JSON inválido:\n  - " + "\n  - ".join(problems))


def _report(doc: dict, targets: list[Site], analogs: list[Site]) -> None:
    print(f"{len(doc['targets'])} alvos · {len(doc['analogs'])} análogos usados de {len(analogs)} · "
          f"{len(doc['links'])} ligações")
    linked = {l["target"] for l in doc["links"]}
    for t in targets:
        if t.id not in linked:
            print(f"  aviso: {t.id} ficou sem nenhuma ligação (nenhum análogo passou do mínimo)")
    pending = [(s.id, s.revisar) for s in targets + analogs if s.revisar]
    if pending:
        print(f"  {len(pending)} locais com valores a revisar (campo `revisar` no sites.yaml):")
        for sid, fields in pending:
            print(f"    - {sid}: {', '.join(fields)}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--config", default=ROOT / "pipeline" / "config.yaml")
    parser.add_argument("--check", action="store_true", help="só valida, sem escrever o arquivo")
    args = parser.parse_args(argv)

    config = load_config(args.config)
    try:
        targets, analogs = load_sites(config)
        doc = build_document(config, targets, analogs)
        with open(ROOT / config["paths"]["schema"], encoding="utf-8") as f:
            validate_document(doc, json.load(f))
    except (SiteError, ExportError) as err:
        print(err, file=sys.stderr)
        return 1

    _report(doc, targets, analogs)
    if not args.check:
        out = ROOT / config["paths"]["output"]
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"escrito: {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
