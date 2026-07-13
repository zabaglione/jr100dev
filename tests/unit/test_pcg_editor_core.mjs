import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

import {
  ARCADE_DIGITS,
  applyArcadeDigits,
  applyPcgAnimationPreset,
  applyPcgPreset,
  asciiToRomCode,
  assertWorkspace,
  bresenhamPoints,
  constrainEndpoint,
  createScreen,
  createProject,
  DISPLAY_MODES,
  exportAssembly,
  exportCombinedAssembly,
  exportScreenAssembly,
  getPixel,
  inspectPcgAnimationPresetConflicts,
  inspectPcgPresetConflicts,
  parseProject,
  resolveScreenGlyph,
  removeGroup,
  serializeProject,
  setPixel,
  setScreenCell,
  setScreenMode,
  setVramPcgPixel,
  shiftWorkspace,
  upsertGroup,
  visiblePcgSlots,
  vramPcgSourceOffset,
} from "../../tools/pcg_editor/core.js";
import {
  PCG_PRESET_CATEGORY_OPTIONS,
  PCG_PRESET_CATEGORIES,
  PCG_PRESETS,
  filterPcgPresets,
  getPcgPreset,
} from "../../tools/pcg_editor/preset_library.js";
import { extractCharacterRom } from "../../tools/pcg_editor/rom_font.js";
import en from "../../tools/pcg_editor/locales/en.js";
import ja from "../../tools/pcg_editor/locales/ja.js";
import { getLanguage, resolveStoredLanguage, setLanguage, t } from "../../tools/pcg_editor/i18n.js";
import { createFrameScheduler } from "../../tools/pcg_editor/frame_scheduler.js";
import {
  applyAnimationFrame,
  captureAnimationFrame,
  createAnimationClip,
  exportAnimationAssembly,
  replaceAnimationFrame,
  validateAnimationClips,
} from "../../tools/pcg_editor/animation.js";
import {
  PCG_ANIMATION_TEMPLATES,
  createPcgAnimationFromTemplate,
  filterPcgAnimationTemplates,
  getPcgAnimationTemplate,
} from "../../tools/pcg_editor/animation_templates.js";
import {
  applyImageMosaicResult,
  buildGlyphCandidates,
  convertLuminanceToScreen,
  generatePcgMosaic,
  IMAGE_PIXEL_HEIGHT,
  IMAGE_PIXEL_WIDTH,
  rgbaToEnhancedLuminance,
} from "../../tools/pcg_editor/image_mosaic.js";

const editorHtml = await readFile(new URL("../../tools/pcg_editor/index.html", import.meta.url), "utf8");
const editorStyles = await readFile(new URL("../../tools/pcg_editor/styles.css", import.meta.url), "utf8");
const editorApp = await readFile(new URL("../../tools/pcg_editor/app.js", import.meta.url), "utf8");

test("UI defaults to Japanese and exposes an English language switch", () => {
  assert.match(editorHtml, /<html lang="ja">/);
  assert.match(editorHtml, /id="language-select"/);
  assert.match(editorHtml, /<option value="ja" selected[^>]*>/);
  assert.match(editorHtml, /<option value="en"[^>]*>/);
});

test("Japanese and English resources expose the same UI keys", () => {
  assert.deepEqual(Object.keys(ja).sort(), Object.keys(en).sort());
  const referencedKeys = [...editorHtml.matchAll(/data-i18n(?:-title|-placeholder|-aria)?="([^"]+)"/g)]
    .map((match) => match[1]);
  referencedKeys.push(...[...editorApp.matchAll(/\bt\("([^"]+)"/g)].map((match) => match[1]));
  assert.ok(referencedKeys.every((key) => Object.hasOwn(ja, key)), "Every HTML translation key must exist");

  assert.equal(getLanguage(), "ja");
  assert.equal(t("actions.new"), "新規");
  setLanguage("en");
  assert.equal(t("actions.new"), "New");
  setLanguage("ja");
});

test("saved language is restored and invalid values fall back to Japanese", () => {
  assert.equal(resolveStoredLanguage({ getItem: () => "en" }), "en");
  assert.equal(resolveStoredLanguage({ getItem: () => "unsupported" }), "ja");
  assert.equal(resolveStoredLanguage({ getItem: () => { throw new Error("blocked"); } }), "ja");
});

test("VRAM-backed glyph source highlighting is optional and explained", () => {
  assert.match(editorHtml, /id="show-vram-source"/);
  assert.match(editorHtml, /class="source-highlight-legend"/);
  assert.doesNotMatch(editorHtml, /id="show-vram-source"[^>]*checked/);
});

test("symbol and semigraphic codes share one palette filter", () => {
  assert.match(editorHtml, /<option value="symbolsAndSemigraphics"[^>]*data-i18n="crt\.symbolAndSemigraphicCodes"/);
  assert.doesNotMatch(editorHtml, /<option value="semigraphics"/);
  assert.match(ja["crt.symbolAndSemigraphicCodes"], /\$40-\$7F/);
  assert.match(en["crt.symbolAndSemigraphicCodes"], /\$40-\$7F/);
});

test("a project always contains 32 eight-byte glyphs", () => {
  const project = createProject();

  assert.equal(project.glyphs.length, 32);
  assert.ok(project.glyphs.every((glyph) => glyph.length === 8));
  assert.ok(project.glyphs.flat().every((value) => value === 0));
  assert.deepEqual(project.animations, []);
});

test("a 2x2 animation keeps any number of frames outside its four resident slots", () => {
  const project = createProject();
  const clip = createAnimationClip({
    id: "player",
    name: "Player",
    baseSlot: 12,
    width: 2,
    height: 2,
    frameDurationMs: 120,
  });

  for (let frame = 0; frame < 8; frame += 1) {
    for (let slot = 12; slot < 16; slot += 1) {
      project.glyphs[slot] = Array(8).fill(frame * 4 + slot - 12);
    }
    captureAnimationFrame(clip, project.glyphs, {
      id: `frame-${frame}`,
      name: `Frame ${frame}`,
    });
  }

  assert.equal(clip.frames.length, 8);
  assert.equal(clip.frames[0].glyphs.length, 4);
  assert.equal(clip.frames[0].glyphs.flat().length, 32);
  assert.equal(clip.baseSlot, 12);
  assert.equal(clip.width * clip.height, 4);
  validateAnimationClips([clip]);
});

test("animation frames can replace and restore only the resident PCG range", () => {
  const project = createProject();
  const clip = createAnimationClip({ id: "player", name: "Player", baseSlot: 4, width: 2, height: 2 });
  project.glyphs[3] = Array(8).fill(0x33);
  project.glyphs[8] = Array(8).fill(0x88);
  for (let slot = 4; slot < 8; slot += 1) {
    project.glyphs[slot] = Array(8).fill(slot);
  }
  captureAnimationFrame(clip, project.glyphs, { id: "left-0", name: "LEFT_0" });

  for (let slot = 4; slot < 8; slot += 1) {
    project.glyphs[slot] = Array(8).fill(0xa0 + slot);
  }
  replaceAnimationFrame(clip, 0, project.glyphs);
  project.glyphs.slice(4, 8).forEach((glyph) => glyph.fill(0));
  applyAnimationFrame(clip, 0, project.glyphs);

  assert.deepEqual(project.glyphs[3], Array(8).fill(0x33));
  assert.deepEqual(project.glyphs[4], Array(8).fill(0xa4));
  assert.deepEqual(project.glyphs[7], Array(8).fill(0xa7));
  assert.deepEqual(project.glyphs[8], Array(8).fill(0x88));
});

test("animation assembly exports fixed-size frame data and pointer metadata", () => {
  const project = createProject();
  const clip = createAnimationClip({ id: "player", name: "Player", baseSlot: 0, width: 2, height: 2 });
  captureAnimationFrame(clip, project.glyphs, { id: "left-0", name: "LEFT_0" });
  project.glyphs[0][0] = 0x80;
  captureAnimationFrame(clip, project.glyphs, { id: "left-1", name: "LEFT_1" });

  const assembly = exportAnimationAssembly([clip], { label: "PLAYER_ANIMATION" });

  assert.match(assembly, /PLAYER_ANIMATION_SLOT_COUNT: \.equ 4/);
  assert.match(assembly, /PLAYER_ANIMATION_FRAME_BYTES: \.equ 32/);
  assert.match(assembly, /PLAYER_ANIMATION_FRAME_00_LEFT_0:/);
  assert.match(assembly, /PLAYER_ANIMATION_FRAME_01_LEFT_1:/);
  assert.match(assembly, /PLAYER_ANIMATION_FRAME_POINTERS:/);
  assert.match(assembly, /\.word PLAYER_ANIMATION_FRAME_00_LEFT_0, PLAYER_ANIMATION_FRAME_01_LEFT_1/);
  assert.equal((assembly.match(/\.byte/g) ?? []).length, 8);
  assert.doesNotMatch(assembly, /[\u3040-\u30ff\u3400-\u9fff]/u);
});

test("animation assembly labels stay unique when clip and frame names repeat", () => {
  const project = createProject();
  const first = createAnimationClip({ id: "first", name: "Player", width: 1, height: 1 });
  const second = createAnimationClip({ id: "second", name: "Player", width: 1, height: 1 });
  captureAnimationFrame(first, project.glyphs, { id: "a", name: "IDLE" });
  captureAnimationFrame(first, project.glyphs, { id: "b", name: "IDLE" });
  captureAnimationFrame(second, project.glyphs, { id: "c", name: "IDLE" });

  const assembly = exportAnimationAssembly([first, second], { label: "ANIM" });
  const labels = [...assembly.matchAll(/^([A-Z0-9_]+):/gm)].map((match) => match[1]);

  assert.equal(new Set(labels).size, labels.length);
  assert.match(assembly, /ANIM_CLIP_00_PLAYER_FRAME_00_IDLE:/);
  assert.match(assembly, /ANIM_CLIP_00_PLAYER_FRAME_01_IDLE:/);
  assert.match(assembly, /ANIM_CLIP_01_PLAYER_FRAME_00_IDLE:/);
});

test("animation clips survive project JSON round trips and old projects migrate", () => {
  const project = createProject();
  const clip = createAnimationClip({ id: "player", name: "Player", baseSlot: 0, width: 2, height: 2 });
  captureAnimationFrame(clip, project.glyphs, { id: "down-0", name: "DOWN_0" });
  project.animations.push(clip);

  assert.deepEqual(parseProject(serializeProject(project)).animations, [clip]);

  const legacy = JSON.parse(serializeProject(project));
  delete legacy.animations;
  legacy.version = 2;
  assert.deepEqual(parseProject(JSON.stringify(legacy)).animations, []);
});

test("animation view exposes clip, frame, playback, and resident-slot controls", () => {
  assert.match(editorHtml, /id="show-animation-view"/);
  assert.match(editorHtml, /id="animation-workbench"/);
  assert.match(editorHtml, /id="animation-base-slot"/);
  assert.match(editorHtml, /id="capture-animation-frame"/);
  assert.match(editorHtml, /id="update-animation-frame"/);
  assert.match(editorHtml, /id="play-animation"/);
  assert.match(editorHtml, /id="animation-frame-list"/);
});

test("image mosaic candidate ranges follow JR-100 display compatibility", () => {
  const project = createProject();

  assert.deepEqual(buildGlyphCandidates(project, { palette: "rom" }).map(({ code }) => code),
    Array.from({ length: 128 }, (_, code) => code));
  assert.deepEqual(buildGlyphCandidates(project, { palette: "symbols" }).map(({ code }) => code),
    Array.from({ length: 64 }, (_, index) => 0x40 + index));
  assert.deepEqual(buildGlyphCandidates(project, { palette: "pcg" }).map(({ code }) => code),
    Array.from({ length: 32 }, (_, index) => 0x80 + index));
  assert.equal(buildGlyphCandidates(project, { palette: "compatible" }).length, 160);

  setScreenMode(project.screen, DISPLAY_MODES.INVERSE);
  assert.equal(buildGlyphCandidates(project, { palette: "compatible" }).length, 256);
  assert.throws(() => buildGlyphCandidates(project, { palette: "pcg" }), /PCG palette/);
});

test("image mosaic recovers an exact 8x8 glyph from a 256x192 luminance image", () => {
  const project = createProject();
  project.romGlyphs[0] = Array(8).fill(0);
  project.romGlyphs[1] = [0x18, 0x3c, 0x7e, 0xdb, 0xff, 0x24, 0x24, 0x00];
  const luminance = new Float32Array(IMAGE_PIXEL_WIDTH * IMAGE_PIXEL_HEIGHT);
  project.romGlyphs[1].forEach((byte, y) => {
    for (let x = 0; x < 8; x += 1) {
      luminance[y * IMAGE_PIXEL_WIDTH + x] = (byte >> (7 - x)) & 1;
    }
  });

  const result = convertLuminanceToScreen(
    luminance,
    buildGlyphCandidates(project, { palette: "rom" }),
  );

  assert.equal(result.cells.length, 32 * 24);
  assert.equal(result.cells[0], 1);
  assert.ok(result.cells.slice(1).every((code) => code === 0));
  assert.equal(result.meanError, 0);
});

test("image mosaic supports inversion, thresholding, and ordered dithering", () => {
  const project = createProject();
  project.romGlyphs[0] = Array(8).fill(0);
  project.romGlyphs[1] = Array(8).fill(0xff);
  project.romGlyphs[2] = [0xaa, 0x55, 0xaa, 0x55, 0xaa, 0x55, 0xaa, 0x55];
  const candidates = buildGlyphCandidates(project, { palette: "rom" }).slice(0, 3);
  const white = new Float32Array(IMAGE_PIXEL_WIDTH * IMAGE_PIXEL_HEIGHT).fill(1);
  const gray = new Float32Array(IMAGE_PIXEL_WIDTH * IMAGE_PIXEL_HEIGHT).fill(0.5);

  assert.ok(convertLuminanceToScreen(white, candidates).cells.every((code) => code === 1));
  assert.ok(convertLuminanceToScreen(white, candidates, { invert: true }).cells.every((code) => code === 0));
  assert.equal(convertLuminanceToScreen(gray, candidates, { toneMode: "threshold", threshold: 0.6 }).cells[0], 0);
  assert.ok(convertLuminanceToScreen(gray, candidates, { toneMode: "bayer", threshold: 0.5 }).cells
    .every((code) => code === 2));
  assert.throws(
    () => convertLuminanceToScreen(gray, [{ code: 0, glyph: [0, 0, 0, 0, 0, 0, 0, "bad"] }]),
    /eight byte values/,
  );
});

test("image mosaic edge enhancement detects equal-luminance color boundaries", () => {
  const rgba = new Uint8ClampedArray(IMAGE_PIXEL_WIDTH * IMAGE_PIXEL_HEIGHT * 4);
  for (let y = 0; y < IMAGE_PIXEL_HEIGHT; y += 1) {
    for (let x = 0; x < IMAGE_PIXEL_WIDTH; x += 1) {
      const offset = (y * IMAGE_PIXEL_WIDTH + x) * 4;
      if (x < IMAGE_PIXEL_WIDTH / 2) {
        rgba[offset] = 255;
      } else {
        rgba[offset + 1] = 76;
      }
      rgba[offset + 3] = 255;
    }
  }

  const plain = rgbaToEnhancedLuminance(rgba, { edgeStrength: 0 });
  const enhanced = rgbaToEnhancedLuminance(rgba, { edgeStrength: 1 });
  const row = Math.floor(IMAGE_PIXEL_HEIGHT / 2) * IMAGE_PIXEL_WIDTH;

  assert.ok(Math.abs(plain[row + 32] - plain[row + 224]) < 0.01);
  assert.equal(enhanced[row + 32], plain[row + 32]);
  assert.ok(enhanced[row + 127] < plain[row + 127]);
  assert.ok(enhanced[row + 128] < plain[row + 128]);
});

test("image mosaic generates PCG glyphs for residual 8x8 patterns", () => {
  const luminance = new Float32Array(IMAGE_PIXEL_WIDTH * IMAGE_PIXEL_HEIGHT);
  const diagonal = [0x80, 0x40, 0x20, 0x10, 0x08, 0x04, 0x02, 0x01];
  diagonal.forEach((byte, y) => {
    for (let x = 0; x < 8; x += 1) {
      luminance[y * IMAGE_PIXEL_WIDTH + x] = (byte >> (7 - x)) & 1;
    }
  });

  const result = generatePcgMosaic(
    luminance,
    [{ code: 0x00, glyph: Array(8).fill(0) }],
    { toneMode: "threshold", threshold: 0.5 },
  );

  assert.deepEqual(result.glyphs, [diagonal]);
  assert.equal(result.cells[0], 0x80);
  assert.ok(result.cells.slice(1).every((code) => code === 0x00));
  assert.equal(result.meanError, 0);
});

test("image mosaic limits generated PCG data to 32 glyphs", () => {
  const luminance = new Float32Array(IMAGE_PIXEL_WIDTH * IMAGE_PIXEL_HEIGHT);
  for (let cell = 0; cell < 40; cell += 1) {
    const pixel = cell;
    const x = (cell % 32) * 8 + (pixel % 8);
    const y = Math.floor(cell / 32) * 8 + Math.floor(pixel / 8);
    luminance[y * IMAGE_PIXEL_WIDTH + x] = 1;
  }

  const result = generatePcgMosaic(
    luminance,
    [{ code: 0x00, glyph: Array(8).fill(0) }],
    { toneMode: "threshold", threshold: 0.5 },
  );

  assert.equal(result.glyphs.length, 32);
  assert.ok(result.cells.every((code) => code === 0x00 || (code >= 0x80 && code <= 0x9f)));
});

test("image mosaic applies generated screen and PCG data as one project result", () => {
  const project = createProject();
  project.glyphs.forEach((glyph) => glyph.fill(0xff));
  project.names[0] = "Old image slot";
  project.names[1] = "Preserved slot";
  project.groups = [
    { id: "overlap", name: "Overlap", baseSlot: 0, width: 1, height: 1 },
    { id: "preserved", name: "Preserved", baseSlot: 1, width: 1, height: 1 },
  ];
  project.animations = [
    createAnimationClip({ id: "overlap-animation", name: "Overlap", baseSlot: 0 }),
    createAnimationClip({ id: "preserved-animation", name: "Preserved", baseSlot: 1 }),
  ];
  const diagonal = [0x80, 0x40, 0x20, 0x10, 0x08, 0x04, 0x02, 0x01];
  const cells = Array(32 * 24).fill(0x80);

  const pcgResult = { cells, glyphs: [diagonal], kind: "screen-pcg" };
  const replacedPcg = applyImageMosaicResult(project, pcgResult);

  assert.equal(replacedPcg, true);
  assert.deepEqual(project.screen.cells, cells);
  assert.deepEqual(project.glyphs[0], diagonal);
  assert.deepEqual(project.glyphs[1], Array(8).fill(0xff));
  assert.equal(project.names[0], "Image PCG 00");
  assert.equal(project.names[1], "Preserved slot");
  assert.deepEqual(project.groups.map(({ id }) => id), ["preserved"]);
  assert.deepEqual(project.animations.map(({ id }) => id), ["preserved-animation"]);
  setScreenMode(project.screen, DISPLAY_MODES.INVERSE);
  assert.throws(() => applyImageMosaicResult(project, pcgResult), /CMODE PCG/);
});

test("CRT editor exposes the experimental image mosaic workflow", () => {
  assert.match(editorHtml, /id="open-image-mosaic"/);
  assert.match(editorHtml, /id="image-mosaic-dialog"/);
  assert.match(editorHtml, /id="image-mosaic-file"/);
  assert.doesNotMatch(editorHtml, /id="generate-image-mosaic"/);
  assert.match(editorHtml, /id="apply-image-mosaic"/);
  assert.match(editorHtml, /id="image-mosaic-edge-strength"/);
  assert.match(editorHtml, /id="image-mosaic-generate-pcg"/);
  assert.match(editorHtml, /id="image-mosaic-pcg-mode-help"/);
  assert.match(editorHtml, /data-i18n="imageMosaic\.experimental"/);
  assert.match(editorApp, /typeof globalThis\.createImageBitmap === "function"/);
  assert.match(editorApp, /new Image\(\)/);
  assert.match(editorApp, /imageMosaicLoadGeneration/);
  assert.match(editorApp, /scheduleImageMosaicGeneration/);
  assert.ok((editorApp.match(/scheduleImageMosaicGeneration\(\)/g) ?? []).length >= 4);
  assert.match(editorApp, /imageMosaicPreview = null;\s+document\.querySelector\("#apply-image-mosaic"\)\.disabled = true;/);
  assert.match(editorApp, /imageMosaicGenerationScheduler\.cancel\(\)/);
  assert.match(editorApp, /#image-mosaic-palette, #image-mosaic-tone, #image-mosaic-contrast, #image-mosaic-threshold, #image-mosaic-invert, #image-mosaic-generate-pcg/);
  assert.match(editorApp, /document\.querySelector\("dialog\[open\]"\)/);
});

test("image mosaic preview scheduler coalesces continuous input into the next frame", () => {
  let callback = null;
  let requested = 0;
  let canceled = 0;
  let generated = 0;
  const scheduler = createFrameScheduler({
    requestFrame: (next) => {
      callback = next;
      requested += 1;
      return requested;
    },
    cancelFrame: () => {
      canceled += 1;
    },
    task: () => {
      generated += 1;
    },
  });

  assert.equal(scheduler.schedule(), true);
  assert.equal(scheduler.schedule(), false);
  assert.equal(scheduler.schedule(), false);
  assert.equal(requested, 1);
  assert.equal(canceled, 0);
  assert.equal(scheduler.isPending(), true);

  callback();
  assert.equal(generated, 1);
  assert.equal(scheduler.isPending(), false);
  assert.equal(scheduler.schedule(), true);
  assert.equal(scheduler.cancel(), true);
  assert.equal(canceled, 1);
  assert.equal(scheduler.isPending(), false);
});

test("composite coordinates map across 8x8 slot boundaries", () => {
  const project = createProject({ withPreset: false });
  const workspace = { baseSlot: 0, width: 2, height: 2 };

  setPixel(project.glyphs, workspace, 7, 7, 1);
  setPixel(project.glyphs, workspace, 8, 7, 1);
  setPixel(project.glyphs, workspace, 7, 8, 1);
  setPixel(project.glyphs, workspace, 8, 8, 1);

  assert.equal(project.glyphs[0][7], 0x01);
  assert.equal(project.glyphs[1][7], 0x80);
  assert.equal(project.glyphs[2][0], 0x01);
  assert.equal(project.glyphs[3][0], 0x80);
  assert.equal(getPixel(project.glyphs, workspace, 8, 8), 1);
});

test("the full 8x4 bank maps its last pixel to slot 31", () => {
  const project = createProject();
  const workspace = { baseSlot: 0, width: 8, height: 4 };

  setPixel(project.glyphs, workspace, 63, 31, 1);

  assert.equal(project.glyphs[31][7], 0x01);
});

test("a workspace cannot run past the 32 PCG slots", () => {
  assert.throws(
    () => assertWorkspace({ baseSlot: 28, width: 3, height: 2 }),
    /32 slots/,
  );
});

test("line interpolation covers every cell between pointer samples", () => {
  assert.deepEqual(bresenhamPoints(0, 0, 4, 2), [
    [0, 0],
    [1, 1],
    [2, 1],
    [3, 2],
    [4, 2],
  ]);
});

test("shape constraints snap lines and rectangles without leaving the workspace", () => {
  assert.deepEqual(constrainEndpoint({ x: 2, y: 2 }, { x: 7, y: 3 }, "line", { width: 8, height: 8 }), { x: 7, y: 2 });
  assert.deepEqual(constrainEndpoint({ x: 2, y: 2 }, { x: 4, y: 7 }, "line", { width: 8, height: 8 }), { x: 2, y: 7 });
  assert.deepEqual(constrainEndpoint({ x: 2, y: 2 }, { x: 5, y: 6 }, "rectangle", { width: 8, height: 8 }), { x: 6, y: 6 });
  assert.deepEqual(constrainEndpoint({ x: 6, y: 6 }, { x: 7, y: 2 }, "rectangle", { width: 8, height: 8 }), { x: 7, y: 5 });
});

test("desktop layout keeps the editor in one viewport and compacts all 32 slots", () => {
  assert.match(editorStyles, /height: calc\(100vh - 54px\)/);
  assert.match(editorStyles, /grid-template-columns: repeat\(8, minmax\(0, 1fr\)\)/);
  assert.match(editorStyles, /overflow: auto/);
  assert.match(editorStyles, /@media \(max-width: 1180px\)/);
  assert.match(editorHtml, /<details class="group-disclosure">/);
  assert.match(editorHtml, /id="show-grid"/);
});

test("PCG library exposes searchable presets and a guarded replacement flow", () => {
  assert.match(editorHtml, /id="open-pcg-library"/);
  assert.match(editorHtml, /ready-to-place sets, and animation loops/);
  assert.match(editorHtml, /id="pcg-library-dialog"/);
  assert.match(editorHtml, /id="pcg-library-search"/);
  assert.match(editorHtml, /id="pcg-library-category"/);
  assert.match(editorHtml, /id="pcg-library-size"/);
  assert.match(editorHtml, /id="pcg-library-kind"/);
  assert.match(editorHtml, /<option value="animation">Animation<\/option>/);
  assert.match(editorHtml, /id="pcg-library-generate-animation"/);
  assert.match(editorHtml, /<dialog id="pcg-animation-builder-dialog"[^>]*aria-labelledby="pcg-animation-builder-title"/);
  assert.match(editorHtml, /id="pcg-animation-template"/);
  assert.match(editorHtml, /id="generate-pcg-library-animation"/);
  assert.match(editorHtml, /id="pcg-library-gallery"/);
  assert.match(editorHtml, /id="pcg-library-start-slot"/);
  assert.match(editorHtml, /id="pcg-library-apply"/);
  assert.match(editorHtml, /id="pcg-library-conflict-dialog"/);
  assert.match(editorHtml, /id="confirm-pcg-library-replace"/);
  assert.match(editorHtml, /id="pcg-library-start-slot"[^>]*step="1"/);
  assert.match(editorApp, /PCG_PRESET_CATEGORY_OPTIONS/);
  assert.match(editorApp, /function populatePcgLibraryCategoryOptions/);
  assert.match(editorApp, /function renderPcgLibrary/);
  assert.match(editorApp, /inspectPcgPresetConflicts/);
  assert.match(editorApp, /inspectPcgAnimationPresetConflicts/);
  assert.match(editorApp, /applyPcgAnimationPreset/);
  assert.match(editorApp, /setActiveView\("animation"\)/);
  assert.match(editorApp, /createPcgAnimationFromTemplate/);
  assert.match(editorApp, /filterPcgAnimationTemplates/);
  assert.match(editorApp, /stopPcgAnimationBuilderPreview/);
  assert.match(editorApp, /preset\.category.*preset\.kind\.toUpperCase\(\)/);
  assert.match(editorApp, /tags\.textContent = preset\.tags\.join/);
  assert.match(editorApp, /function pcgPresetConflictSummary/);
  assert.match(editorStyles, /\.pcg-library-dialog/);
});

test("CRT screen model can display every PCG slot", () => {
  const screen = createScreen({ mode: "pcg" });
  for (let slot = 0; slot < 32; slot += 1) {
    setScreenCell(screen, slot, 0, 0x80 + slot);
  }

  assert.deepEqual(visiblePcgSlots(screen), Array.from({ length: 32 }, (_, slot) => slot));
});

test("screen codes resolve through the selected CMODE", () => {
  const project = createProject();
  project.romGlyphs[0] = [0x00, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40];
  project.glyphs[0] = [0x80, 0x40, 0x20, 0x10, 0x08, 0x04, 0x02, 0x01];
  project.glyphs[9] = Array(8).fill(0x99);

  assert.deepEqual(resolveScreenGlyph(project, 0x00), project.romGlyphs[0]);
  assert.deepEqual(resolveScreenGlyph(project, 0x80), project.glyphs[0]);
  assert.deepEqual(resolveScreenGlyph(project, 0x89), project.glyphs[9]);

  setScreenMode(project.screen, DISPLAY_MODES.INVERSE);
  assert.deepEqual(resolveScreenGlyph(project, 0x80), project.romGlyphs[0].map((byte) => byte ^ 0xff));
});

test("VRAM-backed PCG edits the eight screen bytes that define its glyph", () => {
  const project = createProject();
  const code = 0xa9;
  const offset = vramPcgSourceOffset(code);

  setVramPcgPixel(project.screen, code, 0, 0, 1);
  setVramPcgPixel(project.screen, code, 7, 7, 1);

  assert.equal(project.screen.cells[offset], 0x80);
  assert.equal(project.screen.cells[offset + 7], 0x01);
  assert.deepEqual(resolveScreenGlyph(project, code), [0x80, 0, 0, 0, 0, 0, 0, 0x01]);
});

test("all 256 VRAM codes are exposed by the CRT editor", () => {
  assert.match(editorHtml, /All codes \$00-\$FF/);
  assert.match(editorHtml, /id="screen-canvas"/);
  assert.match(editorHtml, /Normal \+ inverse \(CMODE inverse\)/);
  assert.match(editorHtml, /ROM \+ PCG \(CMODE PCG\)/);
});

test("screen and combined assembly exports include all 768 VRAM bytes", () => {
  const project = createProject();
  const screenAssembly = exportScreenAssembly(project);
  const combined = exportCombinedAssembly(project);

  assert.equal((screenAssembly.match(/\.byte/g) ?? []).length, 48);
  assert.match(screenAssembly, /SCREEN_DATA_MODE: \.equ 1/);
  assert.match(combined, /^PCG_DATA:/);
  assert.match(combined, /SCREEN_DATA:/);
  assert.doesNotMatch(combined, /[\u3040-\u30ff\u3400-\u9fff]/u);
});

test("ASCII text input maps to the ROM text code range", () => {
  assert.equal(asciiToRomCode(" "), 0x00);
  assert.equal(asciiToRomCode("0"), 0x10);
  assert.equal(asciiToRomCode("A"), 0x21);
  assert.equal(asciiToRomCode("z"), 0x3a);
});

test("character ROM import supports raw bytes and version 2 PROG sections", () => {
  const raw = Uint8Array.from({ length: 1024 }, (_, index) => index & 0xff);
  assert.deepEqual(extractCharacterRom(raw)[9], Array.from(raw.slice(72, 80)));

  const name = new TextEncoder().encode("TEST");
  const pnamPayload = new Uint8Array(4 + name.length);
  new DataView(pnamPayload.buffer).setUint32(0, name.length, true);
  pnamPayload.set(name, 4);
  const binaryPayload = new Uint8Array(8 + raw.length);
  const binaryView = new DataView(binaryPayload.buffer);
  binaryView.setUint32(0, 0xe000, true);
  binaryView.setUint32(4, raw.length, true);
  binaryPayload.set(raw, 8);
  const section = (identifier, payload) => {
    const result = new Uint8Array(8 + payload.length);
    result.set(new TextEncoder().encode(identifier), 0);
    new DataView(result.buffer).setUint32(4, payload.length, true);
    result.set(payload, 8);
    return result;
  };
  const header = new Uint8Array(8);
  header.set(new TextEncoder().encode("PROG"), 0);
  new DataView(header.buffer).setUint32(4, 2, true);
  const pnam = section("PNAM", pnamPayload);
  const pbin = section("PBIN", binaryPayload);
  const prog = new Uint8Array(header.length + pnam.length + pbin.length);
  prog.set(header, 0);
  prog.set(pnam, header.length);
  prog.set(pbin, header.length + pnam.length);

  assert.deepEqual(extractCharacterRom(prog)[9], Array.from(raw.slice(72, 80)));
});

test("character ROM import supports the emulator ROM version 1 PROG format", () => {
  const rom = Uint8Array.from({ length: 0x2000 }, (_, index) => (index * 3) & 0xff);
  const name = new TextEncoder().encode("JR100ROM");
  const prog = new Uint8Array(24 + name.length + rom.length);
  const view = new DataView(prog.buffer);
  prog.set(new TextEncoder().encode("PROG"), 0);
  view.setUint32(4, 1, true);
  view.setUint32(8, name.length, true);
  prog.set(name, 12);
  const blockOffset = 12 + name.length;
  view.setUint32(blockOffset, 0xe000, true);
  view.setUint32(blockOffset + 4, rom.length, true);
  view.setUint32(blockOffset + 8, 0, true);
  prog.set(rom, blockOffset + 12);

  assert.deepEqual(extractCharacterRom(prog)[9], Array.from(rom.slice(72, 80)));
});

test("shifting a composite crosses slot boundaries", () => {
  const project = createProject({ withPreset: false });
  const workspace = { baseSlot: 0, width: 2, height: 1 };
  setPixel(project.glyphs, workspace, 7, 3, 1);

  shiftWorkspace(project.glyphs, workspace, 1, 0);

  assert.equal(getPixel(project.glyphs, workspace, 7, 3), 0);
  assert.equal(getPixel(project.glyphs, workspace, 8, 3), 1);
});

test("the arcade preset installs digits and a colon as one undoable block", () => {
  const project = createProject({ withPreset: false });
  applyArcadeDigits(project, 5);

  assert.deepEqual(project.glyphs[5], ARCADE_DIGITS.glyphs[0]);
  assert.deepEqual(project.glyphs[15], ARCADE_DIGITS.glyphs[10]);
  assert.equal(project.names[5], "Digit 0");
  assert.equal(project.names[15], "Colon");

  applyArcadeDigits(project, 16);
  assert.deepEqual(project.groups.filter(({ id }) => id === "arcade-digits"), [{
    id: "arcade-digits",
    name: "Arcade Digits",
    baseSlot: 16,
    width: 11,
    height: 1,
  }]);
});

test("the PCG library exposes 380 searchable assets, sets, and animations", () => {
  assert.equal(PCG_PRESETS.length, 380);
  assert.equal(new Set(PCG_PRESETS.map(({ id }) => id)).size, 380);
  assert.ok(PCG_PRESETS.every(({ glyphs, width, height }) => glyphs.length === width * height));
  assert.ok(PCG_PRESETS.every(({ glyphs }) => glyphs.every((glyph) => glyph.length === 8 && glyph.every((value) => value >= 0 && value <= 0xff))));
  assert.equal(filterPcgPresets({ kind: "asset", size: "8x8" }).length, 166);
  assert.equal(filterPcgPresets({ kind: "asset", size: "16x16" }).length, 122);
  assert.equal(filterPcgPresets({ kind: "set" }).length, 32);
  assert.equal(filterPcgPresets({ kind: "animation" }).length, 60);
  assert.equal(filterPcgPresets({ kind: "animation", size: "8x8" }).length, 32);
  assert.equal(filterPcgPresets({ kind: "animation", size: "16x16" }).length, 28);
  const animationPresets = filterPcgPresets({ kind: "animation" });
  assert.ok(animationPresets.every((preset) => (
    preset.id.startsWith("anim-")
    && preset.tags.includes("animation")
    && preset.frames.length >= 2
    && preset.frames.every((frame) => frame.glyphs.length === preset.width * preset.height)
    && preset.frames.every((frame) => frame.glyphs.every((glyph) => glyph.length === 8 && glyph.every((value) => value >= 0 && value <= 0xff)))
    && new Set(preset.frames.map((frame) => frame.glyphs.flat().join(","))).size >= 2
  )));
  assert.ok(PCG_PRESET_CATEGORIES.every((category) => filterPcgPresets({ category, kind: "animation" }).length === 4));
  assert.deepEqual(PCG_PRESET_CATEGORY_OPTIONS, [
    { id: "side-view", label: "Side view" },
    { id: "top-view", label: "Top view" },
    { id: "symbols", label: "Symbols" },
    { id: "stationery", label: "Stationery" },
    { id: "vehicles", label: "Vehicles" },
    { id: "creatures", label: "Creatures" },
    { id: "construction", label: "Construction" },
    { id: "cave", label: "Cave" },
    { id: "forest", label: "Forest" },
    { id: "underwater", label: "Underwater" },
    { id: "village", label: "Village" },
    { id: "city", label: "City" },
    { id: "electronics", label: "Electronics" },
    { id: "chibi", label: "Chibi" },
    { id: "flora", label: "Flora" },
  ]);
  assert.deepEqual(PCG_PRESET_CATEGORIES, [
    "side-view", "top-view", "symbols", "stationery", "vehicles", "creatures",
    "construction", "cave", "forest", "underwater", "village", "city", "electronics", "chibi", "flora",
  ]);
  assert.equal(filterPcgPresets({ category: "side-view", kind: "asset" }).length, 30);
  assert.equal(filterPcgPresets({ category: "top-view", kind: "asset" }).length, 38);
  assert.equal(filterPcgPresets({ category: "symbols", kind: "asset" }).length, 28);
  assert.equal(filterPcgPresets({ category: "stationery", kind: "asset" }).length, 22);
  assert.equal(filterPcgPresets({ category: "vehicles", kind: "asset" }).length, 20);
  assert.equal(filterPcgPresets({ category: "creatures", kind: "asset" }).length, 36);
  assert.equal(filterPcgPresets({ category: "construction", kind: "asset" }).length, 14);
  assert.equal(filterPcgPresets({ category: "cave", kind: "asset" }).length, 12);
  assert.equal(filterPcgPresets({ category: "forest", kind: "asset" }).length, 12);
  assert.equal(filterPcgPresets({ category: "underwater", kind: "asset" }).length, 12);
  assert.equal(filterPcgPresets({ category: "village", kind: "asset" }).length, 12);
  assert.equal(filterPcgPresets({ category: "city", kind: "asset" }).length, 12);
  assert.equal(filterPcgPresets({ category: "electronics", kind: "asset" }).length, 14);
  assert.equal(filterPcgPresets({ category: "chibi", kind: "asset" }).length, 12);
  assert.equal(filterPcgPresets({ category: "flora", kind: "asset" }).length, 14);
  assert.deepEqual(filterPcgPresets({ ids: ["vehicle-fighter-jet", "side-grass-top"] }).map(({ id }) => id), [
    "vehicle-fighter-jet",
    "side-grass-top",
  ]);

  const grass = getPcgPreset("side-grass-top");
  const aircraft = getPcgPreset("set-aircraft");
  const chibiHero = getPcgPreset("chibi-hero");
  const stationeryDesk = getPcgPreset("set-stationery-desk");
  const constructionMachines = getPcgPreset("set-construction-machines");
  const torchFlame = getPcgPreset("anim-torch-flame");
  const chibiWalk = getPcgPreset("anim-chibi-hero-walk");
  const symbolArrow = getPcgPreset("anim-symbol-arrow-pulse");
  const dragonBreathe = getPcgPreset("anim-chibi-dragon-breathe");

  assert.deepEqual({ kind: grass.kind, width: grass.width, height: grass.height, name: grass.name }, {
    kind: "asset", width: 1, height: 1, name: "Grass Top",
  });
  assert.deepEqual({ kind: aircraft.kind, width: aircraft.width, height: aircraft.height, glyphs: aircraft.glyphs.length }, {
    kind: "set", width: 4, height: 4, glyphs: 16,
  });
  assert.deepEqual({ category: chibiHero.category, width: chibiHero.width, height: chibiHero.height, tag: chibiHero.tags.includes("chibi") }, {
    category: "chibi", width: 2, height: 2, tag: true,
  });
  assert.deepEqual({ width: stationeryDesk.width, height: stationeryDesk.height, glyphs: stationeryDesk.glyphs.length }, {
    width: 18, height: 1, glyphs: 18,
  });
  assert.deepEqual({ category: constructionMachines.category, width: constructionMachines.width, height: constructionMachines.height, glyphs: constructionMachines.glyphs.length }, {
    category: "construction", width: 4, height: 4, glyphs: 16,
  });
  assert.deepEqual({ kind: torchFlame.kind, width: torchFlame.width, height: torchFlame.height, frames: torchFlame.frames.length, duration: torchFlame.frameDurationMs }, {
    kind: "animation", width: 1, height: 1, frames: 4, duration: 120,
  });
  assert.deepEqual({ kind: chibiWalk.kind, width: chibiWalk.width, height: chibiWalk.height, frames: chibiWalk.frames.length, duration: chibiWalk.frameDurationMs }, {
    kind: "animation", width: 2, height: 2, frames: 4, duration: 120,
  });
  assert.deepEqual({ category: symbolArrow.category, width: symbolArrow.width, height: symbolArrow.height, frames: symbolArrow.frames.length, duration: symbolArrow.frameDurationMs }, {
    category: "symbols", width: 1, height: 1, frames: 4, duration: 140,
  });
  assert.deepEqual({ category: dragonBreathe.category, width: dragonBreathe.width, height: dragonBreathe.height, frames: dragonBreathe.frames.length, duration: dragonBreathe.frameDurationMs }, {
    category: "chibi", width: 2, height: 2, frames: 4, duration: 110,
  });
  assert.deepEqual(filterPcgPresets({ query: "fighter", kind: "asset" }).map(({ id }) => id), ["vehicle-fighter-jet"]);
  assert.deepEqual(filterPcgPresets({ query: "torch", kind: "animation" }).map(({ id }) => id), ["anim-torch-flame"]);
  assert.deepEqual(filterPcgPresets({ query: "helicopter", kind: "animation" }).map(({ id }) => id), ["anim-vehicle-helicopter-rotor"]);
});

test("animation templates derive editable loops from existing library definitions", () => {
  assert.deepEqual(PCG_ANIMATION_TEMPLATES.map(({ id }) => id), [
    "blink", "pulse", "bounce", "shake", "scroll-right", "scroll-down", "wave", "sparkle",
  ]);
  assert.equal(getPcgAnimationTemplate("wave").name, "Wave");
  assert.throws(() => getPcgAnimationTemplate("unknown"), /Unknown PCG animation template/);

  const hero = getPcgPreset("chibi-hero");
  const aircraft = getPcgPreset("set-aircraft");
  const generatedShake = createPcgAnimationFromTemplate(hero, "shake", { frameDurationMs: 90 });
  const generatedBlink = createPcgAnimationFromTemplate(aircraft, "blink");

  assert.equal(filterPcgAnimationTemplates(hero).length, 8);
  assert.deepEqual(filterPcgAnimationTemplates(getPcgPreset("anim-torch-flame")), []);
  const road = getPcgPreset("top-road-horizontal");
  assert.equal(filterPcgAnimationTemplates(road).some(({ id }) => id === "scroll-right"), false);
  assert.deepEqual({ id: generatedShake.id, kind: generatedShake.kind, category: generatedShake.category, width: generatedShake.width, height: generatedShake.height, frames: generatedShake.frames.length, duration: generatedShake.frameDurationMs }, {
    id: "generated-animation-chibi-hero-shake", kind: "animation", category: "chibi", width: 2, height: 2, frames: 4, duration: 90,
  });
  assert.deepEqual(generatedShake.glyphs, hero.glyphs);
  assert.deepEqual(generatedShake.slotNames, hero.slotNames);
  assert.notDeepEqual(generatedShake.frames[1].glyphs, hero.glyphs);
  assert.deepEqual(generatedBlink.glyphs, aircraft.glyphs);
  assert.deepEqual(generatedBlink.slotNames, aircraft.slotNames);
  assert.ok(generatedBlink.frames[1].glyphs.flat().every((value) => value === 0));
  const staticSources = PCG_PRESETS.filter(({ kind }) => ["asset", "set"].includes(kind));
  assert.equal(staticSources.length, 320);
  staticSources.forEach((source) => {
    const templates = filterPcgAnimationTemplates(source);
    assert.ok(templates.length > 0, `${source.id} has an animation template`);
    templates.forEach(({ id }) => {
      const generated = createPcgAnimationFromTemplate(source, id);
      assert.ok(new Set(generated.frames.map((frame) => frame.glyphs.flat().join(","))).size > 1);
    });
  });
  [
    getPcgPreset("side-grass-top"),
    hero,
    getPcgPreset("set-stationery-desk"),
    aircraft,
  ].forEach((source) => {
    const templates = filterPcgAnimationTemplates(source);
    assert.ok(templates.length > 0);
    templates.forEach(({ id }) => {
      const generated = createPcgAnimationFromTemplate(source, id);
      assert.deepEqual(generated.glyphs, source.glyphs);
      assert.equal(generated.width, source.width);
      assert.equal(generated.height, source.height);
      assert.ok(generated.frames.every((frame) => frame.glyphs.length === source.width * source.height));
      assert.ok(new Set(generated.frames.map((frame) => frame.glyphs.flat().join(","))).size > 1);
    });
  });
  assert.throws(() => createPcgAnimationFromTemplate(getPcgPreset("anim-torch-flame"), "shake"), /asset or set/);
  assert.throws(() => createPcgAnimationFromTemplate(road, "scroll-right"), /does not change/);
  assert.throws(() => createPcgAnimationFromTemplate(hero, "shake", { frameDurationMs: 15 }), /16 and 60000/);

  const project = createProject({ withPreset: false });
  const result = applyPcgAnimationPreset(project, generatedBlink, 16);
  assert.deepEqual(result.workspace, { baseSlot: 16, width: 4, height: 4 });
  assert.deepEqual(project.glyphs.slice(16, 32), aircraft.glyphs);
  assert.deepEqual(project.names.slice(16, 32), aircraft.slotNames);
  assert.equal(project.animations[0].frames.length, 4);
  assert.throws(() => applyPcgAnimationPreset(project, generatedBlink, 17), /32 slots/);
});

test("applying a library preset reports and replaces only overlapping project data", () => {
  const project = createProject({ withPreset: false });
  const fighter = getPcgPreset("vehicle-fighter-jet");
  project.glyphs[4][0] = 0xff;
  project.groups = [
    { id: "replace", name: "Replace", baseSlot: 4, width: 2, height: 2 },
    { id: "keep", name: "Keep", baseSlot: 16, width: 1, height: 1 },
  ];
  project.animations = [
    createAnimationClip({ id: "replace-animation", name: "Replace", baseSlot: 6, width: 1, height: 1 }),
    createAnimationClip({ id: "keep-animation", name: "Keep", baseSlot: 20, width: 1, height: 1 }),
  ];

  assert.deepEqual(inspectPcgPresetConflicts(project, fighter, 4), {
    startSlot: 4,
    endSlot: 7,
    occupiedSlots: [4],
    groupIds: ["replace"],
    animationIds: ["replace-animation"],
  });

  const result = applyPcgPreset(project, fighter, 4);

  assert.deepEqual(project.glyphs.slice(4, 8), fighter.glyphs);
  assert.deepEqual(project.names.slice(4, 8), fighter.slotNames);
  assert.equal(project.groups.some(({ id }) => id === "replace"), false);
  assert.equal(project.groups.some(({ id }) => id === "keep"), true);
  assert.ok(project.groups.some(({ id, width, height }) => id === "preset-vehicle-fighter-jet-4" && width === 2 && height === 2));
  assert.deepEqual(project.animations.map(({ id }) => id), ["keep-animation"]);
  assert.deepEqual(result, {
    workspace: { baseSlot: 4, width: 2, height: 2 },
    replacedSlotCount: 4,
    removedGroupIds: ["replace"],
    removedAnimationIds: ["replace-animation"],
  });
});

test("8x8 assets and multi-asset sets preserve their declared workspace shape", () => {
  const project = createProject({ withPreset: false });
  const grass = getPcgPreset("side-grass-top");
  const structures = getPcgPreset("set-top-structures");
  const waters = getPcgPreset("set-top-waters");

  assert.deepEqual(inspectPcgPresetConflicts(project, grass, 31), {
    startSlot: 31,
    endSlot: 31,
    occupiedSlots: [],
    groupIds: [],
    animationIds: [],
  });
  assert.deepEqual(applyPcgPreset(project, grass, 31), {
    workspace: { baseSlot: 31, width: 1, height: 1 },
    replacedSlotCount: 1,
    removedGroupIds: [],
    removedAnimationIds: [],
  });
  assert.deepEqual(project.groups, []);
  assert.deepEqual(project.glyphs[31], grass.glyphs[0]);

  const setResult = applyPcgPreset(project, structures, 20);
  assert.deepEqual(setResult.workspace, { baseSlot: 20, width: 4, height: 1 });
  assert.deepEqual(project.glyphs.slice(20, 24), structures.glyphs);
  assert.ok(project.groups.some(({ id, width, height }) => id === "preset-set-top-structures-20" && width === 4 && height === 1));
  assert.throws(() => applyPcgPreset(project, waters, 21), /32 slots/);
});

test("expanded 16x16 assets and sets register editable composite groups", () => {
  const project = createProject({ withPreset: false });
  const chibiHero = getPcgPreset("chibi-hero");
  const constructionMachines = getPcgPreset("set-construction-machines");

  assert.deepEqual(applyPcgPreset(project, chibiHero, 4), {
    workspace: { baseSlot: 4, width: 2, height: 2 },
    replacedSlotCount: 4,
    removedGroupIds: [],
    removedAnimationIds: [],
  });
  assert.ok(project.groups.some(({ id, width, height }) => id === "preset-chibi-hero-4" && width === 2 && height === 2));

  assert.deepEqual(applyPcgPreset(project, constructionMachines, 16), {
    workspace: { baseSlot: 16, width: 4, height: 4 },
    replacedSlotCount: 16,
    removedGroupIds: [],
    removedAnimationIds: [],
  });
  assert.ok(project.groups.some(({ id, width, height }) => id === "preset-set-construction-machines-16" && width === 4 && height === 4));
  assert.throws(() => applyPcgPreset(project, constructionMachines, 17), /32 slots/);
});

test("animation presets register editable clips and replace only overlapping data", () => {
  const project = createProject({ withPreset: false });
  const chibiWalk = getPcgPreset("anim-chibi-hero-walk");
  project.glyphs[4][0] = 0xff;
  project.groups = [
    { id: "replace", name: "Replace", baseSlot: 4, width: 2, height: 2 },
    { id: "keep", name: "Keep", baseSlot: 20, width: 1, height: 1 },
  ];
  project.animations = [
    createAnimationClip({ id: "replace-animation", name: "Replace", baseSlot: 6, width: 1, height: 1 }),
    createAnimationClip({ id: "keep-animation", name: "Keep", baseSlot: 24, width: 1, height: 1 }),
    createAnimationClip({ id: "preset-animation-anim-chibi-hero-walk-4", name: "Keep generated id", baseSlot: 28, width: 1, height: 1 }),
  ];

  assert.deepEqual(inspectPcgAnimationPresetConflicts(project, chibiWalk, 4), {
    startSlot: 4,
    endSlot: 7,
    occupiedSlots: [4],
    groupIds: ["replace"],
    animationIds: ["replace-animation"],
  });

  const result = applyPcgAnimationPreset(project, chibiWalk, 4);

  assert.deepEqual(project.glyphs.slice(4, 8), chibiWalk.glyphs);
  assert.deepEqual(project.names.slice(4, 8), chibiWalk.slotNames);
  assert.deepEqual(project.groups.map(({ id }) => id), ["keep"]);
  assert.deepEqual(project.animations.map(({ id }) => id), ["keep-animation", "preset-animation-anim-chibi-hero-walk-4", "preset-animation-anim-chibi-hero-walk-4-2"]);
  assert.deepEqual(project.animations[2], {
    id: "preset-animation-anim-chibi-hero-walk-4-2",
    name: "Chibi Hero Walk",
    baseSlot: 4,
    width: 2,
    height: 2,
    frameDurationMs: 120,
    frames: chibiWalk.frames,
  });
  assert.deepEqual(result, {
    workspace: { baseSlot: 4, width: 2, height: 2 },
    replacedSlotCount: 4,
    removedGroupIds: ["replace"],
    removedAnimationIds: ["replace-animation"],
    animationId: "preset-animation-anim-chibi-hero-walk-4-2",
  });
  assert.match(exportAnimationAssembly(project.animations, { label: "LIBRARY_ANIMATIONS" }), /CHIBI_HERO_WALK_FRAME_COUNT: \.equ 4/);
  assert.deepEqual(parseProject(serializeProject(project)).animations, project.animations);
  assert.throws(() => applyPcgAnimationPreset(project, chibiWalk, 29), /32 slots/);
});

test("JSON serialization validates and preserves all glyph data", () => {
  const source = createProject({ withPreset: true });
  const restored = parseProject(serializeProject(source));

  assert.deepEqual(restored, source);
});

test("named composite groups survive JSON round trips and can be removed", () => {
  const project = createProject();
  upsertGroup(project, {
    id: "boss",
    name: "Boss 3x3",
    baseSlot: 12,
    width: 3,
    height: 3,
  });

  const restored = parseProject(serializeProject(project));

  assert.deepEqual(restored.groups[0], {
    id: "boss",
    name: "Boss 3x3",
    baseSlot: 12,
    width: 3,
    height: 3,
  });
  assert.equal(removeGroup(restored, "boss"), true);
  assert.deepEqual(restored.groups, []);
});

test("assembly export emits all 256 PCG bytes without localized output", () => {
  const project = createProject({ withPreset: true });
  const assembly = exportAssembly(project, { label: "PCG_DATA" });

  assert.match(assembly, /^PCG_DATA:/);
  assert.equal((assembly.match(/\.byte/g) ?? []).length, 32);
  assert.match(assembly, /\.byte \$3C, \$66, \$6E, \$76, \$66, \$66, \$3C, \$00/);
  assert.doesNotMatch(assembly, /[\u3040-\u30ff\u3400-\u9fff]/u);
});
