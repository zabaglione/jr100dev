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
  upgradeStarterSamples,
} from "../../tools/sound_editor/core.js";
import { TRANSLATIONS } from "../../tools/sound_editor/i18n.js";

const soundEditorHtml = await readFile(new URL("../../tools/sound_editor/index.html", import.meta.url), "utf8");
const soundEditorApp = await readFile(new URL("../../tools/sound_editor/app.js", import.meta.url), "utf8");
const sampleProvenance = await readFile(new URL("../../docs/sound_samples.md", import.meta.url), "utf8");

test("default sound project separates locked sample assets from editable user assets", () => {
  const project = createProject();
  assert.deepEqual(project.tracks.map(({ id }) => id), [
    "ode-to-joy-opening",
    "ah-vous-diraije-opening",
    "fur-elise-opening",
    "bach-prelude-c-opening",
    "eine-kleine-nachtmusik-opening",
    "vivaldi-spring-opening",
    "handel-water-music-opening",
    "pachelbel-canon-opening",
    "rameau-gavotte-opening",
    "haydn-surprise-opening",
    "swan-lake-opening",
    "carmen-habanera-opening",
  ]);
  assert.deepEqual(project.effects.map(({ id }) => id), [
    "blip", "click", "laser", "jump", "hit", "explode", "pickup", "alert", "start", "game-over", "coin",
  ]);
  assert.equal(project.tracks.every(({ origin }) => origin === "sample"), true);
  assert.equal(project.effects.every(({ origin }) => origin === "sample"), true);
  assert.equal(project.tracks.every(({ notes }) => notes.length >= 16), true);
  assert.deepEqual(project.tracks.filter(({ included }) => included).map(({ id }) => id), ["ode-to-joy-opening"]);
  assert.deepEqual(project.effects.filter(({ included }) => included).map(({ id }) => id), ["blip"]);
  for (const { id } of [...project.tracks, ...project.effects]) {
    assert.equal(sampleProvenance.includes("| `" + id.toUpperCase().replaceAll("-", "_") + "`"), true);
  }
});

test("consecutive equal BGM cells remain separate note attacks", () => {
  assert.deepEqual(
    compileBgmTrack({ notes: [25, 25, 0, 0, 29] }, 3),
    [[25, 3], [25, 3], [0, 3], [0, 3], [29, 3]],
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

test("assembly output contains only assets selected for the target PRG", () => {
  const project = createProject();
  project.tracks[0].included = false;
  project.tracks[2].included = true;
  project.effects[0].included = false;
  project.effects[3].included = true;
  const assembly = exportAssembly(project);
  assert.match(assembly, /SOUND_BGM_FUR_ELISE_OPENING:/);
  assert.match(assembly, /SOUND_SFX_JUMP:/);
  assert.doesNotMatch(assembly, /SOUND_BGM_ODE_TO_JOY_OPENING:/);
  assert.doesNotMatch(assembly, /SOUND_SFX_BLIP:/);
});

test("sample assets reject hand-edited project data while user copies remain editable", () => {
  const project = createProject();
  project.tracks[0].notes[0] = 18;
  assert.throws(() => exportAssembly(project), /Sample assets/);
  project.tracks[0].origin = "user";
  assert.throws(() => exportAssembly(project), /reserved/);
  project.tracks[0].id = "user-ode-copy";
  assert.doesNotThrow(() => exportAssembly(project));
});

test("assembly export rejects a hand-edited legacy sample before it can bypass the lock", () => {
  const project = createProject();
  project.tracks[0].notes[0] = 18;
  delete project.tracks[0].origin;
  assert.throws(() => exportAssembly(project), /require a sample origin/);
});

test("legacy starter assets are restored as locked samples without discarding user assets", () => {
  const legacy = createProject();
  legacy.tracks = legacy.tracks.slice(0, 2).map(({ origin, included, ...asset }) => asset);
  legacy.effects = legacy.effects.slice(0, 1).map(({ origin, included, ...asset }) => asset);
  legacy.tracks.push({ id: "user-track", name: "User Track", notes: [25], loopCell: 0 });
  const upgraded = upgradeStarterSamples(legacy);
  assert.equal(upgraded.tracks.length, 13);
  assert.equal(upgraded.effects.length, 11);
  assert.equal(upgraded.tracks[0].origin, "sample");
  assert.equal(upgraded.tracks[0].included, true);
  assert.equal(upgraded.tracks.some(({ id }) => id === "user-track"), true);
});

test("four-cell sample tracks from the previous catalog upgrade to the longer locked samples", () => {
  const legacy = createProject();
  legacy.tracks[2].notes = [29, 28, 29, 28];
  legacy.tracks[2].included = true;
  legacy.tracks.push({ id: "user-track", name: "User Track", notes: [25], loopCell: 0, origin: "user" });
  const upgraded = upgradeStarterSamples(parseProject(JSON.stringify(legacy)));
  const furElise = upgraded.tracks.find(({ id }) => id === "fur-elise-opening");
  assert.deepEqual(furElise.notes, createProject().tracks[2].notes);
  assert.equal(furElise.included, true);
  assert.equal(upgraded.tracks.some(({ id }) => id === "user-track"), true);
});

test("asset ids that normalize to the same assembly label are rejected", () => {
  const project = createProject();
  project.tracks[0].origin = "user";
  project.tracks[1].origin = "user";
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

test("sound editor offers PRG inclusion controls and copies samples before editing", () => {
  assert.match(soundEditorHtml, /id="copy-sample"/);
  assert.match(soundEditorApp, /asset\.origin === "sample"/);
  assert.match(soundEditorApp, /copySampleToUserAssets/);
  assert.match(soundEditorApp, /deleteAsset: document\.querySelector\("#delete-asset"\)/);
  assert.match(soundEditorApp, /asset\.included/);
  assert.match(soundEditorApp, /input\.type = "checkbox"/);
  assert.match(soundEditorApp, /selectedBgmRequired/);
});
