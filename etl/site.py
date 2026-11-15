"""Monta o web/data/analogs.json (contrato v2 com o front-end 3D) a partir do modelo recalculado.

O front-end não calcula nada: cada número e cada frase que aparece na tela sai daqui.
- targets  = os 2 alvos (Lua – Shackleton, Marte – Jezero), pontos nos globos da Lua e de Marte.
- analogs  = os 14 locais da Terra, pontos no globo da Terra.
- links    = 14 × 2 ligações (todo local é avaliado contra os dois alvos). `score` = aderência ÷ 3.
- dimensions = as categorias de utilidade; "Limitações universais" aparece, mas não entra no score.
Os ids são os mesmos de data/processed (local_id, alvo_id, utilidade_id), para cruzar os dois.
"""
from . import config

ROUND = 4


def _r(x):
    return None if x is None else round(float(x), ROUND)


def fmt(x):
    """Número para texto em pt-BR: 1.5 -> '1,5'; 3.0 -> '3'; 0.6667 -> '0,67'."""
    s = f"{x:.2f}".rstrip("0").rstrip(".")
    return s.replace(".", ",")


def _ordem_fonte(fid):
    return ("FGHR".index(fid[0]), int(fid[1:]))


def _fontes_do_local(local, model):
    ids = set(local["fonte_ids"])
    if local["lote"] == "base-v1-1":
        for c in model["catalogo_referencia"]:
            if c["entidade_id"] == local["id"] and not c["a_medir"]:
                ids.update(c["fonte_ids"])
        for v in model["validacao_casos"]:
            if v["local_id"] == local["id"]:
                ids.update(v["fonte_ids"])
    else:
        for v in model["valores"]:
            if v["local_id"] == local["id"] and v["status"] == "com_valor":
                ids.update(v["fonte_ids"])
    por_id = {f["id"]: f for f in model["fontes"]}
    out = []
    for fid in sorted(ids, key=_ordem_fonte):
        f = por_id.get(fid)
        if f and f["link"] and f["link"].startswith("http"):
            out.append({"id": fid, "label": f["referencia"], "url": f["link"]})
    return out


def build(model, res, gerado_em):
    utils = {u["id"]: u for u in model["utilidades"]}
    cats = {c["id"]: c for c in model["categorias"]}
    nu = {(n["local_id"], n["utilidade_id"], n["alvo_id"]): n for n in res["notas_utilidade"]}
    nc = {(n["local_id"], n["categoria_id"], n["alvo_id"]): n for n in res["notas_categoria"]}
    ad = {(a["local_id"], a["alvo_id"]): a for a in res["aderencia"]}
    melhor = {(m["utilidade_id"], m["alvo_id"]): m for m in res["melhor_por_utilidade"]}
    pares = [(m["utilidade_id"], m["alvo_id"]) for m in res["melhor_por_utilidade"]]

    targets = [{
        "id": a["id"], "body": a["corpo"], "name": a["nome"], "short_name": a["local_referencia"],
        "lat": a["lat"], "lon": a["lon"], "description": a["por_que_recorte"] or "", "clipping": a["recorte"],
    } for a in model["alvos"]]

    analogs, links = [], []
    for l in model["locais"]:
        a0 = ad[(l["id"], "lua")]
        analogs.append({
            "id": l["id"], "name": l["nome"], "full_name": l["nome_completo"], "country": l["pais"],
            "lat": l["lat"], "lon": l["lon"], "approximate_coords": l["coordenada_aproximada"],
            "description": l["justificativa"] or l["por_que_recorte"] or l["recorte"] or "",
            "clipping": l["recorte"], "data_notes": l["obs_dados"],
            "listed_as": l["listado_como"], "batch": config.PLANILHAS[l["lote"]]["rotulo"],
            "model_indicates": a0["modelo_indica"], "matches_listing": a0["bate"],
        })
        fontes = _fontes_do_local(l, model)
        leituras = {q["alvo_id"]: q for q in l["leitura_qualitativa"]}
        for t in model["alvos"]:
            a = t["id"]
            row = ad[(l["id"], a)]
            if row["aderencia"] is None:
                continue  # sem nenhuma utilidade avaliada: não há o que ligar (nunca inventar 0)
            dims = {}
            for cid in cats:
                n = nc.get((l["id"], cid, a))
                if n and n["nota"] is not None:
                    dims[cid] = {"score": _r(n["nota"] / 3), "adherence": _r(n["nota"]),
                                 "evaluated": n["n_avaliadas_local"], "total": n["n_utilidades"]}
            us = []
            for (u, al) in pares:
                if al != a:
                    continue
                n = nu[(l["id"], u, a)]
                m = melhor[(u, a)]
                us.append({
                    "id": u, "name": utils[u]["nome_curto"], "category": utils[u]["categoria_id"],
                    "adherence": _r(n["nota"]), "score": _r(None if n["nota"] is None else n["nota"] / 3),
                    "status": n["status"],
                    "variables_evaluated": n["n_variaveis_avaliadas"], "variables_total": n["n_variaveis"],
                    "best_in_network": bool(m["melhor_nota"] is not None and m["melhor_nota"] >= 2
                                            and l["id"] in m["empatados"]),
                    "reading": n["leitura"],
                })
            avaliadas = [x for x in us if x["adherence"] is not None]
            strengths, limits = [], []
            q = leituras.get(a)
            if q and q["similar_em"]:
                strengths.append(f"Parecido em: {q['similar_em']}")
            for x in sorted(avaliadas, key=lambda x: (-x["adherence"], x["id"])):
                if x["adherence"] >= config.LIMIAR_FORTE:
                    strengths.append(f"{x['name']} ({fmt(x['adherence'])}/3)")
            if q and q["diferente_em"]:
                limits.append(f"Diferente em: {q['diferente_em']}")
            for x in sorted(avaliadas, key=lambda x: (x["adherence"], x["id"])):
                if x["adherence"] <= config.LIMIAR_FRACO:
                    texto = f"{x['name']} ({fmt(x['adherence'])}/3)"
                    if x["category"] in config.CATEGORIAS_FORA_DA_ADERENCIA:
                        texto += f": {utils[x['id']]['criterio_aderencia']}"
                    limits.append(texto)
            if not limits:
                limits.append("Nenhuma utilidade avaliada ficou com nota ≤ 1; veja as utilidades a medir.")
            links.append({
                "analog": l["id"], "target": a,
                "score": _r(row["aderencia"] / 3),
                "adherence": _r(row["aderencia"]),
                "rank": row["rank"],
                "rank_tied": row["rank_empatado"],
                "listed_as_target": a in l["listado_como"],
                "dimensions": dims,
                "utilities": us,
                "strengths": strengths,
                "limits": limits,
                "to_measure": [x["name"] for x in us if x["status"] == "a_medir"],
                "best_in_network_count": row["n_melhor_em"],
                "exploration_use": (q["utilidade"] if q and q["utilidade"] else l["justificativa"]) or "",
                "sources": fontes,
            })

    textos_rede = {t["bloco"]: t for t in model["textos"] if t["planilha_id"] == "rede"}
    return {
        "version": 2,
        "generated_at": gerado_em,
        "model": {
            "name": model["metadata"]["modelo"],
            "data_date": model["metadata"]["data_planilhas"],
            "scale": "Aderência de 0 a 3 (0 = não serve, 3 = forte); score = aderência ÷ 3. "
                     "Utilidade sem nota = a medir (não entra na média).",
            "excluded_from_score": sorted(config.CATEGORIAS_FORA_DA_ADERENCIA),
        },
        "dimensions": [{"id": c["id"], "label": c["nome"], "in_score": c["entra_na_aderencia"]}
                       for c in model["categorias"]],
        "targets": targets,
        "analogs": analogs,
        "links": links,
        "network": {
            "coverage": [{"target": c["alvo_id"], "evaluated": c["avaliadas"], "covered": c["cobertas"],
                          "gaps": c["lacunas"], "to_measure": c["a_medir"]} for c in res["cobertura"]],
            "best_by_utility": [{
                "utility": m["utilidade_id"], "name": utils[m["utilidade_id"]]["nome_curto"], "target": m["alvo_id"],
                "best_score": _r(m["melhor_nota"]), "best": m["empatados"], "status": m["situacao"],
            } for m in res["melhor_por_utilidade"]],
            "conclusions": [x for k, t in textos_rede.items() if k.startswith("conclusao") for x in t["linhas"]],
            "caveats": textos_rede.get("cuidados-ao-ler", {}).get("linhas", []),
        },
    }
