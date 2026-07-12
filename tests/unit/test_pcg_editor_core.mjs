import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

import {
  ARCADE_DIGITS,
  applyArcadeDigits,
  assertWorkspace,
  bresenhamPoints,
  constrainEndpoint,
  createProject,
  exportAssembly,
  getPixel,
  parseProject,
  removeGroup,
  serializeProject,
  setPixel,
  shiftWorkspace,
  upsertGroup,
} from "../../tools/pcg_editor/core.js";

const editorHtml = await readFile(new URL("../../tools/pcg_editor/index.html", import.meta.url), "utf8");
const editorStyles = await readFile(new URL("../../tools/pcg_editor/styles.css", import.meta.url), "utf8");

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
