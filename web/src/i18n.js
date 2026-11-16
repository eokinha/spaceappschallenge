// Idioma da página: inglês por padrão, com troca para pt-BR pelo botão do cabeçalho.
// Os textos da interface nascem em português no código e passam por t(); em inglês, t() consulta EN abaixo.
// Os textos que vêm do analogs.json são trocados de uma vez por translateData(), com o dicionário
// data/i18n-en.json (português → inglês). Sem tradução, o texto fica em português.
// Trocar de idioma recarrega a página (a seleção atual é guardada e restaurada pelo main.js).

const STORE_KEY = 'analogs-lang';
const RESTORE_KEY = 'analogs-lang-restore';
export const LANGS = ['en', 'pt'];

function initialLang() {
  try {
    const saved = localStorage.getItem(STORE_KEY);
    if (LANGS.includes(saved)) return saved;
  } catch { /* sem armazenamento: fica o padrão */ }
  return 'en';
}

export const lang = initialLang();
export const locale = lang === 'pt' ? 'pt-BR' : 'en-US';

const EN = {
  // index.html / main.js
  'Análogos Terra · Lua · Marte': 'Earth · Moon · Mars Analogs',
  '{t} alvos · {a} análogos · {l} ligações': '{t} targets · {a} analogs · {l} links',
  'Erro ao carregar os dados. Veja o console.': 'Error loading the data. See the console.',
  'Arco:': 'Arc:',
  'cor = patamar · espessura = nota': 'color = tier · thickness = rating',
  'Aderência (0 a 3):': 'Adherence (0 to 3):',
  // format.js
  'a medir': 'to be measured',
  'Lua': 'Moon', 'Marte': 'Mars', 'da Lua': 'for the Moon', 'de Marte': 'for Mars', 'de {name}': 'for {name}',
  ' e ': ' and ',
  '{rank} de {total}': '{rank} of {total}',
  'Forte': 'Strong', 'Forte analogia': 'Strong analogy', '2 a 3': '2 to 3',
  'Parcial': 'Partial', 'Analogia parcial': 'Partial analogy', 'entre 1 e 2': 'between 1 and 2',
  'Fraca': 'Weak', 'Baixa aderência': 'Low adherence', '0 a 1': '0 to 1',
  'A medir': 'To be measured', 'sem dado': 'no data',
  'nota 3 se {a} · 2 se {b} · 1 se {c}': 'rated 3 if {a} · 2 if {b} · 1 if {c}',
  'Missão NASA': 'NASA mission',
  'Artigo revisado': 'Peer-reviewed',
  'Órgão público': 'Public agency',
  'Planilha': 'Spreadsheet',
  'Documento, dado ou página oficial da NASA': 'Official NASA document, dataset or page',
  'Artigo revisado por pares com dados de missão da NASA': 'Peer-reviewed paper with NASA mission data',
  'Artigo científico revisado por pares': 'Peer-reviewed scientific paper',
  'Órgão público ou repositório científico (NPS, USGS, SGB, PANGAEA)':
    'Public agency or scientific repository (NPS, USGS, SGB, PANGAEA)',
  'Planilha da equipe': 'Team spreadsheet',
  // list.js
  'Alvo da comparação': 'Comparison target',
  ' (empate)': ' (tie)',
  'listado': 'listed',
  'aderência ': 'adherence ',
  'Locais análogos na Terra': 'Analog sites on Earth',
  'Ordenados pela aderência a {name}. Nota de 0 a 3.': 'Ranked by adherence to {name}. Rated 0 to 3.',
  'Empate: outro local tem a mesma aderência': 'Tie: another site has the same adherence',
  'Listado pela equipe como análogo {of}': 'Listed by the team as an analog {of}',
  // panel.js
  '≈ Coordenada aproximada: o ponto no globo é só indicativo.':
    '≈ Approximate coordinates: the point on the globe is only indicative.',
  'Recolher o card': 'Collapse the card',
  'Expandir o card': 'Expand the card',
  'Fechar o card': 'Close the card',
  'utilidade': 'utility', 'utilidades': 'utilities',
  '{n} de {total} {word}': '{n} of {total} {word}',
  'nenhuma utilidade avaliada': 'no utility assessed',
  'melhor da rede': 'best in the network',
  'Leitura da equipe para esta utilidade (base v1.1): ': 'Team reading for this utility (base v1.1): ',
  'Terra: {v}': 'Earth: {v}',
  'nota {n}': 'rated {n}',
  'sem faixa': 'no thresholds',
  'No alvo: {v}': 'At the target: {v}',
  'Fontes da variável no Catálogo da base (não só deste local):':
    "Sources for the variable in the base's Catalog (not only for this site):",
  'Fonte:': 'Source:', 'Fontes:': 'Sources:',
  'Dataset de referência — {v}': 'Reference dataset — {v}',
  'Leitura da equipe — {label}': 'Team reading — {label}',
  'O que mede': 'What it measures',
  'Em {target}: ': 'On {target}: ',
  'Critério: ': 'Criterion: ',
  'Por que essa nota aqui': 'Why this rating here',
  'Sem variável medida.': 'No measured variable.',
  'Ainda a medir: {list}.': 'Still to be measured: {list}.',
  'Leitura da equipe (base v1.1): ': 'Team reading (base v1.1): ',
  'Recolher todos': 'Collapse all', 'Expandir todos': 'Expand all',
  'A equipe listou este local como análogo {of}. ': 'The team listed this site as an analog {of}. ',
  'Ver {target}': 'View {target}',
  'Veredito para {name}': 'Verdict for {name}',
  'aderência': 'adherence',
  'posição na rede': 'rank in the network',
  'Empate: outro local tem a mesma aderência para este alvo; a ordem entre eles segue a da planilha.':
    'Tie: another site has the same adherence for this target; their order follows the spreadsheet.',
  'Melhor da rede em {n} {word}.': 'Best in the network in {n} {word}.',
  'Para referência: a escala vai de 0 a 3 e o 1º colocado para {target} ({name}) tem {value}.':
    'For reference: the scale runs from 0 to 3 and the top-ranked site for {target} ({name}) has {value}.',
  'Por que é análogo': 'Why it is an analog',
  'Na planilha: ': 'In the spreadsheet: ',
  'Recorte usado: ': 'Study area: ',
  'Sobre os dados: ': 'About the data: ',
  'Pontos fortes da analogia': 'Strengths of the analogy',
  'Nenhuma utilidade com nota ≥ 2 para este alvo.': 'No utility rated ≥ 2 for this target.',
  'Onde a analogia falha': 'Where the analogy fails',
  'Nenhuma falha registrada.': 'No failure recorded.',
  'Ainda a medir': 'Still to be measured',
  'Sem dado ainda: não entram na média e não valem zero.':
    'No data yet: they are left out of the average and do not count as zero.',
  'Desempenho por categoria': 'Performance by category',
  'Fora da nota': 'Outside the rating',
  'Não entra na aderência: vale para qualquer lugar da Terra.':
    'Not part of the adherence: it applies anywhere on Earth.',
  'Uso na exploração': 'Use in exploration',
  'Utilidades': 'Utilities',
  'fora da nota': 'outside the rating',
  'Fontes dos dados deste local': 'Data sources for this site',
  'Ampliar a foto: {caption}': 'Enlarge the photo: {caption}',
  'Ampliar a foto': 'Enlarge the photo',
  'Imagem de satélite': 'Satellite image',
  'Imagem: ': 'Image: ', 'Foto: ': 'Photo: ',
  'fonte': 'source',
  'Sem ligação com {name} nos dados: {v}.': 'No link to {name} in the data: {v}.',
  // help.js
  'Como navegar': 'How to navigate', 'Fechar a ajuda': 'Close help',
  'Mouse': 'Mouse', 'Teclado': 'Keyboard', 'Gestos': 'Gestures', 'Botões': 'Buttons',
  'Arrastar sobre um globo': 'Drag on a globe', 'gira só aquele globo': 'rotates only that globe',
  'Arrastar no vazio': 'Drag on empty space',
  'gira a cena inteira, com os três globos juntos': 'rotates the whole scene, all three globes together',
  '+ arrastar, ou botão direito': '+ drag, or right button',
  'desloca a cena para os lados': 'pans the scene sideways',
  'Roda do mouse': 'Mouse wheel', 'aproxima ou afasta (zoom)': 'zooms in or out',
  'Clique num ponto da Terra': 'Click a point on Earth',
  'seleciona o local, gira até ele e abre os detalhes': 'selects the site, rotates to it and opens the details',
  'Clique no ponto da Lua ou de Marte': 'Click the point on the Moon or Mars',
  'troca o alvo da comparação': 'switches the comparison target',
  'Clique no vazio': 'Click empty space', 'fecha a seleção': 'clears the selection',
  'Duplo clique no vazio ou': 'Double-click empty space or', 'volta à vista padrão': 'returns to the default view',
  'passa pela lista de locais, pelos botões e pelo card': 'moves through the site list, the buttons and the card',
  'percorrem a lista de locais': 'move through the site list',
  'Espaço': 'Space', 'seleciona o local destacado': 'selects the highlighted site',
  'trocam a aba Lua | Marte do card': 'switch the card\'s Moon | Mars tab',
  'fecha esta ajuda, a foto ampliada ou o card': 'closes this help, the enlarged photo or the card',
  'Um dedo sobre um globo': 'One finger on a globe', 'Um dedo no vazio': 'One finger on empty space',
  'Pinça (dois dedos)': 'Pinch (two fingers)',
  'afaste os dedos para aproximar e junte para afastar': 'spread your fingers to zoom in, pinch them to zoom out',
  'Arrastar com dois dedos': 'Drag with two fingers',
  'Tocar num ponto da Terra': 'Tap a point on Earth',
  'seleciona o local e abre os detalhes embaixo': 'selects the site and opens the details below',
  'Tocar no ponto da Lua ou de Marte': 'Tap the point on the Moon or Mars',
  'Tocar no vazio': 'Tap empty space', 'Toque duplo no vazio ou': 'Double-tap empty space or',
  'Locais': 'Sites',
  'abre a lista dos análogos; escolher um item fecha a lista': 'opens the list of analogs; picking one closes it',
  'expande ou recolhe o card de detalhes': 'expands or collapses the details card',
  'fecha o card ou a foto': 'closes the card or the photo',
  'Sem local selecionado, a vista volta sozinha ao padrão depois de 10 s sem mexer na cena.':
    'With no site selected, the view returns to the default on its own after 10 s without touching the scene.',
  // lightbox.js
  'Foto ampliada': 'Enlarged photo',
  'Fechar a foto': 'Close the photo',
};

/** Texto da interface no idioma ativo. A chave é o texto em português; `{nome}` é trocado por vars.nome. */
export function t(text, vars) {
  const out = lang === 'en' ? (EN[text] ?? text) : text;
  return vars ? out.replace(/\{(\w+)\}/g, (m, k) => (k in vars ? String(vars[k]) : m)) : out;
}

/** "1º" em português; "1st", "2nd", "3rd", "4th" em inglês. */
export function ordinal(n) {
  if (lang === 'pt') return `${n}º`;
  const tens = n % 100;
  const suffix = tens >= 11 && tens <= 13 ? 'th' : ({ 1: 'st', 2: 'nd', 3: 'rd' }[n % 10] ?? 'th');
  return `${n}${suffix}`;
}

// Campos de texto do analogs.json que têm tradução (os demais são ids, códigos e URLs usados pelo código).
// A mesma lista está em tests/test_i18n.py.
const DATA_KEYS = new Set(['name', 'short_name', 'full_name', 'country', 'description', 'narrative', 'clipping',
  'batch', 'alt', 'caption', 'license', 'author', 'data_notes', 'reading', 'purpose', 'condition', 'criterion',
  'variable', 'unit', 'target_value', 'dataset_earth', 'dataset_target', 'label', 'text', 'to_measure',
  'exploration_use', 'observation', 'value_note', 'scale', 'conclusions', 'caveats']);

/** Troca, no próprio objeto, os textos do analogs.json pelos do dicionário (português → idioma ativo). */
export function translateData(node, dict, key = null) {
  if (Array.isArray(node)) {
    node.forEach((item, i) => {
      if (typeof item === 'string') { if (DATA_KEYS.has(key)) node[i] = dict[item] ?? item; }
      else translateData(item, dict, key);
    });
  } else if (node && typeof node === 'object') {
    for (const [k, value] of Object.entries(node)) {
      if (typeof value === 'string') { if (DATA_KEYS.has(k)) node[k] = dict[value] ?? value; }
      else translateData(value, dict, k);
    }
  }
  return node;
}

/** Guarda o idioma e recarrega; `restore` (a seleção atual) volta depois da recarga por takeRestore(). */
export function setLang(next, restore) {
  if (!LANGS.includes(next) || next === lang) return;
  try {
    localStorage.setItem(STORE_KEY, next);
    if (restore) sessionStorage.setItem(RESTORE_KEY, JSON.stringify(restore));
  } catch { /* sem armazenamento a troca não persiste */ }
  location.reload();
}

export function takeRestore() {
  try {
    const raw = sessionStorage.getItem(RESTORE_KEY);
    sessionStorage.removeItem(RESTORE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch { return null; }
}

/**
 * Textos fixos do index.html: o HTML já vem em inglês (o padrão), com o português em `data-pt`
 * (texto), `data-pt-title` e `data-pt-aria-label`. Aqui só se aplica o português quando ele é o idioma ativo.
 * O título da aba é o nome do desafio, igual nos dois idiomas, então não é traduzido.
 */
export function applyStaticTexts() {
  document.documentElement.lang = lang === 'pt' ? 'pt-BR' : 'en';
  if (lang !== 'pt') return;
  for (const node of document.querySelectorAll('[data-pt]')) node.textContent = node.dataset.pt;
  for (const node of document.querySelectorAll('[data-pt-title]')) node.title = node.dataset.ptTitle;
  for (const node of document.querySelectorAll('[data-pt-aria-label]')) node.setAttribute('aria-label', node.dataset.ptAriaLabel);
}
