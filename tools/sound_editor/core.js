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

export function createProject() {
  return {
    version: PROJECT_VERSION,
    name: "JR-100 Sound Project",
    tickHz: DEFAULT_TICK_HZ,
    gridTicks: DEFAULT_GRID_TICKS,
    tracks: [
      {
        id: "ode-to-joy-opening",
        name: "Ode To Joy Opening",
        notes: [...ODE_TO_JOY],
        loopCell: 0,
      },
      {
        id: "ah-vous-diraije-opening",
        name: "Ah Vous Dirai-je Opening",
        notes: [...AH_VOUS_DIRAIJE],
        loopCell: 0,
      },
    ],
    effects: [
      {
        id: "blip",
        name: "Blip",
        notes: [37, 41, 45, 0],
      },
    ],
  };
}

export function validateProject(project) {
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
    validateTrack(track, ids, trackLabels);
    compileBgmDescriptor(track, project.gridTicks);
  }
  for (const effect of project.effects) {
    validateEffect(effect, ids, effectLabels);
    compileSfx(effect);
  }
  return project;
}

function validateTrack(track, ids, labels) {
  validateAssetIdentity(track, ids, labels, "BGM");
  validateNotes(track.notes, "BGM notes");
  if (!Number.isInteger(track.loopCell) || track.loopCell < -1 || track.loopCell >= track.notes.length) {
    throw new RangeError("loopCell must be -1 or a BGM cell index");
  }
}

function validateEffect(effect, ids, labels) {
  validateAssetIdentity(effect, ids, labels, "SFX");
  validateNotes(effect.notes, "SFX notes");
}

function validateAssetIdentity(asset, ids, labels, type) {
  if (!asset || typeof asset !== "object" || typeof asset.id !== "string" || !asset.id.trim()) {
    throw new TypeError("Sound asset id is required");
  }
  if (typeof asset.name !== "string" || !asset.name.trim()) {
    throw new TypeError("Sound asset name is required");
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
    const pitch = notes[cell];
    const previous = events.at(-1);
    const mayMerge = previous && previous[0] === pitch && cell !== loopCell && previous[1] + durationPerCell <= 255;
    if (mayMerge) {
      previous[1] += durationPerCell;
    } else {
      events.push([pitch, durationPerCell]);
    }
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
  for (const track of project.tracks) {
    const label = `SOUND_BGM_${normalizeAssemblyLabel(track.id)}`;
    const { events, loopEvent } = compileBgmDescriptor(track, project.gridTicks);
    lines.push(`${label}:`);
    lines.push(`        .word ${label}_EVENTS`);
    lines.push(`        .byte ${events.length}, ${formatByte(loopEvent < 0 ? 0xff : loopEvent)}`);
    lines.push(`${label}_EVENTS:`);
    appendEvents(lines, events);
  }
  for (const effect of project.effects) {
    const label = `SOUND_SFX_${normalizeAssemblyLabel(effect.id)}`;
    const events = compileSfx(effect);
    lines.push(`${label}:`);
    lines.push(`        .byte ${events.length}`);
    appendEvents(lines, events);
  }
  return `${lines.join("\n")}\n`;
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
  validateProject(project);
  return project;
}
