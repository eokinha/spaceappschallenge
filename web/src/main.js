import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { createGlobe, addMarker } from './globe.js';

// Layout dos globos. Raios e posições configuráveis (ver docs/instrucoes-desenvolvimento.md, seção 5).
// Rotação inicial: yaw para mostrar uma face útil e inclinação para deixar o polo sul lunar visível.
const LAYOUT = {
  earth: { radius: 1.0,  x: 0,    texture: 'textures/earth.jpg', rotation: [0.25, 0, 0] },
  moon:  { radius: 0.4,  x: -2.8, texture: 'textures/moon.jpg',  rotation: [-0.6, -Math.PI / 2, 0] },
  mars:  { radius: 0.55, x: 2.8,  texture: 'textures/mars.jpg',  rotation: [0.2, 0, 0] },
};
// Meia largura da cena que precisa caber na tela (Marte em x=2,8 + raio + folga).
const SCENE_HALF_WIDTH = 3.6;
const SCENE_HALF_HEIGHT = 1.4;

// Pontos fáceis de reconhecer para conferir a projeção (ativar com ?debug=1).
const DEBUG_POINTS = [
  { body: 'earth', name: 'Rio de Janeiro', lat: -22.9,  lon: -43.2 },
  { body: 'moon',  name: 'Cratera Tycho',  lat: -43.3,  lon: -11.4 },
  { body: 'mars',  name: 'Olympus Mons',   lat: 18.65,  lon: -133.8 },
];

const params = new URLSearchParams(location.search);
const DEBUG = params.get('debug') === '1';

const canvas = document.getElementById('scene');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.outputColorSpace = THREE.SRGBColorSpace;

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x05070d);

const camera = new THREE.PerspectiveCamera(40, 1, 0.1, 100);
camera.position.set(0, 0, 9);

const controls = new OrbitControls(camera, canvas);
controls.enableDamping = true;
controls.minDistance = 2.5;
controls.maxDistance = 25;

scene.add(new THREE.AmbientLight(0xffffff, 0.35));
const sun = new THREE.DirectionalLight(0xffffff, 2.2);
sun.position.set(3, 2, 6);
scene.add(sun);

const globes = {};
for (const [id, cfg] of Object.entries(LAYOUT)) {
  const globe = createGlobe({ id, radius: cfg.radius, texture: cfg.texture, renderer });
  globe.position.x = cfg.x;
  globe.rotation.set(...cfg.rotation);
  scene.add(globe);
  globes[id] = globe;
}

if (DEBUG) {
  for (const p of DEBUG_POINTS) addMarker(globes[p.body], p.lat, p.lon, 'debug', { id: `debug-${p.body}`, name: p.name });
}

async function loadData() {
  const res = await fetch('data/analogs.json');
  if (!res.ok) throw new Error(`Falha ao carregar analogs.json: HTTP ${res.status}`);
  const data = await res.json();

  for (const t of data.targets) addMarker(globes[t.body], t.lat, t.lon, 'target', t);
  for (const a of data.analogs) addMarker(globes.earth, a.lat, a.lon, 'analog', a);

  document.getElementById('status').textContent =
    `${data.targets.length} alvos · ${data.analogs.length} análogos · ${data.links.length} ligações`;
  return data;
}

function resize() {
  const w = canvas.clientWidth;
  const h = canvas.clientHeight;
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  // Afasta a câmera o suficiente para os três globos caberem na largura e na altura.
  const tanHalf = Math.tan(THREE.MathUtils.degToRad(camera.fov / 2));
  const dist = Math.max(SCENE_HALF_WIDTH / (tanHalf * camera.aspect), SCENE_HALF_HEIGHT / tanHalf);
  camera.position.setLength(dist);
  camera.updateProjectionMatrix();
}
window.addEventListener('resize', resize);
resize();

renderer.setAnimationLoop(() => {
  controls.update();
  renderer.render(scene, camera);
});

loadData().catch((err) => {
  console.error(err);
  document.getElementById('status').textContent = 'Erro ao carregar os dados. Veja o console.';
});

// Exposto para depuração no console e para as próximas fases (arcos, interação).
window.__app = { scene, camera, globes, renderer };
