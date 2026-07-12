import {
  applyArcadeDigits,
  assertWorkspace,
  bresenhamPoints,
  clearWorkspace,
  cloneProject,
  createProject,
  exportAssembly,
  flipWorkspace,
  floodFill,
  getPixel,
  invertWorkspace,
  matrixToWorkspace,
  parseProject,
  removeGroup,
  serializeProject,
  setPixel,
  shiftWorkspace,
  upsertGroup,
  workspaceToMatrix,
} from "./core.js";

const STORAGE_KEY = "jr100dev.pcg-workbench.v1";
const HISTORY_LIMIT = 64;
const canvas = document.querySelector("#editor-canvas");
const canvasContext = canvas.getContext("2d");
const crtCanvas = document.querySelector("#crt-preview");
const crtContext = crtCanvas.getContext("2d");

let project = restoreProject();
let workspace = { baseSlot: 0, width: 1, height: 1 };
let tool = "pencil";
let gesture = null;
let hoverCell = null;
let clipboardMatrix = null;
let undoStack = [];
let redoStack = [];
let activeGroupId = null;

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

function persistProject(message = "Autosaved") {
  localStorage.setItem(STORAGE_KEY, serializeProject(project));
  document.querySelector("#save-status").textContent = message;
  setMessage(message);
}

function snapshotMutation(mutator, message) {
  const before = cloneProject(project);
  mutator();
  undoStack.push(before);
  if (undoStack.length > HISTORY_LIMIT) {
    undoStack.shift();
  }
  redoStack = [];
  persistProject(message);
  renderAll();
}

function undo() {
  if (!undoStack.length) {
    return;
  }
  redoStack.push(cloneProject(project));
  project = undoStack.pop();
  persistProject("Undo applied");
  renderAll();
}

function redo() {
  if (!redoStack.length) {
    return;
  }
  undoStack.push(cloneProject(project));
  project = redoStack.pop();
  persistProject("Redo applied");
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
  const cellSize = Math.max(14, Math.min(48, Math.floor(560 / longest)));
  canvas.width = dimensions.width * cellSize;
  canvas.height = dimensions.height * cellSize;
  canvas.dataset.cellSize = String(cellSize);
}

function renderEditor() {
  resizeEditorCanvas();
  const cellSize = Number(canvas.dataset.cellSize);
  const dimensions = workspacePixelSize();
  canvasContext.fillStyle = "#09100b";
  canvasContext.fillRect(0, 0, canvas.width, canvas.height);

  for (let y = 0; y < dimensions.height; y += 1) {
    for (let x = 0; x < dimensions.width; x += 1) {
      if (getPixel(project.glyphs, workspace, x, y)) {
        canvasContext.fillStyle = "#f0c35a";
        canvasContext.fillRect(x * cellSize + 2, y * cellSize + 2, cellSize - 3, cellSize - 3);
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

  for (let x = 0; x <= dimensions.width; x += 1) {
    canvasContext.beginPath();
    canvasContext.strokeStyle = x % 8 === 0 ? "#ac8738" : "#344339";
    canvasContext.lineWidth = x % 8 === 0 ? 3 : 1;
    canvasContext.moveTo(x * cellSize, 0);
    canvasContext.lineTo(x * cellSize, canvas.height);
    canvasContext.stroke();
  }
  for (let y = 0; y <= dimensions.height; y += 1) {
    canvasContext.beginPath();
    canvasContext.strokeStyle = y % 8 === 0 ? "#ac8738" : "#344339";
    canvasContext.lineWidth = y % 8 === 0 ? 3 : 1;
    canvasContext.moveTo(0, y * cellSize);
    canvasContext.lineTo(canvas.width, y * cellSize);
    canvasContext.stroke();
  }
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
    button.setAttribute("aria-label", `Slot ${slot}, code ${hex(0x80 + slot)}, ${project.names[slot] || (used ? "used" : "empty")}`);
    mini.width = 64;
    mini.height = 64;
    const miniContext = mini.getContext("2d");
    miniContext.fillStyle = "#0a100c";
    miniContext.fillRect(0, 0, 64, 64);
    drawGlyphPreview(miniContext, glyph, 0, 0, 8, "#8de3a2");
    meta.className = "slot-meta";
    meta.innerHTML = `<span>${slot.toString().padStart(2, "0")}</span><span>${hex(0x80 + slot)}</span>`;
    name.className = "slot-name";
    name.textContent = project.names[slot] || (used ? "Custom glyph" : "Empty");
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

function renderCrt() {
  crtContext.fillStyle = "#020503";
  crtContext.fillRect(0, 0, crtCanvas.width, crtCanvas.height);
  crtContext.fillStyle = "rgba(48, 105, 57, 0.14)";
  for (let y = 0; y < crtCanvas.height; y += 2) {
    crtContext.fillRect(0, y, crtCanvas.width, 1);
  }

  const arcadeBase = project.groups.find((group) => group.id === "arcade-digits")?.baseSlot ?? 0;
  const clock = [1, 2, 10, 3, 4, 10, 5, 6].map((slot) => arcadeBase + slot);
  const clockX = 12;
  const clockY = 4;
  clock.forEach((slot, index) => drawGlyphPreview(crtContext, project.glyphs[slot], (clockX + index) * 8, clockY * 8, 1, "#a6ffb3"));

  const startColumn = Math.floor((32 - workspace.width) / 2);
  const startRow = 12;
  for (let tileY = 0; tileY < workspace.height; tileY += 1) {
    for (let tileX = 0; tileX < workspace.width; tileX += 1) {
      const slot = workspace.baseSlot + tileY * workspace.width + tileX;
      drawGlyphPreview(crtContext, project.glyphs[slot], (startColumn + tileX) * 8, (startRow + tileY) * 8, 1, "#74dc89");
    }
  }
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
    heading.textContent = `SLOT ${slot.toString().padStart(2, "0")} / CODE ${hex(0x80 + slot)}${project.names[slot] ? ` / ${project.names[slot]}` : ""}`;
    code.textContent = project.glyphs[slot]
      .map((value, row) => `${row}: ${hex(value)}  ${value.toString(2).padStart(8, "0")}`)
      .join("\n");
    entry.append(heading, code);
    inspector.append(entry);
  }
}

function renderUsage() {
  const used = project.glyphs.filter((glyph) => glyph.some(Boolean)).length;
  document.querySelector("#usage-status").textContent = `${used} / 32 slots used`;
  document.querySelector("#undo").disabled = undoStack.length === 0;
  document.querySelector("#redo").disabled = redoStack.length === 0;
  document.querySelector("#paste-selection").disabled = clipboardMatrix === null;
}

function renderSavedGroups() {
  const select = document.querySelector("#saved-group");
  const selected = activeGroupId ?? "";
  select.replaceChildren(new Option("Current layout", ""));
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
}

function updateAssemblyOutput() {
  const label = document.querySelector("#assembly-label").value;
  document.querySelector("#assembly-output").value = exportAssembly(project, { label });
}

function renderAll() {
  renderEditor();
  renderSlotRack();
  renderCrt();
  renderByteInspector();
  renderUsage();
  renderSavedGroups();
  updateAssemblyOutput();
  updateToolButtons();
}

function updateToolButtons() {
  document.querySelectorAll("[data-tool]").forEach((button) => {
    button.classList.toggle("active", button.dataset.tool === tool);
    button.setAttribute("aria-pressed", button.dataset.tool === tool ? "true" : "false");
  });
}

function syncWorkspaceInputs() {
  document.querySelector("#base-slot").value = String(workspace.baseSlot);
  document.querySelector("#workspace-width").value = String(workspace.width);
  document.querySelector("#workspace-height").value = String(workspace.height);
  const count = workspace.width * workspace.height;
  const end = workspace.baseSlot + count - 1;
  const slots = count === 1
    ? `Slot ${workspace.baseSlot.toString().padStart(2, "0")}`
    : `Slots ${workspace.baseSlot.toString().padStart(2, "0")}-${end.toString().padStart(2, "0")}`;
  document.querySelector("#workspace-summary").textContent = `${slots} / ${workspace.width * 8}x${workspace.height * 8} px`;
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
    setMessage(`Editing ${candidate.width}x${candidate.height} composite from slot ${candidate.baseSlot}`);
  } catch (error) {
    setMessage(error.message, "error");
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
  }, `Group ${name} saved`);
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
  }, `Group ${group.name} deleted`);
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
}

function moveGesture(event) {
  const cell = cellFromPointer(event);
  hoverCell = cell;
  updatePointerStatus(cell);
  if (!gesture || gesture.pointerId !== event.pointerId || !cell) {
    renderEditor();
    return;
  }
  if (tool === "pencil" || tool === "eraser") {
    gesture.changed = paintLine(gesture.last, cell, gesture.value) || gesture.changed;
    gesture.last = cell;
  } else if (tool === "line") {
    gesture.preview = bresenhamPoints(gesture.start.x, gesture.start.y, cell.x, cell.y);
    gesture.last = cell;
  } else if (tool === "rectangle") {
    gesture.preview = rectanglePoints(gesture.start, cell);
    gesture.last = cell;
  }
  renderEditor();
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
    undoStack.push(gesture.before);
    if (undoStack.length > HISTORY_LIMIT) {
      undoStack.shift();
    }
    redoStack = [];
    persistProject("Stroke saved");
  }
  gesture = null;
  renderAll();
}

function updatePointerStatus(cell) {
  const output = document.querySelector("#pointer-status");
  if (!cell) {
    output.textContent = "Pointer outside canvas";
    return;
  }
  const tileX = Math.floor(cell.x / 8);
  const tileY = Math.floor(cell.y / 8);
  const slot = workspace.baseSlot + tileY * workspace.width + tileX;
  const row = cell.y % 8;
  output.textContent = `X ${cell.x.toString().padStart(2, "0")}  Y ${cell.y.toString().padStart(2, "0")}  SLOT ${slot.toString().padStart(2, "0")}  ROW ${row}  ${getPixel(project.glyphs, workspace, cell.x, cell.y) ? "ON" : "OFF"}`;
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

function applyTransform(action) {
  const transform = TRANSFORM_ACTIONS[action];
  if (!transform) {
    setMessage(`Unknown transform: ${action}`, "error");
    return;
  }
  snapshotMutation(
    () => transform({ wrap: document.querySelector("#wrap-shift").checked }),
    `${action.replaceAll("-", " ")} applied`,
  );
}

function copyWorkspace() {
  clipboardMatrix = workspaceToMatrix(project.glyphs, workspace);
  renderUsage();
  setMessage(`Copied ${clipboardMatrix[0].length}x${clipboardMatrix.length} pixels`);
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
  }, "Clipboard pasted");
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

function handleKeyboard(event) {
  const target = event.target;
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
  const toolKeys = { b: "pencil", e: "eraser", l: "line", r: "rectangle", g: "fill" };
  if (toolKeys[event.key.toLowerCase()]) {
    tool = toolKeys[event.key.toLowerCase()];
    updateToolButtons();
    setMessage(`${tool} tool selected`);
    return;
  }
  const actionKeys = {
    ArrowUp: "shift-up",
    ArrowDown: "shift-down",
    ArrowLeft: "shift-left",
    ArrowRight: "shift-right",
  };
  if (actionKeys[event.key]) {
    event.preventDefault();
    applyTransform(actionKeys[event.key]);
  } else if (event.key === "Delete" || event.key === "Backspace") {
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
  button.addEventListener("click", () => applyTransform(button.dataset.action));
});

document.querySelector("#apply-workspace").addEventListener("click", applyWorkspaceInputs);
document.querySelector("#save-group").addEventListener("click", saveWorkspaceGroup);
document.querySelector("#delete-group").addEventListener("click", deleteWorkspaceGroup);
document.querySelector("#saved-group").addEventListener("change", (event) => loadWorkspaceGroup(event.target.value));
document.querySelector("#copy-selection").addEventListener("click", copyWorkspace);
document.querySelector("#paste-selection").addEventListener("click", pasteWorkspace);
document.querySelector("#undo").addEventListener("click", undo);
document.querySelector("#redo").addEventListener("click", redo);

document.querySelector("#apply-preset").addEventListener("click", () => {
  const start = Number(document.querySelector("#preset-start").value);
  try {
    snapshotMutation(() => applyArcadeDigits(project, start), "Arcade digits applied");
  } catch (error) {
    setMessage(error.message, "error");
  }
});

document.querySelector("#new-project").addEventListener("click", () => {
  if (!window.confirm("Create a new blank project? Current work can still be recovered with Undo.")) {
    return;
  }
  undoStack.push(cloneProject(project));
  project = createProject({ withPreset: false });
  activeGroupId = null;
  document.querySelector("#group-name").value = "";
  redoStack = [];
  persistProject("Blank project created");
  renderAll();
});

document.querySelector("#save-project").addEventListener("click", () => {
  downloadText("jr100-pcg-project.json", serializeProject(project), "application/json");
  setMessage("Project JSON downloaded");
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
    activeGroupId = null;
    document.querySelector("#group-name").value = "";
    redoStack = [];
    persistProject("Project imported");
    renderAll();
  } catch (error) {
    setMessage(error.message, "error");
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
document.querySelector("#copy-assembly").addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(document.querySelector("#assembly-output").value);
    setMessage("Assembly copied to clipboard");
  } catch {
    document.querySelector("#assembly-output").select();
    setMessage("Select and copy the assembly text manually", "error");
  }
});
document.querySelector("#download-assembly").addEventListener("click", () => {
  downloadText("pcg_data.inc", document.querySelector("#assembly-output").value, "text/plain");
  setMessage("Assembly include downloaded");
});

canvas.addEventListener("contextmenu", (event) => event.preventDefault());
canvas.addEventListener("pointerdown", beginGesture);
canvas.addEventListener("pointermove", moveGesture);
canvas.addEventListener("pointerup", finishGesture);
canvas.addEventListener("pointercancel", finishGesture);
canvas.addEventListener("pointerleave", () => {
  if (!gesture) {
    hoverCell = null;
    updatePointerStatus(null);
    renderEditor();
  }
});
window.addEventListener("keydown", handleKeyboard);

syncWorkspaceInputs();
renderAll();
