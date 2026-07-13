import { createFallbackRomGlyphs, extractCharacterRom } from "./rom_font.js";
import { validateAnimationClips } from "./animation.js";
import { ARCADE_DIGITS } from "./preset_library.js";

export { ARCADE_DIGITS };

export const SLOT_COUNT = 32;
export const GLYPH_SIZE = 8;
export const PROJECT_VERSION = 3;
export const SCREEN_WIDTH = 32;
export const SCREEN_HEIGHT = 24;
export const SCREEN_CELL_COUNT = SCREEN_WIDTH * SCREEN_HEIGHT;
export const DISPLAY_MODES = Object.freeze({ INVERSE: "inverse", PCG: "pcg" });

export function createProject({ withPreset = false } = {}) {
  const project = {
    version: PROJECT_VERSION,
    name: "JR-100 PCG Project",
    glyphs: Array.from({ length: SLOT_COUNT }, () => Array(GLYPH_SIZE).fill(0)),
    names: Array(SLOT_COUNT).fill(""),
    groups: [],
    animations: [],
    screen: createScreen(),
    romGlyphs: createFallbackRomGlyphs(),
    romSource: "Built-in approximation",
  };
  if (withPreset) {
    applyArcadeDigits(project, 0);
  }
  return project;
}

export function createScreen({ mode = DISPLAY_MODES.PCG, withPcgGallery = true } = {}) {
  assertDisplayMode(mode);
  const screen = {
    mode,
    cells: Array(SCREEN_CELL_COUNT).fill(0x00),
  };
  if (withPcgGallery && mode === DISPLAY_MODES.PCG) {
    applyPcgGallery(screen);
  }
  return screen;
}

function assertDisplayMode(mode) {
  if (!Object.values(DISPLAY_MODES).includes(mode)) {
    throw new RangeError("Display mode must be inverse or pcg");
  }
}

export function validateScreen(screen) {
  if (!screen || typeof screen !== "object") {
    throw new TypeError("Screen is required");
  }
  assertDisplayMode(screen.mode);
  if (!Array.isArray(screen.cells) || screen.cells.length !== SCREEN_CELL_COUNT || !screen.cells.every(validateByte)) {
    throw new TypeError("Screen must contain exactly 768 byte cells");
  }
  return screen;
}

function screenIndex(x, y) {
  if (!Number.isInteger(x) || !Number.isInteger(y) || x < 0 || x >= SCREEN_WIDTH || y < 0 || y >= SCREEN_HEIGHT) {
    throw new RangeError("Screen cell is outside the 32x24 display");
  }
  return y * SCREEN_WIDTH + x;
}

export function getScreenCell(screen, x, y) {
  validateScreen(screen);
  return screen.cells[screenIndex(x, y)];
}

export function setScreenCell(screen, x, y, code) {
  validateScreen(screen);
  if (!validateByte(code)) {
    throw new RangeError("Screen code must be a byte");
  }
  screen.cells[screenIndex(x, y)] = code;
}

export function setScreenMode(screen, mode) {
  validateScreen(screen);
  assertDisplayMode(mode);
  screen.mode = mode;
}

export function fillScreen(screen, code = 0x00) {
  validateScreen(screen);
  if (!validateByte(code)) {
    throw new RangeError("Screen code must be a byte");
  }
  screen.cells.fill(code);
}

export function applyPcgGallery(screen) {
  validateScreen(screen);
  screen.mode = DISPLAY_MODES.PCG;
  for (let slot = 0; slot < SLOT_COUNT; slot += 1) {
    const x = slot % 16 + 8;
    const y = Math.floor(slot / 16) + 10;
    setScreenCell(screen, x, y, 0x80 + slot);
  }
  return screen;
}

export function visiblePcgSlots(screen) {
  validateScreen(screen);
  if (screen.mode !== DISPLAY_MODES.PCG) {
    return [];
  }
  return [...new Set(screen.cells.filter((code) => code >= 0x80 && code <= 0x9f).map((code) => code - 0x80))]
    .sort((left, right) => left - right);
}

export function resolveScreenGlyph(project, code) {
  if (!validateByte(code)) {
    throw new RangeError("Screen code must be a byte");
  }
  if (code < 0x80) {
    return project.romGlyphs[code];
  }
  if (project.screen.mode === DISPLAY_MODES.INVERSE) {
    return project.romGlyphs[code - 0x80].map((value) => value ^ 0xff);
  }
  if (code <= 0x9f) {
    return project.glyphs[code - 0x80];
  }
  const sourceOffset = vramPcgSourceOffset(code);
  return project.screen.cells.slice(sourceOffset, sourceOffset + GLYPH_SIZE);
}

export function vramPcgSourceOffset(code) {
  if (!Number.isInteger(code) || code < 0xa0 || code > 0xff) {
    throw new RangeError("VRAM-backed PCG code must be between $A0 and $FF");
  }
  return (code - 0xa0) * GLYPH_SIZE;
}

export function setVramPcgPixel(screen, code, x, y, value) {
  validateScreen(screen);
  if (!Number.isInteger(x) || !Number.isInteger(y) || x < 0 || x >= GLYPH_SIZE || y < 0 || y >= GLYPH_SIZE) {
    throw new RangeError("VRAM-backed PCG pixel is outside the 8x8 glyph");
  }
  const sourceOffset = vramPcgSourceOffset(code);
  const mask = 1 << (7 - x);
  screen.cells[sourceOffset + y] = value
    ? (screen.cells[sourceOffset + y] | mask) & 0xff
    : screen.cells[sourceOffset + y] & ~mask & 0xff;
}

export function asciiToRomCode(character) {
  const source = String(character || " ").toUpperCase();
  const value = source.codePointAt(0) ?? 0x20;
  if (value >= 0x20 && value <= 0x5f) {
    return value - 0x20;
  }
  return 0x1f;
}

export function loadCharacterRom(project, input) {
  project.romGlyphs = extractCharacterRom(input);
  project.romSource = "Imported $E000-$E3FF ROM";
  validateProjectShape(project);
  return project.romGlyphs;
}

export function cloneProject(project) {
  return parseProject(serializeProject(project));
}

export function assertWorkspace(workspace) {
  if (!workspace || typeof workspace !== "object") {
    throw new TypeError("Workspace is required");
  }
  const { baseSlot, width, height } = workspace;
  for (const [name, value] of Object.entries({ baseSlot, width, height })) {
    if (!Number.isInteger(value)) {
      throw new TypeError(`${name} must be an integer`);
    }
  }
  if (baseSlot < 0 || baseSlot >= SLOT_COUNT) {
    throw new RangeError("Base slot must be between 0 and 31");
  }
  if (width < 1 || height < 1) {
    throw new RangeError("Workspace dimensions must be positive");
  }
  if (baseSlot + width * height > SLOT_COUNT) {
    throw new RangeError("Workspace exceeds the 32 slots available on JR-100");
  }
  return workspace;
}

function assertGlyphBank(glyphs) {
  if (!Array.isArray(glyphs) || glyphs.length !== SLOT_COUNT) {
    throw new TypeError("Glyph bank must contain 32 slots");
  }
}

function assertPixel(workspace, x, y) {
  assertWorkspace(workspace);
  const widthPixels = workspace.width * GLYPH_SIZE;
  const heightPixels = workspace.height * GLYPH_SIZE;
  if (!Number.isInteger(x) || !Number.isInteger(y) || x < 0 || y < 0 || x >= widthPixels || y >= heightPixels) {
    throw new RangeError("Pixel is outside the workspace");
  }
}

export function pixelAddress(workspace, x, y) {
  assertPixel(workspace, x, y);
  const tileX = Math.floor(x / GLYPH_SIZE);
  const tileY = Math.floor(y / GLYPH_SIZE);
  return {
    slot: workspace.baseSlot + tileY * workspace.width + tileX,
    row: y % GLYPH_SIZE,
    bit: 7 - (x % GLYPH_SIZE),
  };
}

export function getPixel(glyphs, workspace, x, y) {
  assertGlyphBank(glyphs);
  const { slot, row, bit } = pixelAddress(workspace, x, y);
  return (glyphs[slot][row] >> bit) & 1;
}

export function setPixel(glyphs, workspace, x, y, value) {
  assertGlyphBank(glyphs);
  const { slot, row, bit } = pixelAddress(workspace, x, y);
  const mask = 1 << bit;
  glyphs[slot][row] = value
    ? (glyphs[slot][row] | mask) & 0xff
    : glyphs[slot][row] & ~mask & 0xff;
}

export function bresenhamPoints(x0, y0, x1, y1) {
  const points = [];
  let x = x0;
  let y = y0;
  const dx = Math.abs(x1 - x0);
  const sx = x0 < x1 ? 1 : -1;
  const dy = -Math.abs(y1 - y0);
  const sy = y0 < y1 ? 1 : -1;
  let error = dx + dy;
  while (true) {
    points.push([x, y]);
    if (x === x1 && y === y1) {
      return points;
    }
    const twiceError = 2 * error;
    if (twiceError >= dy) {
      error += dy;
      x += sx;
    }
    if (twiceError <= dx) {
      error += dx;
      y += sy;
    }
  }
}

export function constrainEndpoint(start, end, mode, { width = Infinity, height = Infinity } = {}) {
  const deltaX = end.x - start.x;
  const deltaY = end.y - start.y;
  const distanceX = Math.abs(deltaX);
  const distanceY = Math.abs(deltaY);
  if (mode === "line" && distanceX >= distanceY * 2) {
    return { x: end.x, y: start.y };
  }
  if (mode === "line" && distanceY >= distanceX * 2) {
    return { x: start.x, y: end.y };
  }
  if (mode !== "line" && mode !== "rectangle") {
    throw new RangeError("Constraint mode must be line or rectangle");
  }
  const directionX = Math.sign(deltaX) || 1;
  const directionY = Math.sign(deltaY) || 1;
  const horizontalLimit = directionX > 0 ? width - 1 - start.x : start.x;
  const verticalLimit = directionY > 0 ? height - 1 - start.y : start.y;
  const distance = Math.max(0, Math.min(Math.max(distanceX, distanceY), horizontalLimit, verticalLimit));
  return {
    x: start.x + directionX * distance,
    y: start.y + directionY * distance,
  };
}

export function workspaceToMatrix(glyphs, workspace) {
  assertWorkspace(workspace);
  return Array.from({ length: workspace.height * GLYPH_SIZE }, (_, y) =>
    Array.from({ length: workspace.width * GLYPH_SIZE }, (_, x) => getPixel(glyphs, workspace, x, y)),
  );
}

export function matrixToWorkspace(glyphs, workspace, matrix) {
  assertWorkspace(workspace);
  const expectedHeight = workspace.height * GLYPH_SIZE;
  const expectedWidth = workspace.width * GLYPH_SIZE;
  if (!Array.isArray(matrix) || matrix.length !== expectedHeight || matrix.some((row) => !Array.isArray(row) || row.length !== expectedWidth)) {
    throw new TypeError("Matrix dimensions do not match the workspace");
  }
  for (let y = 0; y < expectedHeight; y += 1) {
    for (let x = 0; x < expectedWidth; x += 1) {
      setPixel(glyphs, workspace, x, y, matrix[y][x] ? 1 : 0);
    }
  }
}

export function shiftWorkspace(glyphs, workspace, dx, dy, { wrap = false } = {}) {
  const source = workspaceToMatrix(glyphs, workspace);
  const height = source.length;
  const width = source[0].length;
  const shifted = Array.from({ length: height }, () => Array(width).fill(0));
  for (let y = 0; y < height; y += 1) {
    for (let x = 0; x < width; x += 1) {
      if (!source[y][x]) {
        continue;
      }
      let targetX = x + dx;
      let targetY = y + dy;
      if (wrap) {
        targetX = ((targetX % width) + width) % width;
        targetY = ((targetY % height) + height) % height;
      }
      if (targetX >= 0 && targetX < width && targetY >= 0 && targetY < height) {
        shifted[targetY][targetX] = 1;
      }
    }
  }
  matrixToWorkspace(glyphs, workspace, shifted);
}

export function flipWorkspace(glyphs, workspace, axis) {
  const source = workspaceToMatrix(glyphs, workspace);
  let flipped;
  if (axis === "horizontal") {
    flipped = source.map((row) => [...row].reverse());
  } else if (axis === "vertical") {
    flipped = [...source].reverse().map((row) => [...row]);
  } else {
    throw new RangeError("Axis must be horizontal or vertical");
  }
  matrixToWorkspace(glyphs, workspace, flipped);
}

export function invertWorkspace(glyphs, workspace) {
  const matrix = workspaceToMatrix(glyphs, workspace).map((row) => row.map((value) => (value ? 0 : 1)));
  matrixToWorkspace(glyphs, workspace, matrix);
}

export function clearWorkspace(glyphs, workspace) {
  const matrix = Array.from({ length: workspace.height * GLYPH_SIZE }, () =>
    Array(workspace.width * GLYPH_SIZE).fill(0),
  );
  matrixToWorkspace(glyphs, workspace, matrix);
}

export function floodFill(glyphs, workspace, startX, startY, value) {
  const target = getPixel(glyphs, workspace, startX, startY);
  const replacement = value ? 1 : 0;
  if (target === replacement) {
    return;
  }
  const width = workspace.width * GLYPH_SIZE;
  const height = workspace.height * GLYPH_SIZE;
  const pending = [[startX, startY]];
  while (pending.length) {
    const [x, y] = pending.pop();
    if (x < 0 || y < 0 || x >= width || y >= height || getPixel(glyphs, workspace, x, y) !== target) {
      continue;
    }
    setPixel(glyphs, workspace, x, y, replacement);
    pending.push([x - 1, y], [x + 1, y], [x, y - 1], [x, y + 1]);
  }
}

function assertPcgPreset(preset) {
  if (!preset || typeof preset !== "object") {
    throw new TypeError("PCG preset is required");
  }
  const { id, kind, name, width, height, glyphs, slotNames } = preset;
  if (typeof id !== "string" || !id || !["asset", "set"].includes(kind) || typeof name !== "string" || !name) {
    throw new TypeError("PCG preset metadata is invalid");
  }
  if (!Number.isInteger(width) || !Number.isInteger(height) || width < 1 || height < 1) {
    throw new TypeError("PCG preset dimensions are invalid");
  }
  if (!Array.isArray(glyphs) || glyphs.length !== width * height || glyphs.some((glyph) => !Array.isArray(glyph) || glyph.length !== GLYPH_SIZE || !glyph.every(validateByte))) {
    throw new TypeError("PCG preset glyph data is invalid");
  }
  if (!Array.isArray(slotNames) || slotNames.length !== glyphs.length || slotNames.some((entry) => typeof entry !== "string" || !entry)) {
    throw new TypeError("PCG preset slot names are invalid");
  }
  assertWorkspace({ baseSlot: 0, width, height });
  return preset;
}

function rangesOverlap(leftStart, leftCount, rightStart, rightCount) {
  return leftStart < rightStart + rightCount && rightStart < leftStart + leftCount;
}

function presetWorkspace(preset, startSlot) {
  assertPcgPreset(preset);
  const workspace = { baseSlot: startSlot, width: preset.width, height: preset.height };
  assertWorkspace(workspace);
  return workspace;
}

export function inspectPcgPresetConflicts(project, preset, startSlot) {
  validateProjectShape(project);
  const workspace = presetWorkspace(preset, startSlot);
  const slotCount = workspace.width * workspace.height;
  const occupiedSlots = Array.from({ length: slotCount }, (_, index) => workspace.baseSlot + index)
    .filter((slot) => project.glyphs[slot].some(Boolean));
  const groupIds = project.groups
    .filter((group) => rangesOverlap(workspace.baseSlot, slotCount, group.baseSlot, group.width * group.height))
    .map(({ id }) => id);
  const animationIds = project.animations
    .filter((clip) => rangesOverlap(workspace.baseSlot, slotCount, clip.baseSlot, clip.width * clip.height))
    .map(({ id }) => id);
  return {
    startSlot: workspace.baseSlot,
    endSlot: workspace.baseSlot + slotCount - 1,
    occupiedSlots,
    groupIds,
    animationIds,
  };
}

export function applyPcgPreset(project, preset, startSlot) {
  validateProjectShape(project);
  const workspace = presetWorkspace(preset, startSlot);
  const slotCount = workspace.width * workspace.height;
  const conflict = inspectPcgPresetConflicts(project, preset, startSlot);
  const removedGroupIds = [...conflict.groupIds];
  const removedAnimationIds = [...conflict.animationIds];
  project.groups = project.groups.filter(({ id }) => !removedGroupIds.includes(id));
  project.animations = project.animations.filter(({ id }) => !removedAnimationIds.includes(id));
  preset.glyphs.forEach((glyph, index) => {
    project.glyphs[workspace.baseSlot + index] = [...glyph];
    project.names[workspace.baseSlot + index] = preset.slotNames[index];
  });
  if (slotCount > 1) {
    upsertGroup(project, {
      id: `preset-${preset.id}-${workspace.baseSlot}`,
      name: preset.name,
      ...workspace,
    });
  }
  return {
    workspace,
    replacedSlotCount: slotCount,
    removedGroupIds,
    removedAnimationIds,
  };
}

export function applyArcadeDigits(project, startSlot = 0) {
  applyPcgPreset(project, ARCADE_DIGITS, startSlot);
  const generatedId = `preset-${ARCADE_DIGITS.id}-${startSlot}`;
  const generatedIndex = project.groups.findIndex(({ id }) => id === generatedId);
  if (generatedIndex >= 0) {
    const group = { ...project.groups[generatedIndex], id: ARCADE_DIGITS.id };
    const existingIndex = project.groups.findIndex(({ id }) => id === ARCADE_DIGITS.id);
    if (existingIndex >= 0) {
      project.groups[existingIndex] = group;
      project.groups.splice(generatedIndex, 1);
    } else {
      project.groups[generatedIndex] = group;
    }
  }
  return project;
}

export function upsertGroup(project, group) {
  validateProjectShape(project);
  if (!group || typeof group !== "object") {
    throw new TypeError("Group must be an object");
  }
  if (typeof group.id !== "string" || !group.id || typeof group.name !== "string" || !group.name.trim()) {
    throw new TypeError("Group must have a non-empty id and name");
  }
  assertWorkspace(group);
  const normalized = {
    id: group.id,
    name: group.name.trim(),
    baseSlot: group.baseSlot,
    width: group.width,
    height: group.height,
  };
  const index = project.groups.findIndex((candidate) => candidate.id === group.id);
  if (index >= 0) {
    project.groups[index] = normalized;
  } else {
    project.groups.push(normalized);
  }
  return normalized;
}

export function removeGroup(project, id) {
  validateProjectShape(project);
  const before = project.groups.length;
  project.groups = project.groups.filter((group) => group.id !== id);
  return project.groups.length !== before;
}

function validateByte(value) {
  return Number.isInteger(value) && value >= 0 && value <= 0xff;
}

export function validateProjectShape(project) {
  if (!project || typeof project !== "object") {
    throw new TypeError("Project must be an object");
  }
  if (!Array.isArray(project.glyphs) || project.glyphs.length !== SLOT_COUNT) {
    throw new TypeError("Project must contain exactly 32 glyphs");
  }
  if (project.glyphs.some((glyph) => !Array.isArray(glyph) || glyph.length !== GLYPH_SIZE || !glyph.every(validateByte))) {
    throw new TypeError("Every glyph must contain exactly eight bytes");
  }
  if (!Array.isArray(project.names) || project.names.length !== SLOT_COUNT || project.names.some((name) => typeof name !== "string")) {
    throw new TypeError("Project must contain 32 slot names");
  }
  if (!Array.isArray(project.groups)) {
    throw new TypeError("Project groups must be an array");
  }
  project.groups.forEach((group) => {
    if (typeof group.id !== "string" || !group.id || typeof group.name !== "string" || !group.name) {
      throw new TypeError("Every group must have a non-empty id and name");
    }
    assertWorkspace(group);
  });
  validateAnimationClips(project.animations);
  validateScreen(project.screen);
  if (!Array.isArray(project.romGlyphs) || project.romGlyphs.length !== 128) {
    throw new TypeError("Project must contain 128 ROM glyphs");
  }
  if (project.romGlyphs.some((glyph) => !Array.isArray(glyph) || glyph.length !== GLYPH_SIZE || !glyph.every(validateByte))) {
    throw new TypeError("Every ROM glyph must contain exactly eight bytes");
  }
  if (typeof project.romSource !== "string") {
    throw new TypeError("Project ROM source must be text");
  }
  return project;
}

export function serializeProject(project) {
  validateProjectShape(project);
  return `${JSON.stringify(project, null, 2)}\n`;
}

export function parseProject(text) {
  let parsed;
  try {
    parsed = JSON.parse(text);
  } catch (error) {
    throw new TypeError(`Invalid project JSON: ${error.message}`);
  }
  if (!parsed.screen) {
    parsed.screen = createScreen();
  } else if (parsed.screen.mode === "normal") {
    parsed.screen.mode = DISPLAY_MODES.INVERSE;
  }
  if (!parsed.romGlyphs) {
    parsed.romGlyphs = createFallbackRomGlyphs();
    parsed.romSource = "Built-in approximation";
  }
  if (typeof parsed.romSource !== "string") {
    parsed.romSource = "Built-in approximation";
  }
  if (!Array.isArray(parsed.animations)) {
    parsed.animations = [];
  }
  parsed.version = PROJECT_VERSION;
  validateProjectShape(parsed);
  return parsed;
}

export function normalizeAssemblyLabel(label) {
  const normalized = String(label || "PCG_DATA")
    .toUpperCase()
    .replace(/[^A-Z0-9_]/g, "_")
    .replace(/^[^A-Z_]/, "_$&");
  return normalized || "PCG_DATA";
}

function printableAscii(text) {
  return String(text).replace(/[^\x20-\x7e]/g, "");
}

export function exportAssembly(project, { label = "PCG_DATA" } = {}) {
  validateProjectShape(project);
  const lines = [`${normalizeAssemblyLabel(label)}:`];
  project.glyphs.forEach((glyph, slot) => {
    const code = 0x80 + slot;
    const suffix = project.names[slot] ? ` / ${printableAscii(project.names[slot])}` : "";
    lines.push(`; Slot ${slot.toString().padStart(2, "0")} / Code $${code.toString(16).toUpperCase().padStart(2, "0")}${suffix}`);
    lines.push(`        .byte ${glyph.map((value) => `$${value.toString(16).toUpperCase().padStart(2, "0")}`).join(", ")}`);
  });
  return `${lines.join("\n")}\n`;
}

export function exportScreenAssembly(project, { label = "SCREEN_DATA" } = {}) {
  validateProjectShape(project);
  const normalizedLabel = normalizeAssemblyLabel(label);
  const modeValue = project.screen.mode === DISPLAY_MODES.PCG ? 1 : 0;
  const lines = [
    `; JR-100 display mode: ${project.screen.mode === DISPLAY_MODES.PCG ? "ROM/PCG" : "Normal/inverse"}`,
    `${normalizedLabel}_MODE: .equ ${modeValue}`,
    `${normalizedLabel}:`,
  ];
  for (let offset = 0; offset < project.screen.cells.length; offset += 16) {
    const row = project.screen.cells.slice(offset, offset + 16);
    lines.push(`        .byte ${row.map((value) => `$${value.toString(16).toUpperCase().padStart(2, "0")}`).join(", ")}`);
  }
  return `${lines.join("\n")}\n`;
}

export function exportCombinedAssembly(project, { pcgLabel = "PCG_DATA", screenLabel = "SCREEN_DATA" } = {}) {
  return `${exportAssembly(project, { label: pcgLabel })}\n${exportScreenAssembly(project, { label: screenLabel })}`;
}
