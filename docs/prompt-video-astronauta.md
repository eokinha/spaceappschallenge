# Pedido: vídeo-tutorial de 30 s do LACITE com um astronauta no canto

Leia `AGENTS.md`, `skills/animacao-bonecos/SKILL.md`, `rig/RIG.md` e `skills/animacao-bonecos/references/direcao.md`
antes de começar. Este vídeo **não é um episódio do canal**: é o pitch de um projeto do NASA Space Apps Challenge 2026.
Use a esteira do kit (voz com tempo por palavra, boca sincronizada, legenda, render no HyperFrames), mas siga as
regras deste pedido onde elas forem diferentes das do kit.

**Pule as etapas de pauta, roteiro e dublagem do maestro.** O roteiro dos dois idiomas já está pronto (seção 8). A
versão em inglês é narrada a partir do texto em inglês deste pedido, sem tradução feita por você.

Crie o episódio com `python3 ferramentas/novo_episodio.py lacite-tutorial "LACITE: tutorial"`.

**Fonte de verdade do projeto (só leitura, não altere nada lá):**
- Repositório: `/home/lucas/orca/spaceappschallenge`
- Dados que a plataforma exibe: `/home/lucas/orca/spaceappschallenge/web/data/analogs.json`
- Para ver a plataforma: `cd /home/lucas/orca/spaceappschallenge/web && python3 -m http.server 8000` e abra
  `http://localhost:8000`. Use isso só para conferir textos e posições na tela. Feche o servidor no fim.

## 1. O que é o vídeo

Um tutorial curto, de exatamente **30 s em 16:9 (1920x1080)**. A tela inteira mostra a **gravação real da plataforma
LACITE** sendo usada. No canto, dentro de um **círculo**, um **astronauta animado** explica o que está acontecendo,
como um guia. A voz é a dele.

LACITE é uma plataforma web 3D. Ela compara 14 locais da Terra (análogos) com dois alvos de base permanente: o polo
sul da Lua (Shackleton) e a cratera Jezero, em Marte. Para cada local, mostra os pontos fortes e onde a analogia falha
em 19 utilidades de missão. Cada nota pode ser auditada: o card mostra o valor medido, o critério e as fontes.

O vídeo abre mostrando na tela **qual é o problema do desafio** (cartão do desafio, seção 9). Depois vêm quatro
ideias, uma por cena: **o que é**, **pontos fortes e fracos**, **transparência e auditoria** e
**o que muda com o projeto**. No fim, ele passa por um fade para um cartão com os logos **LACITE | NASA Space Apps
Challenge**.

**Tempo total: 30,0 s**, com a narração em 0–28,0 s no máximo e o cartão final logo depois, até 30,0 s. O cartão começa assim que a voz
termina (seção 10): quanto mais curta a narração, mais tempo os logos ficam na tela.

**Entregas:**
- `lacite_tutorial_pt.mp4`: narração em português, legenda em português, gravação da interface em PT.
- `lacite_tutorial_en.mp4`: narração em inglês, legenda em inglês, gravação da interface em EN.
- Os `.srt` dos dois idiomas.

## 2. Regras que substituem as do kit

- **Sem CTA, sem "segue o perfil", sem "comenta aí", sem banner de canal, sem pergunta final.** Não publique em lugar
  nenhum: `publicar.py` não roda.
- **Sem gancho inventado.** O roteiro abaixo é fechado. Não acrescente, não troque e não arredonde nada.
- **Rigor de fatos:** todo número e todo nome que aparece na tela ou na voz precisa estar visível na gravação da
  plataforma, ou estar listado neste pedido. Na dúvida, não coloque. Os números seguem o formato da interface:
  vírgula em PT (23,69 °C) e ponto em EN (23.69 °C).
- **Logotipos:** o único logo de terceiros permitido é o oficial do **NASA Space Apps Challenge**, e só no cartão final
  (seção 10), do jeito que está no arquivo: sem recolorir, distorcer, cortar ou animar partes dele. Nada de "meatball"
  ou "worm" da NASA no astronauta, nos cartões ou em qualquer outro lugar.
- A gravação da plataforma é o conteúdo principal. Ela não pode ser coberta por cartões grandes, com uma única
  exceção: o cartão do desafio na abertura (seção 9). O que for texto na
  tela entra como cartão pequeno ou etiqueta (`R.tag`, `R.chip`), longe do card de detalhes e da lista.
- Um render por vez, feche os processos que abrir e não imprima chaves (regras normais do kit).

## 3. O astronauta (avatar)

- **Quem é:** um astronauta guia, simpático e calmo, com tom de instrutor de missão. Adulto, aparência neutra.
- **Traje:** traje espacial branco de atividade extraveicular, com colar metálico cinza no pescoço e ombros com reforços.
  Detalhes em azul-petróleo (#2a9d8f) e âmbar (#f4a261). No peito, um emblema redondo simples com a palavra
  **LACITE** (sem bandeira e sem logotipo de agência).
- **Capacete:** bolha redonda transparente, com aro metálico e um reflexo suave em diagonal. **O rosto precisa
  aparecer inteiro através do visor**, porque a boca é sincronizada com a voz. Visor dourado levantado no topo do
  capacete (não cobre o rosto).
- **Estilo:** o mesmo estilo chapado em SVG dos bonecos do `rig.js`. O rig só tem `head: "helmet"`, que é um boné.
  Desenhe o capacete-bolha e o traje como camadas SVG novas por cima do `R.person` (corpo `casual` com camisa e
  calça brancas serve de base), dentro do `cenas.js` ou como função nova no rig. Mantenha `R.idle` e `R.speak`
  funcionando: o boneco respira, pisca e mexe a boca durante toda a fala.
- **Enquadramento:** busto (do peito para cima), olhando para a câmera, levemente virado para o centro da tela.
- **Atuação por trecho** (gestos do rig):
  - s01: `wave` no "LACITE" e depois `open`.
  - s02: `pointR` na direção do card quando ele abre. `happy` em "pontos fortes" e `think` em "falha".
  - s03: `chin` e `think` enquanto o detalhe da nota abre, depois `point` em "fontes".
  - s04: `determined`, com `open` em "qualquer pessoa confere".

## 4. O círculo e o layout

**Layout da plataforma na gravação (1920x1080, desktop):**
- Sem local selecionado (trecho A): lista à esquerda (x 0–480) e cena 3D no resto da tela (x 480–1920).
- Com local selecionado (trechos B–D), a tela fica em três faixas fixas: **lista** (x 0–480), **cena 3D** (x 480–960,
  com a Terra, o alvo e o arco) e **card de detalhes** (x 960–1920).

**O círculo do astronauta:**
- **220 px de diâmetro**, com borda de 4 px na cor #2a9d8f, um brilho externo suave e fundo de céu estrelado escuro
  (#0b1020 com estrelas pequenas, sem animação infinita: use `R.rng`).
- Posição: **canto inferior esquerdo, sobre a parte de baixo da lista** (centro em torno de x 150, y 900). Ali ficam
  os últimos colocados da lista, que o vídeo não usa. Araguainha (4º em Marte) e os itens do topo continuam visíveis.
- Ele **nunca entra** na faixa da cena 3D (x 480–960) nem no card (x 960–1920). Também não pode cobrir o marcador de
  Araguainha, o arco nem a legenda do vídeo. Confira em snapshots de cada trecho e ajuste a posição se algo for
  coberto.
- Entrada: o círculo cresce do zero em 0,3 s no quadro 0 (o astronauta já está falando no 0,2 s). Fica até o fade do cartão final.
- Legenda palavra por palavra na parte de baixo, centralizada na tela, com fundo escuro semitransparente e sem
  cobrir o círculo. Ela fica sobre a base do card. Por isso, nos trechos B e C, a gravação deve manter os itens em
  destaque (Geologia de impacto, Frio extremo e o bloco "Por que essa nota aqui") **acima dos 160 px de baixo** da tela.
- Trilha: pad grátis do kit, calmo e baixo (`volume_lufs` -27). Sem efeitos sonoros, exceto um `click.wav` baixinho
  quando o vídeo mostra um clique na plataforma.

## 5. Voz

- Uma voz adulta, calma e clara, com o mesmo timbre nos dois idiomas, se o motor permitir.
- Antes de narrar, **pergunte à pessoa qual motor usar**. O grátis do Linux (espeak) soa robótico. O Kokoro é grátis
  e soa bem melhor (em PT, `pm_alex`). O ElevenLabs gasta créditos e só pode ser usado com o OK da pessoa.
- Depois de narrar, rode o `conferir_voz.py` nos dois idiomas.

## 6. Caminho técnico sugerido

O `montar.py` não coloca vídeo de fundo. Escolha o caminho mais simples que funcione e diga qual usou:

1. **Recomendado:** renderize só o astronauta no círculo, numa composição 1920x1080 com fundo verde liso (#00ff00) fora
   do círculo, com a narração e a sincronia da boca. Depois junte com ffmpeg: gravação da tela no fundo, astronauta
   por cima (chroma key ou máscara circular), legenda queimada e áudio mixado.
2. Alternativa: adapte a montagem do HyperFrames para ter um `<video>` da gravação como camada de fundo.

O tempo da voz manda, com limite de 28,0 s. Ajuste o ritmo da gravação de tela (cortes ou trechos parados) para
acompanhar a voz, nunca o texto. **Se a narração passar de 28,0 s** em algum idioma, mesmo com o `acelerar` do
kit em no máximo 1,10, **pare e avise a pessoa com a duração medida**. Não corte palavras e não encurte o cartão
final por conta própria.

## 7. Gravações de tela (vêm prontas)

A equipe grava a plataforma e coloca os arquivos em `episodios/<slug>/tela/`:
`tela_pt.mp4` (interface em PT) e `tela_en.mp4` (interface em EN), em 1920x1080 e 30 fps. Se faltar algum arquivo,
**pare e peça**. Não tente recriar a interface em SVG nem inventar telas.

Roteiro de cliques que a gravação segue (para sincronizar com a voz):

| Trecho | O que aparece na gravação |
|---|---|
| A · 0–6 s | Visão inicial com os três globos (Terra, Lua, Marte) e o fundo de estrelas. O globo da Terra é girado devagar com o mouse e os marcadores dos locais aparecem. |
| B · 6–14 s | Na lista da esquerda, aba **Mars/Marte** ativa, clique em **Araguainha**. O globo foca no Brasil, o arco liga Araguainha a Marte (Jezero) e o card abre à direita. O card rola devagar por **Strengths of the analogy / Pontos fortes da analogia**, com **Impact geology / Geologia de impacto** em destaque (nota 3), e depois por **Where the analogy fails / Onde a analogia falha**, parando em **Extreme cold / Frio extremo** (nota 0). Não destaque **Hidrotermalismo de impacto**, porque a própria base marca essa nota como "a verificar". |
| C · 14–23 s | Clique em **Frio extremo** para abrir **Why this rating here / Por que essa nota aqui**. A gravação para alguns segundos para mostrar: temperatura média de **23,69 °C** em Araguainha contra **≈−55 °C** em Jezero, a regra da nota (**nota 3 se ≤ −45 °C · 2 se ≤ −25 · 1 se ≤ −10**), os datasets de referência **MODIS LST** (Terra) e **MEDA** (Marte) e a fonte **NASA POWER** com o selo NASA. Depois, abra **Geologia de impacto** para mostrar a fonte **Lana et al. 2007, GSA Bulletin** com o selo **Peer-reviewed / Artigo revisado**. Use os números exatamente como aparecem na tela. |
| D · 23 s até o fim da voz | Feche o detalhe e volte à visão do card com os dois lados: pontos fortes e onde falha. A câmera dos globos volta devagar para a visão com os três globos. |

## 8. Roteiro fechado

Use exatamente este texto. As frases-âncora das cenas são o começo de cada linha.

### Português (cerca de 76 palavras)

| Cena | Trecho | Ideia | Narração |
|---|---|---|---|
| s01 | A | o que é | O LACITE compara 14 locais da Terra com a Lua e Marte em 19 utilidades de missão. |
| s02 | B | pontos fortes e fracos | Em Araguainha, no Brasil, ele mostra onde a analogia com Marte é forte, como geologia de impacto, e onde falha, como frio extremo. |
| s03 | C | auditoria | E tudo é auditável: cada nota mostra o valor medido, o critério e as fontes, de dados da NASA a artigos revisados. |
| s04 | D | o que muda | Assim, escolher onde testar cada parte da missão se apoia em dados que qualquer pessoa confere. |

### Inglês

| Cena | Trecho | Narração |
|---|---|---|
| s01 | A | LACITE compares 14 places on Earth with the Moon and Mars across 19 mission uses. |
| s02 | B | At Araguainha, in Brazil, it shows where the Mars analogy is strong, like impact geology, and where it fails, like extreme cold. |
| s03 | C | And it's all auditable: every score shows the measured value, the rating rule and the sources, from NASA data to peer-reviewed papers. |
| s04 | D | So choosing where to test each part of a mission rests on data anyone can check. |

Pronúncia: "LACITE" se fala **la-SÍ-te** nos dois idiomas. "Araguainha" se fala **a-ra-gua-Í-nha**, também na
versão em inglês. Adicione essas palavras ao `modelos/palavras-problema.json` se a voz errar, e confira com o
`conferir_voz.py`.

## 9. Textos curtos na tela (os únicos permitidos)

| Trecho | Texto PT | Texto EN | Posição |
|---|---|---|---|
| A (0–4 s) | cartão do desafio (abaixo) | cartão do desafio (abaixo) | sobre a área dos globos, no alto |
| A (4 s até o fim da cena) | `14 análogos · 2 alvos` | `14 analogs · 2 targets` | etiqueta no alto, centro |
| B | `Araguainha × Marte · pontos fortes · onde falha` | `Araguainha × Mars · strengths · where it fails` | etiqueta no alto, centro |
| C | `valor medido · critério · fontes` | `measured value · rating rule · sources` | etiqueta no alto, centro |
| D | `dados que qualquer pessoa pode conferir` | `data anyone can check` | etiqueta no alto, centro |

### Cartão do desafio (o problema), de 0 a 4 s

É o único texto que diz qual é o problema. Ele não tem narração: a voz da cena s01 começa normalmente por cima dele.

| Linha | PT | EN |
|---|---|---|
| Rótulo pequeno, em maiúsculas, cor #2a9d8f | `DESAFIO · NASA SPACE APPS CHALLENGE 2026` | `CHALLENGE · NASA SPACE APPS CHALLENGE 2026` |
| Título, branco, em destaque, entre aspas | `"Identify Earth Locations that Analog the Permanent Moon Base Locations and Mars"` | igual |
| Tradução, menor, cinza-claro (só PT) | `Identificar locais na Terra análogos aos locais de base permanente na Lua e em Marte` | (sem esta linha) |

- O título oficial fica **em inglês nas duas versões**, exatamente como está escrito acima. É o nome oficial do
  desafio, igual ao título da página da plataforma.
- Visual: painel escuro semitransparente (#0b1020 com 80% de opacidade), cantos arredondados e borda fina
  #2a9d8f, com até 1100 px de largura, centralizado na área da cena 3D (x 480–1920, centro em x 1200) e na parte de cima dela. Ele não
  cobre a lista da esquerda nem o globo da Terra inteiro.
- **Já aparece no quadro 0**, sem fade do preto, porque esse é o quadro de capa. Em 3,6 s, ele sobe 20 px e some em
  0,4 s, e a etiqueta `14 análogos · 2 alvos` entra.
- Não acrescente frases sobre o problema além destas três linhas.

No trecho C, a gravação já mostra os números. Não repita números nas etiquetas e não amplie partes do card com
números que não estejam legíveis na gravação. Um zoom suave de câmera sobre o bloco "Por que essa nota aqui" é
permitido, desde que o texto continue nítido.

## 10. Cartão final com os logos (do fim da voz até 30,0 s)

**Arquivos (copie para `episodios/lacite-tutorial/marca/`, sem editar os originais):**
- LACITE: `/home/lucas/orca/spaceappschallenge/db12fc78-0d04-497a-8122-61c67c801d5f.jpeg` (1254x1254, branco
  sobre fundo preto). Não use o `web/images/logos/lacite.png`, porque ele tem só 160x192 px e fica borrado ampliado.
- NASA Space Apps Challenge: `/home/lucas/orca/spaceappschallenge/web/images/logos/nasa-space-apps.png` (440x172,
  branco com "NASA" em vermelho, fundo transparente).

**Animação:**
Chame de **T** o momento em que a última palavra da narração termina, mais 0,1 s. A transição é rápida para deixar
espaço à voz:
1. Em T, a gravação da tela e o círculo do astronauta fazem fade para preto (#000000) em **0,3 s**. A legenda já
   terminou nesse ponto.
2. Em T + 0,2 s, os dois logos fazem fade in juntos em **0,3 s** (opacidade de 0 a 1, com escala de 0,97 a 1,0,
   ease suave).
3. Dali até 30,0 s, os logos ficam parados na tela, **com no mínimo 1,4 s totalmente visíveis**. O vídeo termina no
   cartão, sem fade out.
4. A trilha baixa até sumir no último 1,0 s. Sem voz e sem efeito sonoro no cartão.

Com a narração no limite de 28,0 s, T = 28,1 s e os logos ficam totalmente visíveis de 28,6 s a 30,0 s.

**Layout (tela 1920x1080, fundo #000000):**
- Os dois logos ficam lado a lado e centralizados na tela, nesta ordem: **LACITE | NASA Space Apps**.
- LACITE com cerca de 360 px de altura. O fundo preto do jpeg se funde ao fundo do cartão, então não pode ter borda
  visível: confira num snapshot e, se aparecer emenda, use `mix-blend-mode: screen` ou recorte o fundo.
- Space Apps com 440 px de largura (tamanho original, sem ampliar).
- Entre os dois, uma linha vertical branca de 2 px, com 50% de opacidade e cerca de 200 px de altura, com 80 px de
  espaço para cada lado.
- Os dois logos ficam alinhados pelo centro vertical. Nenhum texto extra no cartão.

## 11. Conferência antes de entregar

- [ ] Duração de 30,0 s (±0,3 s) nos dois idiomas, com a narração terminando até 28,0 s.
- [ ] O cartão final entra logo após a voz, com fade rápido e os logos visíveis por no mínimo 1,4 s, com os dois logos nítidos, sem emenda do fundo do jpeg e sem
      distorção.
- [ ] Boca do astronauta sincronizada, sem ficar parada durante a fala, e o rosto visível o tempo todo.
- [ ] O círculo fica só sobre a parte de baixo da lista e não cobre a cena 3D, o card, o arco, Araguainha na lista nem a legenda em nenhum quadro (snapshots em 3, 10, 18 e 27 s). No trecho C, ele também não pode cobrir o bloco "Por que essa nota aqui".
- [ ] Todo número na tela é igual ao que aparece na gravação da plataforma naquele momento.
- [ ] O cartão do desafio aparece no quadro 0, com o título oficial exatamente igual ao deste pedido.
- [ ] Nenhum logotipo da NASA, nenhum CTA, nenhuma frase fora do roteiro.
- [ ] Legenda igual à narração, palavra por palavra.
- [ ] Mostre os snapshots e os dois mp4 para a pessoa antes de considerar pronto.
