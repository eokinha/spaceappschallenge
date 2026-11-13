# Space Apps 2026 — Análogos Terra · Lua · Marte

Visualizador 3D (Three.js) de análogos terrestres para locais candidatos na Lua e em Marte,
alimentado por um JSON gerado por um pipeline Python.

Antes de implementar qualquer coisa, leia `docs/instrucoes-desenvolvimento.md`: arquitetura,
contrato do `analogs.json`, regras do front-end e critérios de pronto.

- Rodar o front-end: `cd web && python -m http.server 8000`
- Gerar os dados: `.venv/bin/python -m pipeline.export` (dados curados em `pipeline/sites.yaml`)
- Testes do pipeline: `.venv/bin/python -m unittest discover -s tests -t .`
- Deploy de testes: Vercel estática, publica só `web/` (`vercel.json`); o `analogs.json` precisa estar commitado.
- O front-end não calcula semelhanças; todo número vem do JSON.
- Mudanças no formato do JSON exigem atualizar `pipeline/schema.json` e o documento de instruções.
