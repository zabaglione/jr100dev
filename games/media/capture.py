"""Record genuine-ROM, input-only game demonstrations at the JR-100 clock rate.

Long games use a digest unless selected for full-length publication. Playback
is never accelerated. Cut lists, inputs, final states and PRG hashes are retained.
"""

import argparse
import ctypes as C
import hashlib
import importlib.util
import json
import random
import re
import subprocess
import sys
import types
import wave
from contextlib import ExitStack
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "tests"), str(ROOT / "native")]
from checks import Model, assert_state
from machine import Machine, lib
from replay import Player, solve_stage

CALLBACK = C.CFUNCTYPE(None, C.c_void_p)
lib.record_frames.argtypes = [C.c_void_p, CALLBACK, C.c_void_p]
lib.record_frames.restype = None
lib.host_mutations.argtypes = [C.c_void_p]
lib.host_mutations.restype = C.c_uint
CLOCK = 894000
FPS = 30
LUT = bytes([0] + [255] * 255)
FUSE_READ_SECONDS = 0.8
FUSE_ROW_SECONDS = 0.75


def load_module(game, name):
    key = f"media_{game}_{name}"
    spec = importlib.util.spec_from_file_location(key, ROOT / game / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[key] = module
    spec.loader.exec_module(module)
    return module


def idle(m, seconds):
    lib.ticks(m.p, round(seconds * CLOCK))
    m.until("POLL_DONE" if m.directory.name == "relic_dive" else "INPUT_DONE")


class Recorder:
    def __init__(self, m, directory):
        self.m = m
        self.directory = directory
        directory.mkdir(parents=True, exist_ok=True)
        self.base = lib.clocks(m.p)
        self.frames = 0
        self.events = []
        self.fusion_slot = None
        self.last_fusion = 0
        self.last_combat = 0
        if m.metadata["id"] == "phase-pairs":
            slots = json.loads((m.directory / "build/state_slots.json").read_text())
            self.fusion_slot = m.sym[slots["s.merging"]]
        self.error = None
        self.buffer = C.create_string_buffer(256 * 192)
        self.encoder = subprocess.Popen(
            [
                "ffmpeg",
                "-v",
                "error",
                "-y",
                "-f",
                "rawvideo",
                "-pix_fmt",
                "gray",
                "-s",
                "256x192",
                "-r",
                str(FPS),
                "-i",
                "pipe:0",
                "-an",
                "-c:v",
                "libx264",
                "-preset",
                "ultrafast",
                "-crf",
                "12",
                "-pix_fmt",
                "yuv420p",
                str(directory / "full.mp4"),
            ],
            stdin=subprocess.PIPE,
        )
        self.resources = ExitStack()
        self.wav = self.resources.enter_context(
            wave.open(str(directory / "audio.wav"), "wb")  # noqa: SIM115 - owned by ExitStack
        )
        self.wav.setparams((1, 2, 44100, 0, "NONE", "not compressed"))
        lib.audio_peak(m.p)
        self.callback = CALLBACK(self.frame)
        lib.record_frames(m.p, self.callback, None)

    @property
    def time(self):
        return (lib.clocks(self.m.p) - self.base) / CLOCK

    def frame(self, _):
        try:
            self.frames += 1
            if self.frames % 2 == 0:
                lib.pixels(self.m.p, self.buffer)
                self.encoder.stdin.write(self.buffer.raw.translate(LUT))
                if self.fusion_slot is not None:
                    phase = self.m.get(self.fusion_slot)
                    if phase == 2 and self.last_fusion != 2:
                        self.mark("fusion")
                    self.last_fusion = phase
                if self.m.metadata["id"] == "dice-relic":
                    effect = self.m.get("EVENT_KIND")
                    if effect and effect != self.last_combat:
                        self.mark(
                            "combat", effect=effect, value=self.m.get("EVENT_VALUE")
                        )
                    self.last_combat = effect
            size = lib.audio_size(self.m.p)
            pcm = (C.c_int16 * size)()
            lib.audio_copy(self.m.p, pcm)
            self.wav.writeframesraw(bytes(pcm))
        except Exception as exc:  # noqa: BLE001 - exceptions cannot cross the ctypes callback boundary
            self.error = exc

    def mark(self, kind, **fields):
        self.events.append({"time": round(self.time, 4), "kind": kind, **fields})

    def close(self):
        lib.record_frames(self.m.p, CALLBACK(), None)
        self.encoder.stdin.close()
        assert self.encoder.wait() == 0, "Video encoder failed"
        self.resources.close()
        if self.error:
            raise self.error


class DemoPlayer(Player):
    def __init__(self, name, rom, recorder=None, pacing=0):
        self.name = name
        self.pad = False
        self.capture = False
        self.actions = self.ticks = 0
        self.directory = ROOT / name
        self.m = Machine(name, rom)
        self.pacing = pacing
        self.rng = random.Random(name)
        self.rec = Recorder(self.m, recorder) if recorder else None
        if self.rec or self.m.metadata.get("seededDeck"):
            idle(self.m, 1.8)
        if self.rec:
            self.rec.mark("input", action=5)
        self.m.action(5)
        self.r = Model(name, machine=self.m)
        self.r.s.action = 5
        assert_state(self.m, self.r)
        if self.rec:
            self.rec.mark("stage-start")
            self.m.capture(recorder / "start.png")
            if name == "fuse_box":
                self.rec.mark("read-clues")
                idle(self.m, FUSE_READ_SECONDS)

    def press(self, a):
        if self.rec and self.m.metadata.get("rate", 255) == 255:
            # Cursor travel stays brisk; selecting/committing gets thinking time.
            weight = 1.5 if a == 5 else 0.8
            idle(self.m, self.pacing * weight * self.rng.uniform(0.8, 1.2))
        if self.rec:
            self.rec.mark("input", action=a)
        super().press(a)
        if self.rec:
            self.rec.mark("settled", action=a)
            if self.name == "fuse_box" and a == 5 and self.s.mode == 1:
                row = self.s.cursor // 5
                cells = slice(row * 5, row * 5 + 5)
                if sum(self.r.b[cells]) == sum(self.r.d[cells]):
                    remaining = [
                        sum(self.r.d[col:25:5]) - sum(self.r.b[col:25:5])
                        for col in range(5)
                    ]
                    self.rec.mark(
                        "row-complete", row=row + 1, remaining_columns=remaining
                    )
                    idle(self.m, FUSE_ROW_SECONDS)


def probe_native(name, rom):
    p = DemoPlayer(name, rom)
    before = lib.clocks(p.m.p)
    solve_stage(p)
    assert p.s.mode == 2, (name, "No first-stage clear", vars(p.s))
    return {
        "seconds": (lib.clocks(p.m.p) - before) / CLOCK,
        "actions": p.actions,
        "ticks": p.ticks,
    }


def choose_segments(duration, clear_time, full_length=False):
    """Keep the opening and unbroken final action/jingle at original speed."""
    if full_length or duration <= 35:
        return [[0, round(duration, 4)]]
    # A hard cut, visibly labelled in the player, removes only the middle.
    tail = max(10, min(16, duration - clear_time + 7))
    opening = 12
    middle = 30 - opening - tail
    mid_start = (opening + duration - tail - middle) / 2
    return [
        [0, opening],
        [round(mid_start, 4), round(mid_start + middle, 4)],
        [round(duration - tail, 4), round(duration, 4)],
    ]


def encode(rec, destination, clear_time, outcome, extra):
    duration = rec.frames // 2 / FPS
    segments = choose_segments(
        duration,
        clear_time,
        full_length=rec.m.metadata["id"]
        in ("peg-garden", "seed-merge", "dice-relic", "five-forge", "orbit-draft"),
    )
    filters = []
    for i, (start, end) in enumerate(segments):
        filters += [
            f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS[v{i}]",
            f"[1:a]atrim=start={start}:end={end},asetpts=PTS-STARTPTS[a{i}]",
        ]
    inputs = "".join(f"[v{i}][a{i}]" for i in range(len(segments)))
    filters += [f"{inputs}concat=n={len(segments)}:v=1:a=1[v][a]"]
    visual = "[v]scale=768:576:flags=neighbor,pad=816:624:24:24:black"
    elapsed = 0
    labels = []
    for start, end in segments[:-1]:
        elapsed += end - start
        labels.append(f"between(t,{elapsed},{elapsed + 1.2})")
    label_input = []
    if labels:
        from PIL import Image, ImageDraw, ImageFont

        label = Image.new("L", (816, 24))
        draw = ImageDraw.Draw(label)
        draw.text(
            (408, 12),
            "LATER",
            fill=255,
            anchor="mm",
            font=ImageFont.load_default(size=15),
        )
        label.save(rec.directory / "cut-label.png")
        label_input = ["-i", str(rec.directory / "cut-label.png")]
        filters += [
            visual + "[screen]",
            f"[screen][2:v]overlay=0:600:enable='{'+'.join(labels)}'[out]",
        ]
    else:
        filters.append(visual + "[out]")
    destination.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-y",
            "-i",
            str(rec.directory / "full.mp4"),
            "-i",
            str(rec.directory / "audio.wav"),
            *label_input,
            "-filter_complex",
            ";".join(filters),
            "-map",
            "[out]",
            "-map",
            "[a]",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "20",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "96k",
            "-movflags",
            "+faststart",
            "-map_metadata",
            "-1",
            str(rec.directory / "edited.mp4"),
        ],
        check=True,
    )
    # Three separate gameplay moments; retain the existing title and extra art.
    from shutil import copyfile

    copyfile(rec.directory / "edited.mp4", destination / "play.mp4")
    copyfile(rec.directory / "start.png", destination / "demo-start.png")
    copyfile(rec.directory / "clear.png", destination / "demo-clear.png")
    candidates = [
        e["time"]
        for e in rec.events
        if e["kind"] == "settled"
        and e["time"] < clear_time - 0.25
        and e.get("mode", 1) == 1
    ]
    fraction = {"loop_ten": 0.7, "relic_dive": 0.6}.get(rec.m.directory.name, 0.5)
    middle = (
        candidates[int(len(candidates) * fraction)] if candidates else clear_time / 2
    )
    if rec.m.metadata["id"] == "phase-pairs":
        fusions = [e["time"] for e in rec.events if e["kind"] == "fusion"]
        # The state precedes rendering; choose a frame once the ten is visible.
        middle = fusions[len(fusions) // 2] + 0.25
    if rec.m.metadata["id"] == "dice-relic":
        # Keep the three assignments and absorbed damage together in the image.
        middle = (
            next(
                e["time"]
                for e in rec.events
                if e["kind"] == "combat" and e["effect"] == 6
            )
            + 0.65
        )
    subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-y",
            "-ss",
            str(middle),
            "-i",
            str(rec.directory / "full.mp4"),
            "-frames:v",
            "1",
            "-vf",
            "scale=768:576:flags=neighbor,pad=816:624:24:24:black",
            str(destination / "demo-play.png"),
        ],
        check=True,
    )
    prg = ROOT / rec.m.directory.name / "build" / (rec.m.metadata["id"] + ".prg")
    report = {
        "id": rec.m.metadata["id"],
        "recording": "automated keyboard replay",
        "boot": "owned BASIC ROM and PRG autostart",
        "clock_hz": CLOCK,
        "fps": FPS,
        "source_seconds": round(duration, 3),
        "video_seconds": round(sum(b - a for a, b in segments), 3),
        "playback_speed": 1,
        "edited": len(segments) > 1,
        "source_segments": segments,
        "clear_time": round(clear_time, 4),
        "outcome": outcome,
        "host_state_writes": (
            rec.verified_writes
            if hasattr(rec, "verified_writes")
            else lib.host_mutations(rec.m.p)
        ),
        "prg_sha256": hashlib.sha256(prg.read_bytes()).hexdigest(),
        "images": ["demo-start.png", "demo-play.png", "demo-clear.png"],
        "events": rec.events,
        **extra,
    }
    assert report["host_state_writes"] == 0
    (destination / "play.json").write_text(json.dumps(report, indent=2) + "\n")
    print(
        f"PASS {report['id']}: {report['video_seconds']:.2f}s, "
        f"source {duration:.2f}s, {outcome}, no host writes",
        flush=True,
    )
    return report


def record_native(name, rom, work):
    probe_file = work / "probe.json"
    probe = (
        json.loads(probe_file.read_text())
        if probe_file.exists()
        else probe_native(name, rom)
    )
    work.mkdir(parents=True, exist_ok=True)
    probe_file.write_text(json.dumps(probe) + "\n")
    observations = FUSE_READ_SECONDS + 4 * FUSE_ROW_SECONDS if name == "fuse_box" else 0
    pacing = max(
        0.15,
        min(5.5, (25 - observations - probe["seconds"]) / max(1, probe["actions"])),
    )
    p = DemoPlayer(name, rom, work, pacing)
    try:
        if name == "pendulum_port":
            # Watch a swing before releasing each load, as a player would.
            last_drop = p.rec.time
            while p.s.mode == 1:
                if abs(p.s.swing - p.s.target) <= 1 and p.rec.time - last_drop >= 2.5:
                    p.press(5)
                    last_drop = p.rec.time
                if p.s.mode == 1:
                    p.wait()
        else:
            solve_stage(p)
        stages = 1
        if name == "lunar_touchdown" and p.rec.time < 20:
            p.rec.mark("clear")
            idle(p.m, 1)
            p.rec.mark("input", action=5)
            p.next()
            solve_stage(p)
            stages = 2
        assert p.s.mode == 2, (name, "No first-stage clear", vars(p.s))
        clear_time = p.rec.time
        p.rec.mark("clear")
        p.m.capture(work / "clear.png")
        idle(p.m, max(3, 30 - p.rec.time))
        assert p.s.mode == 2 and p.m.get("MODE") == 2
        assert_state(p.m, p.r)
        assert p.m.read(0x300, len(p.m.code)) == p.m.code
    finally:
        p.rec.close()
    return encode(
        p.rec,
        p.directory / "images",
        clear_time,
        "first stage cleared" if stages == 1 else "first two stages cleared",
        {
            "actions": p.actions,
            "ticks": p.ticks,
            "final_mode": 2,
            "stages_cleared": stages,
        },
    )


class DemoMachine(Machine):
    def action(self, number, pad=False):
        mean = {
            "loop_ten": 0.28,
            "chrono_breach": 1.4,
            "sigil_deck": 0.95,
            "dice_relic": 0.65,
            "trace_blade": 0.72,
        }.get(self.directory.name, 0.475)
        if self.directory.name == "dice_relic" and number != 5:
            mean = 0.28
        idle(self, mean * self.rng.uniform(0.8, 1.2))
        self.rec.mark("input", action=number)
        super().action(number, pad)
        self.rec.mark("settled", action=number, mode=self.get("MODE"))


class RelicMachine(DemoMachine):
    def __init__(self, rom):
        self.directory = ROOT / "relic_dive"
        self.metadata = json.loads((self.directory / "game.json").read_text())
        self.fonts = None
        self.sym = {
            key: int(value, 16)
            for key, value in re.findall(
                r"^(\w+)\s*=\s*\$([0-9A-Fa-f]+)",
                (self.directory / "build/relic-dive.map").read_text(),
                re.MULTILINE,
            )
        }
        self.code = (self.directory / "build/relic-dive.bin").read_bytes()
        self.p = lib.create(rom, len(rom))
        for _ in range(100):
            lib.frame(self.p)
        prg = (self.directory / "build/relic-dive.prg").read_bytes()
        assert lib.load_prg(self.p, prg, len(prg))
        for _ in range(450):
            lib.frame(self.p)
        self.until("POLL_DONE")
        assert self.get("G_MODE") == 0

    def action(self, number, pad=False):
        keys = {
            1: (2, 1),
            2: (0, 3),
            3: (1, 0),
            4: (1, 2),
            5: (8, 3),
            6: (8, 1),
            7: (2, 0),
            8: (2, 2),
            9: (0, 2),
            10: (0, 4),
            11: (1, 1),
        }
        idle(self, self.rng.uniform(0.18, 0.32))
        self.rec.mark("input", action=number)
        before = lib.clocks(self.p)
        lib.key(self.p, *keys[number], 1)
        self.until("DISPATCH", 90_000_000)
        self.until("FRAME_READY", 90_000_000)
        lib.key(self.p, *keys[number], 0)
        self.until("POLL_DONE")
        self.rec.mark("settled", action=number, mode=self.get("G_MODE"))
        return lib.clocks(self.p) - before

    def word(self, name):
        return int.from_bytes(self.read(name, 2), "big")

    def map(self):
        return [
            value
            for byte in self.read("FLOORS", self.sym["TERRAIN_BYTES"])
            for value in (byte & 15, byte >> 4)
        ]

    def entities(self):
        raw = self.read(self.sym["FLOORS"] + self.sym["ENEMY_START"], 256)
        return [list(raw[i : i + 8]) for i in range(0, 256, 8)]

    def items(self):
        raw = self.read(self.sym["FLOORS"] + self.sym["ITEM_START"], 96)
        return [list(raw[i : i + 3]) for i in range(0, 96, 3)]


def record_custom(name, rom, work):
    m = RelicMachine(rom) if name == "relic_dive" else DemoMachine(name, rom)
    m.rng = random.Random(name)
    m.rec = Recorder(m, work)
    try:
        idle(m, 1.8)
        if name == "relic_dive":
            m.action(1)  # EASY, selected through the ordinary title controls.
        m.action(5)
        if name == "dice_relic":
            model = load_module(name, "model")
            saved_model = sys.modules.get("model")
            sys.modules["model"] = model
            replay = load_module(name, "replay")
            if saved_model is None:
                del sys.modules["model"]
            else:
                sys.modules["model"] = saved_model
            replay.settle(m)
        m.rec.mark("stage-start")
        m.capture(work / "start.png")
        outcome = "first stage cleared"
        if name == "chrono_breach":
            path = json.loads((m.directory / "solutions.json").read_text())[0][
                "actions"
            ]
            for number in path:
                if number >= 9:
                    m.action(5)
                    while m.get("FACING") != number - 8:
                        m.action(4)
                    m.action(5)
                else:
                    m.action(number)
            assert m.get("MODE") == 4
        elif name == "sigil_deck":
            replay = load_module(name, "replay")
            for _ in range(150):
                if m.get("MODE") != 1:
                    break
                hand = m.read("HAND", 4)
                choices = [
                    (replay.preference(m, i, replay.CARDS[c]), i)
                    for i, c in enumerate(hand)
                    if c != 255 and replay.CARDS[c]["cost"] <= m.get("ENERGY")
                ]
                choices = [item for item in choices if item[0] > 0]
                replay.select(m, max(choices)[1] if choices else 4, False)
                m.action(5)
                replay.invariant(m)
            assert m.get("MODE") == 2
            outcome = "first battle won"
        elif name == "dice_relic":
            state = model.State(rng=m.get("RNG"), turn=1, dice=list(m.read("DICE", 3)))
            replay.compare(m, state)
            for _ in range(150):
                if state.mode != 1:
                    break
                if state.turn == 1:
                    # Start with a small guard die, then attack with the others.
                    # The first retaliation demonstrates shield absorption.
                    die = (
                        min(range(3), key=lambda i: state.dice[i])
                        if not state.used
                        else next(i for i in range(3) if not state.used >> i & 1)
                    )
                    choice = 1 if not state.used else 0
                elif state.hp < 42 and not state.used:
                    # Recover visible damage before committing the next attack.
                    die = min(range(3), key=lambda i: state.dice[i])
                    choice = 2
                else:
                    die, choice = replay.policy(state)
                replay.choose(m, die, choice, False)
                state.use(die, choice)
                replay.compare(m, state)
            assert state.mode == m.get("MODE") == 2
            outcome = "first battle won"
        elif name == "trace_blade":
            replay = load_module(name, "replay")
            for number in replay.LEVELS[0]["solution"]:
                m.action(number)
            m.action(8)
            replay.finish(m)
            assert m.get("MODE") == 4
        elif name == "loop_ten":
            replay = load_module(name, "replay")
            for room in range(2):
                if room:
                    m.action(5)
                    m.action(5)
                for number in replay.route(
                    room, (m.get("PLAYER_X"), m.get("PLAYER_Y")), (12, 4)
                ):
                    m.action(number)
                m.action(5)
                assert m.get("FLAGS") == (1 << (room + 1)) - 1
            outcome = "first two chamber seals collected"
        elif name == "abyss_signal":
            model = load_module(name, "model")
            saved_model = sys.modules.get("model")
            sys.modules["model"] = model
            replay = load_module(name, "replay")
            if saved_model is None:
                del sys.modules["model"]
            else:
                sys.modules["model"] = saved_model
            state = model.State()
            for i, target in enumerate([*model.SITES, (2, 2)]):
                if i < 5:
                    replay.act(m, 8, False)
                    state = model.advance(state, 8)
                for number in model.route(state, target, 1 if i < 5 else 0):
                    replay.act(m, number, False)
                    state = model.advance(state, number)
                    replay.compare(m, state)
                if i < 5:
                    replay.act(m, 9, False)
                    state = model.advance(state, 9)
                    assert state.mode == 3
                    m.action(5)
                    state.mode = 1
            assert state.mode == m.get("MODE") == 5 and state.flags == 31
            outcome = "all five records recovered and returned to base"
        elif name == "relic_dive":
            # Reuse the read-only route policy against the real BASIC-booted core.
            saved = sys.modules["machine"]
            sys.modules["machine"] = types.SimpleNamespace(
                ROOT=m.directory, SYMS=m.sym, Machine=RelicMachine, lib=lib
            )
            replay = load_module(name, "tests/play_game")
            sys.modules["machine"] = saved

            class RelicPlayer(replay.Player):
                def menu(self, index):
                    tile = self.m.map()[
                        self.m.get("G_Y") * replay.WIDTH + self.m.get("G_X")
                    ]
                    if index == 1 + int(tile == 3):
                        self.press(11)  # The visible S shortcut waits one turn.
                    else:
                        super().menu(index)

            player = RelicPlayer.__new__(RelicPlayer)
            player.m = m
            player.actions = []
            player.max_turn = player.max_floor = 0
            player.difficulty = player.wait = player.policy = 0
            player.route_cache = None
            result = player.run(limit=1500, stop_floor=1, save=False)
            assert result["mode"] == 1 and result["floor"] == 2
            outcome = "first floor completed; entered floor 2"
        else:
            raise ValueError(name)
        clear_time = m.rec.time
        m.rec.mark("clear")
        m.capture(work / "clear.png")
        idle(m, max(3, 30 - m.rec.time))
        assert m.read(0x300, len(m.code)) == m.code
    finally:
        m.rec.close()
    return encode(
        m.rec,
        m.directory / "images",
        clear_time,
        outcome,
        {
            "actions": sum(e["kind"] == "input" for e in m.rec.events),
            "final_mode": m.get("G_MODE" if name == "relic_dive" else "MODE"),
        },
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("games", nargs="*")
    parser.add_argument("--rom", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--probe", action="store_true")
    parser.add_argument("--reencode", action="store_true")
    args = parser.parse_args()
    games = args.games or json.loads((ROOT / "collection.json").read_text())["games"]
    rom = args.rom.read_bytes()
    for name in games:
        metadata = json.loads((ROOT / name / "game.json").read_text())
        if args.reencode:
            report = json.loads((ROOT / name / "images/play.json").read_text())
            rec = types.SimpleNamespace(
                frames=round(report["source_seconds"] * 60),
                directory=args.work / name,
                events=report["events"],
                m=types.SimpleNamespace(directory=ROOT / name, metadata=metadata),
                verified_writes=report["host_state_writes"],
            )
            extra = {
                key: report[key]
                for key in ("actions", "ticks", "final_mode", "stages_cleared")
                if key in report
            }
            encode(
                rec,
                ROOT / name / "images",
                report["clear_time"],
                report["outcome"],
                extra,
            )
        elif args.probe:
            assert metadata.get("nativeRules"), "Probe supports native games only"
            result = probe_native(name, rom)
            work = args.work / name
            work.mkdir(parents=True, exist_ok=True)
            (work / "probe.json").write_text(json.dumps(result) + "\n")
            print(name, result, flush=True)
        else:
            record = record_native if metadata.get("nativeRules") else record_custom
            record(name, rom, args.work / name)


if __name__ == "__main__":
    main()
