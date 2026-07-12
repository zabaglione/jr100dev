import {
  DISPLAY_MODES,
  resolveScreenGlyph,
  SCREEN_HEIGHT,
  SCREEN_WIDTH,
} from "./core.js";

export const IMAGE_PIXEL_WIDTH = SCREEN_WIDTH * 8;
export const IMAGE_PIXEL_HEIGHT = SCREEN_HEIGHT * 8;
export const PCG_CODE_START = 0x80;
export const PCG_CODE_END = 0x9f;

const MAX_GENERATED_PCG = PCG_CODE_END - PCG_CODE_START + 1;
const TONE_MODES = new Set(["grayscale", "threshold", "bayer"]);

const BAYER_4X4 = [
  0, 8, 2, 10,
  12, 4, 14, 6,
  3, 11, 1, 9,
  15, 7, 13, 5,
];

function codeRange(start, end) {
  return Array.from({ length: end - start + 1 }, (_, index) => start + index);
}

function candidateCodes(project, palette) {
  switch (palette) {
    case "compatible":
      return project.screen.mode === DISPLAY_MODES.PCG
        ? codeRange(0x00, PCG_CODE_END)
        : codeRange(0x00, 0xff);
    case "rom":
      return codeRange(0x00, 0x7f);
    case "symbols":
      return codeRange(0x40, 0x7f);
    case "pcg":
      if (project.screen.mode !== DISPLAY_MODES.PCG) {
        throw new RangeError("PCG palette requires CMODE PCG");
      }
      return codeRange(PCG_CODE_START, PCG_CODE_END);
    default:
      throw new RangeError("Unknown image mosaic palette");
  }
}

export function buildGlyphCandidates(project, { palette = "compatible" } = {}) {
  return candidateCodes(project, palette).map((code) => ({
    code,
    glyph: [...resolveScreenGlyph(project, code)],
  }));
}

function clampUnit(value) {
  return Math.max(0, Math.min(1, value));
}

function rgbChannel(rgba, x, y, channel) {
  const clampedX = Math.max(0, Math.min(IMAGE_PIXEL_WIDTH - 1, x));
  const clampedY = Math.max(0, Math.min(IMAGE_PIXEL_HEIGHT - 1, y));
  return rgba[(clampedY * IMAGE_PIXEL_WIDTH + clampedX) * 4 + channel] / 255;
}

export function rgbaToEnhancedLuminance(rgba, { edgeStrength = 0 } = {}) {
  if (!rgba || rgba.length !== IMAGE_PIXEL_WIDTH * IMAGE_PIXEL_HEIGHT * 4) {
    throw new TypeError("Image mosaic RGBA source must contain exactly 256x192 pixels");
  }
  if (!Number.isFinite(edgeStrength) || edgeStrength < 0 || edgeStrength > 2) {
    throw new RangeError("Image mosaic edge strength must be between 0 and 2");
  }

  const luminance = new Float32Array(IMAGE_PIXEL_WIDTH * IMAGE_PIXEL_HEIGHT);
  for (let y = 0; y < IMAGE_PIXEL_HEIGHT; y += 1) {
    for (let x = 0; x < IMAGE_PIXEL_WIDTH; x += 1) {
      const index = y * IMAGE_PIXEL_WIDTH + x;
      const sourceIndex = index * 4;
      const base = (
        rgba[sourceIndex] * 0.2126
        + rgba[sourceIndex + 1] * 0.7152
        + rgba[sourceIndex + 2] * 0.0722
      ) / 255;
      if (edgeStrength === 0) {
        luminance[index] = base;
        continue;
      }

      let gradientSquared = 0;
      for (let channel = 0; channel < 3; channel += 1) {
        const topLeft = rgbChannel(rgba, x - 1, y - 1, channel);
        const top = rgbChannel(rgba, x, y - 1, channel);
        const topRight = rgbChannel(rgba, x + 1, y - 1, channel);
        const left = rgbChannel(rgba, x - 1, y, channel);
        const right = rgbChannel(rgba, x + 1, y, channel);
        const bottomLeft = rgbChannel(rgba, x - 1, y + 1, channel);
        const bottom = rgbChannel(rgba, x, y + 1, channel);
        const bottomRight = rgbChannel(rgba, x + 1, y + 1, channel);
        const gradientX = -topLeft + topRight - 2 * left + 2 * right - bottomLeft + bottomRight;
        const gradientY = -topLeft - 2 * top - topRight + bottomLeft + 2 * bottom + bottomRight;
        gradientSquared += gradientX * gradientX + gradientY * gradientY;
      }
      const colorEdge = clampUnit(Math.sqrt(gradientSquared) / (4 * Math.sqrt(3)));
      luminance[index] = clampUnit(base - colorEdge * edgeStrength);
    }
  }
  return luminance;
}

function prepareLuminance(source, { contrast, invert, threshold, toneMode }) {
  const prepared = new Float32Array(source.length);
  for (let index = 0; index < source.length; index += 1) {
    let value = clampUnit(Number(source[index]));
    if (invert) value = 1 - value;
    value = clampUnit((value - 0.5) * contrast + 0.5);
    if (toneMode === "threshold") {
      value = value >= threshold ? 1 : 0;
    } else if (toneMode === "bayer") {
      const x = index % IMAGE_PIXEL_WIDTH;
      const y = Math.floor(index / IMAGE_PIXEL_WIDTH);
      const bayer = BAYER_4X4[(y % 4) * 4 + (x % 4)];
      const localThreshold = threshold + (bayer / 15 - 0.5) * 0.35;
      value = value >= localThreshold ? 1 : 0;
    }
    prepared[index] = value;
  }
  return prepared;
}

function validateCandidates(candidates) {
  if (!Array.isArray(candidates) || candidates.length === 0) {
    throw new TypeError("Image mosaic requires at least one glyph candidate");
  }
  for (const candidate of candidates) {
    if (!Number.isInteger(candidate?.code) || candidate.code < 0 || candidate.code > 0xff) {
      throw new TypeError("Image mosaic candidate code must be a byte");
    }
    if (
      !Array.isArray(candidate.glyph)
      || candidate.glyph.length !== 8
      || !candidate.glyph.every((value) => Number.isInteger(value) && value >= 0 && value <= 0xff)
    ) {
      throw new TypeError("Image mosaic candidate glyph must contain eight byte values");
    }
  }
}

function validateConversionInputs(source, candidates, { contrast, threshold, toneMode }) {
  if (!source || source.length !== IMAGE_PIXEL_WIDTH * IMAGE_PIXEL_HEIGHT) {
    throw new TypeError("Image mosaic source must contain exactly 256x192 luminance values");
  }
  validateCandidates(candidates);
  if (!Number.isFinite(contrast) || contrast <= 0 || !Number.isFinite(threshold) || threshold < 0 || threshold > 1) {
    throw new RangeError("Image mosaic tone settings are outside their supported range");
  }
  if (!TONE_MODES.has(toneMode)) {
    throw new RangeError("Unknown image mosaic tone mode");
  }
}

function glyphErrorAt(luminance, cellX, cellY, glyph) {
  let error = 0;
  for (let row = 0; row < 8; row += 1) {
    const glyphRow = glyph[row];
    const sourceOffset = (cellY * 8 + row) * IMAGE_PIXEL_WIDTH + cellX * 8;
    for (let column = 0; column < 8; column += 1) {
      const pixel = (glyphRow >> (7 - column)) & 1;
      const difference = luminance[sourceOffset + column] - pixel;
      error += difference * difference;
    }
  }
  return error;
}

function matchPreparedLuminance(luminance, candidates) {
  const cells = new Array(SCREEN_WIDTH * SCREEN_HEIGHT);
  let totalError = 0;

  for (let cellY = 0; cellY < SCREEN_HEIGHT; cellY += 1) {
    for (let cellX = 0; cellX < SCREEN_WIDTH; cellX += 1) {
      let bestCode = candidates[0].code;
      let bestError = Infinity;
      for (const candidate of candidates) {
        const error = glyphErrorAt(luminance, cellX, cellY, candidate.glyph);
        if (error < bestError) {
          bestError = error;
          bestCode = candidate.code;
        }
      }
      cells[cellY * SCREEN_WIDTH + cellX] = bestCode;
      totalError += bestError;
    }
  }

  return {
    cells,
    meanError: totalError / (cells.length * 64),
  };
}

function glyphFromCell(luminance, cellX, cellY, threshold) {
  return Array.from({ length: 8 }, (_, row) => {
    const sourceOffset = (cellY * 8 + row) * IMAGE_PIXEL_WIDTH + cellX * 8;
    let byte = 0;
    for (let column = 0; column < 8; column += 1) {
      if (luminance[sourceOffset + column] >= threshold) {
        byte |= 1 << (7 - column);
      }
    }
    return byte;
  });
}

export function convertLuminanceToScreen(source, candidates, {
  contrast = 1,
  invert = false,
  threshold = 0.5,
  toneMode = "grayscale",
} = {}) {
  validateConversionInputs(source, candidates, { contrast, threshold, toneMode });
  const luminance = prepareLuminance(source, { contrast, invert, threshold, toneMode });
  return { ...matchPreparedLuminance(luminance, candidates), kind: "screen" };
}

export function generatePcgMosaic(source, baseCandidates, {
  contrast = 1,
  invert = false,
  threshold = 0.5,
  toneMode = "grayscale",
} = {}) {
  validateConversionInputs(source, baseCandidates, { contrast, threshold, toneMode });
  const candidates = baseCandidates.filter(({ code }) => code < PCG_CODE_START || code > PCG_CODE_END);
  if (candidates.length === 0) {
    throw new RangeError("Automatic PCG generation requires at least one non-PCG candidate");
  }
  const luminance = prepareLuminance(source, { contrast, invert, threshold, toneMode });
  const patterns = new Map();
  for (let cellY = 0; cellY < SCREEN_HEIGHT; cellY += 1) {
    for (let cellX = 0; cellX < SCREEN_WIDTH; cellX += 1) {
      const glyph = glyphFromCell(luminance, cellX, cellY, threshold);
      const targetError = glyphErrorAt(luminance, cellX, cellY, glyph);
      let baseError = Infinity;
      for (const candidate of candidates) {
        baseError = Math.min(baseError, glyphErrorAt(luminance, cellX, cellY, candidate.glyph));
      }
      const benefit = baseError - targetError;
      if (benefit <= Number.EPSILON) continue;
      const key = glyph.join(",");
      const pattern = patterns.get(key) ?? { glyph, benefit: 0, uses: 0, key };
      pattern.benefit += benefit;
      pattern.uses += 1;
      patterns.set(key, pattern);
    }
  }

  const glyphs = [...patterns.values()]
    .sort((left, right) => right.benefit - left.benefit || right.uses - left.uses || left.key.localeCompare(right.key))
    .slice(0, MAX_GENERATED_PCG)
    .map(({ glyph }) => glyph);
  const generatedCandidates = glyphs.map((glyph, slot) => ({ code: PCG_CODE_START + slot, glyph }));
  const result = matchPreparedLuminance(luminance, [...candidates, ...generatedCandidates]);
  return { ...result, glyphs, kind: "screen-pcg" };
}

export function applyImageMosaicResult(project, result) {
  if (
    !Array.isArray(result?.cells)
    || result.cells.length !== SCREEN_WIDTH * SCREEN_HEIGHT
    || !result.cells.every((code) => Number.isInteger(code) && code >= 0 && code <= 0xff)
  ) {
    throw new TypeError("Image mosaic result must contain 768 screen bytes");
  }
  const replacesPcg = result.kind === "screen-pcg";
  if (replacesPcg) {
    if (project?.screen?.mode !== DISPLAY_MODES.PCG) {
      throw new RangeError("Automatic PCG data requires CMODE PCG");
    }
    if (!Array.isArray(result.glyphs) || result.glyphs.length > MAX_GENERATED_PCG) {
      throw new TypeError("Image mosaic result must contain no more than 32 PCG glyphs");
    }
    if (result.glyphs.length > 0) {
      validateCandidates(result.glyphs.map((glyph, slot) => ({ code: PCG_CODE_START + slot, glyph })));
    }
  }

  project.screen.cells = [...result.cells];
  if (replacesPcg) {
    const generatedCount = result.glyphs.length;
    result.glyphs.forEach((glyph, slot) => {
      project.glyphs[slot] = [...glyph];
      project.names[slot] = `Image PCG ${String(slot).padStart(2, "0")}`;
    });
    project.groups = project.groups.filter(({ baseSlot }) => baseSlot >= generatedCount);
    project.animations = project.animations.filter(({ baseSlot }) => baseSlot >= generatedCount);
  }
  return replacesPcg;
}
