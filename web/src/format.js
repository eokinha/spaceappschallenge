// Formatação pt-BR e rótulos. Aqui só se formata: nenhum número é recalculado (tudo vem do analogs.json).

const formatters = new Map();
function nf(min, max) {
  const key = `${min}-${max}`;
  if (!formatters.has(key)) {
    formatters.set(key, new Intl.NumberFormat('pt-BR', { minimumFractionDigits: min, maximumFractionDigits: max }));
  }
  return formatters.get(key);
}

export const A_MEDIR = 'a medir';

/** Nota com casas fixas (1.5385 → "1,54"); null/undefined → "a medir", nunca 0. */
export function fmtFixed(value, digits = 2) {
  return value == null ? A_MEDIR : nf(digits, digits).format(value);
}

/** Nota sem zeros à direita (2 → "2"; 0.6667 → "0,67"); null/undefined → "a medir". */
export function fmtNote(value) {
  return value == null ? A_MEDIR : nf(0, 2).format(value);
}

/** "1,54 / 3" ou "a medir". */
export function fmtOutOf3(value, digits = 2) {
  return value == null ? A_MEDIR : `${fmtFixed(value, digits)} / 3`;
}

export function fmtNoteOutOf3(value) {
  return value == null ? A_MEDIR : `${fmtNote(value)} / 3`;
}

/** "1º de 14". */
export function fmtRank(rank, total) {
  return rank == null ? A_MEDIR : `${rank}º de ${total}`;
}

/** Largura de uma barra a partir do score 0–1 do JSON (o trilho inteiro é a escala 0–3). */
export function barWidth(score) {
  if (score == null) return '0%';
  return `${Math.min(Math.max(score, 0), 1) * 100}%`;
}

export function plural(n, one, many) {
  return n === 1 ? one : many;
}

// Rótulos curtos por corpo celeste (o JSON traz o nome completo do alvo em targets[].name).
const BODY = {
  moon: { short: 'Lua', of: 'da Lua' },
  mars: { short: 'Marte', of: 'de Marte' },
};

export function targetShort(target) {
  return BODY[target?.body]?.short ?? target?.name ?? '';
}

/** "da Lua" / "de Marte". */
export function targetOf(target) {
  return BODY[target?.body]?.of ?? `de ${target?.name ?? ''}`;
}

/** ["lua","marte"] → "da Lua e de Marte". */
export function targetsOf(ids, targetById) {
  return ids.map((id) => targetOf(targetById.get(id))).join(' e ');
}

// Níveis semânticos de aderência. O nível vem pronto do JSON (`level`, etl/config.py › nivel):
// ≥ 2 forte, ≤ 1 fraco, entre os dois parcial, null = a medir. Aqui só há rótulo e classe CSS.
export const LEVELS = {
  high: { cls: 'lv-high', label: 'Forte', tag: 'Forte analogia', range: '2 a 3' },
  moderate: { cls: 'lv-moderate', label: 'Parcial', tag: 'Analogia parcial', range: 'entre 1 e 2' },
  low: { cls: 'lv-low', label: 'Fraca', tag: 'Baixa aderência', range: '0 a 1' },
  none: { cls: 'lv-none', label: 'A medir', tag: 'A medir', range: 'sem dado' },
};

export function levelInfo(level) {
  return LEVELS[level] ?? LEVELS.none;
}

/** Valor de uma variável com a unidade: "−16 °C", "13 mm/ano", "3 (escala 0–3)". */
export function fmtValue(value, unit) {
  if (value == null) return A_MEDIR;
  const n = fmtNote(value);
  if (!unit) return n;
  if (/^escala/i.test(unit)) return `${n} (${unit})`;
  if (unit === '%') return `${n}%`;
  return `${n} ${unit}`;
}

const isScale = (unit) => /^escala/i.test(unit ?? '');

/** Faixas do critério: "nota 3 se ≤ −45 °C · 2 se ≤ −25 · 1 se ≤ −10" (null se não houver faixa útil). */
export function fmtThresholds(thresholds, direction, unit) {
  if (!thresholds || thresholds['3'] == null || isScale(unit)) return null;
  const op = direction === 'menor' ? '≤' : '≥';
  const u = unit && unit !== '%' ? ` ${unit}` : unit === '%' ? '%' : '';
  return `nota 3 se ${op} ${fmtNote(thresholds['3'])}${u} · 2 se ${op} ${fmtNote(thresholds['2'])} · 1 se ${op} ${fmtNote(thresholds['1'])}`;
}

// Classe da fonte (vem pronta do JSON: source_index[id].kind e links[].sources[].kind; etl/config.py › FONTES_CLASSE).
export const SOURCE_KINDS = {
  nasa: { label: 'NASA', title: 'Documento, dado ou página oficial da NASA' },
  nasa_mission: { label: 'Missão NASA', title: 'Artigo revisado por pares com dados de missão da NASA' },
  peer_reviewed: { label: 'Artigo revisado', title: 'Artigo científico revisado por pares' },
  agency: { label: 'Órgão público', title: 'Órgão público ou repositório científico (NPS, USGS, SGB, PANGAEA)' },
  team: { label: 'Planilha', title: 'Planilha da equipe' },
};

export function sourceKind(kind) {
  return SOURCE_KINDS[kind] ?? null;
}
