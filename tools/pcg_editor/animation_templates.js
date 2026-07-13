const GLYPH_SIZE = 8;
const SLOT_COUNT = 32;

const TEMPLATE_DEFINITIONS = [
  { id: "blink", name: "Blink", frameDurationMs: 160 },
  { id: "pulse", name: "Pulse", frameDurationMs: 140 },
  { id: "bounce", name: "Bounce", frameDurationMs: 120 },
  { id: "shake", name: "Shake", frameDurationMs: 90 },
  { id: "scroll-right", name: "Scroll Right", frameDurationMs: 100 },
  { id: "scroll-down", name: "Scroll Down", frameDurationMs: 100 },
  { id: "wave", name: "Wave", frameDurationMs: 140 },
  { id: "sparkle", name: "Sparkle", frameDurationMs: 160 },
];

export const PCG_ANIMATION_TEMPLATES = Object.freeze(TEMPLATE_DEFINITIONS.map((template) => Object.freeze({ ...template })));

const TEMPLATE_BY_ID = new Map(PCG_ANIMATION_TEMPLATES.map((template) => [template.id, template]));

function validateByte(value) {
  return Number.isInteger(value) && value >= 0 && value <= 0xff;
}

function assertSourcePreset(preset) {
  if (!preset || typeof preset !== "object" || !["asset", "set"].includes(preset.kind)) {
    throw new TypeError("Animation templates require an asset or set preset");
  }
  if (typeof preset.id !== "string" || !preset.id || typeof preset.name !== "string" || !preset.name || typeof preset.category !== "string" || !preset.category) {
    throw new TypeError("Source preset metadata is invalid");
  }
  if (!Array.isArray(preset.tags) || !Number.isInteger(preset.width) || !Number.isInteger(preset.height) || preset.width < 1 || preset.height < 1 || preset.width * preset.height > SLOT_COUNT) {
    throw new RangeError("Source preset dimensions must fit in the 32-slot PCG bank");
  }
  const slotCount = preset.width * preset.height;
  if (!Array.isArray(preset.glyphs) || preset.glyphs.length !== slotCount || preset.glyphs.some((glyph) => !Array.isArray(glyph) || glyph.length !== GLYPH_SIZE || !glyph.every(validateByte))) {
    throw new TypeError("Source preset glyph data is invalid");
  }
  if (!Array.isArray(preset.slotNames) || preset.slotNames.length !== slotCount || preset.slotNames.some((name) => typeof name !== "string" || !name)) {
    throw new TypeError("Source preset slot names are invalid");
  }
  return preset;
}

function cloneMatrix(matrix) {
  return matrix.map((row) => [...row]);
}

function emptyMatrix(width, height) {
  return Array.from({ length: height }, () => Array(width).fill(0));
}

function glyphsToMatrix(glyphs, width, height) {
  return Array.from({ length: height * GLYPH_SIZE }, (_, y) =>
    Array.from({ length: width * GLYPH_SIZE }, (_, x) => {
      const tile = Math.floor(y / GLYPH_SIZE) * width + Math.floor(x / GLYPH_SIZE);
      return (glyphs[tile][y % GLYPH_SIZE] >> (7 - (x % GLYPH_SIZE))) & 1;
    }),
  );
}

function matrixToGlyphs(matrix, width, height) {
  return Array.from({ length: width * height }, (_, tile) => {
    const tileX = (tile % width) * GLYPH_SIZE;
    const tileY = Math.floor(tile / width) * GLYPH_SIZE;
    return Array.from({ length: GLYPH_SIZE }, (_, row) => {
      let value = 0;
      for (let column = 0; column < GLYPH_SIZE; column += 1) {
        if (matrix[tileY + row][tileX + column]) value |= 1 << (7 - column);
      }
      return value;
    });
  });
}

function shiftMatrix(matrix, deltaX, deltaY, { wrap = false } = {}) {
  const height = matrix.length;
  const width = matrix[0].length;
  const shifted = emptyMatrix(width, height);
  for (let y = 0; y < height; y += 1) {
    for (let x = 0; x < width; x += 1) {
      if (!matrix[y][x]) continue;
      let targetX = x + deltaX;
      let targetY = y + deltaY;
      if (wrap) {
        targetX = (targetX + width) % width;
        targetY = (targetY + height) % height;
      }
      if (targetX >= 0 && targetX < width && targetY >= 0 && targetY < height) {
        shifted[targetY][targetX] = 1;
      }
    }
  }
  return shifted;
}

function dilateMatrix(matrix) {
  const height = matrix.length;
  const width = matrix[0].length;
  const expanded = cloneMatrix(matrix);
  for (let y = 0; y < height; y += 1) {
    for (let x = 0; x < width; x += 1) {
      if (!matrix[y][x]) continue;
      for (let offsetY = -1; offsetY <= 1; offsetY += 1) {
        for (let offsetX = -1; offsetX <= 1; offsetX += 1) {
          const targetX = x + offsetX;
          const targetY = y + offsetY;
          if (targetX >= 0 && targetX < width && targetY >= 0 && targetY < height) expanded[targetY][targetX] = 1;
        }
      }
    }
  }
  return expanded;
}

function waveMatrix(matrix, phase) {
  const offsets = [0, 1, 0, -1];
  const height = matrix.length;
  const width = matrix[0].length;
  return matrix.map((row, y) => {
    const shifted = Array(width).fill(0);
    const offset = offsets[(y + phase) % offsets.length];
    row.forEach((value, x) => {
      if (value) shifted[(x + offset + width) % width] = 1;
    });
    return shifted;
  });
}

function sparkleMatrix(matrix, phase) {
  const sparkling = cloneMatrix(matrix);
  const height = sparkling.length;
  const width = sparkling[0].length;
  const positions = [
    [[1, 1], [width - 2, height - 2]],
    [[width - 2, 1], [1, height - 2]],
    [[Math.floor(width / 2), 1], [Math.floor(width / 2), height - 2]],
    [[1, Math.floor(height / 2)], [width - 2, Math.floor(height / 2)]],
  ];
  positions[phase % positions.length].forEach(([x, y]) => {
    if (x >= 0 && x < width && y >= 0 && y < height) sparkling[y][x] = 1;
  });
  return sparkling;
}

function buildTemplateMatrices(templateId, source) {
  const blank = emptyMatrix(source[0].length, source.length);
  if (templateId === "blink") return [cloneMatrix(source), blank, cloneMatrix(source), blank];
  if (templateId === "pulse") return [cloneMatrix(source), dilateMatrix(source), cloneMatrix(source), dilateMatrix(source)];
  if (templateId === "bounce") return [cloneMatrix(source), shiftMatrix(source, 0, -1), cloneMatrix(source), shiftMatrix(source, 0, 1)];
  if (templateId === "shake") return [cloneMatrix(source), shiftMatrix(source, 1, 0), cloneMatrix(source), shiftMatrix(source, -1, 0)];
  if (templateId === "scroll-right") return [cloneMatrix(source), shiftMatrix(source, 1, 0, { wrap: true }), shiftMatrix(source, 2, 0, { wrap: true }), shiftMatrix(source, 3, 0, { wrap: true })];
  if (templateId === "scroll-down") return [cloneMatrix(source), shiftMatrix(source, 0, 1, { wrap: true }), shiftMatrix(source, 0, 2, { wrap: true }), shiftMatrix(source, 0, 3, { wrap: true })];
  if (templateId === "wave") return [cloneMatrix(source), waveMatrix(source, 1), waveMatrix(source, 2), waveMatrix(source, 3)];
  if (templateId === "sparkle") return [cloneMatrix(source), sparkleMatrix(source, 0), sparkleMatrix(source, 1), sparkleMatrix(source, 2)];
  throw new RangeError(`Unknown PCG animation template: ${templateId}`);
}

function hasDistinctFrames(matrices) {
  return new Set(matrices.map((matrix) => matrix.map((row) => row.join("")).join("/"))).size > 1;
}

export function getPcgAnimationTemplate(id) {
  const template = TEMPLATE_BY_ID.get(id);
  if (!template) throw new RangeError(`Unknown PCG animation template: ${id}`);
  return template;
}

export function filterPcgAnimationTemplates(sourcePreset) {
  try {
    const source = assertSourcePreset(sourcePreset);
    const sourceMatrix = glyphsToMatrix(source.glyphs, source.width, source.height);
    return PCG_ANIMATION_TEMPLATES.filter(({ id }) => hasDistinctFrames(buildTemplateMatrices(id, sourceMatrix)));
  } catch {
    return [];
  }
}

export function createPcgAnimationFromTemplate(sourcePreset, templateId, { frameDurationMs = null } = {}) {
  const source = assertSourcePreset(sourcePreset);
  const template = getPcgAnimationTemplate(templateId);
  const duration = frameDurationMs === null ? template.frameDurationMs : frameDurationMs;
  if (!Number.isInteger(duration) || duration < 16 || duration > 60000) {
    throw new RangeError("Animation frame duration must be between 16 and 60000 ms");
  }
  const sourceMatrix = glyphsToMatrix(source.glyphs, source.width, source.height);
  const matrices = buildTemplateMatrices(template.id, sourceMatrix);
  if (!hasDistinctFrames(matrices)) {
    throw new RangeError("Animation template does not change the source preset");
  }
  const frames = matrices.map((matrix, index) => ({
    id: `frame-${index}`,
    name: `${template.name} ${index + 1}`,
    glyphs: matrixToGlyphs(matrix, source.width, source.height),
  }));
  return Object.freeze({
    id: `generated-animation-${source.id}-${template.id}`,
    kind: "animation",
    name: `${source.name} ${template.name}`,
    category: source.category,
    tags: Object.freeze([...new Set([...source.tags, "animation", "generated", template.id])]),
    width: source.width,
    height: source.height,
    glyphs: Object.freeze(frames[0].glyphs.map((glyph) => Object.freeze([...glyph]))),
    slotNames: Object.freeze([...source.slotNames]),
    frameDurationMs: duration,
    frames: Object.freeze(frames.map((frame) => Object.freeze({
      id: frame.id,
      name: frame.name,
      glyphs: Object.freeze(frame.glyphs.map((glyph) => Object.freeze([...glyph]))),
    }))),
  });
}
