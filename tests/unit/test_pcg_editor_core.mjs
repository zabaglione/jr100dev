import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

import {
  ARCADE_DIGITS,
  applyArcadeDigits,
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
import { extractCharacterRom } from "../../tools/pcg_editor/rom_font.js";
import en from "../../tools/pcg_editor/locales/en.js";
import ja from "../../tools/pcg_editor/locales/ja.js";
import { getLanguage, resolveStoredLanguage, setLanguage, t } from "../../tools/pcg_editor/i18n.js";

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
