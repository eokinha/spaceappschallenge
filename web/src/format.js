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
