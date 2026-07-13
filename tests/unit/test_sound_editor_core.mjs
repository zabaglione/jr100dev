import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

import {
  compileBgmTrack,
  compileSfx,
  createProject,
  exportAssembly,
  parseProject,
  serializeProject,
} from "../../tools/sound_editor/core.js";
import { TRANSLATIONS } from "../../tools/sound_editor/i18n.js";

const soundEditorHtml = await readFile(new URL("../../tools/sound_editor/index.html", import.meta.url), "utf8");
const soundEditorApp = await readFile(new URL("../../tools/sound_editor/app.js", import.meta.url), "utf8");

test("default sound project contains the two public-domain melody samples", () => {
  const project = createProject();
  assert.deepEqual(project.tracks.map(({ id }) => id), ["ode-to-joy-opening", "ah-vous-diraije-opening"]);
  assert.equal(project.effects.length, 1);
});

test("BGM cells are run-length encoded into tick events", () => {
  assert.deepEqual(
    compileBgmTrack({ notes: [25, 25, 0, 0, 29] }, 3),
    [[25, 6], [0, 6], [29, 3]],
  );
});

test("SFX cells reject a duration longer than 500ms", () => {
  assert.throws(() => compileSfx({ notes: Array(51).fill(25) }), /50/);
});

test("sound projects round-trip and emit ASCII-only assembly assets", () => {
  const project = createProject();
  const restored = parseProject(serializeProject(project));
  const assembly = exportAssembly(restored);
  assert.match(assembly, /SOUND_BGM_ODE_TO_JOY_OPENING:/);
  assert.match(assembly, /SOUND_SFX_BLIP:/);
  assert.equal(/[^\x00-\x7F]/.test(assembly), false);
});

test("asset ids that normalize to the same assembly label are rejected", () => {
  const project = createProject();
  project.tracks[0].id = "same-id";
  project.tracks[1].id = "same_id";
  assert.throws(() => exportAssembly(project), /labels/);
});

test("sound editor defaults to Japanese and exposes an English language switch", () => {
  assert.match(soundEditorHtml, /<html lang="ja">/);
  assert.match(soundEditorHtml, /id="language-select"/);
  assert.match(soundEditorHtml, /option value="ja" selected/);
  assert.match(soundEditorHtml, /option value="en"/);
  assert.match(soundEditorApp, /translateDocument\(\)/);
  assert.match(soundEditorApp, /#language-select/);
  assert.match(soundEditorHtml, /data-i18n-aria="project.settings"/);
});

test("Japanese and English sound editor translations expose the same keys", () => {
  assert.deepEqual(Object.keys(TRANSLATIONS.ja).sort(), Object.keys(TRANSLATIONS.en).sort());
});

test("sound editor keeps essential error messages localized and supports keyboard piano-roll editing", () => {
  assert.match(soundEditorHtml, /tabindex="0"/);
  assert.match(soundEditorHtml, /aria-describedby="roll-help"/);
  assert.match(soundEditorApp, /canvas\.addEventListener\("keydown"/);
  assert.match(soundEditorApp, /event\.key === "ArrowLeft"/);
  assert.match(soundEditorApp, /event\.key === " " \|\| event\.key === "Enter"/);
  assert.match(soundEditorApp, /elements\.language\.addEventListener\("change"/);
  assert.match(soundEditorApp, /t\("error\.invalidProject"\)/);
  assert.match(soundEditorApp, /t\("error\.loadFailed"\)/);
  assert.equal(soundEditorApp.includes("error.message"), false);
});
