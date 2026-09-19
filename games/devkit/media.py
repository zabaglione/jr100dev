"""Capture actual ROM-booted frames and PCM, using only normal inputs."""

import importlib.util
import json
import subprocess
import wave

from devkit.project import ROOT, Problem, digest, require
from devkit.verify import KEYS, expect, harness, load_replay


def capture(directory, rom_path):
    require(rom_path is not None and rom_path.is_file(), "A user-owned ROM file is required for capture.", rom_path,
            "Pass --rom /path/to/owned-rom.prg (or set JR100_ROM). Test needs no ROM.")
    checks = harness()
    spec = importlib.util.spec_from_file_location("devkit_recorder", ROOT / "media/capture.py")
    recorder_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(recorder_module)
    data = load_replay(directory)
    scenario = next(s for s in data["scenarios"] if s["name"] == data["demo"])
    output = directory / "build/media"
    output.mkdir(parents=True, exist_ok=True)
    m = checks.Machine(str(directory), rom=rom_path.read_bytes())
    recorder = None
    images, events = [], []
    try:
        require(checks.lib.host_mutations(m.p) == 0, "Capture must boot through BASIC without host state writes.")
        recorder = recorder_module.Recorder(m, output / "raw")
        recorder_module.idle(m, 1.8)
        m.capture(output / "title.png")
        images.append("title.png")
        events.append({"time": round(recorder.time, 4), "press": "RETURN"})
        m.action(5)
        recorder_module.idle(m, 0.5)
        for i, step in enumerate(scenario["steps"]):
            if "press" in step:
                for _ in range(step.get("repeat", 1)):
                    recorder_module.idle(m, 0.35)
                    events.append({"time": round(recorder.time, 4), "press": step["press"]})
                    m.action(KEYS[step["press"]])
                    if m.get("CN_ACTIVE"):
                        require("confirm" in step, "Demo opened a confirmation without an answer.")
                        m.answer_reset(step["confirm"])
                        events[-1]["confirm"] = step["confirm"]
            elif "ticks" in step:
                events.append({"time": round(recorder.time, 4), "ticks": step["ticks"]})
                for _ in range(step["ticks"]):
                    require(m.get("MODE") == 1, "Demo tick requires active gameplay.")
                    m.until("FN_TICK")
                    m.until("FRAME_READY")
                    m.until("INPUT_DONE")
            try:
                expect(m, step.get("expect", {}))
            except AssertionError as exc:
                raise Problem("CAPTURE_REPLAY", f"Demo step {i+1}: {exc}", "Recording includes real elapsed time. Adjust game timing or author a stable demo; never patch emulator state.") from exc
            if "capture" in step:
                filename = step["capture"] + ".png"
                m.capture(output / filename)
                m.export_workbench(output / (step["capture"] + ".pcg.json"))
                images.append(filename)
                events.append({"time": round(recorder.time, 4), "capture": filename})
        require(m.get("MODE") in (2, 4), "The demo must finish at a verified clear or ending.", hint="Author a complete successful input path in tests/replay.json.")
        recorder_module.idle(m, max(2, 25.2 - recorder.time))
        outcome = m.get("MODE")
        writes = checks.lib.host_mutations(m.p)
        require(writes == 0, "Host mutations occurred during capture.")
        require(len(images) >= 3, "Add at least two named capture steps to the demo.")
        seconds = recorder.time
    finally:
        try:
            if recorder is not None:
                recorder.close()
        finally:
            m.__del__()
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(output / "raw/full.mp4"), "-i", str(output / "raw/audio.wav"),
                    "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "96k", "-shortest", "-map_metadata", "-1", "-movflags", "+faststart", str(output / "play.mp4")], check=True, timeout=120)
    with wave.open(str(output / "raw/audio.wav"), "rb") as wav:
        require(wav.getnchannels() == 1 and wav.getframerate() == 44100 and any(wav.readframes(wav.getnframes())), "Capture PCM is missing or completely silent.")
    probe = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(output / "play.mp4")], text=True, timeout=30))
    kinds = {s["codec_type"] for s in probe["streams"]}
    require({"video", "audio"} <= kinds and float(probe["format"]["duration"]) > 0, "Encoded video/audio validation failed.")
    return {"evidence": "user-owned-ROM emulator; not physical hardware", "host_state_writes": writes,
            "playback_speed": 1, "edited": False, "outcome": "ending" if outcome == 4 else "clear", "scenario": scenario["name"],
            "seconds": round(seconds, 3), "images": images, "events": events,
            "files": {name: digest(output / name) for name in ["play.mp4", *images]}}
