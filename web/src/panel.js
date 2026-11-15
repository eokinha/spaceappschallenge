import { el } from './dom.js';
import { openLightbox } from './lightbox.js';
import {
  A_MEDIR, barWidth, fmtNoteOutOf3, fmtOutOf3, fmtRank, plural, targetOf, targetShort, targetsOf,
} from './format.js';

// Card de detalhes do local selecionado (direita; gaveta no celular). Não é modal.
// O cabeçalho e as abas são criados uma vez; só o corpo é refeito a cada mudança de seleção.

/**
 * @param {object} opts
 * @param {HTMLElement} opts.root   #panel
 * @param {object} opts.data        analogs.json
 * @param {(analogId: string, targetId: string) => object | undefined} opts.linkOf
 * @param {ReturnType<import('./selection.js').createSelection>} opts.selection
 * @param {() => void} [opts.onLayout]  o card abriu, fechou ou mudou de tamanho
 */
export function createPanel({ root, data, linkOf, selection, onLayout }) {
  const analogById = new Map(data.analogs.map((a) => [a.id, a]));
  const targetById = new Map(data.targets.map((t) => [t.id, t]));
  const total = data.analogs.length;
  // Seções recolhíveis: lembram se o usuário abriu, mesmo trocando de local ou de aba.
  const open = { utilities: false, sources: false };

  const title = el('h2', { id: 'panel-title' });
  const subtitle = el('p', { class: 'card-sub' });
  const approx = el('p', { class: 'card-approx', hidden: true }, '≈ Coordenada aproximada: o ponto no globo é só indicativo.');
  const expand = el('button', { type: 'button', class: 'icon-btn card-expand', 'aria-expanded': 'false',
    onclick: () => {
      const expanded = root.classList.toggle('is-expanded');
      expand.setAttribute('aria-expanded', String(expanded));
      expand.textContent = expanded ? '▾' : '▴';
      expand.setAttribute('aria-label', expanded ? 'Recolher o card' : 'Expandir o card');
    } }, '▴');
  expand.setAttribute('aria-label', 'Expandir o card');
  const close = el('button', { type: 'button', class: 'icon-btn', 'aria-label': 'Fechar o card',
    onclick: () => selection.clear() }, '✕');

  const tabs = new Map();
  const tablist = el('div', { class: 'tabs', role: 'tablist', 'aria-label': 'Alvo da comparação' },
    data.targets.map((t) => {
      const badge = el('span', { class: 'tag tag-listed', hidden: true }, 'listado');
      const tab = el('button', { type: 'button', role: 'tab', class: 'tab', id: `tab-${t.id}`,
        'aria-controls': 'panel-body', 'aria-selected': 'false',
        onclick: () => selection.setTarget(t.id) }, targetShort(t), ' ', badge);
      tabs.set(t.id, { tab, badge });
      return tab;
    }));
  tablist.addEventListener('keydown', (event) => {
    if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
    const ids = data.targets.map((t) => t.id);
    const step = event.key === 'ArrowRight' ? 1 : -1;
    const next = ids[(ids.indexOf(selection.state.targetId) + step + ids.length) % ids.length];
    selection.setTarget(next);
    tabs.get(next).tab.focus();
    event.preventDefault();
  });

  const body = el('div', { class: 'card-body', id: 'panel-body', role: 'tabpanel', tabindex: '0' });

  root.removeAttribute('aria-live');
  root.setAttribute('aria-labelledby', 'panel-title');
  root.hidden = true;
  const photo = el('figure', { class: 'card-photo', hidden: true });
  root.replaceChildren(
    photo,
    el('div', { class: 'card-head' },
      el('div', { class: 'card-title' }, title, subtitle, approx),
      el('div', { class: 'card-actions' }, expand, close)),
    tablist, body);

  const section = (heading, attrs, ...children) =>
    el('section', { class: 'sec', ...attrs }, el('h3', {}, heading), ...children);
  const bullets = (texts, cls) => el('ul', { class: cls ?? 'bullets' }, texts.map((t) => el('li', {}, t)));

  /** Uma linha "rótulo · barra · nota · N de M utilidades"; categoria ausente = "a medir". */
  function dimensionRow(dim, value) {
    return el('div', { class: `dim${value ? '' : ' is-unmeasured'}` },
      el('span', { class: 'dim-label' }, dim.label),
      el('span', { class: 'bar', 'aria-hidden': 'true' }, el('span', { class: 'bar-fill', style: `width:${barWidth(value?.score)}` })),
      el('span', { class: 'dim-note' }, value ? fmtOutOf3(value.adherence) : A_MEDIR),
      el('span', { class: 'dim-count' },
        value ? `${value.evaluated} de ${value.total} ${plural(value.total, 'utilidade', 'utilidades')}` : 'nenhuma utilidade avaliada'));
  }

  function utilityRow(u) {
    const measured = u.adherence != null && u.status !== 'a_medir';
    return el('li', { class: `util${measured ? '' : ' is-unmeasured'}` },
      el('div', { class: 'util-line' },
        el('span', { class: 'util-id' }, u.id),
        el('span', { class: 'util-name' }, u.name),
        u.best_in_network ? el('span', { class: 'tag tag-best' }, 'melhor da rede') : null,
        el('span', { class: 'util-note' }, measured ? fmtNoteOutOf3(u.adherence) : A_MEDIR)),
      u.reading
        ? el('p', { class: 'util-reading' },
            el('span', { class: 'util-reading-label' }, 'Leitura da equipe para esta utilidade (base v1.1): '), u.reading)
        : null);
  }

  function renderBody(analog, target, link) {
    const parts = [];

    // Aviso discreto quando o card está num alvo em que a equipe não listou o local.
    const listed = (analog.listed_as ?? []).filter((id) => targetById.has(id));
    if (!link.listed_as_target && listed.length) {
      parts.push(el('p', { class: 'listed-elsewhere' },
        `A equipe listou este local como análogo ${targetsOf(listed, targetById)}. `,
        listed.map((id) => el('button', { type: 'button', class: 'link-btn', onclick: () => selection.setTarget(id) },
          `Ver ${targetShort(targetById.get(id))}`))));
    }

    // 1. Por que é análogo
    parts.push(section('Por que é análogo', {},
      analog.description ? el('p', {}, analog.description) : null,
      analog.clipping ? el('p', { class: 'kv' }, el('span', { class: 'k' }, 'Recorte usado: '), analog.clipping) : null,
      analog.data_notes ? el('p', { class: 'kv' }, el('span', { class: 'k' }, 'Sobre os dados: '), analog.data_notes) : null));

    // 2. Veredito
    const best = data.links.find((l) => l.target === target.id && l.rank === 1);
    const bestAnalog = best ? analogById.get(best.analog) : null;
    const n = link.best_in_network_count;
    parts.push(section(`Veredito para ${target.name}`, { class: 'sec verdict' },
      el('div', { class: 'verdict-row' },
        el('div', { class: 'verdict-main' },
          el('span', { class: 'verdict-value' }, fmtOutOf3(link.adherence)),
          el('span', { class: 'verdict-cap' }, 'aderência')),
        el('div', { class: 'verdict-main' },
          el('span', { class: 'verdict-value' }, fmtRank(link.rank, total)),
          el('span', { class: 'verdict-cap' }, 'posição na rede'))),
      el('span', { class: 'bar bar-lg', 'aria-hidden': 'true' }, el('span', { class: 'bar-fill', style: `width:${barWidth(link.score)}` })),
      link.rank_tied
        ? el('p', { class: 'muted' }, 'Empate: outro local tem a mesma aderência para este alvo; a ordem entre eles segue a da planilha.')
        : null,
      n != null ? el('p', {}, `Melhor da rede em ${n} ${plural(n, 'utilidade', 'utilidades')}.`) : null,
      best && bestAnalog
        ? el('p', { class: 'muted' },
            `Para referência: a escala vai de 0 a 3 e o 1º colocado para ${targetShort(target)} ` +
            `(${bestAnalog.name}) tem ${fmtOutOf3(best.adherence)}.`)
        : null,
      analog.matches_listing === false && listed.length
        ? el('p', { class: 'notice' },
            `A equipe listou este local como análogo ${targetsOf(listed, targetById)}, mas o modelo indica ` +
            `${targetById.has(analog.model_indicates) ? targetShort(targetById.get(analog.model_indicates)) : analog.model_indicates}.`)
        : null));

    // 3. Por categoria
    const inScore = data.dimensions.filter((d) => d.in_score);
    const outOfScore = data.dimensions.filter((d) => !d.in_score);
    parts.push(section('Por categoria', {},
      el('div', { class: 'dims' }, inScore.map((d) => dimensionRow(d, link.dimensions?.[d.id]))),
      outOfScore.length
        ? el('div', { class: 'dims dims-out' },
            el('p', { class: 'dims-out-title' }, 'Fora da nota'),
            outOfScore.map((d) => dimensionRow(d, link.dimensions?.[d.id])),
            el('p', { class: 'muted' }, 'Não entra na aderência: vale para qualquer lugar da Terra.'))
        : null));

    // 4. Pontos fortes
    parts.push(section('Pontos fortes', {},
      link.strengths?.length ? bullets(link.strengths) : el('p', { class: 'muted' }, 'Nenhum ponto forte registrado para este alvo.')));

    // 5. Onde a analogia falha: sempre aberta, nunca recolhível.
    parts.push(section('Onde a analogia falha', { class: 'sec limits' }, bullets(link.limits ?? [])));

    // 6. Ainda a medir
    if (link.to_measure?.length) {
      parts.push(section('Ainda a medir', {},
        el('ul', { class: 'chips' }, link.to_measure.map((t) => el('li', {}, t))),
        el('p', { class: 'muted' }, 'Sem dado ainda: não entram na média e não valem zero.')));
    }

    // 7. Utilidades, agrupadas por categoria
    const groups = data.dimensions
      .map((d) => ({ dim: d, utils: (link.utilities ?? []).filter((u) => u.category === d.id) }))
      .filter((g) => g.utils.length);
    const utilities = el('details', { class: 'sec fold', open: open.utilities },
      el('summary', {}, el('h3', {}, 'Utilidades'), el('span', { class: 'count' }, String(link.utilities?.length ?? 0))),
      groups.map((g) => el('div', { class: 'util-group' },
        el('h4', {}, g.dim.label, g.dim.in_score ? null : el('span', { class: 'tag' }, 'fora da nota')),
        el('ul', { class: 'utils' }, g.utils.map(utilityRow)))));
    utilities.addEventListener('toggle', () => { open.utilities = utilities.open; });
    parts.push(utilities);

    // 8. Uso na exploração
    if (link.exploration_use) parts.push(section('Uso na exploração', {}, el('p', {}, link.exploration_use)));

    // 9. Fontes
    const sources = el('details', { class: 'sec fold', open: open.sources },
      el('summary', {}, el('h3', {}, 'Fontes dos dados deste local'), el('span', { class: 'count' }, String(link.sources?.length ?? 0))),
      el('ul', { class: 'sources' }, (link.sources ?? []).map((s) =>
        el('li', {}, el('span', { class: 'src-id' }, s.id), ' ',
          el('a', { href: s.url, target: '_blank', rel: 'noopener' }, s.label)))));
    sources.addEventListener('toggle', () => { open.sources = sources.open; });
    parts.push(sources);

    body.replaceChildren(...parts);
  }

  /** Foto do local (analogs[].image) no topo do card; sem imagem ou com erro de carga, o card segue sem ela. */
  function renderPhoto(analog) {
    const img = analog.image;
    if (!img) { photo.hidden = true; photo.replaceChildren(); return; }
    const picture = el('img', { src: img.src, alt: img.alt, decoding: 'async', width: '1200', height: '800',
      onerror: () => { photo.hidden = true; } });
    const name = analog.full_name ?? analog.name;
    photo.replaceChildren(
      el('button', { type: 'button', class: 'photo-open', 'aria-label': `Ampliar a foto: ${img.caption}`,
        title: 'Ampliar a foto', onclick: () => openLightbox(img, name, creditLine) },
        picture, el('span', { class: 'photo-zoom', 'aria-hidden': 'true' }, '⤢')),
      img.kind === 'satelite' ? el('span', { class: 'photo-kind' }, 'Imagem de satélite') : null,
      el('figcaption', {},
        el('span', { class: 'photo-caption' }, img.caption),
        el('span', { class: 'photo-credit' }, creditLine(img))));
    photo.hidden = false;
  }

  /** "Foto: autor · licença · fonte", com links; usada no card e no modal. */
  function creditLine(img) {
    const { author, license, license_url: licenseUrl, source_url: sourceUrl } = img.credit;
    const ext = (href, text) => el('a', { href, target: '_blank', rel: 'noopener' }, text);
    const frag = document.createDocumentFragment();
    frag.append(img.kind === 'satelite' ? 'Imagem: ' : 'Foto: ', author, ' · ',
      licenseUrl ? ext(licenseUrl, license) : license, ' · ', ext(sourceUrl, 'fonte'));
    return frag;
  }

  function render(state, prev) {
    const analog = state.analogId ? analogById.get(state.analogId) : null;
    const wasHidden = root.hidden;
    if (!analog) {
      root.hidden = true;
      body.replaceChildren();
      if (!wasHidden) onLayout?.();
      return;
    }
    const target = targetById.get(state.targetId);
    const link = linkOf(analog.id, target.id);

    if (!prev || prev.analogId !== state.analogId) renderPhoto(analog);
    title.textContent = analog.full_name ?? analog.name;
    subtitle.textContent = [analog.country, analog.batch].filter(Boolean).join(' · ');
    approx.hidden = !analog.approximate_coords;
    for (const [id, { tab, badge }] of tabs) {
      const selected = id === state.targetId;
      tab.setAttribute('aria-selected', String(selected));
      tab.tabIndex = selected ? 0 : -1;
      badge.hidden = !(analog.listed_as ?? []).includes(id);
      badge.title = `Listado pela equipe como análogo ${targetOf(targetById.get(id))}`;
    }
    body.setAttribute('aria-labelledby', `tab-${state.targetId}`);

    if (link) renderBody(analog, target, link);
    else body.replaceChildren(el('p', { class: 'muted' }, `Sem ligação com ${target.name} nos dados: ${A_MEDIR}.`));
    if (!prev || prev.analogId !== state.analogId || prev.targetId !== state.targetId) body.scrollTop = 0;

    root.hidden = false;
    if (wasHidden) onLayout?.();
  }

  selection.subscribe(render);
  render(selection.state, null);
  return { root };
}
