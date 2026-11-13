# Instruções de desenvolvimento — Visualizador de análogos Terra · Lua · Marte

Projeto para o desafio **Identify Earth Locations that Analog the Permanent Moon Base Locations and Mars**
(NASA Space Apps 2026, 14–15/11/2026).
Documento do desafio: https://claude.ai/artifact/CEd5y9NhnDyDDwbRRJTuE1
Página oficial: https://www.spaceappschallenge.org/2026/challenges/permanent-moon-base-locations-and-mars/

## 1. O que vamos construir

Uma página web com três globos 3D (Terra, Lua e Marte) que mostra os análogos terrestres de locais
candidatos na Lua e em Marte e explica por que eles se parecem e onde a analogia falha.

- **Layout:** a Terra fica grande no centro, com a Lua e Marte como globos menores dos lados.
- **Locais:** cada local candidato na Lua ou em Marte aparece como um ponto no globo dele.
  Os análogos na Terra também são pontos.
- **Arcos:** saem de cada análogo na Terra até o local correspondente na Lua ou em Marte.
  A espessura e a cor do arco mostram o grau de semelhança.
- **Seleção:** ao clicar num local, os três globos destacam o grupo dele e um painel explica a
  semelhança por dimensão: gelo, temperatura, regolito, iluminação e relevo.

O desafio exige dizer **onde a analogia falha**. O painel precisa mostrar isso, não só os pontos fortes.

## 2. Arquitetura

```
pipeline Python  ──gera──▶  web/data/analogs.json  ──lido por──▶  web/index.html (Three.js)
```

- **Python** faz toda a análise: lê os dados da NASA e das outras agências, calcula as semelhanças e
  escreve um único JSON.
- **Front-end** é estático: um HTML que carrega Three.js e lê o JSON. Não há back-end.
- O front-end não calcula semelhança. Se um número aparece na tela, ele veio do JSON.
- **Deploy de testes:** Vercel, como site estático. O `vercel.json` publica só a pasta `web/`, sem build.
  O pipeline não roda na Vercel: gere o `analogs.json` localmente e commite. Cada branch ou PR ganha uma
  URL de preview (ver README).

### Estrutura de pastas

```
.
├── pipeline/                 # Python
│   ├── config.yaml           # pesos das dimensões, lista de alvos, caminhos
│   ├── sources/              # um módulo por fonte de dados (download + leitura)
│   ├── features.py           # extrai as 5 dimensões para cada local
│   ├── similarity.py         # notas por dimensão e nota geral
│   ├── export.py             # monta e valida o analogs.json
│   └── schema.json           # JSON Schema do analogs.json
├── data/
│   ├── raw/                  # downloads (fora do git)
│   └── processed/            # intermediários (fora do git)
├── web/
│   ├── index.html
│   ├── src/
│   │   ├── main.js           # cena, câmera, render loop
│   │   ├── globe.js          # criação de um globo + conversão lat/lon
│   │   ├── arcs.js           # arcos entre corpos
│   │   ├── interaction.js    # raycasting, hover, clique, seleção
│   │   └── panel.js          # painel lateral
│   ├── textures/             # earth.jpg, moon.jpg, mars.jpg
│   └── data/analogs.json     # gerado pelo pipeline (pode ir pro git para a demo)
└── docs/
```

## 3. Contrato de dados: `analogs.json`

Este arquivo é a fronteira entre Python e front-end. Mudanças nele precisam ser combinadas entre os dois lados
e refletidas em `pipeline/schema.json`.

```json
{
  "version": 1,
  "generated_at": "2026-11-14T12:00:00Z",
  "dimensions": [
    { "id": "gelo",        "label": "Gelo / água" },
    { "id": "temperatura", "label": "Temperatura" },
    { "id": "regolito",    "label": "Regolito / materiais" },
    { "id": "iluminacao",  "label": "Iluminação" },
    { "id": "relevo",      "label": "Relevo" }
  ],
  "targets": [
    {
      "id": "moon-shackleton",
      "body": "moon",
      "name": "Borda da cratera Shackleton",
      "lat": -89.9,
      "lon": 0.0,
      "description": "Candidato a base no polo sul lunar."
    }
  ],
  "analogs": [
    {
      "id": "earth-exemplo-1",
      "name": "Local terrestre de exemplo",
      "lat": 75.4,
      "lon": -89.7,
      "description": "Texto curto sobre o local."
    }
  ],
  "links": [
    {
      "analog": "earth-exemplo-1",
      "target": "moon-shackleton",
      "score": 0.72,
      "dimensions": {
        "gelo":        { "score": 0.85, "earth": "permafrost contínuo", "target": "gelo em crateras sombreadas", "note": "..." },
        "temperatura": { "score": 0.40, "earth": "-50 a 10 °C", "target": "-230 a 50 °C", "note": "..." },
        "regolito":    { "score": 0.60, "earth": "...", "target": "...", "note": "..." },
        "iluminacao":  { "score": 0.90, "earth": "sol baixo no horizonte", "target": "sol rasante quase contínuo", "note": "..." },
        "relevo":      { "score": 0.75, "earth": "...", "target": "...", "note": "..." }
      },
      "strengths": ["Iluminação rasante parecida", "Gelo no subsolo"],
      "limits": ["Atmosfera e gravidade terrestres", "Faixa de temperatura bem menor"],
      "exploration_use": "Testar rovers e perfuração em gelo sob luz rasante.",
      "sources": [{ "label": "Nome do dataset", "url": "https://..." }]
    }
  ]
}
```

Regras:

- `lat` em graus, de -90 a 90. `lon` em graus, de -180 a 180, positivo para leste, no sistema de coordenadas
  planetocêntrico de cada corpo. Converta longitudes 0–360 (comuns em dados de Marte) no Python.
- Todas as notas (`score`) ficam entre 0 e 1. A nota geral do link é calculada no Python, como média
  ponderada das dimensões com os pesos do `config.yaml`.
- Uma dimensão sem dado fica de fora do objeto `dimensions`. Nunca invente valor.
- Um análogo pode ter links para mais de um alvo (Lua e Marte).
- `limits` é obrigatório e não pode ser vazio.
- Os valores do exemplo acima são ilustrativos, não são resultado da análise.

## 4. Pipeline Python

- Python 3.11+. Dependências em `requirements.txt` (sugestão: `numpy`, `pandas`, `rasterio`, `xarray`,
  `pyyaml`, `jsonschema`).
- Comando único: `python -m pipeline.export` gera `web/data/analogs.json`.
- Cada dimensão é normalizada para 0–1 antes da comparação. Documente no código de onde vem cada valor
  e qual a fórmula da nota.
- Valide o JSON contra `pipeline/schema.json` antes de escrever o arquivo. Se não validar, o comando falha.
- Cada link guarda em `sources` os datasets usados, para citarmos na entrega.
- Arquivos grandes de `data/raw` e `data/processed` ficam fora do git (`.gitignore`).

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

1. Nome do análogo na Terra → nome do alvo, com a nota geral.
2. Uma barra por dimensão (gelo, temperatura, regolito, iluminação, relevo) com a nota e os valores
   da Terra e do alvo lado a lado.
3. **Pontos fortes** (`strengths`).
4. **Onde a analogia falha** (`limits`), sempre visível.
5. Uso na exploração (`exploration_use`).
6. Fontes dos dados, com links.

Dimensão ausente no JSON aparece como "sem dado", não como zero.

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
7. Pipeline Python gerando o JSON real (em paralelo aos passos 2–6).
8. Lista acessível, ajustes de celular e polimento visual.
9. README com como rodar, fontes de dados e créditos das texturas.

## 7. Critérios de pronto

- [ ] `python -m pipeline.export` gera um JSON válido contra o schema.
- [ ] A página abre com `python -m http.server` sem erros no console.
- [ ] Os pontos de teste caem no lugar certo nos três globos.
- [ ] Todo link do JSON aparece como arco, com largura e cor coerentes com a legenda.
- [ ] Clicar num alvo ou análogo destaca o grupo nos três globos e abre o painel.
- [ ] O painel mostra as 5 dimensões, os pontos fortes, os limites e as fontes.
- [ ] Toda a interação funciona também pela lista de locais.
- [ ] README cita todos os datasets e texturas usados.
- [ ] O deploy na Vercel abre sem erros no console e mostra o mesmo que a versão local.
