import {
  applyPcgGallery,
  applyPcgAnimationPreset,
  applyPcgPreset,
  asciiToRomCode,
  assertWorkspace,
  bresenhamPoints,
  clearWorkspace,
  cloneProject,
  constrainEndpoint,
  createProject,
  DISPLAY_MODES,
  exportAssembly,
  exportCombinedAssembly,
  exportScreenAssembly,
  fillScreen,
  flipWorkspace,
  floodFill,
  getPixel,
  getScreenCell,
  invertWorkspace,
  inspectPcgAnimationPresetConflicts,
  inspectPcgPresetConflicts,
  loadCharacterRom,
  matrixToWorkspace,
  parseProject,
  removeGroup,
  serializeProject,
  setScreenCell,
  setScreenMode,
  setVramPcgPixel,
  setPixel,
  shiftWorkspace,
  upsertGroup,
  workspaceToMatrix,
  resolveScreenGlyph,
  SCREEN_HEIGHT,
  SCREEN_WIDTH,
  visiblePcgSlots,
  vramPcgSourceOffset,
} from "./core.js";
import {
  filterPcgPresets,
  getPcgPreset,
  PCG_PRESET_CATEGORY_OPTIONS,
  PCG_PRESET_CATEGORIES,
  PCG_PRESETS,
} from "./preset_library.js";
import {
  createPcgAnimationFromTemplate,
  filterPcgAnimationTemplates,
} from "./animation_templates.js";
import { getLanguage, setLanguage, t, translateDocument } from "./i18n.js";
import { createFrameScheduler } from "./frame_scheduler.js";
import {
  applyAnimationFrame,
  captureAnimationFrame,
  createAnimationClip,
  duplicateAnimationFrame,
  exportAnimationAssembly,
  removeAnimationFrame,
  replaceAnimationFrame,
  validateAnimationClips,
} from "./animation.js";
import {
  applyImageMosaicResult,
  buildGlyphCandidates,
  convertLuminanceToScreen,
  generatePcgMosaic,
  IMAGE_PIXEL_HEIGHT,
  IMAGE_PIXEL_WIDTH,
  PCG_CODE_END,
  PCG_CODE_START,
  rgbaToEnhancedLuminance,
} from "./image_mosaic.js";

const STORAGE_KEY = "jr100dev.pcg-workbench.v1";
const PCG_LIBRARY_STORAGE_KEY = "jr100dev.pcg-library.v1";
const HISTORY_LIMIT = 64;
const PCG_CATEGORY_LABELS = Object.freeze(Object.fromEntries(
  PCG_PRESET_CATEGORY_OPTIONS.map(({ id, label }) => [id, label]),
));
const canvas = document.querySelector("#editor-canvas");
const canvasContext = canvas.getContext("2d");
const crtCanvas = document.querySelector("#crt-preview");
const crtContext = crtCanvas.getContext("2d");
const screenCanvas = document.querySelector("#screen-canvas");
const screenContext = screenCanvas.getContext("2d");
const vramGlyphCanvas = document.querySelector("#vram-glyph-canvas");
const vramGlyphContext = vramGlyphCanvas.getContext("2d");
const animationCanvas = document.querySelector("#animation-preview");
const animationContext = animationCanvas.getContext("2d");
const imageMosaicDialog = document.querySelector("#image-mosaic-dialog");
const imageMosaicSourceCanvas = document.querySelector("#image-mosaic-source");
const imageMosaicSourceContext = imageMosaicSourceCanvas.getContext("2d", { willReadFrequently: true });
const imageMosaicResultCanvas = document.querySelector("#image-mosaic-result");
const imageMosaicResultContext = imageMosaicResultCanvas.getContext("2d");
const pcgLibraryDialog = document.querySelector("#pcg-library-dialog");
const pcgLibraryConflictDialog = document.querySelector("#pcg-library-conflict-dialog");
const pcgLibraryPreviewCanvas = document.querySelector("#pcg-library-preview");
const pcgLibraryPreviewContext = pcgLibraryPreviewCanvas.getContext("2d");
const pcgAnimationBuilderDialog = document.querySelector("#pcg-animation-builder-dialog");
const pcgAnimationBuilderPreviewCanvas = document.querySelector("#pcg-animation-builder-preview");
const pcgAnimationBuilderPreviewContext = pcgAnimationBuilderPreviewCanvas.getContext("2d");

translateDocument();
document.querySelector("#language-select").value = getLanguage();

let project = restoreProject();
let workspace = { baseSlot: 0, width: 1, height: 1 };
let tool = "pencil";
let gesture = null;
let hoverCell = null;
let clipboardMatrix = null;
let undoStack = [];
let redoStack = [];
let activeGroupId = null;
let gridVisible = true;
let screenGridVisible = true;
let selectedScreenCode = 0x80;
let screenCursor = { x: 0, y: 0 };
let screenGesture = null;
let vramGlyphGesture = null;
let activeView = "pcg";
let vramSourceVisible = false;
let activeAnimationId = null;
let activeAnimationFrame = 0;
let animationTimer = null;
let imageMosaicBitmap = null;
let imageMosaicRgba = null;
let imageMosaicLuminance = null;
let imageMosaicPreview = null;
let imageMosaicLoadGeneration = 0;
let activePcgLibraryPresetId = "side-grass-top";
let pcgLibraryScope = "all";
let pcgLibraryPendingApply = null;
let pcgLibraryStartSlot = null;
let pcgLibraryPreferences = restorePcgLibraryPreferences();
let pcgLibraryPreviewTimer = null;
let pcgAnimationBuilderSourcePreset = null;
let pcgAnimationBuilderPreviewTimer = null;
const imageMosaicGenerationScheduler = createFrameScheduler({
  requestFrame: (callback) => requestAnimationFrame(callback),
  cancelFrame: (frameId) => cancelAnimationFrame(frameId),
  task: generateImageMosaic,
});

const DIRECTION_KEYS = {
  ArrowUp: { action: "shift-up", deltaX: 0, deltaY: -1 },
  ArrowDown: { action: "shift-down", deltaX: 0, deltaY: 1 },
  ArrowLeft: { action: "shift-left", deltaX: -1, deltaY: 0 },
  ArrowRight: { action: "shift-right", deltaX: 1, deltaY: 0 },
};

function restoreProject() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    return saved ? parseProject(saved) : createProject({ withPreset: false });
  } catch {
    return createProject({ withPreset: false });
  }
}

function setMessage(message, tone = "normal") {
  const output = document.querySelector("#message-status");
  output.textContent = message;
  output.style.color = tone === "error" ? "var(--red)" : "var(--green)";
}

function formatError(error) {
  const detail = getLanguage() === "en" && error?.message ? `: ${error.message}` : "";
  return t("error.operationFailed", { detail });
}

function persistProject(message = t("message.autosaved")) {
  localStorage.setItem(STORAGE_KEY, serializeProject(project));
  document.querySelector("#save-status").textContent = message;
  setMessage(message);
}

function snapshotMutation(mutator, message) {
  const before = cloneProject(project);
  mutator();
  commitHistory(before, message);
  renderAll();
}

function commitHistory(before, message) {
  undoStack.push(before);
  if (undoStack.length > HISTORY_LIMIT) {
    undoStack.shift();
  }
  redoStack = [];
  persistProject(message);
}

function undo() {
  if (!undoStack.length) {
    return;
  }
  redoStack.push(cloneProject(project));
  project = undoStack.pop();
  persistProject(t("message.undo"));
  renderAll();
}

function redo() {
  if (!redoStack.length) {
    return;
  }
  undoStack.push(cloneProject(project));
  project = redoStack.pop();
  persistProject(t("message.redo"));
  renderAll();
}

function workspacePixelSize() {
  return {
    width: workspace.width * 8,
    height: workspace.height * 8,
  };
}

function resizeEditorCanvas() {
  const dimensions = workspacePixelSize();
  const longest = Math.max(dimensions.width, dimensions.height);
  const cellSize = Math.max(12, Math.min(48, Math.floor(520 / longest)));
  canvas.width = dimensions.width * cellSize;
  canvas.height = dimensions.height * cellSize;
  canvas.dataset.cellSize = String(cellSize);
}

function drawGridLines(count, vertical) {
  for (let index = 0; index <= count; index += 1) {
    if (!gridVisible && index % 8 !== 0) {
      continue;
    }
    const position = index * Number(canvas.dataset.cellSize);
    canvasContext.beginPath();
    canvasContext.strokeStyle = index % 8 === 0 ? "#ac8738" : "#344339";
    canvasContext.lineWidth = index % 8 === 0 ? 3 : 1;
    canvasContext.moveTo(vertical ? position : 0, vertical ? 0 : position);
    canvasContext.lineTo(vertical ? position : canvas.width, vertical ? canvas.height : position);
    canvasContext.stroke();
  }
}

function renderEditor() {
  resizeEditorCanvas();
  const cellSize = Number(canvas.dataset.cellSize);
  const dimensions = workspacePixelSize();
  canvasContext.fillStyle = "#09100b";
  canvasContext.fillRect(0, 0, canvas.width, canvas.height);
  const pixelInset = gridVisible ? 2 : 0;
  const pixelTrim = gridVisible ? 3 : 0;

  for (let y = 0; y < dimensions.height; y += 1) {
    for (let x = 0; x < dimensions.width; x += 1) {
      if (getPixel(project.glyphs, workspace, x, y)) {
        canvasContext.fillStyle = "#f0c35a";
        canvasContext.fillRect(x * cellSize + pixelInset, y * cellSize + pixelInset, cellSize - pixelTrim, cellSize - pixelTrim);
      }
    }
  }

  if (gesture?.preview) {
    canvasContext.fillStyle = "rgba(141, 227, 162, 0.62)";
    for (const [x, y] of gesture.preview) {
      canvasContext.fillRect(x * cellSize + 3, y * cellSize + 3, cellSize - 5, cellSize - 5);
    }
  }

  if (hoverCell) {
    canvasContext.strokeStyle = "#ffffff";
    canvasContext.lineWidth = 2;
    canvasContext.strokeRect(hoverCell.x * cellSize + 2, hoverCell.y * cellSize + 2, cellSize - 4, cellSize - 4);
  }

  drawGridLines(dimensions.width, true);
  drawGridLines(dimensions.height, false);
}

function drawGlyphPreview(context, glyph, x, y, scale, color) {
  context.fillStyle = color;
  for (let row = 0; row < 8; row += 1) {
    for (let column = 0; column < 8; column += 1) {
      if ((glyph[row] >> (7 - column)) & 1) {
        context.fillRect(x + column * scale, y + row * scale, scale, scale);
      }
    }
  }
}

function renderSlotRack() {
  const rack = document.querySelector("#slot-rack");
  rack.replaceChildren();
  const workspaceEnd = workspace.baseSlot + workspace.width * workspace.height;
  project.glyphs.forEach((glyph, slot) => {
    const button = document.createElement("button");
    const mini = document.createElement("canvas");
    const meta = document.createElement("span");
    const name = document.createElement("span");
    const used = glyph.some(Boolean);
    button.type = "button";
    button.className = "slot-card";
    button.classList.toggle("used", used);
    button.classList.toggle("in-workspace", slot >= workspace.baseSlot && slot < workspaceEnd);
    button.setAttribute("role", "gridcell");
    const state = project.names[slot] || (used ? t("common.customGlyph") : t("common.empty"));
    const description = t("pcg.slotDescription", { slot, code: hex(0x80 + slot), state });
    button.setAttribute("aria-label", description);
    button.title = description;
    if (slot >= workspace.baseSlot && slot < workspaceEnd) {
      button.setAttribute("aria-current", "true");
    }
    mini.width = 64;
    mini.height = 64;
    const miniContext = mini.getContext("2d");
    miniContext.fillStyle = "#0a100c";
    miniContext.fillRect(0, 0, 64, 64);
    drawGlyphPreview(miniContext, glyph, 0, 0, 8, "#8de3a2");
    meta.className = "slot-meta";
    meta.innerHTML = `<span>${slot.toString().padStart(2, "0")}</span><span>${hex(0x80 + slot)}</span>`;
    name.className = "slot-name";
    name.textContent = project.names[slot] || (used ? t("common.customGlyph") : t("common.empty"));
    button.append(mini, meta, name);
    button.addEventListener("click", () => {
      workspace = { baseSlot: slot, width: 1, height: 1 };
      activeGroupId = null;
      document.querySelector("#group-name").value = "";
      syncWorkspaceInputs();
      renderAll();
      canvas.focus();
    });
    rack.append(button);
  });
}

function renderScreenCanvas(context, target, scale, { cursor = false } = {}) {
  context.fillStyle = "#020503";
  context.fillRect(0, 0, target.width, target.height);
  for (let y = 0; y < SCREEN_HEIGHT; y += 1) {
    for (let x = 0; x < SCREEN_WIDTH; x += 1) {
      const code = getScreenCell(project.screen, x, y);
      drawGlyphPreview(context, resolveScreenGlyph(project, code), x * 8 * scale, y * 8 * scale, scale, "#8de3a2");
    }
  }
  context.fillStyle = "rgba(31, 82, 43, 0.12)";
  for (let y = 0; y < target.height; y += Math.max(2, scale * 2)) {
    context.fillRect(0, y, target.width, Math.max(1, scale));
  }
  if (cursor) {
    if (vramSourceVisible && project.screen.mode === DISPLAY_MODES.PCG && selectedScreenCode >= 0xa0) {
      const sourceOffset = vramPcgSourceOffset(selectedScreenCode);
      context.strokeStyle = "#e97867";
      context.lineWidth = 2;
      for (let index = 0; index < 8; index += 1) {
        const cellOffset = sourceOffset + index;
        const sourceX = cellOffset % SCREEN_WIDTH;
        const sourceY = Math.floor(cellOffset / SCREEN_WIDTH);
        context.strokeRect(sourceX * 8 * scale + 2, sourceY * 8 * scale + 2, 8 * scale - 4, 8 * scale - 4);
      }
    }
    context.strokeStyle = "#f0c35a";
    context.lineWidth = 2;
    context.strokeRect(screenCursor.x * 8 * scale + 1, screenCursor.y * 8 * scale + 1, 8 * scale - 2, 8 * scale - 2);
    if (screenGridVisible) {
      context.strokeStyle = "rgba(82, 117, 92, 0.28)";
      context.lineWidth = 1;
      for (let x = 0; x <= SCREEN_WIDTH; x += 1) {
        context.beginPath();
        context.moveTo(x * 8 * scale, 0);
        context.lineTo(x * 8 * scale, target.height);
        context.stroke();
      }
      for (let y = 0; y <= SCREEN_HEIGHT; y += 1) {
        context.beginPath();
        context.moveTo(0, y * 8 * scale);
        context.lineTo(target.width, y * 8 * scale);
        context.stroke();
      }
    }
  }
}

function renderCrt() {
  renderScreenCanvas(crtContext, crtCanvas, 1);
  renderScreenCanvas(screenContext, screenCanvas, 3, { cursor: true });
}

function paletteBounds(range) {
  const ranges = {
    all: [0x00, 0xff],
    text: [0x00, 0x3f],
    symbolsAndSemigraphics: [0x40, 0x7f],
    upper: [0x80, project.screen.mode === DISPLAY_MODES.PCG ? 0x9f : 0xff],
    extended: [0xa0, 0xff],
  };
  return ranges[range] ?? ranges.all;
}

function screenCodeKind(code) {
  if (code < 0x40) return t("crt.romTextKind");
  if (code < 0x60) return t("crt.romSymbolKind");
  if (code < 0x80) return t("crt.romSemigraphicKind");
  if (project.screen.mode === DISPLAY_MODES.INVERSE) return t("crt.inverseRomKind");
  if (code < 0xa0) return t("crt.pcgSlotKind", { slot: code - 0x80 });
  return t("crt.vramPcgKind");
}

function renderCharacterPalette() {
  const palette = document.querySelector("#character-palette");
  const range = document.querySelector("#palette-range").value;
  const [start, end] = paletteBounds(range);
  palette.replaceChildren();
  document.querySelector("#palette-range-address").textContent = `${hex(start)}-${hex(end)}`;
  for (let code = start; code <= end; code += 1) {
    const button = document.createElement("button");
    const preview = document.createElement("canvas");
    const label = document.createElement("span");
    button.type = "button";
    button.className = "character-card";
    button.classList.toggle("selected", code === selectedScreenCode);
    button.setAttribute("role", "gridcell");
    button.setAttribute("aria-label", t("crt.codeDescription", { code: hex(code), kind: screenCodeKind(code) }));
    preview.width = 64;
    preview.height = 64;
    const context = preview.getContext("2d");
    context.fillStyle = "#050906";
    context.fillRect(0, 0, 64, 64);
    drawGlyphPreview(context, resolveScreenGlyph(project, code), 0, 0, 8, "#8de3a2");
    label.textContent = hex(code);
    button.append(preview, label);
    button.addEventListener("click", () => {
      selectedScreenCode = code;
      renderCharacterPalette();
      renderSelectedCharacter();
      renderDisplayState();
      renderCrt();
      screenCanvas.focus();
    });
    palette.append(button);
  }
}

function renderSelectedCharacter() {
  const preview = document.querySelector("#selected-character-preview");
  const context = preview.getContext("2d");
  context.fillStyle = "#050906";
  context.fillRect(0, 0, preview.width, preview.height);
  drawGlyphPreview(context, resolveScreenGlyph(project, selectedScreenCode), 0, 0, 8, "#8de3a2");
  document.querySelector("#selected-character-code").textContent = hex(selectedScreenCode);
  document.querySelector("#selected-character-kind").textContent = screenCodeKind(selectedScreenCode);
  renderVramGlyphEditor();
}

function renderVramGlyphEditor() {
  const editor = document.querySelector("#vram-glyph-editor");
  const available = project.screen.mode === DISPLAY_MODES.PCG && selectedScreenCode >= 0xa0;
  editor.hidden = !available;
  if (!available) return;
  const sourceOffset = vramPcgSourceOffset(selectedScreenCode);
  const startAddress = 0xc100 + sourceOffset;
  document.querySelector("#vram-glyph-address").textContent = `$${startAddress.toString(16).toUpperCase()}-$${(startAddress + 7).toString(16).toUpperCase()}`;
  vramGlyphContext.fillStyle = "#050906";
  vramGlyphContext.fillRect(0, 0, vramGlyphCanvas.width, vramGlyphCanvas.height);
  drawGlyphPreview(vramGlyphContext, resolveScreenGlyph(project, selectedScreenCode), 0, 0, 32, "#8de3a2");
  vramGlyphContext.strokeStyle = "#344339";
  vramGlyphContext.lineWidth = 2;
  for (let index = 0; index <= 8; index += 1) {
    const position = index * 32;
    vramGlyphContext.beginPath();
    vramGlyphContext.moveTo(position, 0);
    vramGlyphContext.lineTo(position, 256);
    vramGlyphContext.stroke();
    vramGlyphContext.beginPath();
    vramGlyphContext.moveTo(0, position);
    vramGlyphContext.lineTo(256, position);
    vramGlyphContext.stroke();
  }
}

function renderDisplayState() {
  const pcgMode = project.screen.mode === DISPLAY_MODES.PCG;
  document.querySelector("#display-mode").value = project.screen.mode;
  document.querySelector("#display-plane-state").textContent = pcgMode ? "CMODE PCG" : "CMODE inverse";
  document.querySelector("#inverse-state").textContent = pcgMode ? t("common.unavailable") : t("common.available");
  document.querySelector("#pcg-state").textContent = pcgMode ? t("common.available") : t("common.unavailable");
  document.querySelector("#mode-compatibility").textContent = pcgMode
    ? t("crt.modePcgHelp")
    : t("crt.modeInverseHelp");
  document.querySelector("#rom-source").textContent = project.romSource === "Built-in approximation"
    ? t("crt.romBuiltIn")
    : t("crt.romImported");
  const upperOption = document.querySelector('#palette-range option[value="upper"]');
  const extendedOption = document.querySelector('#palette-range option[value="extended"]');
  upperOption.textContent = pcgMode ? t("crt.pcgCodes") : t("crt.inverseCodes");
  extendedOption.textContent = pcgMode ? t("crt.vramPcgCodes") : t("crt.inverseExtended");
  document.querySelector(".warning-panel").hidden = !pcgMode;
  const sourceAvailable = pcgMode && selectedScreenCode >= 0xa0;
  document.querySelector("#source-highlight-control").hidden = !sourceAvailable;
  document.querySelector("#show-vram-source").checked = vramSourceVisible;
  document.querySelector("#source-highlight-legend").hidden = !sourceAvailable || !vramSourceVisible;
  const visible = new Set(visiblePcgSlots(project.screen));
  document.querySelector("#visible-pcg-count").textContent = `${visible.size} / 32`;
  const coverage = document.querySelector("#visible-pcg-slots");
  coverage.replaceChildren();
  for (let slot = 0; slot < 32; slot += 1) {
    const cell = document.createElement("span");
    cell.className = "coverage-cell";
    cell.classList.toggle("visible", visible.has(slot));
    cell.textContent = slot.toString().padStart(2, "0");
    coverage.append(cell);
  }
  updateScreenCursorSummary();
}

function updateScreenCursorSummary() {
  const address = 0xc100 + screenCursor.y * SCREEN_WIDTH + screenCursor.x;
  const code = getScreenCell(project.screen, screenCursor.x, screenCursor.y);
  document.querySelector("#screen-cursor-summary").textContent = `X ${screenCursor.x.toString().padStart(2, "0")} / Y ${screenCursor.y.toString().padStart(2, "0")} / $${address.toString(16).toUpperCase()} / ${hex(code)}`;
}

function renderByteInspector() {
  const inspector = document.querySelector("#byte-inspector");
  inspector.replaceChildren();
  const count = workspace.width * workspace.height;
  for (let offset = 0; offset < count; offset += 1) {
    const slot = workspace.baseSlot + offset;
    const entry = document.createElement("div");
    const heading = document.createElement("strong");
    const code = document.createElement("code");
    entry.className = "byte-entry";
    heading.textContent = t("inspection.slotCode", {
      slot: slot.toString().padStart(2, "0"),
      code: hex(0x80 + slot),
      name: project.names[slot] ? ` / ${project.names[slot]}` : "",
    });
    code.textContent = project.glyphs[slot]
      .map((value, row) => `${row}: ${hex(value)}  ${value.toString(2).padStart(8, "0")}`)
      .join("\n");
    entry.append(heading, code);
    inspector.append(entry);
  }
}

function renderUsage() {
  const used = project.glyphs.filter((glyph) => glyph.some(Boolean)).length;
  document.querySelector("#usage-status").textContent = t("status.usage", { used });
  document.querySelector("#undo").disabled = undoStack.length === 0;
  document.querySelector("#redo").disabled = redoStack.length === 0;
  document.querySelector("#paste-selection").disabled = clipboardMatrix === null;
}

function renderSavedGroups() {
  const select = document.querySelector("#saved-group");
  const selected = activeGroupId ?? "";
  select.replaceChildren(new Option(t("pcg.currentLayout"), ""));
  project.groups.forEach((group) => {
    const start = group.baseSlot.toString().padStart(2, "0");
    select.add(new Option(`${group.name} (${group.width}x${group.height}, S${start})`, group.id));
  });
  if (project.groups.some((group) => group.id === selected)) {
    select.value = selected;
  } else {
    activeGroupId = null;
    select.value = "";
    document.querySelector("#group-name").value = "";
  }
  document.querySelector("#delete-group").disabled = activeGroupId === null;
  const activeGroup = project.groups.find((group) => group.id === activeGroupId);
  document.querySelector("#group-summary").textContent = activeGroup
    ? t("pcg.groupSummary", { name: activeGroup.name, width: activeGroup.width, height: activeGroup.height })
    : t("pcg.currentSummary", { width: workspace.width, height: workspace.height, slot: workspace.baseSlot.toString().padStart(2, "0") });
}

function knownPcgPresetIds(values, limit) {
  const known = new Set(PCG_PRESETS.map(({ id }) => id));
  return [...new Set(Array.isArray(values) ? values.filter((id) => typeof id === "string" && known.has(id)) : [])].slice(0, limit);
}

function restorePcgLibraryPreferences() {
  try {
    const saved = JSON.parse(localStorage.getItem(PCG_LIBRARY_STORAGE_KEY) || "{}");
    return {
      favorites: knownPcgPresetIds(saved.favorites, PCG_PRESETS.length),
      recent: knownPcgPresetIds(saved.recent, 12),
    };
  } catch {
    return { favorites: [], recent: [] };
  }
}

function persistPcgLibraryPreferences() {
  try {
    localStorage.setItem(PCG_LIBRARY_STORAGE_KEY, JSON.stringify(pcgLibraryPreferences));
  } catch {
    // Preferences remain available for the current page session.
  }
}

function activePcgLibraryPreset() {
  try {
    return getPcgPreset(activePcgLibraryPresetId);
  } catch {
    return null;
  }
}

function pcgPresetSlotCount(preset) {
  return preset.width * preset.height;
}

function presetDimensions(preset) {
  return `${preset.width * 8}x${preset.height * 8}`;
}

function pcgPresetConflictSummary(conflict) {
  return [
    conflict.occupiedSlots.length ? `${conflict.occupiedSlots.length} used slot(s)` : "",
    conflict.groupIds.length ? `${conflict.groupIds.length} saved group(s)` : "",
    conflict.animationIds.length ? `${conflict.animationIds.length} animation clip(s)` : "",
  ].filter(Boolean);
}

function clampPcgStartSlot(preset, requested) {
  const maximum = 32 - pcgPresetSlotCount(preset);
  const baseSlot = Number.isInteger(requested) ? requested : workspace.baseSlot;
  return Math.max(0, Math.min(maximum, baseSlot));
}

function clampPcgLibraryStartSlot(preset) {
  const input = document.querySelector("#pcg-library-start-slot");
  const maximum = 32 - pcgPresetSlotCount(preset);
  const requested = pcgLibraryStartSlot ?? Number(input.value);
  pcgLibraryStartSlot = clampPcgStartSlot(preset, requested);
  input.min = "0";
  input.max = String(maximum);
  input.value = String(pcgLibraryStartSlot);
  return pcgLibraryStartSlot;
}

function drawPcgPresetPreview(context, target, preset, frameIndex = 0) {
  context.imageSmoothingEnabled = false;
  context.fillStyle = "#020503";
  context.fillRect(0, 0, target.width, target.height);
  if (!preset) return;
  const glyphs = preset.kind === "animation"
    ? preset.frames[frameIndex % preset.frames.length].glyphs
    : preset.glyphs;
  const width = preset.width * 8;
  const height = preset.height * 8;
  const scale = Math.max(1, Math.floor(Math.min(target.width / width, target.height / height)));
  const offsetX = Math.floor((target.width - width * scale) / 2);
  const offsetY = Math.floor((target.height - height * scale) / 2);
  context.fillStyle = "#8de3a2";
  for (let y = 0; y < height; y += 1) {
    for (let x = 0; x < width; x += 1) {
      const tile = Math.floor(y / 8) * preset.width + Math.floor(x / 8);
      const glyph = glyphs[tile];
      if ((glyph[y % 8] >> (7 - (x % 8))) & 1) {
        context.fillRect(offsetX + x * scale, offsetY + y * scale, scale, scale);
      }
    }
  }
}

function stopPcgLibraryPreview() {
  if (pcgLibraryPreviewTimer !== null) {
    clearInterval(pcgLibraryPreviewTimer);
    pcgLibraryPreviewTimer = null;
  }
}

function startPcgLibraryPreview(preset) {
  stopPcgLibraryPreview();
  drawPcgPresetPreview(pcgLibraryPreviewContext, pcgLibraryPreviewCanvas, preset);
  if (!preset || preset.kind !== "animation") return;
  let frameIndex = 0;
  pcgLibraryPreviewTimer = setInterval(() => {
    if (!pcgLibraryDialog.open || activePcgLibraryPresetId !== preset.id) {
      stopPcgLibraryPreview();
      return;
    }
    frameIndex = (frameIndex + 1) % preset.frames.length;
    drawPcgPresetPreview(pcgLibraryPreviewContext, pcgLibraryPreviewCanvas, preset, frameIndex);
  }, preset.frameDurationMs);
}

function stopPcgAnimationBuilderPreview() {
  if (pcgAnimationBuilderPreviewTimer !== null) {
    clearInterval(pcgAnimationBuilderPreviewTimer);
    pcgAnimationBuilderPreviewTimer = null;
  }
}

function startPcgAnimationBuilderPreview(animation) {
  stopPcgAnimationBuilderPreview();
  drawPcgPresetPreview(pcgAnimationBuilderPreviewContext, pcgAnimationBuilderPreviewCanvas, animation);
  let frameIndex = 0;
  pcgAnimationBuilderPreviewTimer = setInterval(() => {
    if (!pcgAnimationBuilderDialog.open) {
      stopPcgAnimationBuilderPreview();
      return;
    }
    frameIndex = (frameIndex + 1) % animation.frames.length;
    drawPcgPresetPreview(pcgAnimationBuilderPreviewContext, pcgAnimationBuilderPreviewCanvas, animation, frameIndex);
  }, animation.frameDurationMs);
}

function pcgAnimationBuilderTemplate(sourcePreset) {
  const templates = filterPcgAnimationTemplates(sourcePreset);
  const selectedId = document.querySelector("#pcg-animation-template").value;
  return templates.find(({ id }) => id === selectedId) ?? templates[0] ?? null;
}

function clampPcgAnimationBuilderDuration(template) {
  const input = document.querySelector("#pcg-animation-duration");
  const requested = Number(input.value);
  const duration = Number.isInteger(requested) && requested >= 16 && requested <= 60000
    ? requested
    : template.frameDurationMs;
  input.value = String(duration);
  return duration;
}

function clampPcgAnimationBuilderStartSlot(preset) {
  const input = document.querySelector("#pcg-animation-start-slot");
  const maximum = 32 - pcgPresetSlotCount(preset);
  const startSlot = clampPcgStartSlot(preset, Number(input.value));
  input.min = "0";
  input.max = String(maximum);
  input.value = String(startSlot);
  return startSlot;
}

function renderPcgAnimationBuilder() {
  const source = pcgAnimationBuilderSourcePreset;
  const sourceOutput = document.querySelector("#pcg-animation-builder-source");
  const templateSelect = document.querySelector("#pcg-animation-template");
  const summary = document.querySelector("#pcg-animation-builder-summary");
  const generate = document.querySelector("#generate-pcg-library-animation");
  const templates = filterPcgAnimationTemplates(source);
  if (!source || templates.length === 0) {
    stopPcgAnimationBuilderPreview();
    sourceOutput.textContent = "Choose an asset or set from the PCG Library.";
    templateSelect.replaceChildren();
    summary.textContent = "No animation source is selected.";
    drawPcgPresetPreview(pcgAnimationBuilderPreviewContext, pcgAnimationBuilderPreviewCanvas, null);
    generate.disabled = true;
    return;
  }

  const selectedId = templates.some(({ id }) => id === templateSelect.value)
    ? templateSelect.value
    : templates[0].id;
  templateSelect.replaceChildren(...templates.map(({ id, name }) => new Option(name, id)));
  templateSelect.value = selectedId;
  const template = pcgAnimationBuilderTemplate(source);
  const duration = clampPcgAnimationBuilderDuration(template);
  const startSlot = clampPcgAnimationBuilderStartSlot(source);
  const animation = createPcgAnimationFromTemplate(source, template.id, { frameDurationMs: duration });
  const endSlot = startSlot + pcgPresetSlotCount(source) - 1;
  sourceOutput.textContent = `Source: ${source.name} / ${presetDimensions(source)} / ${source.kind.toUpperCase()}`;
  summary.textContent = `${animation.frames.length} frames / ${duration} ms / ${animation.frames.length * pcgPresetSlotCount(source) * 8} bytes / Slots ${String(startSlot).padStart(2, "0")}-${String(endSlot).padStart(2, "0")}`;
  if (pcgAnimationBuilderDialog.open) {
    startPcgAnimationBuilderPreview(animation);
  } else {
    stopPcgAnimationBuilderPreview();
    drawPcgPresetPreview(pcgAnimationBuilderPreviewContext, pcgAnimationBuilderPreviewCanvas, animation);
  }
  generate.disabled = false;
}

function openPcgAnimationBuilder() {
  const source = activePcgLibraryPreset();
  if (!source || source.kind === "animation") return;
  const templates = filterPcgAnimationTemplates(source);
  if (templates.length === 0) return;
  pcgAnimationBuilderSourcePreset = source;
  const templateSelect = document.querySelector("#pcg-animation-template");
  templateSelect.replaceChildren(...templates.map(({ id, name }) => new Option(name, id)));
  templateSelect.value = templates[0].id;
  document.querySelector("#pcg-animation-duration").value = String(templates[0].frameDurationMs);
  document.querySelector("#pcg-animation-start-slot").value = String(clampPcgLibraryStartSlot(source));
  renderPcgAnimationBuilder();
  if (!pcgAnimationBuilderDialog.open) pcgAnimationBuilderDialog.showModal();
  renderPcgAnimationBuilder();
  templateSelect.focus();
}

function generatePcgLibraryAnimation() {
  const source = pcgAnimationBuilderSourcePreset;
  const template = pcgAnimationBuilderTemplate(source);
  if (!source || !template) return;
  const duration = clampPcgAnimationBuilderDuration(template);
  const startSlot = clampPcgAnimationBuilderStartSlot(source);
  let animation;
  try {
    animation = createPcgAnimationFromTemplate(source, template.id, { frameDurationMs: duration });
  } catch (error) {
    setMessage(formatError(error), "error");
    return;
  }
  const recentPresetId = source.id;
  if (pcgAnimationBuilderDialog.open) pcgAnimationBuilderDialog.close();
  requestPcgLibraryApply(animation, startSlot, recentPresetId);
}

function pcgLibraryScopedIds() {
  if (pcgLibraryScope === "favorites") return pcgLibraryPreferences.favorites;
  if (pcgLibraryScope === "recent") return pcgLibraryPreferences.recent;
  return null;
}

function pcgLibraryFilters() {
  return {
    category: document.querySelector("#pcg-library-category").value,
    size: document.querySelector("#pcg-library-size").value,
    kind: document.querySelector("#pcg-library-kind").value,
    query: document.querySelector("#pcg-library-search").value,
    ids: pcgLibraryScopedIds(),
  };
}

function populatePcgLibraryCategoryOptions() {
  const select = document.querySelector("#pcg-library-category");
  const selected = select.value;
  select.replaceChildren(
    new Option("All categories", "all"),
    ...PCG_PRESET_CATEGORY_OPTIONS.map(({ id, label }) => new Option(label, id)),
  );
  select.value = PCG_PRESET_CATEGORIES.includes(selected) ? selected : "all";
}

function pcgCategoryLabel(category) {
  return PCG_CATEGORY_LABELS[category] ?? category;
}

function renderPcgLibraryTotals() {
  const total = PCG_PRESETS.length;
  document.querySelector("#pcg-library-launch-count").textContent = `${total} presets`;
  document.querySelector("#pcg-library-intro").textContent = `${total} original assets, sets, and animations for JR-100 projects.`;
}

function renderPcgLibraryCard(preset) {
  const button = document.createElement("button");
  const preview = document.createElement("canvas");
  const title = document.createElement("strong");
  const details = document.createElement("small");
  const tags = document.createElement("small");
  button.type = "button";
  button.className = "pcg-library-card";
  button.setAttribute("role", "option");
  button.setAttribute("aria-selected", preset.id === activePcgLibraryPresetId ? "true" : "false");
  button.title = `${preset.name} / ${presetDimensions(preset)} / ${preset.kind}`;
  preview.width = 72;
  preview.height = 72;
  drawPcgPresetPreview(preview.getContext("2d"), preview, preset);
  title.textContent = preset.name;
  details.textContent = `${pcgCategoryLabel(preset.category)} / ${preset.kind.toUpperCase()} / ${presetDimensions(preset)} / ${pcgPresetSlotCount(preset)} slots`;
  tags.textContent = preset.tags.join(", ");
  button.append(preview, title, details, tags);
  button.addEventListener("click", () => {
    activePcgLibraryPresetId = preset.id;
    renderPcgLibrary();
  });
  return button;
}

function inspectPcgLibraryPresetConflicts(preset, startSlot) {
  return preset.kind === "animation"
    ? inspectPcgAnimationPresetConflicts(project, preset, startSlot)
    : inspectPcgPresetConflicts(project, preset, startSlot);
}

function renderPcgLibraryDetail(preset) {
  const title = document.querySelector("#pcg-library-detail-title");
  const category = document.querySelector("#pcg-library-detail-category");
  const tags = document.querySelector("#pcg-library-detail-tags");
  const favorite = document.querySelector("#pcg-library-favorite");
  const destination = document.querySelector("#pcg-library-destination");
  const conflicts = document.querySelector("#pcg-library-conflicts");
  const apply = document.querySelector("#pcg-library-apply");
  const generateAnimation = document.querySelector("#pcg-library-generate-animation");
  startPcgLibraryPreview(preset);
  if (!preset) {
    title.textContent = "No matching preset";
    category.textContent = "Library";
    tags.textContent = "Adjust the filters to find an asset, set, or animation.";
    favorite.disabled = true;
    destination.textContent = "No destination selected.";
    conflicts.textContent = "";
    conflicts.dataset.conflict = "false";
    apply.disabled = true;
    generateAnimation.disabled = true;
    generateAnimation.title = "Choose an asset or set to create an animation.";
    return;
  }
  const startSlot = clampPcgLibraryStartSlot(preset);
  const conflict = inspectPcgLibraryPresetConflicts(preset, startSlot);
  const conflictDetails = pcgPresetConflictSummary(conflict);
  const endCode = 0x80 + conflict.endSlot;
  title.textContent = preset.name;
  category.textContent = `${pcgCategoryLabel(preset.category)} / ${preset.kind.toUpperCase()}`;
  const animationMetadata = preset.kind === "animation"
    ? ` / ${preset.frames.length} frames / ${preset.frameDurationMs} ms / ${preset.frames.length * pcgPresetSlotCount(preset) * 8} bytes`
    : "";
  tags.textContent = `${presetDimensions(preset)} / ${pcgPresetSlotCount(preset)} slots${animationMetadata} / ${preset.tags.join(", ")}`;
  favorite.disabled = false;
  favorite.textContent = pcgLibraryPreferences.favorites.includes(preset.id) ? "Remove favorite" : "Favorite";
  destination.textContent = `Slots ${String(startSlot).padStart(2, "0")}-${String(conflict.endSlot).padStart(2, "0")} / $${(0x80 + startSlot).toString(16).toUpperCase()}-$${endCode.toString(16).toUpperCase()}`;
  if (conflictDetails.length === 0) {
    conflicts.textContent = "Destination is clear.";
    conflicts.dataset.conflict = "false";
  } else {
    conflicts.textContent = `Replacement will remove ${conflictDetails.join(", ")}.`;
    conflicts.dataset.conflict = "true";
  }
  apply.disabled = false;
  const canGenerateAnimation = preset.kind !== "animation" && filterPcgAnimationTemplates(preset).length > 0;
  generateAnimation.disabled = !canGenerateAnimation;
  generateAnimation.title = canGenerateAnimation
    ? "Create an editable animation from this asset or set."
    : "Animation presets cannot be used as template sources.";
}

function renderPcgLibrary() {
  const presets = filterPcgPresets(pcgLibraryFilters());
  if (presets.length && !presets.some(({ id }) => id === activePcgLibraryPresetId)) {
    activePcgLibraryPresetId = presets[0].id;
  }
  const gallery = document.querySelector("#pcg-library-gallery");
  gallery.replaceChildren(...presets.map(renderPcgLibraryCard));
  document.querySelector("#pcg-library-count").textContent = `${presets.length} result${presets.length === 1 ? "" : "s"}`;
  document.querySelectorAll("[data-pcg-library-scope]").forEach((button) => {
    const active = button.dataset.pcgLibraryScope === pcgLibraryScope;
    button.classList.toggle("active", active);
    button.setAttribute("aria-pressed", active ? "true" : "false");
  });
  renderPcgLibraryDetail(presets.find(({ id }) => id === activePcgLibraryPresetId) ?? null);
}

function togglePcgLibraryFavorite() {
  const preset = activePcgLibraryPreset();
  if (!preset) return;
  const isFavorite = pcgLibraryPreferences.favorites.includes(preset.id);
  pcgLibraryPreferences.favorites = isFavorite
    ? pcgLibraryPreferences.favorites.filter((id) => id !== preset.id)
    : [...pcgLibraryPreferences.favorites, preset.id];
  persistPcgLibraryPreferences();
  renderPcgLibrary();
}

function rememberPcgLibraryPreset(presetId) {
  pcgLibraryPreferences.recent = [presetId, ...pcgLibraryPreferences.recent.filter((id) => id !== presetId)].slice(0, 12);
  persistPcgLibraryPreferences();
}

function applyPcgLibraryPreset(preset, startSlot, { recentPresetId = preset.id } = {}) {
  let result;
  snapshotMutation(() => {
    result = preset.kind === "animation"
      ? applyPcgAnimationPreset(project, preset, startSlot)
      : applyPcgPreset(project, preset, startSlot);
    workspace = result.workspace;
    activeGroupId = preset.kind === "animation" || result.replacedSlotCount === 1
      ? null
      : `preset-${preset.id}-${startSlot}`;
    if (result.animationId) {
      activeAnimationId = result.animationId;
      activeAnimationFrame = 0;
    }
  }, `Applied ${preset.name}`);
  pcgLibraryStartSlot = result.workspace.baseSlot;
  rememberPcgLibraryPreset(recentPresetId);
  syncWorkspaceInputs();
  if (pcgLibraryConflictDialog.open) pcgLibraryConflictDialog.close();
  if (pcgLibraryDialog.open) pcgLibraryDialog.close();
  renderAll();
  if (preset.kind === "animation") {
    setActiveView("animation");
  } else {
    canvas.focus();
  }
}

function requestPcgLibraryApply(preset = activePcgLibraryPreset(), startSlot = null, recentPresetId = preset?.id) {
  if (!preset) return;
  const resolvedStartSlot = startSlot === null
    ? clampPcgLibraryStartSlot(preset)
    : clampPcgStartSlot(preset, startSlot);
  pcgLibraryStartSlot = resolvedStartSlot;
  document.querySelector("#pcg-library-start-slot").value = String(resolvedStartSlot);
  const conflict = inspectPcgLibraryPresetConflicts(preset, resolvedStartSlot);
  const conflictDetails = pcgPresetConflictSummary(conflict);
  if (conflictDetails.length === 0) {
    applyPcgLibraryPreset(preset, resolvedStartSlot, { recentPresetId });
    return;
  }
  pcgLibraryPendingApply = { preset, startSlot: resolvedStartSlot, recentPresetId };
  const sections = [
    `Slots ${String(conflict.startSlot).padStart(2, "0")}-${String(conflict.endSlot).padStart(2, "0")}`,
    ...conflictDetails,
  ];
  document.querySelector("#pcg-library-conflict-details").textContent = `Applying ${preset.name} will replace ${sections.join(", ")}.`;
  if (!pcgLibraryConflictDialog.open) pcgLibraryConflictDialog.showModal();
}

function openPcgLibrary() {
  pcgLibraryStartSlot = workspace.baseSlot;
  renderPcgLibrary();
  if (!pcgLibraryDialog.open) pcgLibraryDialog.showModal();
}

function updateAssemblyOutput() {
  const label = document.querySelector("#assembly-label").value;
  const target = document.querySelector("#export-target").value;
  const exporters = {
    pcg: () => exportAssembly(project, { label }),
    screen: () => exportScreenAssembly(project, { label }),
    combined: () => exportCombinedAssembly(project, { pcgLabel: label, screenLabel: "SCREEN_DATA" }),
    animation: () => exportAnimationAssembly(project.animations, { label }),
  };
  document.querySelector("#assembly-output").value = exporters[target]();
}

function renderAll() {
  clampHoverCellToWorkspace();
  renderPcgLibraryTotals();
  renderEditor();
  renderSlotRack();
  renderCrt();
  renderCharacterPalette();
  renderSelectedCharacter();
  renderDisplayState();
  renderByteInspector();
  renderUsage();
  renderSavedGroups();
  renderAnimation();
  updateAssemblyOutput();
  updateToolButtons();
  updateSizeButtons();
  if (pcgLibraryDialog.open) {
    renderPcgLibrary();
  }
}

function activeAnimation() {
  const selected = project.animations.find((clip) => clip.id === activeAnimationId);
  if (selected) {
    return selected;
  }
  activeAnimationId = project.animations[0]?.id ?? null;
  activeAnimationFrame = 0;
  return project.animations[0] ?? null;
}

function drawAnimationFrame(clip, frame) {
  animationContext.fillStyle = "#050906";
  animationContext.fillRect(0, 0, animationCanvas.width, animationCanvas.height);
  if (!clip || !frame) {
    animationContext.fillStyle = "#718076";
    animationContext.font = "16px sans-serif";
    animationContext.textAlign = "center";
    animationContext.fillText(t("animation.emptyPreview"), animationCanvas.width / 2, animationCanvas.height / 2);
    return;
  }
  const scale = Math.max(1, Math.floor(Math.min(448 / (clip.width * 8), 448 / (clip.height * 8))));
  const renderedWidth = clip.width * 8 * scale;
  const renderedHeight = clip.height * 8 * scale;
  const originX = Math.floor((animationCanvas.width - renderedWidth) / 2);
  const originY = Math.floor((animationCanvas.height - renderedHeight) / 2);
  frame.glyphs.forEach((glyph, offset) => {
    const tileX = offset % clip.width;
    const tileY = Math.floor(offset / clip.width);
    drawGlyphPreview(
      animationContext,
      glyph,
      originX + tileX * 8 * scale,
      originY + tileY * 8 * scale,
      scale,
      "#8de3a2",
    );
  });
  animationContext.strokeStyle = "#ac8738";
  animationContext.lineWidth = 2;
  for (let x = 0; x <= clip.width; x += 1) {
    animationContext.beginPath();
    animationContext.moveTo(originX + x * 8 * scale, originY);
    animationContext.lineTo(originX + x * 8 * scale, originY + renderedHeight);
    animationContext.stroke();
  }
  for (let y = 0; y <= clip.height; y += 1) {
    animationContext.beginPath();
    animationContext.moveTo(originX, originY + y * 8 * scale);
    animationContext.lineTo(originX + renderedWidth, originY + y * 8 * scale);
    animationContext.stroke();
  }
}

function drawAnimationThumbnail(canvasElement, clip, frame) {
  const context = canvasElement.getContext("2d");
  context.fillStyle = "#050906";
  context.fillRect(0, 0, canvasElement.width, canvasElement.height);
  const scale = Math.max(1, Math.floor(Math.min(56 / (clip.width * 8), 56 / (clip.height * 8))));
  const width = clip.width * 8 * scale;
  const height = clip.height * 8 * scale;
  const originX = Math.floor((64 - width) / 2);
  const originY = Math.floor((64 - height) / 2);
  frame.glyphs.forEach((glyph, offset) => {
    drawGlyphPreview(
      context,
      glyph,
      originX + (offset % clip.width) * 8 * scale,
      originY + Math.floor(offset / clip.width) * 8 * scale,
      scale,
      "#8de3a2",
    );
  });
}

function renderAnimation() {
  const clip = activeAnimation();
  const clipList = document.querySelector("#animation-clip-list");
  clipList.replaceChildren();
  project.animations.forEach((candidate) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "animation-clip-card";
    button.classList.toggle("selected", candidate.id === clip?.id);
    button.innerHTML = `<strong></strong><span></span>`;
    button.querySelector("strong").textContent = candidate.name;
    button.querySelector("span").textContent = t("animation.clipMeta", {
      width: candidate.width,
      height: candidate.height,
      frames: candidate.frames.length,
      slot: candidate.baseSlot.toString().padStart(2, "0"),
    });
    button.addEventListener("click", () => {
      activeAnimationId = candidate.id;
      activeAnimationFrame = 0;
      stopAnimationPlayback();
      renderAnimation();
    });
    clipList.append(button);
  });

  const controls = document.querySelector("#animation-settings");
  controls.classList.toggle("disabled-panel", !clip);
  controls.querySelectorAll("input, button").forEach((control) => { control.disabled = !clip; });
  const frameButtons = [
    "#update-animation-frame",
    "#load-animation-frame",
    "#duplicate-animation-frame",
    "#delete-animation-frame",
    "#previous-animation-frame",
    "#play-animation",
    "#next-animation-frame",
  ];
  frameButtons.forEach((selector) => { document.querySelector(selector).disabled = !clip?.frames.length; });
  document.querySelector("#capture-animation-frame").disabled = !clip;
  if (!clip) {
    document.querySelector("#animation-frame-list").replaceChildren();
    document.querySelector("#animation-frame-summary").textContent = t("animation.frameCount", { count: 0 });
    drawAnimationFrame(null, null);
    document.querySelector("#animation-resident-slots").textContent = t("animation.slotCount", { count: 0 });
    document.querySelector("#animation-copy-bytes").textContent = t("animation.byteCount", { count: 0 });
    document.querySelector("#animation-stored-frames").textContent = "0";
    document.querySelector("#animation-data-bytes").textContent = t("animation.byteCount", { count: 0 });
    document.querySelector("#animation-resident-range").textContent = "--";
    document.querySelector("#animation-screen-codes").textContent = "--";
    document.querySelector("#animation-name").value = "";
    return;
  }

  activeAnimationFrame = Math.max(0, Math.min(activeAnimationFrame, Math.max(0, clip.frames.length - 1)));
  const slotCount = clip.width * clip.height;
  const lastSlot = clip.baseSlot + slotCount - 1;
  const firstCode = 0x80 + clip.baseSlot;
  const lastCode = 0x80 + lastSlot;
  document.querySelector("#animation-name").value = clip.name;
  document.querySelector("#animation-base-slot").value = String(clip.baseSlot);
  document.querySelector("#animation-width").value = String(clip.width);
  document.querySelector("#animation-height").value = String(clip.height);
  document.querySelector("#animation-duration").value = String(clip.frameDurationMs);
  document.querySelector("#animation-width").disabled = clip.frames.length > 0;
  document.querySelector("#animation-height").disabled = clip.frames.length > 0;
  document.querySelector("#animation-base-slot").disabled = clip.frames.length > 0;
  document.querySelector("#animation-resident-range").textContent = `${hex(firstCode)}-${hex(lastCode)}`;
  document.querySelector("#animation-screen-codes").textContent = `${hex(firstCode)}-${hex(lastCode)}`;
  document.querySelector("#animation-resident-slots").textContent = t("animation.slotCount", { count: slotCount });
  document.querySelector("#animation-copy-bytes").textContent = t("animation.byteCount", { count: slotCount * 8 });
  document.querySelector("#animation-stored-frames").textContent = String(clip.frames.length);
  document.querySelector("#animation-data-bytes").textContent = t("animation.byteCount", { count: clip.frames.length * slotCount * 8 });
  document.querySelector("#animation-frame-summary").textContent = t("animation.frameCount", { count: clip.frames.length });

  const frameList = document.querySelector("#animation-frame-list");
  frameList.replaceChildren();
  clip.frames.forEach((frame, index) => {
    const button = document.createElement("button");
    const thumbnail = document.createElement("canvas");
    const name = document.createElement("strong");
    const number = document.createElement("span");
    button.type = "button";
    button.className = "animation-frame-card";
    button.classList.toggle("selected", index === activeAnimationFrame);
    thumbnail.width = 64;
    thumbnail.height = 64;
    name.textContent = frame.name;
    number.textContent = `#${index.toString().padStart(2, "0")}`;
    button.append(thumbnail, name, number);
    button.addEventListener("click", () => {
      activeAnimationFrame = index;
      stopAnimationPlayback();
      renderAnimation();
    });
    frameList.append(button);
    drawAnimationThumbnail(thumbnail, clip, frame);
  });
  const selectedFrame = clip.frames[activeAnimationFrame];
  document.querySelector("#animation-frame-name").value = selectedFrame?.name ?? `FRAME_${clip.frames.length}`;
  drawAnimationFrame(clip, selectedFrame ?? null);
}

function stopAnimationPlayback() {
  if (animationTimer !== null) {
    clearInterval(animationTimer);
    animationTimer = null;
  }
  document.querySelector("#play-animation").textContent = t("animation.play");
  document.querySelector("#animation-playback-status").textContent = t("animation.stopped");
}

function toggleAnimationPlayback() {
  const clip = activeAnimation();
  if (!clip?.frames.length) return;
  if (animationTimer !== null) {
    stopAnimationPlayback();
    return;
  }
  document.querySelector("#play-animation").textContent = t("animation.stop");
  document.querySelector("#animation-playback-status").textContent = t("animation.playing", { duration: clip.frameDurationMs });
  animationTimer = setInterval(() => {
    activeAnimationFrame = (activeAnimationFrame + 1) % clip.frames.length;
    renderAnimation();
  }, clip.frameDurationMs);
}

function selectRelativeAnimationFrame(delta) {
  const clip = activeAnimation();
  if (!clip?.frames.length) return;
  stopAnimationPlayback();
  activeAnimationFrame = (activeAnimationFrame + delta + clip.frames.length) % clip.frames.length;
  renderAnimation();
}

function drawImageMosaicPlaceholder(context, textKey) {
  context.fillStyle = "#050906";
  context.fillRect(0, 0, IMAGE_PIXEL_WIDTH, IMAGE_PIXEL_HEIGHT);
  context.fillStyle = "#718076";
  context.font = "11px sans-serif";
  context.textAlign = "center";
  context.fillText(t(textKey), IMAGE_PIXEL_WIDTH / 2, IMAGE_PIXEL_HEIGHT / 2);
}

function setImageMosaicStatus(key, values = {}) {
  document.querySelector("#image-mosaic-status").textContent = t(key, values);
}

function invalidateImageMosaicPreview() {
  imageMosaicGenerationScheduler.cancel();
  imageMosaicPreview = null;
  document.querySelector("#apply-image-mosaic").disabled = true;
  drawImageMosaicPlaceholder(imageMosaicResultContext, "imageMosaic.noPreview");
  setImageMosaicStatus(imageMosaicBitmap ? "imageMosaic.ready" : "imageMosaic.chooseImage");
}

function scheduleImageMosaicGeneration() {
  if (!imageMosaicLuminance) {
    invalidateImageMosaicPreview();
    return;
  }
  imageMosaicPreview = null;
  document.querySelector("#apply-image-mosaic").disabled = true;
  setImageMosaicStatus("imageMosaic.updating");
  imageMosaicGenerationScheduler.schedule();
}

function syncImageMosaicControls() {
  const contrast = Number(document.querySelector("#image-mosaic-contrast").value);
  const threshold = Number(document.querySelector("#image-mosaic-threshold").value);
  const edgeStrength = Number(document.querySelector("#image-mosaic-edge-strength").value);
  const generatePcgControl = document.querySelector("#image-mosaic-generate-pcg");
  generatePcgControl.disabled = project.screen.mode !== DISPLAY_MODES.PCG;
  if (generatePcgControl.disabled) generatePcgControl.checked = false;
  document.querySelector("#image-mosaic-contrast-value").textContent = contrast.toFixed(1);
  document.querySelector("#image-mosaic-threshold-value").textContent = threshold.toFixed(2);
  document.querySelector("#image-mosaic-edge-strength-value").textContent = edgeStrength.toFixed(1);
  const thresholdEnabled = document.querySelector("#image-mosaic-tone").value !== "grayscale" || generatePcgControl.checked;
  document.querySelector("#image-mosaic-threshold").disabled = !thresholdEnabled;
  const pcgOption = document.querySelector('#image-mosaic-palette option[value="pcg"]');
  pcgOption.disabled = project.screen.mode !== DISPLAY_MODES.PCG || generatePcgControl.checked;
  if (pcgOption.disabled && document.querySelector("#image-mosaic-palette").value === "pcg") {
    document.querySelector("#image-mosaic-palette").value = "compatible";
  }
  document.querySelector("#image-mosaic-pcg-warning").hidden = !generatePcgControl.checked;
  document.querySelector("#image-mosaic-pcg-mode-help").hidden = project.screen.mode === DISPLAY_MODES.PCG;
}

function updateImageMosaicLuminance() {
  imageMosaicLuminance = imageMosaicRgba
    ? rgbaToEnhancedLuminance(imageMosaicRgba, {
      edgeStrength: Number(document.querySelector("#image-mosaic-edge-strength").value),
    })
    : null;
}

function renderImageMosaicSource() {
  if (!imageMosaicBitmap) {
    imageMosaicRgba = null;
    imageMosaicLuminance = null;
    drawImageMosaicPlaceholder(imageMosaicSourceContext, "imageMosaic.noImage");
    invalidateImageMosaicPreview();
    return;
  }
  const width = IMAGE_PIXEL_WIDTH;
  const height = IMAGE_PIXEL_HEIGHT;
  const fit = document.querySelector("#image-mosaic-fit").value;
  imageMosaicSourceContext.fillStyle = "#000";
  imageMosaicSourceContext.fillRect(0, 0, width, height);
  imageMosaicSourceContext.imageSmoothingEnabled = true;
  imageMosaicSourceContext.imageSmoothingQuality = "high";
  if (fit === "stretch") {
    imageMosaicSourceContext.drawImage(imageMosaicBitmap, 0, 0, width, height);
  } else {
    const scale = fit === "contain"
      ? Math.min(width / imageMosaicBitmap.width, height / imageMosaicBitmap.height)
      : Math.max(width / imageMosaicBitmap.width, height / imageMosaicBitmap.height);
    const drawWidth = imageMosaicBitmap.width * scale;
    const drawHeight = imageMosaicBitmap.height * scale;
    imageMosaicSourceContext.drawImage(
      imageMosaicBitmap,
      (width - drawWidth) / 2,
      (height - drawHeight) / 2,
      drawWidth,
      drawHeight,
    );
  }
  imageMosaicRgba = new Uint8ClampedArray(imageMosaicSourceContext.getImageData(0, 0, width, height).data);
  updateImageMosaicLuminance();
  scheduleImageMosaicGeneration();
}

function renderImageMosaicResult(preview) {
  imageMosaicResultContext.fillStyle = "#020503";
  imageMosaicResultContext.fillRect(0, 0, IMAGE_PIXEL_WIDTH, IMAGE_PIXEL_HEIGHT);
  preview.cells.forEach((code, index) => {
    const generatedGlyph = code >= PCG_CODE_START && code <= PCG_CODE_END
      ? preview.glyphs?.[code - PCG_CODE_START]
      : null;
    drawGlyphPreview(
      imageMosaicResultContext,
      generatedGlyph ?? resolveScreenGlyph(project, code),
      (index % SCREEN_WIDTH) * 8,
      Math.floor(index / SCREEN_WIDTH) * 8,
      1,
      "#8de3a2",
    );
  });
}

function generateImageMosaic() {
  if (!imageMosaicLuminance) return;
  try {
    syncImageMosaicControls();
    const candidates = buildGlyphCandidates(project, {
      palette: document.querySelector("#image-mosaic-palette").value,
    });
    const options = {
      contrast: Number(document.querySelector("#image-mosaic-contrast").value),
      invert: document.querySelector("#image-mosaic-invert").checked,
      threshold: Number(document.querySelector("#image-mosaic-threshold").value),
      toneMode: document.querySelector("#image-mosaic-tone").value,
    };
    const generatePcg = document.querySelector("#image-mosaic-generate-pcg").checked;
    imageMosaicPreview = generatePcg
      ? generatePcgMosaic(imageMosaicLuminance, candidates, options)
      : convertLuminanceToScreen(imageMosaicLuminance, candidates, options);
    renderImageMosaicResult(imageMosaicPreview);
    document.querySelector("#apply-image-mosaic").disabled = false;
    if (generatePcg) {
      const baseCandidateCount = candidates.filter(({ code }) => code < PCG_CODE_START || code > PCG_CODE_END).length;
      setImageMosaicStatus("imageMosaic.generatedPcg", {
        candidates: baseCandidateCount,
        pcg: imageMosaicPreview.glyphs.length,
        error: imageMosaicPreview.meanError.toFixed(3),
      });
    } else {
      setImageMosaicStatus("imageMosaic.generated", {
        candidates: candidates.length,
        error: imageMosaicPreview.meanError.toFixed(3),
      });
    }
  } catch (error) {
    setImageMosaicStatus("error.operationFailed", { detail: `: ${error.message}` });
    document.querySelector("#apply-image-mosaic").disabled = true;
  }
}

function applyImageMosaic() {
  if (!imageMosaicPreview) return;
  const replacesPcg = imageMosaicPreview.kind === "screen-pcg";
  snapshotMutation(() => {
    applyImageMosaicResult(project, imageMosaicPreview);
  }, t(replacesPcg ? "message.imageMosaicPcgApplied" : "message.imageMosaicApplied"));
  imageMosaicDialog.close();
  screenCanvas.focus();
}

function openImageMosaic() {
  syncImageMosaicControls();
  if (!imageMosaicBitmap) {
    drawImageMosaicPlaceholder(imageMosaicSourceContext, "imageMosaic.noImage");
    invalidateImageMosaicPreview();
  } else {
    scheduleImageMosaicGeneration();
  }
  imageMosaicDialog.showModal();
}

function decodeImageWithElement(file) {
  return new Promise((resolve, reject) => {
    const url = URL.createObjectURL(file);
    const image = new Image();
    image.onload = () => {
      URL.revokeObjectURL(url);
      resolve(image);
    };
    image.onerror = () => {
      URL.revokeObjectURL(url);
      reject(new TypeError("Browser could not decode the selected image"));
    };
    image.src = url;
  });
}

function decodeImageFile(file) {
  return typeof globalThis.createImageBitmap === "function"
    ? globalThis.createImageBitmap(file)
    : decodeImageWithElement(file);
}

function clampHoverCellToWorkspace() {
  if (!hoverCell) {
    return;
  }
  const dimensions = workspacePixelSize();
  hoverCell = {
    x: Math.max(0, Math.min(dimensions.width - 1, hoverCell.x)),
    y: Math.max(0, Math.min(dimensions.height - 1, hoverCell.y)),
  };
  updatePointerStatus(hoverCell);
}

function updateToolButtons() {
  document.querySelectorAll("[data-tool]").forEach((button) => {
    button.classList.toggle("active", button.dataset.tool === tool);
    button.setAttribute("aria-pressed", button.dataset.tool === tool ? "true" : "false");
  });
  const activeButton = document.querySelector(`[data-tool="${tool}"]`);
  document.querySelector("#active-tool-status").textContent = activeButton?.textContent ?? tool;
  canvas.dataset.tool = tool;
}

function updateSizeButtons() {
  document.querySelectorAll("[data-size]").forEach((button) => {
    const selected = button.dataset.size === `${workspace.width}x${workspace.height}`;
    button.classList.toggle("active", selected);
    button.setAttribute("aria-pressed", selected ? "true" : "false");
  });
}

function syncWorkspaceInputs() {
  document.querySelector("#base-slot").value = String(workspace.baseSlot);
  document.querySelector("#workspace-width").value = String(workspace.width);
  document.querySelector("#workspace-height").value = String(workspace.height);
  const count = workspace.width * workspace.height;
  const end = workspace.baseSlot + count - 1;
  const slots = count === 1
    ? t("pcg.singleSlot", { start: workspace.baseSlot.toString().padStart(2, "0") })
    : t("pcg.slotRange", { start: workspace.baseSlot.toString().padStart(2, "0"), end: end.toString().padStart(2, "0") });
  document.querySelector("#workspace-summary").textContent = t("pcg.workspaceSummary", {
    slots,
    width: workspace.width * 8,
    height: workspace.height * 8,
  });
}

function applyWorkspaceInputs() {
  const candidate = {
    baseSlot: Number(document.querySelector("#base-slot").value),
    width: Number(document.querySelector("#workspace-width").value),
    height: Number(document.querySelector("#workspace-height").value),
  };
  try {
    assertWorkspace(candidate);
    workspace = candidate;
    activeGroupId = null;
    document.querySelector("#group-name").value = "";
    syncWorkspaceInputs();
    renderAll();
    setMessage(t("message.editingComposite", { width: candidate.width, height: candidate.height, slot: candidate.baseSlot }));
  } catch (error) {
    setMessage(formatError(error), "error");
  }
}

function useQuickSize(width, height) {
  const count = width * height;
  workspace = {
    baseSlot: Math.min(workspace.baseSlot, 32 - count),
    width,
    height,
  };
  activeGroupId = null;
  document.querySelector("#group-name").value = "";
  syncWorkspaceInputs();
  renderAll();
  canvas.focus();
}

function saveWorkspaceGroup() {
  const requestedName = document.querySelector("#group-name").value.trim();
  const name = requestedName || `Composite ${workspace.width}x${workspace.height}`;
  snapshotMutation(() => {
    const existing = activeGroupId
      ? project.groups.find((group) => group.id === activeGroupId)
      : null;
    if (existing) {
      upsertGroup(project, { id: existing.id, name, ...workspace });
    } else {
      activeGroupId = globalThis.crypto?.randomUUID?.() ?? `group-${Date.now()}`;
      upsertGroup(project, { id: activeGroupId, name, ...workspace });
    }
  }, t("message.groupSaved", { name }));
  document.querySelector("#group-name").value = name;
}

function loadWorkspaceGroup(id) {
  if (!id) {
    activeGroupId = null;
    document.querySelector("#group-name").value = "";
    renderSavedGroups();
    return;
  }
  const group = project.groups.find((candidate) => candidate.id === id);
  if (!group) {
    return;
  }
  activeGroupId = group.id;
  workspace = { baseSlot: group.baseSlot, width: group.width, height: group.height };
  document.querySelector("#group-name").value = group.name;
  syncWorkspaceInputs();
  renderAll();
  canvas.focus();
}

function deleteWorkspaceGroup() {
  if (!activeGroupId) {
    return;
  }
  const group = project.groups.find((candidate) => candidate.id === activeGroupId);
  if (!group) {
    return;
  }
  snapshotMutation(() => {
    removeGroup(project, activeGroupId);
    activeGroupId = null;
  }, t("message.groupDeleted", { name: group.name }));
  document.querySelector("#group-name").value = "";
}

function cellFromPointer(event) {
  const rect = canvas.getBoundingClientRect();
  const dimensions = workspacePixelSize();
  const x = Math.floor(((event.clientX - rect.left) / rect.width) * dimensions.width);
  const y = Math.floor(((event.clientY - rect.top) / rect.height) * dimensions.height);
  if (x < 0 || y < 0 || x >= dimensions.width || y >= dimensions.height) {
    return null;
  }
  return { x, y };
}

function paintLine(start, end, value) {
  let changed = false;
  for (const [x, y] of bresenhamPoints(start.x, start.y, end.x, end.y)) {
    if (getPixel(project.glyphs, workspace, x, y) !== value) {
      setPixel(project.glyphs, workspace, x, y, value);
      changed = true;
    }
  }
  return changed;
}

function rectanglePoints(start, end) {
  const minX = Math.min(start.x, end.x);
  const maxX = Math.max(start.x, end.x);
  const minY = Math.min(start.y, end.y);
  const maxY = Math.max(start.y, end.y);
  const points = [];
  for (let x = minX; x <= maxX; x += 1) {
    points.push([x, minY], [x, maxY]);
  }
  for (let y = minY + 1; y < maxY; y += 1) {
    points.push([minX, y], [maxX, y]);
  }
  return points;
}

function beginGesture(event) {
  if (event.button !== 0 && event.button !== 2) {
    return;
  }
  event.preventDefault();
  canvas.focus();
  const cell = cellFromPointer(event);
  if (!cell) {
    return;
  }
  canvas.setPointerCapture(event.pointerId);
  const value = event.button === 2 || tool === "eraser" ? 0 : 1;
  gesture = {
    pointerId: event.pointerId,
    start: cell,
    last: cell,
    value,
    before: cloneProject(project),
    changed: false,
    preview: null,
  };
  if (tool === "pencil" || tool === "eraser") {
    gesture.changed = paintLine(cell, cell, value);
  } else if (tool === "fill") {
    if (getPixel(project.glyphs, workspace, cell.x, cell.y) !== value) {
      floodFill(project.glyphs, workspace, cell.x, cell.y, value);
      gesture.changed = true;
    }
    finishGesture(event);
  } else {
    gesture.preview = [[cell.x, cell.y]];
  }
  renderEditor();
  renderCrt();
}

function moveGesture(event) {
  const cell = cellFromPointer(event);
  hoverCell = cell;
  updatePointerStatus(cell);
  if (!gesture || gesture.pointerId !== event.pointerId || !cell) {
    renderEditor();
    return;
  }
  let endpoint = cell;
  if (event.shiftKey && (tool === "line" || tool === "rectangle")) {
    const dimensions = workspacePixelSize();
    endpoint = constrainEndpoint(gesture.start, cell, tool, dimensions);
  }
  if (tool === "pencil" || tool === "eraser") {
    gesture.changed = paintLine(gesture.last, cell, gesture.value) || gesture.changed;
    gesture.last = cell;
  } else if (tool === "line") {
    gesture.preview = bresenhamPoints(gesture.start.x, gesture.start.y, endpoint.x, endpoint.y);
    gesture.last = endpoint;
  } else if (tool === "rectangle") {
    gesture.preview = rectanglePoints(gesture.start, endpoint);
    gesture.last = endpoint;
  }
  renderEditor();
  renderCrt();
}

function finishGesture(event) {
  if (!gesture || (event.pointerId !== undefined && gesture.pointerId !== event.pointerId)) {
    return;
  }
  if ((tool === "line" || tool === "rectangle") && gesture.preview) {
    for (const [x, y] of gesture.preview) {
      if (getPixel(project.glyphs, workspace, x, y) !== gesture.value) {
        setPixel(project.glyphs, workspace, x, y, gesture.value);
        gesture.changed = true;
      }
    }
  }
  if (gesture.changed) {
    commitHistory(gesture.before, t("message.strokeSaved"));
  }
  gesture = null;
  renderAll();
}

function updatePointerStatus(cell) {
  const output = document.querySelector("#pointer-status");
  if (!cell) {
    output.textContent = t("status.pointerOutside");
    return;
  }
  const tileX = Math.floor(cell.x / 8);
  const tileY = Math.floor(cell.y / 8);
  const slot = workspace.baseSlot + tileY * workspace.width + tileX;
  const row = cell.y % 8;
  output.textContent = t("status.pointer", {
    x: cell.x.toString().padStart(2, "0"),
    y: cell.y.toString().padStart(2, "0"),
    slot: slot.toString().padStart(2, "0"),
    row,
    state: getPixel(project.glyphs, workspace, cell.x, cell.y) ? t("status.on") : t("status.off"),
  });
}

const TRANSFORM_ACTIONS = {
  "shift-up": ({ wrap }) => shiftWorkspace(project.glyphs, workspace, 0, -1, { wrap }),
  "shift-down": ({ wrap }) => shiftWorkspace(project.glyphs, workspace, 0, 1, { wrap }),
  "shift-left": ({ wrap }) => shiftWorkspace(project.glyphs, workspace, -1, 0, { wrap }),
  "shift-right": ({ wrap }) => shiftWorkspace(project.glyphs, workspace, 1, 0, { wrap }),
  "flip-horizontal": () => flipWorkspace(project.glyphs, workspace, "horizontal"),
  "flip-vertical": () => flipWorkspace(project.glyphs, workspace, "vertical"),
  invert: () => invertWorkspace(project.glyphs, workspace),
  clear: () => clearWorkspace(project.glyphs, workspace),
};

const TRANSFORM_LABELS = {
  "shift-up": "tool.up",
  "shift-down": "tool.down",
  "shift-left": "tool.left",
  "shift-right": "tool.right",
  "flip-horizontal": "tool.flipH",
  "flip-vertical": "tool.flipV",
  invert: "tool.invert",
  clear: "tool.clear",
};

function applyTransform(action) {
  const transform = TRANSFORM_ACTIONS[action];
  if (!transform) {
    setMessage(t("message.unknownTransform", { action }), "error");
    return;
  }
  snapshotMutation(
    () => transform({ wrap: document.querySelector("#wrap-shift").checked }),
    t("message.transformApplied", { action: t(TRANSFORM_LABELS[action]) }),
  );
}

function copyWorkspace() {
  clipboardMatrix = workspaceToMatrix(project.glyphs, workspace);
  renderUsage();
  setMessage(t("message.copiedPixels", { width: clipboardMatrix[0].length, height: clipboardMatrix.length }));
}

function pasteWorkspace() {
  if (!clipboardMatrix) {
    return;
  }
  snapshotMutation(() => {
    const target = workspaceToMatrix(project.glyphs, workspace);
    for (let y = 0; y < Math.min(target.length, clipboardMatrix.length); y += 1) {
      for (let x = 0; x < Math.min(target[0].length, clipboardMatrix[0].length); x += 1) {
        target[y][x] = clipboardMatrix[y][x];
      }
    }
    matrixToWorkspace(project.glyphs, workspace, target);
  }, t("message.clipboardPasted"));
}

function moveCanvasCursor(deltaX, deltaY) {
  const dimensions = workspacePixelSize();
  const current = hoverCell ?? { x: 0, y: 0 };
  hoverCell = {
    x: Math.max(0, Math.min(dimensions.width - 1, current.x + deltaX)),
    y: Math.max(0, Math.min(dimensions.height - 1, current.y + deltaY)),
  };
  updatePointerStatus(hoverCell);
  renderEditor();
}

function paintCanvasCursor() {
  const cell = hoverCell ?? { x: 0, y: 0 };
  const value = tool === "eraser" ? 0 : 1;
  if (getPixel(project.glyphs, workspace, cell.x, cell.y) === value) {
    setMessage(value ? t("message.pixelOn") : t("message.pixelOff"));
    return;
  }
  snapshotMutation(() => setPixel(project.glyphs, workspace, cell.x, cell.y, value), value ? t("message.pixelDrawn") : t("message.pixelErased"));
  hoverCell = cell;
  updatePointerStatus(cell);
  canvas.focus();
}

function selectAdjacentWorkspace(direction) {
  const count = workspace.width * workspace.height;
  const nextBase = Math.max(0, Math.min(32 - count, workspace.baseSlot + direction));
  if (nextBase === workspace.baseSlot) {
    return;
  }
  workspace = { ...workspace, baseSlot: nextBase };
  activeGroupId = null;
  document.querySelector("#group-name").value = "";
  syncWorkspaceInputs();
  renderAll();
  canvas.focus();
}

function cancelGesture() {
  if (!gesture) {
    return false;
  }
  if (canvas.hasPointerCapture(gesture.pointerId)) {
    canvas.releasePointerCapture(gesture.pointerId);
  }
  project = gesture.before;
  gesture = null;
  renderAll();
  setMessage(t("message.strokeCancelled"));
  return true;
}

function hex(value) {
  return `$${value.toString(16).toUpperCase().padStart(2, "0")}`;
}

function downloadText(filename, text, type) {
  const blob = new Blob([text], { type });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}

function setActiveView(view) {
  if (!new Set(["pcg", "screen", "animation"]).has(view)) {
    throw new RangeError("Unknown editor view");
  }
  if (activeView === "animation" && view !== "animation") {
    stopAnimationPlayback();
  }
  activeView = view;
  const screenActive = view === "screen";
  const animationActive = view === "animation";
  document.querySelector("#pcg-workbench").hidden = screenActive || animationActive;
  document.querySelector("#screen-workbench").hidden = !screenActive;
  document.querySelector("#animation-workbench").hidden = !animationActive;
  document.querySelector("#show-pcg-view").classList.toggle("active", view === "pcg");
  document.querySelector("#show-screen-view").classList.toggle("active", screenActive);
  document.querySelector("#show-animation-view").classList.toggle("active", animationActive);
  document.querySelector("#show-pcg-view").setAttribute("aria-selected", view === "pcg" ? "true" : "false");
  document.querySelector("#show-screen-view").setAttribute("aria-selected", screenActive ? "true" : "false");
  document.querySelector("#show-animation-view").setAttribute("aria-selected", animationActive ? "true" : "false");
  document.querySelector("#shortcut-help").textContent = t(
    screenActive ? "status.crtShortcuts" : animationActive ? "status.animationShortcuts" : "status.pcgShortcuts",
  );
  if (screenActive) {
    screenCanvas.focus();
  } else if (animationActive) {
    animationCanvas.focus();
  } else {
    canvas.focus();
  }
}

function createNewAnimationClip() {
  const clip = createAnimationClip({
    id: `animation-${Date.now()}-${project.animations.length}`,
    name: t("animation.defaultName"),
    baseSlot: 0,
    width: 2,
    height: 2,
    frameDurationMs: 160,
  });
  const before = cloneProject(project);
  project.animations.push(clip);
  activeAnimationId = clip.id;
  activeAnimationFrame = 0;
  commitHistory(before, t("message.animationCreated"));
  renderAll();
}

function saveAnimationSettings() {
  const clip = activeAnimation();
  if (!clip) return;
  const candidate = {
    ...clip,
    name: document.querySelector("#animation-name").value.trim(),
    baseSlot: Number(document.querySelector("#animation-base-slot").value),
    width: Number(document.querySelector("#animation-width").value),
    height: Number(document.querySelector("#animation-height").value),
    frameDurationMs: Number(document.querySelector("#animation-duration").value),
  };
  try {
    validateAnimationClips([candidate]);
    snapshotMutation(() => Object.assign(clip, candidate), t("message.animationSaved"));
  } catch (error) {
    setMessage(formatError(error), "error");
  }
}

function deleteAnimationClip() {
  const clip = activeAnimation();
  if (!clip || !window.confirm(t("confirm.deleteAnimation", { name: clip.name }))) return;
  stopAnimationPlayback();
  snapshotMutation(() => {
    project.animations = project.animations.filter((candidate) => candidate.id !== clip.id);
    activeAnimationId = project.animations[0]?.id ?? null;
    activeAnimationFrame = 0;
  }, t("message.animationDeleted"));
}

function captureCurrentAnimationFrame() {
  const clip = activeAnimation();
  if (!clip) return;
  const name = document.querySelector("#animation-frame-name").value.trim() || `FRAME_${clip.frames.length}`;
  snapshotMutation(() => {
    captureAnimationFrame(clip, project.glyphs, {
      id: `frame-${Date.now()}-${clip.frames.length}`,
      name,
    });
    activeAnimationFrame = clip.frames.length - 1;
  }, t("message.animationCaptured", { name }));
}

function updateCurrentAnimationFrame() {
  const clip = activeAnimation();
  const frame = clip?.frames[activeAnimationFrame];
  if (!frame) return;
  const name = document.querySelector("#animation-frame-name").value.trim() || frame.name;
  snapshotMutation(() => {
    frame.name = name;
    replaceAnimationFrame(clip, activeAnimationFrame, project.glyphs);
  }, t("message.animationUpdated", { name }));
}

function loadCurrentAnimationFrame() {
  const clip = activeAnimation();
  const frame = clip?.frames[activeAnimationFrame];
  if (!frame) return;
  const before = cloneProject(project);
  applyAnimationFrame(clip, activeAnimationFrame, project.glyphs);
  workspace = { baseSlot: clip.baseSlot, width: clip.width, height: clip.height };
  commitHistory(before, t("message.animationLoaded", { name: frame.name }));
  syncWorkspaceInputs();
  renderAll();
  setActiveView("pcg");
}

function duplicateCurrentAnimationFrame() {
  const clip = activeAnimation();
  const frame = clip?.frames[activeAnimationFrame];
  if (!frame) return;
  snapshotMutation(() => {
    duplicateAnimationFrame(clip, activeAnimationFrame, {
      id: `frame-${Date.now()}-${clip.frames.length}`,
      name: `${frame.name}_COPY`,
    });
    activeAnimationFrame += 1;
  }, t("message.animationDuplicated"));
}

function deleteCurrentAnimationFrame() {
  const clip = activeAnimation();
  const frame = clip?.frames[activeAnimationFrame];
  if (!frame) return;
  stopAnimationPlayback();
  snapshotMutation(() => {
    removeAnimationFrame(clip, activeAnimationFrame);
    activeAnimationFrame = Math.min(activeAnimationFrame, Math.max(0, clip.frames.length - 1));
  }, t("message.animationFrameDeleted", { name: frame.name }));
}

function screenCellFromPointer(event) {
  const rect = screenCanvas.getBoundingClientRect();
  const x = Math.floor(((event.clientX - rect.left) / rect.width) * SCREEN_WIDTH);
  const y = Math.floor(((event.clientY - rect.top) / rect.height) * SCREEN_HEIGHT);
  if (x < 0 || y < 0 || x >= SCREEN_WIDTH || y >= SCREEN_HEIGHT) {
    return null;
  }
  return { x, y };
}

function paintScreenCell(cell, code) {
  if (getScreenCell(project.screen, cell.x, cell.y) === code) {
    return false;
  }
  setScreenCell(project.screen, cell.x, cell.y, code);
  return true;
}

function beginScreenGesture(event) {
  if (event.button !== 0 && event.button !== 2) {
    return;
  }
  const cell = screenCellFromPointer(event);
  if (!cell) {
    return;
  }
  event.preventDefault();
  screenCanvas.focus();
  screenCanvas.setPointerCapture(event.pointerId);
  screenCursor = cell;
  screenGesture = {
    pointerId: event.pointerId,
    code: event.button === 2 ? 0x00 : selectedScreenCode,
    before: cloneProject(project),
    changed: false,
    last: null,
  };
  moveScreenGesture(event);
}

function moveScreenGesture(event) {
  const cell = screenCellFromPointer(event);
  if (!cell) {
    return;
  }
  screenCursor = cell;
  updateScreenCursorSummary();
  if (!screenGesture || screenGesture.pointerId !== event.pointerId) {
    renderCrt();
    return;
  }
  const previous = screenGesture.last ?? cell;
  if (!screenGesture.last || previous.x !== cell.x || previous.y !== cell.y) {
    for (const [x, y] of bresenhamPoints(previous.x, previous.y, cell.x, cell.y)) {
      screenGesture.changed = paintScreenCell({ x, y }, screenGesture.code) || screenGesture.changed;
    }
    screenGesture.last = cell;
    renderCrt();
  }
}

function finishScreenGesture(event) {
  if (!screenGesture || screenGesture.pointerId !== event.pointerId) {
    return;
  }
  if (screenGesture.changed) {
    commitHistory(screenGesture.before, t("message.screenStrokeSaved"));
  }
  screenGesture = null;
  renderAll();
}

function moveScreenCursor(deltaX, deltaY) {
  screenCursor = {
    x: Math.max(0, Math.min(SCREEN_WIDTH - 1, screenCursor.x + deltaX)),
    y: Math.max(0, Math.min(SCREEN_HEIGHT - 1, screenCursor.y + deltaY)),
  };
  updateScreenCursorSummary();
  renderCrt();
}

function stampScreenCursor(code = selectedScreenCode) {
  if (getScreenCell(project.screen, screenCursor.x, screenCursor.y) === code) {
    return;
  }
  snapshotMutation(() => setScreenCell(project.screen, screenCursor.x, screenCursor.y, code), t("message.codePlaced", { code: hex(code) }));
  screenCanvas.focus();
}

function placeScreenText() {
  const text = document.querySelector("#screen-text").value;
  if (!text) return;
  snapshotMutation(() => {
    [...text].slice(0, SCREEN_WIDTH - screenCursor.x).forEach((character, offset) => {
      setScreenCell(project.screen, screenCursor.x + offset, screenCursor.y, asciiToRomCode(character));
    });
  }, t("message.screenTextPlaced"));
  screenCanvas.focus();
}

function vramGlyphCellFromPointer(event) {
  const rect = vramGlyphCanvas.getBoundingClientRect();
  const x = Math.floor(((event.clientX - rect.left) / rect.width) * 8);
  const y = Math.floor(((event.clientY - rect.top) / rect.height) * 8);
  return x >= 0 && x < 8 && y >= 0 && y < 8 ? { x, y } : null;
}

function beginVramGlyphGesture(event) {
  if ((event.button !== 0 && event.button !== 2) || selectedScreenCode < 0xa0) return;
  const cell = vramGlyphCellFromPointer(event);
  if (!cell) return;
  event.preventDefault();
  vramGlyphCanvas.setPointerCapture(event.pointerId);
  vramGlyphGesture = {
    pointerId: event.pointerId,
    code: selectedScreenCode,
    value: event.button === 2 ? 0 : 1,
    before: cloneProject(project),
    changed: false,
    last: null,
  };
  moveVramGlyphGesture(event);
}

function moveVramGlyphGesture(event) {
  const cell = vramGlyphCellFromPointer(event);
  if (!cell || !vramGlyphGesture || vramGlyphGesture.pointerId !== event.pointerId) return;
  const previous = vramGlyphGesture.last ?? cell;
  for (const [x, y] of bresenhamPoints(previous.x, previous.y, cell.x, cell.y)) {
    const sourceOffset = vramPcgSourceOffset(vramGlyphGesture.code);
    const before = project.screen.cells[sourceOffset + y];
    setVramPcgPixel(project.screen, vramGlyphGesture.code, x, y, vramGlyphGesture.value);
    vramGlyphGesture.changed = project.screen.cells[sourceOffset + y] !== before || vramGlyphGesture.changed;
  }
  vramGlyphGesture.last = cell;
  renderVramGlyphEditor();
  renderCrt();
}

function finishVramGlyphGesture(event) {
  if (!vramGlyphGesture || vramGlyphGesture.pointerId !== event.pointerId) return;
  if (vramGlyphGesture.changed) commitHistory(vramGlyphGesture.before, t("message.vramGlyphSaved"));
  vramGlyphGesture = null;
  renderAll();
}

function handleKeyboard(event) {
  const target = event.target;
  if (document.querySelector("dialog[open]")) {
    return;
  }
  if (event.key === "Escape" && cancelGesture()) {
    event.preventDefault();
    return;
  }
  if (target instanceof HTMLInputElement || target instanceof HTMLTextAreaElement) {
    return;
  }
  const modifier = event.ctrlKey || event.metaKey;
  if (modifier && event.key.toLowerCase() === "z") {
    event.preventDefault();
    event.shiftKey ? redo() : undo();
    return;
  }
  if (modifier && event.key.toLowerCase() === "y") {
    event.preventDefault();
    redo();
    return;
  }
  if (target === animationCanvas && (event.key === "ArrowLeft" || event.key === "ArrowRight")) {
    event.preventDefault();
    selectRelativeAnimationFrame(event.key === "ArrowLeft" ? -1 : 1);
    return;
  }
  if (target === animationCanvas && event.key === " ") {
    event.preventDefault();
    toggleAnimationPlayback();
    return;
  }
  if (modifier && event.key.toLowerCase() === "c") {
    event.preventDefault();
    copyWorkspace();
    return;
  }
  if (modifier && event.key.toLowerCase() === "v") {
    event.preventDefault();
    pasteWorkspace();
    return;
  }
  const direction = DIRECTION_KEYS[event.key];
  if (target === screenCanvas && direction) {
    event.preventDefault();
    moveScreenCursor(direction.deltaX, direction.deltaY);
    return;
  }
  if (target === screenCanvas && (event.key === " " || event.key === "Enter")) {
    event.preventDefault();
    stampScreenCursor();
    return;
  }
  if (target === screenCanvas && (event.key === "Delete" || event.key === "Backspace")) {
    event.preventDefault();
    stampScreenCursor(0x00);
    return;
  }
  if (event.altKey && direction) {
    event.preventDefault();
    applyTransform(direction.action);
    canvas.focus();
    return;
  }
  if (target === canvas && direction) {
    event.preventDefault();
    moveCanvasCursor(direction.deltaX, direction.deltaY);
    return;
  }
  if (target === canvas && (event.key === " " || event.key === "Enter")) {
    event.preventDefault();
    paintCanvasCursor();
    return;
  }
  if (target === canvas && (event.key === "[" || event.key === "]")) {
    event.preventDefault();
    selectAdjacentWorkspace(event.key === "[" ? -1 : 1);
    return;
  }
  if (target === canvas && ["1", "2", "3"].includes(event.key)) {
    event.preventDefault();
    const size = Number(event.key);
    useQuickSize(size, size);
    return;
  }
  if (event.key.toLowerCase() === "x") {
    tool = tool === "eraser" ? "pencil" : "eraser";
    updateToolButtons();
    setMessage(t("message.toolSelected", { tool: t(`tool.${tool}`) }));
    return;
  }
  const toolKeys = { b: "pencil", e: "eraser", l: "line", r: "rectangle", g: "fill" };
  if (toolKeys[event.key.toLowerCase()]) {
    tool = toolKeys[event.key.toLowerCase()];
    updateToolButtons();
    setMessage(t("message.toolSelected", { tool: t(`tool.${tool}`) }));
    return;
  }
  if (event.key === "Delete" || event.key === "Backspace") {
    event.preventDefault();
    applyTransform("clear");
  }
}

document.querySelectorAll("[data-tool]").forEach((button) => {
  button.addEventListener("click", () => {
    tool = button.dataset.tool;
    updateToolButtons();
    canvas.focus();
  });
});

document.querySelectorAll("[data-size]").forEach((button) => {
  button.addEventListener("click", () => {
    const [width, height] = button.dataset.size.split("x").map(Number);
    useQuickSize(width, height);
  });
});

document.querySelectorAll("[data-action]").forEach((button) => {
  button.addEventListener("click", () => {
    applyTransform(button.dataset.action);
    canvas.focus();
  });
});

document.querySelector("#apply-workspace").addEventListener("click", applyWorkspaceInputs);
document.querySelector("#save-group").addEventListener("click", saveWorkspaceGroup);
document.querySelector("#delete-group").addEventListener("click", deleteWorkspaceGroup);
document.querySelector("#saved-group").addEventListener("change", (event) => loadWorkspaceGroup(event.target.value));
document.querySelector("#open-pcg-library").addEventListener("click", openPcgLibrary);
document.querySelector("#close-pcg-library").addEventListener("click", () => pcgLibraryDialog.close());
pcgLibraryDialog.addEventListener("close", () => {
  stopPcgLibraryPreview();
  stopPcgAnimationBuilderPreview();
  if (pcgAnimationBuilderDialog.open) pcgAnimationBuilderDialog.close();
  pcgAnimationBuilderSourcePreset = null;
});
document.querySelectorAll("#pcg-library-search, #pcg-library-category, #pcg-library-size, #pcg-library-kind").forEach((input) => {
  input.addEventListener(input.id === "pcg-library-search" ? "input" : "change", renderPcgLibrary);
});
document.querySelectorAll("[data-pcg-library-scope]").forEach((button) => {
  button.addEventListener("click", () => {
    pcgLibraryScope = button.dataset.pcgLibraryScope;
    renderPcgLibrary();
  });
});
document.querySelector("#pcg-library-favorite").addEventListener("click", togglePcgLibraryFavorite);
document.querySelector("#pcg-library-generate-animation").addEventListener("click", openPcgAnimationBuilder);
document.querySelector("#pcg-library-start-slot").addEventListener("input", (event) => {
  pcgLibraryStartSlot = Number(event.target.value);
  renderPcgLibrary();
});
document.querySelector("#pcg-library-apply").addEventListener("click", () => requestPcgLibraryApply());
document.querySelector("#close-pcg-animation-builder").addEventListener("click", () => pcgAnimationBuilderDialog.close());
document.querySelector("#cancel-pcg-animation-builder").addEventListener("click", () => pcgAnimationBuilderDialog.close());
document.querySelector("#pcg-animation-template").addEventListener("change", () => {
  const template = pcgAnimationBuilderTemplate(pcgAnimationBuilderSourcePreset);
  if (template) document.querySelector("#pcg-animation-duration").value = String(template.frameDurationMs);
  renderPcgAnimationBuilder();
});
document.querySelectorAll("#pcg-animation-duration, #pcg-animation-start-slot").forEach((input) => {
  input.addEventListener("change", renderPcgAnimationBuilder);
});
document.querySelector("#generate-pcg-library-animation").addEventListener("click", generatePcgLibraryAnimation);
pcgAnimationBuilderDialog.addEventListener("close", () => {
  stopPcgAnimationBuilderPreview();
  pcgAnimationBuilderSourcePreset = null;
});
document.querySelector("#close-pcg-library-conflict").addEventListener("click", () => {
  pcgLibraryPendingApply = null;
  pcgLibraryConflictDialog.close();
});
document.querySelector("#cancel-pcg-library-replace").addEventListener("click", () => {
  pcgLibraryPendingApply = null;
  pcgLibraryConflictDialog.close();
});
document.querySelector("#confirm-pcg-library-replace").addEventListener("click", () => {
  if (!pcgLibraryPendingApply) {
    pcgLibraryConflictDialog.close();
    return;
  }
  const { preset, startSlot, recentPresetId } = pcgLibraryPendingApply;
  pcgLibraryPendingApply = null;
  applyPcgLibraryPreset(preset, startSlot, { recentPresetId });
});
pcgLibraryConflictDialog.addEventListener("cancel", () => {
  pcgLibraryPendingApply = null;
});
document.querySelector("#copy-selection").addEventListener("click", copyWorkspace);
document.querySelector("#paste-selection").addEventListener("click", pasteWorkspace);
document.querySelector("#show-grid").addEventListener("change", (event) => {
  gridVisible = event.target.checked;
  renderEditor();
  canvas.focus();
});
document.querySelector("#undo").addEventListener("click", undo);
document.querySelector("#redo").addEventListener("click", redo);
document.querySelector("#show-pcg-view").addEventListener("click", () => setActiveView("pcg"));
document.querySelector("#show-screen-view").addEventListener("click", () => setActiveView("screen"));
document.querySelector("#show-animation-view").addEventListener("click", () => setActiveView("animation"));
document.querySelector("#new-animation-clip").addEventListener("click", createNewAnimationClip);
document.querySelector("#save-animation-settings").addEventListener("click", saveAnimationSettings);
document.querySelector("#delete-animation-clip").addEventListener("click", deleteAnimationClip);
document.querySelector("#capture-animation-frame").addEventListener("click", captureCurrentAnimationFrame);
document.querySelector("#update-animation-frame").addEventListener("click", updateCurrentAnimationFrame);
document.querySelector("#load-animation-frame").addEventListener("click", loadCurrentAnimationFrame);
document.querySelector("#duplicate-animation-frame").addEventListener("click", duplicateCurrentAnimationFrame);
document.querySelector("#delete-animation-frame").addEventListener("click", deleteCurrentAnimationFrame);
document.querySelector("#previous-animation-frame").addEventListener("click", () => selectRelativeAnimationFrame(-1));
document.querySelector("#next-animation-frame").addEventListener("click", () => selectRelativeAnimationFrame(1));
document.querySelector("#play-animation").addEventListener("click", toggleAnimationPlayback);
document.querySelector("#open-animation-export").addEventListener("click", () => {
  document.querySelector("#export-target").value = "animation";
  document.querySelector("#assembly-label").value = "ANIMATION_DATA";
  exportPanel.hidden = false;
  updateAssemblyOutput();
  document.querySelector("#assembly-output").focus();
});
document.querySelector("#language-select").addEventListener("change", (event) => {
  stopAnimationPlayback();
  setLanguage(event.target.value);
  translateDocument();
  document.querySelector("#language-select").value = getLanguage();
  renderAll();
  setActiveView(activeView);
  setMessage(t("message.languageChanged"));
});
document.querySelector("#display-mode").addEventListener("change", (event) => {
  const modeLabel = t(event.target.value === DISPLAY_MODES.PCG ? "crt.modePcg" : "crt.modeInverse");
  snapshotMutation(() => setScreenMode(project.screen, event.target.value), t("message.cmodeChanged", { mode: modeLabel }));
  screenCanvas.focus();
});
document.querySelector("#palette-range").addEventListener("change", renderCharacterPalette);
document.querySelector("#show-screen-grid").addEventListener("change", (event) => {
  screenGridVisible = event.target.checked;
  renderCrt();
  screenCanvas.focus();
});
document.querySelector("#show-vram-source").addEventListener("change", (event) => {
  vramSourceVisible = event.target.checked;
  renderDisplayState();
  renderCrt();
  screenCanvas.focus();
});
document.querySelector("#place-screen-text").addEventListener("click", placeScreenText);
document.querySelector("#screen-text").addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    event.preventDefault();
    placeScreenText();
  }
});
document.querySelector("#fill-screen").addEventListener("click", () => {
  snapshotMutation(() => fillScreen(project.screen, selectedScreenCode), t("message.screenFilled", { code: hex(selectedScreenCode) }));
  screenCanvas.focus();
});
document.querySelector("#clear-screen").addEventListener("click", () => {
  snapshotMutation(() => fillScreen(project.screen, 0x00), t("message.screenCleared"));
  screenCanvas.focus();
});
document.querySelector("#show-pcg-gallery").addEventListener("click", () => {
  snapshotMutation(() => applyPcgGallery(project.screen), t("message.allPcgPlaced"));
  document.querySelector("#palette-range").value = "all";
  screenCanvas.focus();
});
document.querySelector("#open-image-mosaic").addEventListener("click", openImageMosaic);
document.querySelector("#close-image-mosaic").addEventListener("click", () => imageMosaicDialog.close());
document.querySelector("#image-mosaic-file").addEventListener("change", async (event) => {
  const [file] = event.target.files;
  if (!file) return;
  const generation = ++imageMosaicLoadGeneration;
  imageMosaicBitmap?.close?.();
  imageMosaicBitmap = null;
  imageMosaicRgba = null;
  imageMosaicLuminance = null;
  invalidateImageMosaicPreview();
  setImageMosaicStatus("imageMosaic.loading");
  try {
    const bitmap = await decodeImageFile(file);
    if (generation !== imageMosaicLoadGeneration) {
      bitmap.close?.();
      return;
    }
    imageMosaicBitmap = bitmap;
    setImageMosaicStatus("imageMosaic.loaded", {
      name: file.name,
      width: bitmap.width,
      height: bitmap.height,
    });
    renderImageMosaicSource();
  } catch (error) {
    if (generation !== imageMosaicLoadGeneration) return;
    imageMosaicBitmap = null;
    imageMosaicRgba = null;
    imageMosaicLuminance = null;
    imageMosaicPreview = null;
    document.querySelector("#apply-image-mosaic").disabled = true;
    drawImageMosaicPlaceholder(imageMosaicSourceContext, "imageMosaic.noImage");
    drawImageMosaicPlaceholder(imageMosaicResultContext, "imageMosaic.noPreview");
    event.target.value = "";
    setImageMosaicStatus("error.operationFailed", { detail: `: ${error.message}` });
  }
});
document.querySelector("#image-mosaic-fit").addEventListener("change", renderImageMosaicSource);
document.querySelector("#image-mosaic-edge-strength").addEventListener("input", () => {
  syncImageMosaicControls();
  updateImageMosaicLuminance();
  scheduleImageMosaicGeneration();
});
document.querySelectorAll("#image-mosaic-palette, #image-mosaic-tone, #image-mosaic-contrast, #image-mosaic-threshold, #image-mosaic-invert, #image-mosaic-generate-pcg")
  .forEach((control) => control.addEventListener("input", () => {
    syncImageMosaicControls();
    scheduleImageMosaicGeneration();
  }));
document.querySelector("#apply-image-mosaic").addEventListener("click", applyImageMosaic);
document.querySelector("#import-rom").addEventListener("click", () => document.querySelector("#rom-file").click());
document.querySelector("#rom-file").addEventListener("change", async (event) => {
  const [file] = event.target.files;
  if (!file) return;
  try {
    const bytes = new Uint8Array(await file.arrayBuffer());
    snapshotMutation(() => loadCharacterRom(project, bytes), t("message.romImported"));
  } catch (error) {
    setMessage(formatError(error), "error");
  } finally {
    event.target.value = "";
  }
});

document.querySelector("#new-project").addEventListener("click", () => {
  if (!window.confirm(t("confirm.newProject"))) {
    return;
  }
  undoStack.push(cloneProject(project));
  project = createProject({ withPreset: false });
  stopAnimationPlayback();
  activeAnimationId = null;
  activeAnimationFrame = 0;
  activeGroupId = null;
  document.querySelector("#group-name").value = "";
  redoStack = [];
  persistProject(t("message.projectCreated"));
  renderAll();
});

document.querySelector("#save-project").addEventListener("click", () => {
  downloadText("jr100-pcg-project.json", serializeProject(project), "application/json");
  setMessage(t("message.projectDownloaded"));
});

document.querySelector("#import-project").addEventListener("click", () => document.querySelector("#import-file").click());
document.querySelector("#import-file").addEventListener("change", async (event) => {
  const [file] = event.target.files;
  if (!file) {
    return;
  }
  try {
    const imported = parseProject(await file.text());
    undoStack.push(cloneProject(project));
    project = imported;
    stopAnimationPlayback();
    activeAnimationId = null;
    activeAnimationFrame = 0;
    activeGroupId = null;
    document.querySelector("#group-name").value = "";
    redoStack = [];
    persistProject(t("message.projectImported"));
    renderAll();
  } catch (error) {
    setMessage(formatError(error), "error");
  } finally {
    event.target.value = "";
  }
});

const exportPanel = document.querySelector("#export-panel");
document.querySelector("#toggle-export").addEventListener("click", () => {
  exportPanel.hidden = false;
  updateAssemblyOutput();
  document.querySelector("#assembly-output").focus();
});
document.querySelector("#close-export").addEventListener("click", () => {
  exportPanel.hidden = true;
});
document.querySelector("#assembly-label").addEventListener("input", updateAssemblyOutput);
document.querySelector("#export-target").addEventListener("change", updateAssemblyOutput);
document.querySelector("#copy-assembly").addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(document.querySelector("#assembly-output").value);
    setMessage(t("message.asmCopied"));
  } catch {
    document.querySelector("#assembly-output").select();
    setMessage(t("message.asmManual"), "error");
  }
});
document.querySelector("#download-assembly").addEventListener("click", () => {
  downloadText("jr100_data.inc", document.querySelector("#assembly-output").value, "text/plain");
  setMessage(t("message.asmDownloaded"));
});

canvas.addEventListener("contextmenu", (event) => event.preventDefault());
canvas.addEventListener("pointerdown", beginGesture);
canvas.addEventListener("pointermove", moveGesture);
canvas.addEventListener("pointerup", finishGesture);
canvas.addEventListener("pointercancel", finishGesture);
canvas.addEventListener("focus", () => {
  if (!hoverCell) {
    hoverCell = { x: 0, y: 0 };
    updatePointerStatus(hoverCell);
    renderEditor();
  }
});
canvas.addEventListener("pointerleave", () => {
  if (!gesture) {
    hoverCell = null;
    updatePointerStatus(null);
    renderEditor();
  }
});
screenCanvas.addEventListener("contextmenu", (event) => event.preventDefault());
screenCanvas.addEventListener("pointerdown", beginScreenGesture);
screenCanvas.addEventListener("pointermove", moveScreenGesture);
screenCanvas.addEventListener("pointerup", finishScreenGesture);
screenCanvas.addEventListener("pointercancel", finishScreenGesture);
vramGlyphCanvas.addEventListener("contextmenu", (event) => event.preventDefault());
vramGlyphCanvas.addEventListener("pointerdown", beginVramGlyphGesture);
vramGlyphCanvas.addEventListener("pointermove", moveVramGlyphGesture);
vramGlyphCanvas.addEventListener("pointerup", finishVramGlyphGesture);
vramGlyphCanvas.addEventListener("pointercancel", finishVramGlyphGesture);
window.addEventListener("keydown", handleKeyboard);

populatePcgLibraryCategoryOptions();
syncWorkspaceInputs();
renderAll();
setActiveView(activeView);
