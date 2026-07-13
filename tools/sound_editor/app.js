import {
  DEFAULT_GRID_TICKS,
  MAX_PITCH,
  MAX_SFX_UNITS,
  PITCHES,
  compileBgmTrack,
  compileSfx,
  createProject,
  exportAssembly,
  parseProject,
  serializeProject,
  upgradeStarterSamples,
  validateProject,
} from "./core.js";
import { getLanguage, setLanguage, t, translateDocument } from "./i18n.js";

const STORAGE_KEY = "jr100dev.sound-workbench.v1";
const DISPLAY_CELLS = 48;
const CELL_WIDTH = 24;
const CELL_HEIGHT = 12;
const canvas = document.querySelector("#piano-roll");
const context = canvas.getContext("2d");
const elements = {
  projectName: document.querySelector("#project-name"),
  tickHz: document.querySelector("#tick-hz"),
  gridTicks: document.querySelector("#grid-ticks"),
  trackList: document.querySelector("#track-list"),
  effectList: document.querySelector("#effect-list"),
  assetKind: document.querySelector("#asset-kind"),
  assetTitle: document.querySelector("#asset-title"),
  assetName: document.querySelector("#asset-name"),
  assetId: document.querySelector("#asset-id"),
  assetLength: document.querySelector("#asset-length"),
  loopCell: document.querySelector("#loop-cell"),
  loopControl: document.querySelector("#loop-control"),
  rollHelp: document.querySelector("#roll-help"),
  copySample: document.querySelector("#copy-sample"),
  deleteAsset: document.querySelector("#delete-asset"),
  status: document.querySelector("#status"),
  language: document.querySelector("#language-select"),
  importFile: document.querySelector("#import-file"),
};

let project = restoreProject();
let active = { kind: "track", index: 0 };
let cursor = { column: 0, pitch: 25 };
let audioContext = null;
let activeOscillators = [];

translateDocument();
elements.language.value = getLanguage();

function restoreProject() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored ? upgradeStarterSamples(parseProject(stored)) : createProject();
  } catch {
    return createProject();
  }
}

function currentAsset() {
  return active.kind === "track" ? project.tracks[active.index] : project.effects[active.index];
}

function isSampleAsset(asset) {
  return asset.origin === "sample";
}

function isIncluded(asset) {
  return asset.included !== false;
}

function persist(message = t("status.saved")) {
  try {
    validateProject(project);
    localStorage.setItem(STORAGE_KEY, serializeProject(project));
    setStatus(message);
  } catch {
    setStatus(t("error.invalidProject"), true);
  }
}

function setStatus(message, isError = false) {
  elements.status.textContent = message;
  elements.status.style.color = isError ? "var(--danger)" : "var(--accent)";
}

function render() {
  if (active.kind === "track" && active.index >= project.tracks.length) active.index = 0;
  if (active.kind === "effect" && active.index >= project.effects.length) active.index = 0;
  elements.projectName.value = project.name;
  elements.tickHz.value = project.tickHz;
  elements.gridTicks.value = project.gridTicks;
  renderAssetList(elements.trackList, project.tracks, "track");
  renderAssetList(elements.effectList, project.effects, "effect");
  const asset = currentAsset();
  const isTrack = active.kind === "track";
  const locked = isSampleAsset(asset);
  cursor.column = Math.min(cursor.column, (isTrack ? 255 : MAX_SFX_UNITS) - 1);
  elements.assetKind.textContent = isTrack ? t("editor.bgm") : t("editor.sfx");
  elements.assetTitle.textContent = asset.name;
  elements.assetName.value = asset.name;
  elements.assetId.value = asset.id;
  elements.assetLength.value = asset.notes.length;
  elements.assetLength.max = isTrack ? "255" : String(MAX_SFX_UNITS);
  elements.loopControl.hidden = !isTrack;
  elements.loopCell.value = isTrack ? asset.loopCell : -1;
  elements.rollHelp.textContent = locked
    ? t("editor.sampleHelp")
    : isTrack
    ? t("editor.bgmHelp", { ticks: project.gridTicks })
    : t("editor.sfxHelp");
  for (const control of [elements.assetName, elements.assetId, elements.assetLength, elements.loopCell]) {
    control.disabled = locked;
  }
  elements.copySample.hidden = !locked;
  elements.deleteAsset.hidden = locked;
  canvas.setAttribute("aria-disabled", String(locked));
  canvas.tabIndex = locked ? -1 : 0;
  canvas.classList.toggle("locked", locked);
  drawRoll();
}

function renderAssetList(container, assets, kind) {
  const groups = [
    ["sample", t("assets.samples")],
    ["user", t("assets.userAssets")],
  ];
  const content = [];
  for (const [origin, title] of groups) {
    const groupAssets = assets
      .map((asset, index) => ({ asset, index }))
      .filter(({ asset }) => (origin === "sample" ? isSampleAsset(asset) : !isSampleAsset(asset)));
    if (!groupAssets.length) continue;
    const heading = document.createElement("h3");
    heading.className = "asset-group-heading";
    heading.textContent = title;
    content.push(heading);
    for (const { asset, index } of groupAssets) {
      const row = document.createElement("div");
      row.className = "asset-row";
      const inclusion = document.createElement("label");
      inclusion.className = "include-control";
      const input = document.createElement("input");
      input.type = "checkbox";
      input.checked = isIncluded(asset);
      input.setAttribute("aria-label", t("assets.includeAsset", { name: asset.name }));
      input.addEventListener("change", () => {
        asset.included = input.checked;
        persist();
        render();
      });
      const marker = document.createElement("span");
      marker.textContent = t("assets.include");
      inclusion.append(input, marker);
    const button = document.createElement("button");
    button.type = "button";
    button.className = `asset-item${active.kind === kind && active.index === index ? " active" : ""}`;
    const title = document.createElement("span");
    title.textContent = asset.name;
    const detail = document.createElement("small");
    detail.textContent = asset.id;
    button.append(title, detail);
    button.addEventListener("click", () => {
      active = { kind, index };
      stopPreview();
      render();
    });
      row.append(inclusion, button);
      content.push(row);
    }
  }
  container.replaceChildren(...content);
}

function drawRoll() {
  const asset = currentAsset();
  const columns = Math.max(DISPLAY_CELLS, asset.notes.length);
  canvas.width = columns * CELL_WIDTH;
  canvas.height = MAX_PITCH * CELL_HEIGHT;
  for (let row = 0; row < MAX_PITCH; row += 1) {
    const pitch = MAX_PITCH - row;
    const dark = PITCHES[pitch - 1].name.includes("#");
    context.fillStyle = dark ? "#111823" : "#18212b";
    context.fillRect(0, row * CELL_HEIGHT, canvas.width, CELL_HEIGHT);
    context.strokeStyle = "#2b3543";
    context.strokeRect(0, row * CELL_HEIGHT, canvas.width, CELL_HEIGHT);
  }
  for (let column = 0; column < columns; column += 1) {
    context.strokeStyle = column % 4 === 0 ? "#586778" : "#34404e";
    context.beginPath();
    context.moveTo(column * CELL_WIDTH + 0.5, 0);
    context.lineTo(column * CELL_WIDTH + 0.5, canvas.height);
    context.stroke();
  }
  if (active.kind === "track" && asset.loopCell >= 0) {
    context.fillStyle = "rgba(122, 215, 255, 0.16)";
    context.fillRect(asset.loopCell * CELL_WIDTH, 0, CELL_WIDTH, canvas.height);
  }
  asset.notes.forEach((pitch, column) => {
    if (!pitch) return;
    const row = MAX_PITCH - pitch;
    context.fillStyle = active.kind === "track" ? "#7ad7ff" : "#ffc77a";
    context.fillRect(column * CELL_WIDTH + 2, row * CELL_HEIGHT + 2, CELL_WIDTH - 4, CELL_HEIGHT - 4);
  });
  context.strokeStyle = "#eff4f7";
  context.lineWidth = 2;
  context.strokeRect(
    cursor.column * CELL_WIDTH + 1,
    (MAX_PITCH - cursor.pitch) * CELL_HEIGHT + 1,
    CELL_WIDTH - 2,
    CELL_HEIGHT - 2,
  );
  context.fillStyle = "#9ba8b7";
  context.font = "9px ui-monospace";
  for (let row = 0; row < MAX_PITCH; row += 6) {
    const pitch = MAX_PITCH - row;
    context.fillText(PITCHES[pitch - 1].name, 2, row * CELL_HEIGHT + 9);
  }
}

function updateProjectSettings() {
  project.name = elements.projectName.value.trim() || "JR-100 Sound Project";
  project.tickHz = numberInRange(elements.tickHz, 1, 240, project.tickHz);
  project.gridTicks = numberInRange(elements.gridTicks, 1, 255, DEFAULT_GRID_TICKS);
  persist();
  render();
}

function updateAssetFields() {
  const asset = currentAsset();
  if (isSampleAsset(asset)) return;
  asset.name = elements.assetName.value.trim() || asset.name;
  asset.id = elements.assetId.value.trim() || asset.id;
  const maximum = active.kind === "track" ? 255 : MAX_SFX_UNITS;
  const requestedLength = numberInRange(elements.assetLength, 1, maximum, asset.notes.length);
  asset.notes = asset.notes.slice(0, requestedLength);
  while (asset.notes.length < requestedLength) asset.notes.push(0);
  if (active.kind === "track") {
    asset.loopCell = numberInRange(elements.loopCell, -1, requestedLength - 1, asset.loopCell);
  }
  persist();
  render();
}

function numberInRange(element, minimum, maximum, fallback) {
  const value = Number(element.value);
  return Number.isInteger(value) && value >= minimum && value <= maximum ? value : fallback;
}

async function playAsset() {
  stopPreview();
  const asset = currentAsset();
  const events = active.kind === "track" ? compileBgmTrack(asset, project.gridTicks) : compileSfx(asset);
  const unitSeconds = active.kind === "track" ? project.gridTicks / project.tickHz : 0.01;
  audioContext ??= new AudioContext();
  await audioContext.resume();
  let at = audioContext.currentTime + 0.03;
  for (const [pitch, units] of events) {
    const duration = units * unitSeconds;
    if (pitch) scheduleSquareWave(pitch, at, duration);
    at += duration;
  }
  setStatus(t("status.previewPlaying"));
}

function scheduleSquareWave(pitch, start, duration) {
  const oscillator = audioContext.createOscillator();
  const gain = audioContext.createGain();
  oscillator.type = "square";
  oscillator.frequency.value = PITCHES[pitch - 1].frequency;
  gain.gain.setValueAtTime(0.08, start);
  gain.gain.setValueAtTime(0, start + Math.max(0.005, duration - 0.003));
  oscillator.connect(gain).connect(audioContext.destination);
  oscillator.start(start);
  oscillator.stop(start + duration);
  activeOscillators.push(oscillator);
  oscillator.addEventListener("ended", () => {
    activeOscillators = activeOscillators.filter((candidate) => candidate !== oscillator);
  });
}

function stopPreview() {
  for (const oscillator of activeOscillators) oscillator.stop();
  activeOscillators = [];
  setStatus(t("status.previewStopped"));
}

function download(name, content, type) {
  const url = URL.createObjectURL(new Blob([content], { type }));
  const link = document.createElement("a");
  link.href = url;
  link.download = name;
  link.click();
  URL.revokeObjectURL(url);
}

async function buildDemo() {
  try {
    validateProject(project);
    if (!project.tracks.some(isIncluded)) {
      setStatus(t("error.selectedBgmRequired"), true);
      return;
    }
    const response = await fetch("/api/build", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: serializeProject(project),
    });
    if (!response.ok) throw new Error(await response.text() || "Build failed");
    download("jr100-sound-build.zip", await response.blob(), "application/zip");
    setStatus(t("status.demoBuilt"));
  } catch {
    setStatus(t("status.buildFailed"), true);
  }
}

function addTrack() {
  project.tracks.push({
    id: nextAssetId("track"),
    name: t("asset.newTrack"),
    notes: Array(16).fill(0),
    loopCell: 0,
    origin: "user",
    included: true,
  });
  active = { kind: "track", index: project.tracks.length - 1 };
  persist();
  render();
}

function addEffect() {
  project.effects.push({
    id: nextAssetId("effect"),
    name: t("asset.newEffect"),
    notes: Array(8).fill(0),
    origin: "user",
    included: true,
  });
  active = { kind: "effect", index: project.effects.length - 1 };
  persist();
  render();
}

function deleteAsset() {
  const assets = active.kind === "track" ? project.tracks : project.effects;
  if (isSampleAsset(currentAsset())) {
    setStatus(t("error.sampleLocked"), true);
    return;
  }
  if (active.kind === "track" && assets.length === 1) {
    setStatus(t("error.bgmRequired"), true);
    return;
  }
  assets.splice(active.index, 1);
  if (active.kind === "effect" && !project.effects.length) {
    active = { kind: "track", index: 0 };
  } else {
    active.index = Math.max(0, active.index - 1);
  }
  persist();
  render();
}

function copySampleToUserAssets() {
  const sample = currentAsset();
  if (!isSampleAsset(sample)) return;
  const assets = active.kind === "track" ? project.tracks : project.effects;
  const copied = {
    ...sample,
    id: nextAssetId(`${active.kind}-copy`),
    name: `${sample.name} Copy`,
    notes: [...sample.notes],
    origin: "user",
  };
  assets.push(copied);
  active = { kind: active.kind, index: assets.length - 1 };
  persist(t("status.sampleCopied"));
  render();
}

function nextAssetId(prefix) {
  const existing = new Set([...project.tracks, ...project.effects].map(({ id }) => id));
  let number = 1;
  while (existing.has(`${prefix}-${number}`)) number += 1;
  return `${prefix}-${number}`;
}

function editRollCell(column, pitch) {
  const asset = currentAsset();
  if (isSampleAsset(asset)) return;
  const maximum = active.kind === "track" ? 255 : MAX_SFX_UNITS;
  if (column < 0 || column >= maximum || pitch < 0 || pitch > MAX_PITCH) return;
  while (asset.notes.length <= column) asset.notes.push(0);
  asset.notes[column] = asset.notes[column] === pitch ? 0 : pitch;
  cursor = { column, pitch: pitch || cursor.pitch };
  persist();
  render();
}

canvas.addEventListener("contextmenu", (event) => event.preventDefault());
canvas.addEventListener("pointerdown", (event) => {
  const rect = canvas.getBoundingClientRect();
  const column = Math.floor((event.clientX - rect.left) * canvas.width / rect.width / CELL_WIDTH);
  const row = Math.floor((event.clientY - rect.top) * canvas.height / rect.height / CELL_HEIGHT);
  const maximum = active.kind === "track" ? 255 : MAX_SFX_UNITS;
  if (column < 0 || column >= maximum || row < 0 || row >= MAX_PITCH) return;
  const pitch = event.button === 2 ? 0 : MAX_PITCH - row;
  cursor = { column, pitch: MAX_PITCH - row };
  canvas.focus();
  editRollCell(column, pitch);
});
canvas.addEventListener("keydown", (event) => {
  const maximum = active.kind === "track" ? 255 : MAX_SFX_UNITS;
  if (event.key === "ArrowLeft") cursor.column = Math.max(0, cursor.column - 1);
  else if (event.key === "ArrowRight") cursor.column = Math.min(maximum - 1, cursor.column + 1);
  else if (event.key === "ArrowUp") cursor.pitch = Math.min(MAX_PITCH, cursor.pitch + 1);
  else if (event.key === "ArrowDown") cursor.pitch = Math.max(1, cursor.pitch - 1);
  else if (event.key === " " || event.key === "Enter") {
    editRollCell(cursor.column, cursor.pitch);
    event.preventDefault();
    return;
  } else if (event.key === "Backspace" || event.key === "Delete") {
    editRollCell(cursor.column, 0);
    event.preventDefault();
    return;
  } else {
    return;
  }
  event.preventDefault();
  drawRoll();
});

document.querySelector("#new-project").addEventListener("click", () => {
  project = createProject();
  active = { kind: "track", index: 0 };
  persist(t("status.newProject"));
  render();
});
document.querySelector("#save-json").addEventListener("click", () => download("jr100-sound-project.json", serializeProject(project), "application/json"));
document.querySelector("#load-json").addEventListener("click", () => elements.importFile.click());
elements.importFile.addEventListener("change", async () => {
  const [file] = elements.importFile.files;
  if (!file) return;
  try {
    project = upgradeStarterSamples(parseProject(await file.text()));
    active = { kind: "track", index: 0 };
    persist(t("status.projectLoaded"));
    render();
  } catch {
    setStatus(t("error.loadFailed"), true);
  }
  elements.importFile.value = "";
});
document.querySelector("#export-assembly").addEventListener("click", () => download("sound_assets.inc", exportAssembly(project), "text/plain"));
document.querySelector("#build-prg").addEventListener("click", buildDemo);
document.querySelector("#add-track").addEventListener("click", addTrack);
document.querySelector("#add-effect").addEventListener("click", addEffect);
document.querySelector("#delete-asset").addEventListener("click", deleteAsset);
elements.copySample.addEventListener("click", copySampleToUserAssets);
document.querySelector("#play-asset").addEventListener("click", playAsset);
document.querySelector("#stop-preview").addEventListener("click", stopPreview);
for (const element of [elements.projectName, elements.tickHz, elements.gridTicks]) element.addEventListener("change", updateProjectSettings);
for (const element of [elements.assetName, elements.assetId, elements.assetLength, elements.loopCell]) element.addEventListener("change", updateAssetFields);
elements.language.addEventListener("change", () => {
  setLanguage(elements.language.value);
  translateDocument();
  render();
  setStatus(t("status.languageChanged"));
});

render();
