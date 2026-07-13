"""Local-only builder for JR-100 sound editor projects."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from dataclasses import dataclass
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from io import BytesIO
from pathlib import Path
from typing import Mapping, Sequence
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from jr100dev.asm.encoder import Assembler
from jr100dev.link.pack_prg import pack_prg


PROJECT_VERSION = 1
MAX_PITCH = 48
MAX_SFX_UNITS = 50
MAX_REQUEST_BYTES = 1_000_000

SAMPLE_TRACKS = {
    "ode-to-joy-opening": (
        "Ode To Joy Opening",
        (17, 17, 18, 20, 20, 18, 17, 15, 13, 13, 15, 17, 17, 15, 15, 0),
        0,
    ),
    "ah-vous-diraije-opening": (
        "Ah Vous Dirai-je Opening",
        (13, 13, 20, 20, 22, 22, 20, 0, 18, 18, 17, 17, 15, 15, 13, 0),
        0,
    ),
    "fur-elise-opening": ("Fur Elise Opening", (29, 28, 29, 28), 0),
    "bach-prelude-c-opening": ("Bach Prelude In C Opening", (13, 17, 20, 25), 0),
    "eine-kleine-nachtmusik-opening": (
        "Eine Kleine Nachtmusik Opening",
        (20, 15, 20, 15),
        0,
    ),
    "vivaldi-spring-opening": ("Vivaldi Spring Opening", (20, 25, 24, 22), 0),
    "handel-water-music-opening": ("Handel Water Music Opening", (15, 20, 22, 24), 0),
    "pachelbel-canon-opening": ("Pachelbel Canon Opening", (15, 22, 24, 20), 0),
    "rameau-gavotte-opening": ("Rameau Gavotte Opening", (13, 15, 17, 18), 0),
    "haydn-surprise-opening": ("Haydn Surprise Opening", (20, 20, 22, 24), 0),
    "swan-lake-opening": ("Swan Lake Opening", (22, 17, 15, 13), 0),
    "carmen-habanera-opening": ("Carmen Habanera Opening", (20, 22, 23, 24), 0),
}

SAMPLE_EFFECTS = {
    "blip": ("Blip", (37, 41, 45, 0)),
    "click": ("Click", (40, 0)),
    "laser": ("Laser", (45, 41, 37, 0)),
    "jump": ("Jump", (25, 29, 34, 0)),
    "hit": ("Hit", (25, 17, 0)),
    "explode": ("Explode", (17, 24, 15, 0)),
    "pickup": ("Pickup", (29, 34, 0)),
    "alert": ("Alert", (37, 37, 0)),
    "start": ("Start", (25, 29, 32, 37, 0)),
    "game-over": ("Game Over", (25, 20, 13, 0)),
    "coin": ("Coin", (37, 44, 0)),
}


class ProjectValidationError(ValueError):
    """Raised when a browser project cannot become a safe sound asset."""


@dataclass(frozen=True)
class SoundEvent:
    pitch: int
    duration: int


@dataclass(frozen=True)
class BgmTrack:
    asset_id: str
    name: str
    events: tuple[SoundEvent, ...]
    loop_event: int
    included: bool


@dataclass(frozen=True)
class SoundEffect:
    asset_id: str
    name: str
    events: tuple[SoundEvent, ...]
    included: bool


@dataclass(frozen=True)
class SoundProject:
    name: str
    tick_hz: int
    grid_ticks: int
    tracks: tuple[BgmTrack, ...]
    effects: tuple[SoundEffect, ...]


def normalize_label(value: object) -> str:
    text = str(value or "SOUND").upper()
    normalized = "".join(
        character
        if character.isascii()
        and (character.isalpha() or character.isdigit() or character == "_")
        else "_"
        for character in text
    )
    if not normalized:
        return "SOUND"
    if not (normalized[0].isalpha() or normalized[0] == "_"):
        return f"_{normalized}"
    return normalized


def build_package(project: Mapping[str, object]) -> bytes:
    """Return a ZIP archive containing an include file and a self-running demo PRG."""
    normalized = validate_project(project)
    assembly_assets = render_assembly(normalized)
    demo_source = render_demo_source(normalized)
    with tempfile.TemporaryDirectory(prefix="jr100_sound_build_") as temp_dir:
        temp_root = Path(temp_dir)
        assets_path = temp_root / "sound_assets.inc"
        source_path = temp_root / "sound_demo.asm"
        assets_path.write_text(assembly_assets, encoding="utf-8")
        source_path.write_text(demo_source, encoding="utf-8")
        result = Assembler(demo_source, filename=str(source_path)).assemble()

    raw_binary = result.machine_code
    program = pack_prg(result.origin, raw_binary, result.entry_point, program_name="SOUND DEMO")
    map_text = "".join(f"{name} = ${value:04X}\n" for name, value in result.symbols.items())
    output = BytesIO()
    with ZipFile(output, "w", compression=ZIP_DEFLATED) as archive:
        archive.writestr("sound_assets.inc", assembly_assets)
        archive.writestr("sound_demo.prg", program)
        archive.writestr("sound_demo.bin", raw_binary)
        archive.writestr("sound_demo.map", map_text)
    return output.getvalue()


def validate_project(project: Mapping[str, object]) -> SoundProject:
    if not isinstance(project, Mapping):
        raise ProjectValidationError("Sound project must be an object")
    if project.get("version") != PROJECT_VERSION:
        raise ProjectValidationError("Unsupported sound project version")
    tick_hz = positive_int(project.get("tickHz"), "tickHz", maximum=240)
    grid_ticks = positive_int(project.get("gridTicks"), "gridTicks", maximum=255)
    name = required_text(project.get("name"), "Project name")
    all_tracks = validate_tracks(project.get("tracks"), grid_ticks)
    all_effects = validate_effects(project.get("effects"), {track.asset_id for track in all_tracks})
    tracks = tuple(track for track in all_tracks if track.included)
    effects = tuple(effect for effect in all_effects if effect.included)
    if not tracks:
        raise ProjectValidationError("At least one selected BGM track is required to build demo PRG")
    return SoundProject(
        name=name,
        tick_hz=tick_hz,
        grid_ticks=grid_ticks,
        tracks=tracks,
        effects=effects,
    )


def validate_tracks(raw_tracks: object, grid_ticks: int) -> tuple[BgmTrack, ...]:
    if not isinstance(raw_tracks, list) or not raw_tracks:
        raise ProjectValidationError("At least one BGM track is required")
    track_ids: set[str] = set()
    labels: set[str] = set()
    tracks: list[BgmTrack] = []
    for raw_track in raw_tracks:
        if not isinstance(raw_track, Mapping):
            raise ProjectValidationError("BGM track must be an object")
        asset_id = required_text(raw_track.get("id"), "BGM id")
        ensure_unique(asset_id, track_ids, "BGM ids")
        label = normalize_label(asset_id)
        ensure_unique(label, labels, "BGM labels")
        notes = validate_notes(raw_track.get("notes"), "BGM notes")
        loop_cell = raw_track.get("loopCell", -1)
        if (
            not isinstance(loop_cell, int)
            or isinstance(loop_cell, bool)
            or loop_cell < -1
            or loop_cell >= len(notes)
        ):
            raise ProjectValidationError("loopCell must be -1 or a BGM cell index")
        name = required_text(raw_track.get("name"), "BGM name")
        validate_sample_track(raw_track, asset_id, name, notes, loop_cell)
        events, loop_event = encode_cells(notes, grid_ticks, loop_cell)
        tracks.append(BgmTrack(
            asset_id=asset_id,
            name=name,
            events=events,
            loop_event=loop_event,
            included=asset_included(raw_track),
        ))
    return tuple(tracks)


def validate_effects(raw_effects: object, known_ids: set[str]) -> tuple[SoundEffect, ...]:
    if not isinstance(raw_effects, list):
        raise ProjectValidationError("Effects must be an array")
    labels: set[str] = set()
    effects: list[SoundEffect] = []
    for raw_effect in raw_effects:
        if not isinstance(raw_effect, Mapping):
            raise ProjectValidationError("SFX must be an object")
        asset_id = required_text(raw_effect.get("id"), "SFX id")
        ensure_unique(asset_id, known_ids, "Sound asset ids")
        label = normalize_label(asset_id)
        ensure_unique(label, labels, "SFX labels")
        notes = validate_notes(raw_effect.get("notes"), "SFX notes")
        if len(notes) > MAX_SFX_UNITS:
            raise ProjectValidationError(f"SFX may not exceed {MAX_SFX_UNITS} units")
        name = required_text(raw_effect.get("name"), "SFX name")
        validate_sample_effect(raw_effect, asset_id, name, notes)
        events, _ = encode_cells(notes, 1, -1)
        effects.append(SoundEffect(
            asset_id=asset_id,
            name=name,
            events=events,
            included=asset_included(raw_effect),
        ))
    return tuple(effects)


def positive_int(value: object, name: str, maximum: int) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1 or value > maximum:
        raise ProjectValidationError(f"{name} must be between 1 and {maximum}")
    return value


def required_text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ProjectValidationError(f"{name} is required")
    return value.strip()


def validate_asset_origin(asset: Mapping[str, object]) -> str:
    origin = asset.get("origin", "user")
    if origin not in {"sample", "user"}:
        raise ProjectValidationError("Sound asset origin must be sample or user")
    return origin


def validate_sample_track(
    asset: Mapping[str, object], asset_id: str, name: str, notes: Sequence[int], loop_cell: int
) -> None:
    origin = validate_asset_origin(asset)
    expected = SAMPLE_TRACKS.get(asset_id)
    if origin == "user" and expected:
        if "origin" not in asset and expected == (name, tuple(notes), loop_cell):
            return
        raise ProjectValidationError("Built-in sample ids are reserved")
    if origin != "sample":
        return
    if expected != (name, tuple(notes), loop_cell):
        raise ProjectValidationError("Sample assets must match the built-in library")


def validate_sample_effect(
    asset: Mapping[str, object], asset_id: str, name: str, notes: Sequence[int]
) -> None:
    origin = validate_asset_origin(asset)
    expected = SAMPLE_EFFECTS.get(asset_id)
    if origin == "user" and expected:
        if "origin" not in asset and expected == (name, tuple(notes)):
            return
        raise ProjectValidationError("Built-in sample ids are reserved")
    if origin != "sample":
        return
    if expected != (name, tuple(notes)):
        raise ProjectValidationError("Sample assets must match the built-in library")


def asset_included(asset: Mapping[str, object]) -> bool:
    included = asset.get("included", True)
    if not isinstance(included, bool):
        raise ProjectValidationError("Sound asset included must be boolean")
    return included


def ensure_unique(value: str, known: set[str], name: str) -> None:
    if value in known:
        raise ProjectValidationError(f"{name} must be unique")
    known.add(value)


def validate_notes(value: object, name: str) -> list[int]:
    if not isinstance(value, list) or not value:
        raise ProjectValidationError(f"{name} are required")
    if any(
        not isinstance(pitch, int)
        or isinstance(pitch, bool)
        or pitch < 0
        or pitch > MAX_PITCH
        for pitch in value
    ):
        raise ProjectValidationError(f"{name} must contain pitches from 0 through {MAX_PITCH}")
    return list(value)


def encode_cells(
    notes: Sequence[int], duration_per_cell: int, loop_cell: int
) -> tuple[tuple[SoundEvent, ...], int]:
    events: list[SoundEvent] = []
    loop_event = -1
    for index, pitch in enumerate(notes):
        if index == loop_cell:
            loop_event = len(events)
        events.append(SoundEvent(pitch, duration_per_cell))
    if len(events) > 255:
        raise ProjectValidationError("Sound asset has more than 255 events")
    return tuple(events), loop_event


def render_assembly(project: SoundProject) -> str:
    lines = [
        "; Generated JR-100 sound assets",
        f"SOUND_TICK_HZ: .equ {project.tick_hz}",
        "",
        ".data",
    ]
    for track in project.tracks:
        label = f"SOUND_BGM_{normalize_label(track.asset_id)}"
        lines.extend([
            f"{label}:",
            f"        .word {label}_EVENTS",
            "        .byte "
            f"{len(track.events)}, "
            f"{format_byte(0xFF if track.loop_event < 0 else track.loop_event)}",
            f"{label}_EVENTS:",
        ])
        lines.extend(format_event(event) for event in track.events)
    for effect in project.effects:
        label = f"SOUND_SFX_{normalize_label(effect.asset_id)}"
        lines.append(f"{label}:")
        lines.append(f"        .byte {len(effect.events)}")
        lines.extend(format_event(event) for event in effect.events)
    return "\n".join(lines) + "\n"


def format_event(event: SoundEvent) -> str:
    return f"        .byte {format_byte(event.pitch)}, {format_byte(event.duration)}"


def format_byte(value: int) -> str:
    return f"${value:02X}"


def render_demo_source(project: SoundProject) -> str:
    first_label = f"SOUND_BGM_{normalize_label(project.tracks[0].asset_id)}"
    delay_count = max(1, min(0xFFFF, round(894_000 / project.tick_hz / 8)))
    return f"""        .org $0300
        JMP MAIN

        .include \"sound.inc\"
        .include \"sound_assets.inc\"

        .code
MAIN:
        JSR SOUND_INIT
        LDX #{first_label}
        JSR SOUND_PLAY_BGM
DEMO_LOOP:
        JSR SOUND_TICK
        JSR DEMO_WAIT
        BRA DEMO_LOOP

DEMO_WAIT:
        LDX #${delay_count:04X}
DEMO_WAIT_LOOP:
        DEX
        BNE DEMO_WAIT_LOOP
        RTS
"""


class SoundEditorHandler(SimpleHTTPRequestHandler):
    """Serve editor files and return build archives only from localhost."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, directory=str(Path(__file__).resolve().parent), **kwargs)

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/api/build":
            self.send_error(HTTPStatus.NOT_FOUND, "Unknown API path")
            return
        content_length = self.headers.get("Content-Length")
        try:
            length = int(content_length or "0")
        except ValueError:
            self.send_error(HTTPStatus.BAD_REQUEST, "Invalid Content-Length")
            return
        if length < 1 or length > MAX_REQUEST_BYTES:
            self.send_error(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, "Invalid request size")
            return
        try:
            project = json.loads(self.rfile.read(length).decode("utf-8"))
            archive = build_package(project)
        except (
            UnicodeDecodeError,
            json.JSONDecodeError,
            ProjectValidationError,
            ValueError,
        ) as error:
            self.send_error(HTTPStatus.BAD_REQUEST, str(error))
            return
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/zip")
        self.send_header("Content-Disposition", 'attachment; filename="jr100-sound-build.zip"')
        self.send_header("Content-Length", str(len(archive)))
        self.end_headers()
        self.wfile.write(archive)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the local JR-100 sound editor")
    parser.add_argument("--port", type=int, default=8001)
    args = parser.parse_args(argv)
    server = ThreadingHTTPServer(("127.0.0.1", args.port), SoundEditorHandler)
    print(f"JR-100 sound editor: http://127.0.0.1:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
