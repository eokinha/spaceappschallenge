import { el } from './dom.js';
import { t } from './i18n.js';

// Ajuda "Como navegar" (botão "?" do cabeçalho, ao lado do EN | PT). Usa <dialog> nativo, como o
// lightbox.js: prende o foco, fecha com Esc, com o ✕ e com clique fora da caixa.
// O conteúdo segue o ponteiro principal na hora de abrir: toque (gestos) ou mouse e teclado (atalhos).

let dialog;

const isTouch = () => window.matchMedia('(pointer: coarse)').matches;

/** Uma linha da ajuda: o gesto/atalho à esquerda e o que ele faz à direita. */
function row(keys, what) {
  const how = el('dt');
  keys.forEach((part, i) => {
    if (i) how.append(' ');
    how.append(part.startsWith('#') ? el('kbd', {}, part.slice(1)) : part);
  });
  return [how, el('dd', {}, what)];
}

function section(title, rows) {
  return el('section', {}, el('h3', {}, title), el('dl', { class: 'help-list' }, rows.flatMap(([k, w]) => row(k, w))));
}

// "#Ctrl" vira <kbd>Ctrl</kbd>; o resto é texto.
function desktopContent() {
  return [
    section(t('Mouse'), [
      [[t('Arrastar sobre um globo')], t('gira só aquele globo')],
      [[t('Arrastar no vazio')], t('gira a cena inteira, com os três globos juntos')],
      [['#Ctrl', '/', '#Shift', '/', '#⌘', t('+ arrastar, ou botão direito')], t('desloca a cena para os lados')],
      [[t('Roda do mouse')], t('aproxima ou afasta (zoom)')],
      [[t('Clique num ponto da Terra')], t('seleciona o local, gira até ele e abre os detalhes')],
      [[t('Clique no ponto da Lua ou de Marte')], t('troca o alvo da comparação')],
      [[t('Clique no vazio')], t('fecha a seleção')],
      [[t('Duplo clique no vazio ou'), '#⟲'], t('volta à vista padrão')],
    ]),
    section(t('Teclado'), [
      [['#Tab', '/', '#Shift', '#Tab'], t('passa pela lista de locais, pelos botões e pelo card')],
      [['#↑', '#↓', '#Home', '#End'], t('percorrem a lista de locais')],
      [['#Enter', '/', '#' + t('Espaço')], t('seleciona o local destacado')],
      [['#←', '#→'], t('trocam a aba Lua | Marte do card')],
      [['#Esc'], t('fecha esta ajuda, a foto ampliada ou o card')],
    ]),
  ];
}

function touchContent() {
  return [
    section(t('Gestos'), [
      [[t('Um dedo sobre um globo')], t('gira só aquele globo')],
      [[t('Um dedo no vazio')], t('gira a cena inteira, com os três globos juntos')],
      [[t('Pinça (dois dedos)')], t('afaste os dedos para aproximar e junte para afastar')],
      [[t('Arrastar com dois dedos')], t('desloca a cena para os lados')],
      [[t('Tocar num ponto da Terra')], t('seleciona o local e abre os detalhes embaixo')],
      [[t('Tocar no ponto da Lua ou de Marte')], t('troca o alvo da comparação')],
      [[t('Tocar no vazio')], t('fecha a seleção')],
      [[t('Toque duplo no vazio ou'), '#⟲'], t('volta à vista padrão')],
    ]),
    section(t('Botões'), [
      [['#' + t('Locais')], t('abre a lista dos análogos; escolher um item fecha a lista')],
      [['#▴', '/', '#▾'], t('expande ou recolhe o card de detalhes')],
      [['#✕'], t('fecha o card ou a foto')],
    ]),
  ];
}

function ensureDialog() {
  if (dialog) return dialog;
  dialog = el('dialog', { class: 'help', 'aria-labelledby': 'help-title' });
  dialog.addEventListener('click', (event) => { if (event.target === dialog) dialog.close(); });
  dialog.addEventListener('close', () => document.getElementById('help-btn')?.setAttribute('aria-expanded', 'false'));
  document.body.append(dialog);
  return dialog;
}

export function openHelp() {
  const d = ensureDialog();
  const close = el('button', { type: 'button', class: 'icon-btn help-close', 'aria-label': t('Fechar a ajuda'),
    onclick: () => d.close() }, '✕');
  d.replaceChildren(el('div', { class: 'help-box' },
    close,
    el('h2', { id: 'help-title' }, t('Como navegar')),
    ...(isTouch() ? touchContent() : desktopContent()),
    el('p', { class: 'muted help-note' },
      t('Sem local selecionado, a vista volta sozinha ao padrão depois de 10 s sem mexer na cena.'))));
  d.showModal();
  document.getElementById('help-btn')?.setAttribute('aria-expanded', 'true');
  close.focus();
}

export const isHelpOpen = () => !!dialog?.open;

export function wireHelp() {
  document.getElementById('help-btn')?.addEventListener('click', openHelp);
}
