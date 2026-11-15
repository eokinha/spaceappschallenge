# Instruções de desenvolvimento — Visualizador de análogos Terra · Lua · Marte

Projeto para o desafio **Identify Earth Locations that Analog the Permanent Moon Base Locations and Mars**
(NASA Space Apps 2026, 14–15/11/2026).
Documento do desafio: https://claude.ai/artifact/CEd5y9NhnDyDDwbRRJTuE1
Página oficial: https://www.spaceappschallenge.org/2026/challenges/permanent-moon-base-locations-and-mars/

## 1. O que vamos construir

Uma página web com três globos 3D (Terra, Lua e Marte) que mostra os análogos terrestres de locais
candidatos na Lua e em Marte e explica por que eles se parecem e onde a analogia falha.

- **Layout:** a Terra fica grande no centro, com a Lua e Marte como globos menores dos lados.
- **Locais:** os dois alvos — Lua (polo sul, Shackleton) e Marte (cratera Jezero) — aparecem como pontos
  nos globos deles. Os 14 análogos na Terra também são pontos.
- **Arcos:** saem de cada análogo na Terra até cada alvo (14 × 2 ligações).
  A espessura e a cor do arco mostram a aderência do análogo àquele alvo.
- **Seleção:** ao clicar num local, os três globos destacam o grupo dele e um painel explica a
  aderência por categoria de utilidade (Engenharia, Ciência, Recursos, Pouso e mobilidade, Operações
  humanas e Limitações universais) e por utilidade (U01–U19).

O desafio exige dizer **onde a analogia falha**. O painel precisa mostrar isso, não só os pontos fortes.

## 2. Arquitetura

```
planilhas da equipe (data/raw/*.xlsx)
        │  python -m etl build
        ▼
ETL Python (etl/) ──gera──▶ data/processed/  (tabelas normalizadas, CSV, relatório de validação)
                  └─gera──▶ web/data/analogs.json  ──lido por──▶  web/index.html (Three.js)
```

- **Python** faz toda a análise: lê as planilhas do modelo de aderência, recalcula todas as notas com a
  mesma lógica das fórmulas do Excel, confere o resultado célula a célula com o Excel e escreve os JSON.
- **Front-end** é estático: um HTML que carrega Three.js e lê o JSON. Não há back-end.
- O front-end não calcula semelhança. Se um número aparece na tela, ele veio do JSON.
- **Deploy de testes:** Vercel, como site estático. O `vercel.json` publica só a pasta `web/`, sem build.
  O ETL não roda na Vercel: gere o `analogs.json` localmente e commite. Cada branch ou PR ganha uma
  URL de preview (ver README).

### Estrutura de pastas

```
.
├── etl/                      # Python: ETL das planilhas
│   ├── __main__.py           # CLI: python -m etl build | check
│   ├── config.py             # ids estáveis, aliases, conjuntos de critérios e decisões de modelagem
│   ├── text.py               # slugs, aliases, números em pt-BR, códigos de fonte
│   ├── extract.py            # lê as abas (openpyxl, valores em cache do Excel)
│   ├── transform.py          # normaliza em tabelas longas (locais, critérios, valores...)
│   ├── scoring.py            # o modelo de aderência (fórmulas na docstring)
│   ├── validate.py           # compara o recalculado com o cache do Excel, célula a célula
│   ├── site.py               # monta o web/data/analogs.json
│   ├── load.py               # grava data/processed/ e o JSON do site
│   ├── analogs.schema.json   # JSON Schema do analogs.json
│   └── SCHEMA.md             # dicionário de dados de data/processed/
├── tests/                    # pytest (regras do modelo + regressão com as planilhas)
├── data/
│   ├── raw/                  # planilhas da equipe (fora do git; copie antes de rodar o ETL)
│   └── processed/            # saída do ETL (fora do git; regenerável)
├── web/
│   ├── index.html
│   ├── src/
│   │   ├── main.js           # cena, câmera, render loop
│   │   ├── globe.js          # criação de um globo + conversão lat/lon
│   │   ├── arcs.js           # arcos entre corpos
│   │   ├── interaction.js    # raycasting, hover, clique, seleção
│   │   └── panel.js          # painel lateral
│   ├── textures/             # earth.jpg, moon.jpg, mars.jpg
│   └── data/analogs.json     # gerado pelo ETL (vai pro git: é o que a Vercel publica)
└── docs/
```

## 3. Contrato de dados: `analogs.json` (versão 2)

Este arquivo é a fronteira entre Python e front-end. Mudanças nele precisam ser combinadas entre os dois lados
e refletidas em `etl/analogs.schema.json`. Os ids são os mesmos de `data/processed/`
(`analogs[].id` = `local_id`, `targets[].id` = `alvo_id`, `utilities[].id` = `U01`…`U19`).

```json
{
  "version": 2,
  "generated_at": "2026-11-15T12:00:00Z",
  "model": { "name": "Base de referência v1.1 – 14/11/2026", "data_date": "2026-11-14",
             "scale": "Aderência de 0 a 3 ...; score = aderência ÷ 3", "excluded_from_score": ["limitacoes-universais"] },
  "dimensions": [
    { "id": "engenharia", "label": "Engenharia", "in_score": true },
    { "id": "limitacoes-universais", "label": "Limitações universais", "in_score": false }
  ],
  "targets": [
    { "id": "marte", "body": "mars", "name": "Marte – Jezero", "short_name": "Jezero",
      "lat": 18.38, "lon": 77.58, "description": "Tem rover em solo...", "clipping": "Cratera Jezero e seu delta" }
  ],
  "analogs": [
    { "id": "haughton", "name": "Haughton", "full_name": "Haughton", "country": "Canadá",
      "lat": 75.383, "lon": -89.667, "approximate_coords": false, "description": "...", "clipping": "...",
      "data_notes": null, "listed_as": ["marte"], "batch": "Base v1.1",
      "model_indicates": "marte", "matches_listing": true }
  ],
  "links": [
    {
      "analog": "haughton", "target": "marte",
      "score": 0.5128, "adherence": 1.5385, "rank": 1, "listed_as_target": true,
      "dimensions": { "ciencia": { "score": 0.8, "adherence": 2.4, "evaluated": 5, "total": 5 } },
      "utilities": [
        { "id": "U06", "name": "Prospecção de gelo", "category": "recursos", "adherence": 2, "score": 0.6667,
          "status": "avaliada", "variables_evaluated": 2, "variables_total": 2, "best_in_network": true,
          "reading": "Permafrost contínuo e polígonos..." }
      ],
      "strengths": ["Parecido em: ...", "Operações humanas e EVA (3/3)"],
      "limits": ["Diferente em: ...", "Proteção contra radiação (0/3): Nenhum lugar da Terra reproduz..."],
      "to_measure": ["Ciclagem térmica", "Mobilidade em encostas"],
      "best_in_network_count": 6,
      "exploration_use": "...",
      "sources": [{ "id": "F2", "label": "Lee & Osinski 2005, ...", "url": "https://..." }]
    }
  ],
  "network": {
    "coverage": [{ "target": "marte", "evaluated": 15, "covered": 13, "gaps": 2, "to_measure": 2 }],
    "best_by_utility": [{ "utility": "U01", "name": "Frio extremo", "target": "lua", "best_score": 0.5,
                          "best": ["mcmurdo"], "status": "Lacuna" }],
    "conclusions": ["..."], "caveats": ["..."]
  }
}
```

Regras:

- `lat` em graus, de -90 a 90. `lon` em graus, de -180 a 180, positivo para leste, no sistema de coordenadas
  planetocêntrico de cada corpo.
- `adherence` vai de 0 a 3 (escala das planilhas). `score` = `adherence ÷ 3`, de 0 a 1, para largura e cor
  dos arcos. A aderência do link é a média das notas de utilidade do alvo **sem** a categoria
  "Limitações universais" (ela aparece em `dimensions`, mas com `in_score: false`).
- Utilidade sem nota tem `adherence: null` e `status: "a_medir"`; mostre "a medir", nunca zero.
  Categoria sem nenhuma utilidade avaliada fica fora do objeto `dimensions`. Nunca invente valor.
- Todo análogo tem um link para cada alvo (Lua e Marte). `rank` é a posição do análogo entre os 14 para
  aquele alvo.
- `strengths` = utilidades com nota ≥ 2 (e, nos 3 locais da base, o "é similar em" da Leitura preliminar).
  `limits` = utilidades com nota ≤ 1 (e o "é diferente em"); é obrigatório e nunca vazio, porque a radiação
  (U15) é uma limitação universal.
- `sources` traz as fontes com link citadas nos dados daquele análogo.

## 4. ETL Python

- Python 3.11+. Dependências em `requirements.txt` (`openpyxl`, `jsonschema`, `pytest`). Ambiente:
  `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`.
- **Entrada:** as planilhas da equipe em `data/raw/` (fora do git): `Base_referencia_v1.1.xlsx`,
  `Lote2_7_locais.xlsx`, `Lote3_locais_brasileiros.xlsx` e `Rede_de_analogos.xlsx`.
- Comando único: `python -m etl build` gera `data/processed/` e `web/data/analogs.json`
  (`python -m etl check` só recalcula e valida, sem gravar). Testes: `python -m pytest`.
- **O ETL recalcula, não copia.** As notas são refeitas em Python (`etl/scoring.py`) a partir dos critérios e
  dos valores de entrada, e depois comparadas célula a célula com os valores em cache do Excel
  (tolerância 1e-9). Se houver divergência, o comando sai com código 1 e não grava nada
  (`--allow-divergences` grava mesmo assim). O relatório fica em `data/processed/relatorio_validacao.md`.
- Modelo (fórmulas na docstring de `etl/scoring.py`):
  - nota da variável 0–3 pelas faixas do critério (`maior`/`menor`); vazio = a medir (`null`, nunca 0);
  - nota da utilidade = média das notas de variável não vazias; categoria = média das utilidades;
  - aderência do local ao alvo = média das utilidades do alvo, sem "Limitações universais";
  - rede: melhor local por utilidade, empates, segunda nota e situação (Coberta ≥ 2, Lacuna < 2, A medir).
  - Todos os pesos valem 1; o código já aceita pesos.
- **Conjuntos de critérios:** a base v1.1 e os lotes usam critérios um pouco diferentes (UV em escala 0–3 na
  base, índice UV do NASA POWER nos lotes; radiação em uma ou duas variáveis). Cada planilha aponta para um
  conjunto (`base-v1-1` ou `lotes-v1-1`) em `etl/config.py`; o ETL confere que os lotes 2 e 3 têm critérios
  idênticos.
- Decisões que não vêm das planilhas (aliases dos locais, coordenada aproximada do Vale da Morte,
  unidade da rugosidade, variáveis renomeadas) ficam todas em `etl/config.py`.
- Dicionário de dados de `data/processed/`: `etl/SCHEMA.md` (copiado para a pasta a cada build).
- O JSON do site é validado contra `etl/analogs.schema.json` e os ids das ligações são conferidos antes de
  gravar.

## 5. Front-end 3D (Three.js)

### Carregamento

- Three.js puro via import map, com versão fixa. Não use `three@latest`.

```html
<script type="importmap">
{ "imports": {
    "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
    "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"
} }
</script>
```

- O JSON é lido com `fetch('data/analogs.json')`. Isso não funciona abrindo o arquivo direto (`file://`).
  Para rodar localmente: `cd web && python -m http.server 8000` e abrir `http://localhost:8000`.

### Cena e layout

- Uma `PerspectiveCamera`, `OrbitControls` para zoom e rotação da cena toda, `AmbientLight` fraca e uma
  `DirectionalLight` como sol.
- Terra: raio 1, na origem.
- Lua e Marte: raios menores, deixe configurável. As proporções reais são Lua 0,27 e Marte 0,53 do raio
  da Terra. Na escala real a Lua fica pequena demais para clicar, então comece com Lua 0,4 e Marte 0,55.
- Lua à esquerda e Marte à direita, em `x = ∓2,8` (ajustar para não cortar em telas estreitas).
- Cada globo é um `THREE.Group` contendo a esfera, os marcadores e o anel de destaque. Girar o grupo gira tudo
  junto.
- Esferas: `SphereGeometry(r, 64, 64)` com `MeshStandardMaterial` e textura equiretangular.

### Texturas

- Use mapas equiretangulares (proporção 2:1) de 2k a 4k pixels, em JPG, em `web/textures/`.
- Fontes sugeridas, a confirmar a licença e citar no README: NASA Blue Marble (Terra), mosaico LROC WAC
  ou o CGI Moon Kit do NASA SVS (Lua), mosaico MOLA/Viking (Marte).
- Configure `texture.colorSpace = THREE.SRGBColorSpace`.

### Conversão lat/lon → posição no globo

Com a `SphereGeometry` padrão e uma textura equiretangular de -180° a 180°, a longitude 0 fica no eixo +X:

```js
export function latLonToVector3(lat, lon, radius) {
  const φ = THREE.MathUtils.degToRad(lat);
  const λ = THREE.MathUtils.degToRad(lon);
  return new THREE.Vector3(
     radius * Math.cos(φ) * Math.cos(λ),
     radius * Math.sin(φ),
    -radius * Math.cos(φ) * Math.sin(λ)
  );
}
```

Teste obrigatório: coloque um marcador num ponto fácil de reconhecer em cada textura (ex.: Rio de Janeiro,
cratera Tycho, Olympus Mons) e confirme que ele cai no lugar certo. Se não cair, a textura tem outra origem
de longitude e é preciso girar a esfera, não a fórmula.

### Marcadores

- Alvos (Lua/Marte): esfera pequena ou sprite, cor por corpo.
- Análogos (Terra): outra forma ou cor, para não confundir com alvos.
- Tamanho em unidades da cena proporcional ao raio do globo, para ter o mesmo tamanho visual nos três.
- Use `InstancedMesh` se passar de algumas centenas de pontos.

### Arcos

- Cada link vira um arco entre o ponto na Terra e o ponto no alvo, em coordenadas do mundo
  (`object.localToWorld`).
- Curva: `CubicBezierCurve3` com os pontos de controle afastados da superfície, para o arco não atravessar
  os globos. Altura proporcional à distância entre os pontos.
- Espessura: `linewidth` de `LineBasicMaterial` é ignorado no WebGL. Use `Line2` + `LineMaterial` dos addons
  (largura em pixels) ou `TubeGeometry`.
- Escala visual da nota (`score` 0–1):
  - largura de 1 px (0) a 6 px (1);
  - cor numa rampa contínua, ex.: cinza-azulado para fraco e amarelo-laranja para forte;
  - mostre uma legenda com essa escala na tela.
- Se os globos giram, as pontas mudam: atualize as posições dos arcos a cada frame (`setPositions` no
  `LineGeometry`), sem recriar a geometria.
- Arcos que saem da face escondida de um globo: reduza a opacidade ou esconda, para não cruzarem a esfera.
- Rotação automática: desligada por padrão, com um botão para ligar.

### Interação

- `Raycaster` nos marcadores para hover (tooltip com o nome) e clique.
- Clique num alvo: seleciona o grupo do alvo e todos os análogos ligados a ele.
  Clique num análogo: seleciona o análogo e todos os alvos ligados a ele.
- Ao selecionar:
  - os elementos fora do grupo ficam com opacidade ~0,15;
  - cada globo gira suavemente (slerp de quaternion, ~600 ms) até o ponto selecionado ficar virado para
    a câmera;
  - um anel de destaque aparece em volta de cada ponto do grupo;
  - o painel lateral abre.
- Clique no vazio ou `Esc` limpa a seleção.

### Painel lateral

Para o link selecionado (se o grupo tiver vários, mostre uma lista ordenada por nota e deixe trocar):

1. Nome do análogo na Terra → nome do alvo, com a aderência (0–3) e a posição na rede (`rank`).
2. Uma barra por categoria (`dimensions`), com a nota e quantas utilidades a sustentam
   (`evaluated` de `total`). "Limitações universais" aparece separada, como fora do score.
3. A lista de utilidades (`utilities`), com nota, "a medir" e destaque quando o local é o melhor da rede.
4. **Pontos fortes** (`strengths`).
5. **Onde a analogia falha** (`limits`), sempre visível.
6. Uso na exploração (`exploration_use`).
7. Fontes dos dados, com links.

Categoria ausente no JSON e utilidade com `adherence: null` aparecem como "a medir", não como zero.

### Acessibilidade e desempenho

- Uma lista de locais em HTML ao lado do canvas, navegável por teclado, que faz a mesma seleção do clique.
- Meta de 60 fps num notebook comum. Limite `renderer.setPixelRatio(Math.min(devicePixelRatio, 2))`.
- Em tela de celular, o painel vira uma gaveta embaixo e os globos ficam menores.

## 6. Ordem de implementação

1. Schema do JSON + um `analogs.json` de exemplo feito à mão (desbloqueia o front-end no primeiro dia).
2. Cena com os três globos texturizados e o teste de posição lat/lon.
3. Marcadores a partir do JSON.
4. Arcos com largura e cor pela nota, mais a legenda.
5. Clique, destaque do grupo e rotação dos globos.
6. Painel lateral.
7. ETL Python gerando o JSON real a partir das planilhas (em paralelo aos passos 2–6).
8. Lista acessível, ajustes de celular e polimento visual.
9. README com como rodar, fontes de dados e créditos das texturas.

## 7. Critérios de pronto

- [ ] `python -m etl build` gera um JSON válido contra o schema, com 0 divergência em relação ao Excel.
- [ ] A página abre com `python -m http.server` sem erros no console.
- [ ] Os pontos de teste caem no lugar certo nos três globos.
- [ ] Todo link do JSON aparece como arco, com largura e cor coerentes com a legenda.
- [ ] Clicar num alvo ou análogo destaca o grupo nos três globos e abre o painel.
- [ ] O painel mostra as categorias, as utilidades, os pontos fortes, os limites e as fontes.
- [ ] Toda a interação funciona também pela lista de locais.
- [ ] README cita todos os datasets e texturas usados.
- [ ] O deploy na Vercel abre sem erros no console e mostra o mesmo que a versão local.
