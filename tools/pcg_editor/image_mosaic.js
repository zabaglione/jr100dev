import {
  DISPLAY_MODES,
  resolveScreenGlyph,
  SCREEN_HEIGHT,
  SCREEN_WIDTH,
} from "./core.js";

export const IMAGE_PIXEL_WIDTH = SCREEN_WIDTH * 8;
export const IMAGE_PIXEL_HEIGHT = SCREEN_HEIGHT * 8;

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
        ? codeRange(0x00, 0x9f)
        : codeRange(0x00, 0xff);
    case "rom":
      return codeRange(0x00, 0x7f);
    case "symbols":
      return codeRange(0x40, 0x7f);
    case "pcg":
      if (project.screen.mode !== DISPLAY_MODES.PCG) {
        throw new RangeError("PCG palette requires CMODE PCG");
      }
      return codeRange(0x80, 0x9f);
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

export function convertLuminanceToScreen(source, candidates, {
  contrast = 1,
  invert = false,
  threshold = 0.5,
  toneMode = "grayscale",
} = {}) {
  if (!source || source.length !== IMAGE_PIXEL_WIDTH * IMAGE_PIXEL_HEIGHT) {
    throw new TypeError("Image mosaic source must contain exactly 256x192 luminance values");
  }
  validateCandidates(candidates);
  if (!Number.isFinite(contrast) || contrast <= 0 || !Number.isFinite(threshold) || threshold < 0 || threshold > 1) {
    throw new RangeError("Image mosaic tone settings are outside their supported range");
  }
  if (!new Set(["grayscale", "threshold", "bayer"]).has(toneMode)) {
    throw new RangeError("Unknown image mosaic tone mode");
  }

  const luminance = prepareLuminance(source, { contrast, invert, threshold, toneMode });
  const cells = new Array(SCREEN_WIDTH * SCREEN_HEIGHT);
  let totalError = 0;

  for (let cellY = 0; cellY < SCREEN_HEIGHT; cellY += 1) {
    for (let cellX = 0; cellX < SCREEN_WIDTH; cellX += 1) {
      let bestCode = candidates[0].code;
      let bestError = Infinity;
      for (const candidate of candidates) {
        let error = 0;
        for (let row = 0; row < 8; row += 1) {
          const glyphRow = candidate.glyph[row];
          const sourceOffset = (cellY * 8 + row) * IMAGE_PIXEL_WIDTH + cellX * 8;
          for (let column = 0; column < 8; column += 1) {
            const pixel = (glyphRow >> (7 - column)) & 1;
            const difference = luminance[sourceOffset + column] - pixel;
            error += difference * difference;
          }
        }
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
