import * as THREE from 'three';
import { MARKER_SIZE } from './globe.js';

// Hover e clique nos marcadores, e arrasto sobre os globos. Usa o raio do Raycaster contra uma esfera de
// toque em volta de cada marcador (maior que o marcador, para ser fácil de acertar) e contra os globos, que
// escondem os marcadores da face de trás.
// Arrastar em cima de um globo gira só aquele globo; arrastar no vazio fica com o OrbitControls (a câmera
// orbita e os três giram juntos).

const CLICK_TOLERANCE_PX = 5; // acima disso o gesto foi um arrasto do OrbitControls, não um clique

/**
 * @param {object} opts
 * @param {HTMLCanvasElement} opts.canvas
 * @param {THREE.Camera} opts.camera
 * @param {Record<string, THREE.Group>} opts.globes
 * @param {THREE.Object3D[]} opts.markers  marcadores clicáveis (userData.kind = 'analog' | 'target')
 * @param {HTMLElement} opts.tooltip
 * @param {(marker: THREE.Object3D | null) => void} opts.onHover
 * @param {(marker: THREE.Object3D | null) => void} opts.onClick  null = clique no vazio
 * @param {import('three/addons/controls/OrbitControls.js').OrbitControls} opts.controls
 * @param {ReturnType<import('./focus.js').createFocus>} opts.focus
 */
export function createInteraction({ canvas, camera, globes, markers, tooltip, onHover, onClick, controls, focus }) {
  const raycaster = new THREE.Raycaster();
  const ndc = new THREE.Vector2();
  const sphere = new THREE.Sphere();
  const hit = new THREE.Vector3();
  const axis = new THREE.Vector3();
  const spin = new THREE.Quaternion();
  let hovered = null;
  let overGlobe = false;
  let down = null;
  let drag = null;      // { globe, x, y, id }: arrasto em cima de um globo
  const touches = new Set(); // dedos na tela: com dois, o gesto é a pinça do OrbitControls

  function rayFrom(event) {
    const rect = canvas.getBoundingClientRect();
    ndc.set(((event.clientX - rect.left) / rect.width) * 2 - 1, -((event.clientY - rect.top) / rect.height) * 2 + 1);
    raycaster.setFromCamera(ndc, camera);
    return raycaster.ray;
  }

  /** Globo sob o ponteiro (o mais perto da câmera) ou null. */
  function pickGlobe(event) {
    const ray = rayFrom(event);
    let best = null;
    let bestDistance = Infinity;
    for (const globe of Object.values(globes)) {
      globe.getWorldPosition(sphere.center);
      sphere.radius = globe.userData.radius;
      if (!ray.intersectSphere(sphere, hit)) continue;
      const distance = hit.distanceTo(ray.origin);
      if (distance < bestDistance) { bestDistance = distance; best = globe; }
    }
    return best;
  }

  function pick(event) {
    const ray = rayFrom(event);

    let globeDistance = Infinity;
    for (const globe of Object.values(globes)) {
      globe.getWorldPosition(sphere.center);
      sphere.radius = globe.userData.radius;
      if (ray.intersectSphere(sphere, hit)) globeDistance = Math.min(globeDistance, hit.distanceTo(ray.origin));
    }

    const hitRadius = MARKER_SIZE * (event.pointerType === 'touch' ? 3.5 : 2.2);
    let best = null;
    let bestMiss = Infinity;
    for (const marker of markers) {
      marker.getWorldPosition(sphere.center);
      sphere.radius = hitRadius;
      if (!ray.intersectSphere(sphere, hit)) continue;
      if (hit.distanceTo(ray.origin) > globeDistance) continue; // atrás de um globo
      const miss = ray.distanceSqToPoint(sphere.center);        // o mais perto do raio vence
      if (miss < bestMiss) { bestMiss = miss; best = marker; }
    }
    return best;
  }

  function showTooltip(marker, event) {
    if (!marker) { tooltip.hidden = true; return; }
    tooltip.textContent = marker.userData.name ?? marker.name;
    tooltip.hidden = false;
    const x = Math.min(event.clientX + 14, window.innerWidth - tooltip.offsetWidth - 8);
    const y = Math.max(event.clientY - tooltip.offsetHeight - 10, 8);
    tooltip.style.transform = `translate(${Math.max(x, 8)}px, ${y}px)`;
  }

  /** Cursor: mão fechada no arrasto de um globo, dedo no marcador, mão aberta sobre um globo. */
  function updateCursor() {
    canvas.style.cursor = drag ? 'grabbing' : hovered ? 'pointer' : overGlobe ? 'grab' : '';
  }

  function setHovered(marker, event) {
    if (marker !== hovered) {
      hovered = marker;
      onHover(marker);
    }
    updateCursor();
    showTooltip(marker, event);
  }

  /**
   * Gira o globo arrastado: dx em torno do "para cima" da câmera e dy em torno do "para a direita".
   * O ângulo é o deslocamento dividido pelo raio do globo na tela, para a superfície acompanhar o ponteiro.
   */
  function rotateDragged(dx, dy) {
    const { globe } = drag;
    globe.getWorldPosition(hit);
    const distance = hit.distanceTo(camera.position);
    const tanHalf = Math.tan(THREE.MathUtils.degToRad(camera.fov / 2));
    const radiusPx = (globe.userData.radius * (canvas.clientHeight / 2)) / (distance * tanHalf);
    if (!(radiusPx > 0)) return;
    camera.updateMatrixWorld();
    spin.setFromAxisAngle(axis.setFromMatrixColumn(camera.matrixWorld, 1).normalize(), dx / radiusPx);
    globe.quaternion.premultiply(spin);
    spin.setFromAxisAngle(axis.setFromMatrixColumn(camera.matrixWorld, 0).normalize(), dy / radiusPx);
    globe.quaternion.premultiply(spin).normalize();
  }

  function endDrag() {
    if (!drag) return;
    if (canvas.hasPointerCapture?.(drag.id)) canvas.releasePointerCapture(drag.id);
    drag = null;
    controls.enabled = !focus.cameraBusy; // durante o voo da câmera quem religa é o focus.js
    updateCursor();
  }

  // Em captura: roda antes do pointerdown do OrbitControls, que só começa a órbita se estiver ligado.
  canvas.addEventListener('pointerdown', (event) => {
    if (event.pointerType === 'touch') touches.add(event.pointerId);
    if (drag) { if (touches.size > 1) endDrag(); return; } // segundo dedo: o gesto vira pinça
    if (event.button !== 0 || touches.size > 1 || focus.cameraBusy) return;
    if (event.ctrlKey || event.shiftKey || event.metaKey) return; // Ctrl/Shift/⌘ + arrastar: o OrbitControls desloca a cena
    const globe = pickGlobe(event);
    if (!globe) return;
    drag = { globe, x: event.clientX, y: event.clientY, id: event.pointerId };
    controls.enabled = false;
    focus.cancelGlobe(globe); // o giro automático do foco não briga com a mão do usuário
    canvas.setPointerCapture?.(event.pointerId);
    updateCursor();
  }, { capture: true });

  canvas.addEventListener('pointermove', (event) => {
    if (drag) {
      if (event.pointerId !== drag.id) return;
      rotateDragged(event.clientX - drag.x, event.clientY - drag.y);
      drag.x = event.clientX;
      drag.y = event.clientY;
      return;
    }
    if (event.pointerType === 'touch' || event.buttons !== 0) return; // sem hover no toque nem durante o arrasto
    overGlobe = Boolean(pickGlobe(event));
    setHovered(pick(event), event);
  });
  canvas.addEventListener('pointerleave', (event) => { overGlobe = false; setHovered(null, event); });
  canvas.addEventListener('pointerdown', (event) => {
    down = { x: event.clientX, y: event.clientY, id: event.pointerId };
    tooltip.hidden = true;
  });
  canvas.addEventListener('pointerup', (event) => {
    touches.delete(event.pointerId);
    if (drag?.id === event.pointerId) endDrag();
    if (!down || down.id !== event.pointerId) return;
    const moved = Math.hypot(event.clientX - down.x, event.clientY - down.y);
    down = null;
    if (moved > CLICK_TOLERANCE_PX || event.button !== 0) return;
    onClick(pick(event));
  });
  canvas.addEventListener('pointercancel', (event) => {
    touches.delete(event.pointerId);
    if (drag?.id === event.pointerId) endDrag();
    down = null;
  });

  return { pick, pickGlobe };
}
