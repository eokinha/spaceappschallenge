# Análogos Terra · Lua · Marte — NASA Space Apps 2026

Visualizador 3D (Three.js) de locais na Terra análogos aos locais candidatos a base na Lua e em Marte,
com o que cada analogia tem de parecido e onde ela falha.

Instruções completas de desenvolvimento: [`docs/instrucoes-desenvolvimento.md`](docs/instrucoes-desenvolvimento.md).

## Rodar localmente

```bash
cd web && python3 -m http.server 8000
# abra http://localhost:8000  (ou http://localhost:8000/?debug=1 para os pontos de teste de posição)
```

Abrir o `index.html` direto (`file://`) não funciona, porque o JSON é carregado com `fetch`.

## Gerar os dados

```bash
python3 -m pipeline.export   # escreve web/data/analogs.json (em construção)
```

## Deploy de testes na Vercel

O site é estático: a Vercel só publica a pasta `web/`, sem build (configurado em `vercel.json`).
O `web/data/analogs.json` é gerado localmente e **precisa estar commitado** para aparecer no deploy.

**Pela integração com o GitHub (recomendado):**

1. Em vercel.com → *Add New… → Project*, importe o repositório.
2. Deixe *Framework Preset* em **Other** e *Root Directory* na raiz; o resto vem do `vercel.json`.
3. Cada push na `main` atualiza a produção, e cada branch ou PR ganha uma URL de preview própria para testes.

**Pela CLI:**

```bash
npx vercel          # primeira vez: login e vínculo com o projeto; gera uma URL de preview
npx vercel --prod   # publica em produção
```

## Créditos

Texturas: ver [`web/textures/CREDITS.md`](web/textures/CREDITS.md). Fontes dos dados: listadas no painel de
cada ligação e neste README quando o pipeline estiver pronto.
