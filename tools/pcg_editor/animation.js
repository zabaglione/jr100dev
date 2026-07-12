const SLOT_COUNT = 32;
const GLYPH_SIZE = 8;

function validateByte(value) {
  return Number.isInteger(value) && value >= 0 && value <= 0xff;
}

function validateGlyph(glyph) {
  return Array.isArray(glyph) && glyph.length === GLYPH_SIZE && glyph.every(validateByte);
}

function assertGlyphBank(glyphs) {
  if (!Array.isArray(glyphs) || glyphs.length !== SLOT_COUNT || !glyphs.every(validateGlyph)) {
    throw new TypeError("Glyph bank must contain 32 eight-byte slots");
  }
}

function normalizeLabel(value, fallback = "ANIMATION") {
  const normalized = String(value || fallback)
    .toUpperCase()
    .replace(/[^A-Z0-9_]/g, "_")
    .replace(/^[^A-Z_]/, "_$&");
  return normalized || fallback;
}

function cloneGlyphs(glyphs) {
  return glyphs.map((glyph) => [...glyph]);
}

function residentGlyphs(clip, glyphBank) {
  assertGlyphBank(glyphBank);
  const count = clip.width * clip.height;
  return cloneGlyphs(glyphBank.slice(clip.baseSlot, clip.baseSlot + count));
}

function animationFrameAt(clip, frameIndex, { allowMissing = false } = {}) {
  validateAnimationClips([clip]);
  if (!Number.isInteger(frameIndex) || frameIndex < 0 || frameIndex >= clip.frames.length) {
    if (allowMissing) return null;
    throw new RangeError("Animation frame index is outside the clip");
  }
  return clip.frames[frameIndex];
}

export function createAnimationClip({
  id = "animation",
  name = "Animation",
  baseSlot = 0,
  width = 2,
  height = 2,
  frameDurationMs = 160,
} = {}) {
  const clip = { id, name, baseSlot, width, height, frameDurationMs, frames: [] };
  validateAnimationClips([clip]);
  return clip;
}

export function validateAnimationClips(clips) {
  if (!Array.isArray(clips)) {
    throw new TypeError("Project animations must be an array");
  }
  const ids = new Set();
  for (const clip of clips) {
    if (!clip || typeof clip !== "object") {
      throw new TypeError("Animation clip must be an object");
    }
    if (typeof clip.id !== "string" || !clip.id || ids.has(clip.id)) {
      throw new TypeError("Animation clip ids must be non-empty and unique");
    }
    ids.add(clip.id);
    if (typeof clip.name !== "string" || !clip.name.trim()) {
      throw new TypeError("Animation clip must have a name");
    }
    for (const value of [clip.baseSlot, clip.width, clip.height, clip.frameDurationMs]) {
      if (!Number.isInteger(value)) {
        throw new TypeError("Animation dimensions and duration must be integers");
      }
    }
    const slotCount = clip.width * clip.height;
    if (clip.baseSlot < 0 || clip.width < 1 || clip.height < 1 || clip.baseSlot + slotCount > SLOT_COUNT) {
      throw new RangeError("Animation resident slots must fit in the 32-slot PCG bank");
    }
    if (clip.frameDurationMs < 16 || clip.frameDurationMs > 60000) {
      throw new RangeError("Animation frame duration must be between 16 and 60000 ms");
    }
    if (!Array.isArray(clip.frames)) {
      throw new TypeError("Animation frames must be an array");
    }
    const frameIds = new Set();
    for (const frame of clip.frames) {
      if (!frame || typeof frame.id !== "string" || !frame.id || frameIds.has(frame.id)) {
        throw new TypeError("Animation frame ids must be non-empty and unique within a clip");
      }
      frameIds.add(frame.id);
      if (typeof frame.name !== "string" || !frame.name.trim()) {
        throw new TypeError("Animation frame must have a name");
      }
      if (!Array.isArray(frame.glyphs) || frame.glyphs.length !== slotCount || !frame.glyphs.every(validateGlyph)) {
        throw new TypeError("Animation frame glyph count must match its clip dimensions");
      }
    }
  }
  return clips;
}

export function captureAnimationFrame(clip, glyphBank, { id, name } = {}) {
  validateAnimationClips([clip]);
  const frameNumber = clip.frames.length;
  const frame = {
    id: id || `frame-${frameNumber}`,
    name: String(name || `FRAME_${frameNumber}`).trim(),
    glyphs: residentGlyphs(clip, glyphBank),
  };
  clip.frames.push(frame);
  validateAnimationClips([clip]);
  return frame;
}

export function replaceAnimationFrame(clip, frameIndex, glyphBank) {
  const frame = animationFrameAt(clip, frameIndex);
  frame.glyphs = residentGlyphs(clip, glyphBank);
  return frame;
}

export function applyAnimationFrame(clip, frameIndex, glyphBank) {
  const frame = animationFrameAt(clip, frameIndex);
  assertGlyphBank(glyphBank);
  frame.glyphs.forEach((glyph, offset) => {
    glyphBank[clip.baseSlot + offset] = [...glyph];
  });
  return glyphBank;
}

export function duplicateAnimationFrame(clip, frameIndex, { id, name } = {}) {
  const source = animationFrameAt(clip, frameIndex);
  const duplicate = {
    id: id || `${source.id}-copy-${clip.frames.length}`,
    name: String(name || `${source.name}_COPY`).trim(),
    glyphs: cloneGlyphs(source.glyphs),
  };
  clip.frames.splice(frameIndex + 1, 0, duplicate);
  validateAnimationClips([clip]);
  return duplicate;
}

export function removeAnimationFrame(clip, frameIndex) {
  if (!animationFrameAt(clip, frameIndex, { allowMissing: true })) return false;
  clip.frames.splice(frameIndex, 1);
  return true;
}

export function exportAnimationAssembly(clips, { label = "ANIMATION_DATA" } = {}) {
  validateAnimationClips(clips);
  const rootLabel = normalizeLabel(label, "ANIMATION_DATA");
  const lines = [];
  clips.forEach((clip, clipIndex) => {
    const clipNumber = clipIndex.toString().padStart(2, "0");
    const clipLabel = clips.length === 1
      ? rootLabel
      : `${rootLabel}_CLIP_${clipNumber}_${normalizeLabel(clip.name, "ANIMATION")}`;
    const slotCount = clip.width * clip.height;
    lines.push(`${clipLabel}_BASE_SLOT: .equ ${clip.baseSlot}`);
    lines.push(`${clipLabel}_WIDTH: .equ ${clip.width}`);
    lines.push(`${clipLabel}_HEIGHT: .equ ${clip.height}`);
    lines.push(`${clipLabel}_SLOT_COUNT: .equ ${slotCount}`);
    lines.push(`${clipLabel}_FRAME_BYTES: .equ ${slotCount * GLYPH_SIZE}`);
    lines.push(`${clipLabel}_FRAME_COUNT: .equ ${clip.frames.length}`);
    lines.push("");
    const frameLabels = clip.frames.map((frame, frameIndex) => {
      const frameNumber = frameIndex.toString().padStart(2, "0");
      const frameLabel = `${clipLabel}_FRAME_${frameNumber}_${normalizeLabel(frame.name, "FRAME")}`;
      lines.push(`${frameLabel}:`);
      frame.glyphs.forEach((glyph, glyphIndex) => {
        const values = glyph.map((value) => `$${value.toString(16).toUpperCase().padStart(2, "0")}`).join(", ");
        lines.push(`        .byte ${values} ; Glyph ${glyphIndex}`);
      });
      lines.push("");
      return frameLabel;
    });
    lines.push(`${clipLabel}_FRAME_POINTERS:`);
    if (frameLabels.length) {
      lines.push(`        .word ${frameLabels.join(", ")}`);
    }
    lines.push("");
  });
  return `${lines.join("\n").trimEnd()}\n`;
}
