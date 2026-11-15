// Título do cabeçalho: a maior fonte em que o texto ainda cabe em duas linhas na largura do <h1>
// (que segue a largura da lista, 25% da janela). O CSS mantém 12px e o corte
// em duas linhas como reserva caso este ajuste não rode.

const MIN = 12;
const MAX = 22;
const LINES = 2;

export function fitTitle(h1) {
  if (!h1) return;
  let lastWidth = -1;

  function fit() {
    const width = h1.clientWidth;
    if (!width || width === lastWidth) return; // escondido (telas estreitas) ou sem mudança
    lastWidth = width;
    h1.classList.add('is-fitting'); // tira o corte em 2 linhas para medir a altura real
    const fits = (px) => {
      h1.style.fontSize = `${px}px`;
      const lineH = parseFloat(getComputedStyle(h1).lineHeight);
      return h1.scrollHeight <= lineH * LINES + 1 && h1.scrollWidth <= width;
    };
    // Busca binária em passos de 0,5px.
    let lo = MIN, hi = MAX;
    if (fits(hi)) lo = hi;
    else {
      while (hi - lo > 0.5) {
        const mid = Math.round((lo + hi)) / 2;
        if (fits(mid)) lo = mid; else hi = mid;
      }
    }
    h1.style.fontSize = `${lo}px`;
    h1.classList.remove('is-fitting');
  }

  new ResizeObserver(fit).observe(h1);
  document.fonts?.ready.then(() => { lastWidth = -1; fit(); });
}
