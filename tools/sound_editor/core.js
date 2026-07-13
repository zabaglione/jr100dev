export const PROJECT_VERSION = 1;
export const MIN_PITCH = 1;
export const MAX_PITCH = 48;
export const MAX_SFX_UNITS = 50;
export const DEFAULT_TICK_HZ = 60;
export const DEFAULT_GRID_TICKS = 6;

const NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"];

export const PITCHES = Object.freeze(Array.from({ length: MAX_PITCH }, (_, index) => {
  const midi = 48 + index;
  const octave = Math.floor(midi / 12) - 1;
  return {
    index: index + 1,
    name: `${NOTE_NAMES[midi % 12]}${octave}`,
    frequency: 440 * 2 ** ((midi - 69) / 12),
  };
}));

const ODE_TO_JOY = [17, 17, 18, 20, 20, 18, 17, 15, 13, 13, 15, 17, 17, 15, 15, 0];
const AH_VOUS_DIRAIJE = [13, 13, 20, 20, 22, 22, 20, 0, 18, 18, 17, 17, 15, 15, 13, 0];

const SAMPLE_TRACKS = Object.freeze([
  ["ode-to-joy-opening", "Ode To Joy Opening", ODE_TO_JOY],
  ["ah-vous-diraije-opening", "Ah Vous Dirai-je Opening", AH_VOUS_DIRAIJE],
  ["fur-elise-opening", "Fur Elise Opening", [
    29, 28, 29, 28, 29, 24, 27, 25, 22, 25, 29, 22, 24, 29, 32, 33,
  ]],
  ["bach-prelude-c-opening", "Bach Prelude In C Opening", [
    13, 17, 20, 25, 17, 20, 25, 29, 15, 18, 22, 27, 18, 22, 27, 30,
  ]],
  ["eine-kleine-nachtmusik-opening", "Eine Kleine Nachtmusik Opening", [
    20, 15, 20, 15, 20, 15, 20, 15, 20, 15, 20, 22, 24, 20, 19, 17,
  ]],
  ["vivaldi-spring-opening", "Vivaldi Spring Opening", [
    20, 25, 24, 22, 20, 25, 24, 22, 20, 25, 29, 27, 25, 24, 22, 20,
  ]],
  ["handel-water-music-opening", "Handel Water Music Opening", [
    15, 20, 22, 24, 25, 24, 22, 20, 19, 20, 22, 24, 20, 22, 24, 25,
  ]],
  ["pachelbel-canon-opening", "Pachelbel Canon Opening", [
    15, 22, 24, 19, 20, 15, 20, 22, 29, 27, 25, 24, 22, 20, 19, 17,
  ]],
  ["rameau-gavotte-opening", "Rameau Gavotte Opening", [
    13, 15, 17, 18, 20, 17, 18, 20, 22, 20, 18, 17, 15, 13, 15, 17,
  ]],
  ["haydn-surprise-opening", "Haydn Surprise Opening", [
    20, 20, 22, 22, 20, 20, 18, 0, 20, 20, 18, 18, 17, 17, 15, 0,
  ]],
  ["swan-lake-opening", "Swan Lake Opening", [
    22, 17, 15, 13, 15, 17, 18, 20, 22, 20, 18, 17, 15, 13, 15, 17,
  ]],
  ["carmen-habanera-opening", "Carmen Habanera Opening", [
    20, 22, 23, 24, 25, 24, 23, 22, 20, 19, 20, 22, 17, 20, 19, 17,
  ]],
]);

const SAMPLE_EFFECTS = Object.freeze([
  ["blip", "Blip", [37, 41, 45, 0]],
  ["click", "Click", [40, 0]],
  ["laser", "Laser", [45, 41, 37, 0]],
  ["jump", "Jump", [25, 29, 34, 0]],
  ["hit", "Hit", [25, 17, 0]],
  ["explode", "Explode", [17, 24, 15, 0]],
  ["pickup", "Pickup", [29, 34, 0]],
  ["alert", "Alert", [37, 37, 0]],
  ["start", "Start", [25, 29, 32, 37, 0]],
  ["game-over", "Game Over", [25, 20, 13, 0]],
  ["coin", "Coin", [37, 44, 0]],
]);

const LEGACY_SAMPLE_TRACKS = Object.freeze([
  ["fur-elise-opening", "Fur Elise Opening", [29, 28, 29, 28]],
  ["bach-prelude-c-opening", "Bach Prelude In C Opening", [13, 17, 20, 25]],
  ["eine-kleine-nachtmusik-opening", "Eine Kleine Nachtmusik Opening", [20, 15, 20, 15]],
  ["vivaldi-spring-opening", "Vivaldi Spring Opening", [20, 25, 24, 22]],
  ["handel-water-music-opening", "Handel Water Music Opening", [15, 20, 22, 24]],
  ["pachelbel-canon-opening", "Pachelbel Canon Opening", [15, 22, 24, 20]],
  ["rameau-gavotte-opening", "Rameau Gavotte Opening", [13, 15, 17, 18]],
  ["haydn-surprise-opening", "Haydn Surprise Opening", [20, 20, 22, 24]],
  ["swan-lake-opening", "Swan Lake Opening", [22, 17, 15, 13]],
  ["carmen-habanera-opening", "Carmen Habanera Opening", [20, 22, 23, 24]],
]);

export function createProject() {
  return {
    version: PROJECT_VERSION,
    name: "JR-100 Sound Project",
    tickHz: DEFAULT_TICK_HZ,
    gridTicks: DEFAULT_GRID_TICKS,
    tracks: SAMPLE_TRACKS.map(([id, name, notes], index) => ({
      id,
      name,
      notes: [...notes],
      loopCell: 0,
      origin: "sample",
      included: index === 0,
    })),
    effects: SAMPLE_EFFECTS.map(([id, name, notes], index) => ({
      id,
      name,
      notes: [...notes],
      origin: "sample",
      included: index === 0,
    })),
  };
}

export function upgradeStarterSamples(project) {
  validateProject(project, { allowLegacyBuiltInIds: true, allowLegacySampleContents: true });
  const starter = createProject();
  const upgraded = {
    ...project,
    tracks: upgradeAssets(project.tracks, starter.tracks, "BGM"),
    effects: upgradeAssets(project.effects, starter.effects, "SFX"),
  };
  validateProject(upgraded);
  return upgraded;
}

function upgradeAssets(assets, starterAssets, type) {
  const originalIds = new Set(assets.map(({ id }) => id));
  const usedIds = new Set();
  const existingAssets = assets.map((asset) => {
    const sample = starterAssets.find(({ id }) => id === asset.id);
    if (sample && matchesLegacyBuiltInSample(asset, type)) {
      usedIds.add(asset.id);
      return { ...sample, included: asset.included ?? true };
    }
    if (asset.origin === undefined && sample && matchesBuiltInSample(asset, type)) {
      usedIds.add(asset.id);
      return { ...asset, origin: "sample", included: asset.included ?? true };
    }
    const id = sample && asset.origin === undefined
      ? nextMigratedId(asset.id, new Set([...originalIds, ...usedIds]))
      : asset.id;
    usedIds.add(id);
    return id === asset.id ? asset : { ...asset, id };
  });
  return [
    ...existingAssets,
    ...starterAssets.filter(({ id }) => !usedIds.has(id)),
  ];
}

function nextMigratedId(id, usedIds) {
  const base = `user-${id}`;
  let candidate = base;
  let index = 2;
  while (usedIds.has(candidate)) {
    candidate = `${base}-${index}`;
    index += 1;
  }
  return candidate;
}

export function validateProject(
  project,
  { allowLegacyBuiltInIds = false, allowLegacySampleContents = false } = {},
) {
  if (!project || typeof project !== "object") {
    throw new TypeError("Sound project is required");
  }
  if (!Number.isInteger(project.version) || project.version !== PROJECT_VERSION) {
    throw new TypeError("Unsupported sound project version");
  }
  if (typeof project.name !== "string" || !project.name.trim()) {
    throw new TypeError("Project name is required");
  }
  if (!Number.isInteger(project.tickHz) || project.tickHz < 1 || project.tickHz > 240) {
    throw new RangeError("tickHz must be between 1 and 240");
  }
  if (!Number.isInteger(project.gridTicks) || project.gridTicks < 1 || project.gridTicks > 255) {
    throw new RangeError("gridTicks must be between 1 and 255");
  }
  if (!Array.isArray(project.tracks) || !project.tracks.length) {
    throw new TypeError("At least one BGM track is required");
  }
  if (!Array.isArray(project.effects)) {
    throw new TypeError("Effects must be an array");
  }
  const ids = new Set();
  const trackLabels = new Set();
  const effectLabels = new Set();
  for (const track of project.tracks) {
    validateTrack(track, ids, trackLabels, allowLegacyBuiltInIds, allowLegacySampleContents);
    compileBgmDescriptor(track, project.gridTicks);
  }
  for (const effect of project.effects) {
    validateEffect(effect, ids, effectLabels, allowLegacyBuiltInIds, allowLegacySampleContents);
    compileSfx(effect);
  }
  return project;
}

function validateTrack(track, ids, labels, allowLegacyBuiltInIds, allowLegacySampleContents) {
  validateAssetIdentity(track, ids, labels, "BGM", allowLegacyBuiltInIds, allowLegacySampleContents);
  validateNotes(track.notes, "BGM notes");
  if (!Number.isInteger(track.loopCell) || track.loopCell < -1 || track.loopCell >= track.notes.length) {
    throw new RangeError("loopCell must be -1 or a BGM cell index");
  }
}

function validateEffect(effect, ids, labels, allowLegacyBuiltInIds, allowLegacySampleContents) {
  validateAssetIdentity(effect, ids, labels, "SFX", allowLegacyBuiltInIds, allowLegacySampleContents);
  validateNotes(effect.notes, "SFX notes");
}

function validateAssetIdentity(
  asset,
  ids,
  labels,
  type,
  allowLegacyBuiltInIds,
  allowLegacySampleContents,
) {
  if (!asset || typeof asset !== "object" || typeof asset.id !== "string" || !asset.id.trim()) {
    throw new TypeError("Sound asset id is required");
  }
  if (typeof asset.name !== "string" || !asset.name.trim()) {
    throw new TypeError("Sound asset name is required");
  }
  if (asset.origin !== undefined && asset.origin !== "sample" && asset.origin !== "user") {
    throw new TypeError("Sound asset origin must be sample or user");
  }
  if (asset.included !== undefined && typeof asset.included !== "boolean") {
    throw new TypeError("Sound asset included must be boolean");
  }
  const builtInSample = findBuiltInSample(asset.id, type);
  if (
    asset.origin === "sample"
    && !matchesBuiltInSample(asset, type)
    && !(allowLegacySampleContents && matchesLegacyBuiltInSample(asset, type))
  ) {
    throw new TypeError("Sample assets must match the built-in library");
  }
  if (asset.origin === "user" && builtInSample) {
    throw new TypeError("Built-in sample ids are reserved");
  }
  if (asset.origin === undefined && builtInSample && !allowLegacyBuiltInIds) {
    throw new TypeError("Built-in sample assets require a sample origin");
  }
  if (ids.has(asset.id)) {
    throw new TypeError("Sound asset ids must be unique");
  }
  ids.add(asset.id);
  const label = normalizeAssemblyLabel(asset.id);
  if (labels.has(label)) {
    throw new TypeError(`${type} labels must be unique after normalization`);
  }
  labels.add(label);
}

function matchesBuiltInSample(asset, type) {
  const sample = findBuiltInSample(asset.id, type);
  if (!sample) return false;
  const [, name, notes] = sample;
  if (asset.name !== name || !sameNotes(asset.notes, notes)) return false;
  return type !== "BGM" || asset.loopCell === 0;
}

function findBuiltInSample(id, type) {
  const samples = type === "BGM" ? SAMPLE_TRACKS : SAMPLE_EFFECTS;
  return samples.find(([sampleId]) => sampleId === id);
}

function matchesLegacyBuiltInSample(asset, type) {
  if (type !== "BGM") return false;
  const sample = LEGACY_SAMPLE_TRACKS.find(([sampleId]) => sampleId === asset.id);
  if (!sample) return false;
  const [, name, notes] = sample;
  return asset.name === name && asset.loopCell === 0 && sameNotes(asset.notes, notes);
}

function sameNotes(notes, expected) {
  return Array.isArray(notes)
    && notes.length === expected.length
    && notes.every((pitch, index) => pitch === expected[index]);
}

function validateNotes(notes, field) {
  if (!Array.isArray(notes) || !notes.length) {
    throw new TypeError(`${field} are required`);
  }
  if (!notes.every((pitch) => Number.isInteger(pitch) && pitch >= 0 && pitch <= MAX_PITCH)) {
    throw new RangeError(`${field} must contain pitches from 0 through ${MAX_PITCH}`);
  }
}

export function compileBgmTrack(track, gridTicks) {
  return compileBgmDescriptor(track, gridTicks).events;
}

export function compileBgmDescriptor(track, gridTicks) {
  validateNotes(track?.notes, "BGM notes");
  if (!Number.isInteger(gridTicks) || gridTicks < 1 || gridTicks > 255) {
    throw new RangeError("gridTicks must be between 1 and 255");
  }
  const loopCell = Number.isInteger(track.loopCell) ? track.loopCell : -1;
  if (loopCell < -1 || loopCell >= track.notes.length) {
    throw new RangeError("loopCell must be -1 or a BGM cell index");
  }
  return encodeCells(track.notes, gridTicks, loopCell);
}

export function compileSfx(effect) {
  validateNotes(effect?.notes, "SFX notes");
  if (effect.notes.length > MAX_SFX_UNITS) {
    throw new RangeError(`SFX may not exceed ${MAX_SFX_UNITS} units`);
  }
  return encodeCells(effect.notes, 1, -1).events;
}

function encodeCells(notes, durationPerCell, loopCell) {
  const events = [];
  let loopEvent = -1;
  for (let cell = 0; cell < notes.length; cell += 1) {
    if (cell === loopCell) {
      loopEvent = events.length;
    }
    events.push([notes[cell], durationPerCell]);
  }
  if (events.length > 255) {
    throw new RangeError("Sound asset has more than 255 events");
  }
  return { events, loopEvent };
}

export function normalizeAssemblyLabel(value) {
  const normalized = String(value || "SOUND")
    .toUpperCase()
    .replace(/[^A-Z0-9_]/g, "_")
    .replace(/^[^A-Z_]/, "_$&");
  return normalized || "SOUND";
}

export function exportAssembly(project) {
  validateProject(project);
  const lines = [
    "; Generated JR-100 sound assets",
    `SOUND_TICK_HZ: .equ ${project.tickHz}`,
    "",
    ".data",
  ];
  for (const track of project.tracks.filter(isIncluded)) {
    const label = `SOUND_BGM_${normalizeAssemblyLabel(track.id)}`;
    const { events, loopEvent } = compileBgmDescriptor(track, project.gridTicks);
    lines.push(`${label}:`);
    lines.push(`        .word ${label}_EVENTS`);
    lines.push(`        .byte ${events.length}, ${formatByte(loopEvent < 0 ? 0xff : loopEvent)}`);
    lines.push(`${label}_EVENTS:`);
    appendEvents(lines, events);
  }
  for (const effect of project.effects.filter(isIncluded)) {
    const label = `SOUND_SFX_${normalizeAssemblyLabel(effect.id)}`;
    const events = compileSfx(effect);
    lines.push(`${label}:`);
    lines.push(`        .byte ${events.length}`);
    appendEvents(lines, events);
  }
  return `${lines.join("\n")}\n`;
}

function isIncluded(asset) {
  return asset.included !== false;
}

function appendEvents(lines, events) {
  for (const [pitch, duration] of events) {
    lines.push(`        .byte ${formatByte(pitch)}, ${formatByte(duration)}`);
  }
}

function formatByte(value) {
  return `$${value.toString(16).toUpperCase().padStart(2, "0")}`;
}

export function serializeProject(project) {
  validateProject(project);
  return `${JSON.stringify(project, null, 2)}\n`;
}

export function parseProject(text) {
  let project;
  try {
    project = JSON.parse(text);
  } catch (error) {
    throw new TypeError(`Invalid sound project JSON: ${error.message}`);
  }
  validateProject(project, { allowLegacyBuiltInIds: true, allowLegacySampleContents: true });
  return project;
}
