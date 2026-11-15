import * as THREE from 'three';

// Fundo de estrelas: pontos espalhados numa esfera grande em volta da câmera. É só cenário — não vem do
// analogs.json, não recebe clique e fica atrás dos globos (os globos escrevem profundidade; as estrelas não).
// A esfera acompanha a posição da câmera (follow), então as estrelas não se aproximam no zoom nem saem do
// alcance da câmera; ao girar a cena elas giram junto, como um céu distante.

const RADIUS = 60; // dentro do `far` da câmera (100)
// Camadas: muitas estrelas fracas e pequenas, poucas grandes e brilhantes. `size` em px de CSS.
const LAYERS = [
  { count: 22000, size: 1.4, min: 0.3, max: 0.8 },
  { count: 3200, size: 2.1, min: 0.5, max: 0.95 },
  { count: 380, size: 3.2, min: 0.8, max: 1 },
];
// Tons: a maioria branca, algumas azuladas e algumas quentes.
const TINTS = [[1, 1, 1], [1, 1, 1], [0.75, 0.85, 1], [0.85, 0.92, 1], [1, 0.9, 0.78], [1, 0.82, 0.7]];

/** Gerador determinístico (mulberry32): o céu é o mesmo a cada carga. */
function rng(seed) {
  let a = seed;
  return () => {
    a = (a + 0x6d2b79f5) | 0;
    let x = Math.imul(a ^ (a >>> 15), 1 | a);
    x = (x + Math.imul(x ^ (x >>> 7), 61 | x)) ^ x;
    return ((x ^ (x >>> 14)) >>> 0) / 4294967296;
  };
}

/** Textura de um ponto redondo com borda suave (sem ela os pontos seriam quadrados). */
function dotTexture() {
  const size = 32;
  const c = document.createElement('canvas');
  c.width = c.height = size;
  const ctx = c.getContext('2d');
  const g = ctx.createRadialGradient(size / 2, size / 2, 0, size / 2, size / 2, size / 2);
  g.addColorStop(0, 'rgba(255,255,255,1)');
  g.addColorStop(0.45, 'rgba(255,255,255,0.85)');
  g.addColorStop(1, 'rgba(255,255,255,0)');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, size, size);
  const texture = new THREE.CanvasTexture(c);
  texture.colorSpace = THREE.SRGBColorSpace;
  return texture;
}

/**
 * @param {THREE.Scene} scene
 * @param {number} pixelRatio  o tamanho dos pontos é em px do buffer; multiplicar mantém o tamanho em telas densas
 * @returns {{ follow: (camera: THREE.Camera) => void }}
 */
export function createStars(scene, pixelRatio = 1) {
  const random = rng(20261115);
  const map = dotTexture();
  const group = new THREE.Group();
  group.name = 'stars';

  for (const layer of LAYERS) {
    const positions = new Float32Array(layer.count * 3);
    const colors = new Float32Array(layer.count * 3);
    for (let i = 0; i < layer.count; i++) {
      // Ponto uniforme na esfera.
      const z = random() * 2 - 1;
      const phi = random() * Math.PI * 2;
      const r = Math.sqrt(1 - z * z);
      positions.set([RADIUS * r * Math.cos(phi), RADIUS * z, RADIUS * r * Math.sin(phi)], i * 3);
      const tint = TINTS[Math.floor(random() * TINTS.length)];
      const brightness = layer.min + random() * (layer.max - layer.min);
      colors.set([tint[0] * brightness, tint[1] * brightness, tint[2] * brightness], i * 3);
    }
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    const material = new THREE.PointsMaterial({
      size: layer.size * pixelRatio, sizeAttenuation: false, map, vertexColors: true,
      transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
    });
    const points = new THREE.Points(geometry, material);
    points.frustumCulled = false;
    points.renderOrder = -1;
    group.add(points);
  }

  scene.add(group);
  return { follow: (camera) => group.position.copy(camera.position) };
}
