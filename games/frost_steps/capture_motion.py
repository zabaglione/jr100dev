"""Record an input-only first-stage clear, including the emulator's actual PCM."""

import argparse
import ctypes as C
import json
import subprocess
import sys
import wave
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "tests"))
from machine import KEYS, Machine, lib


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom", type=Path, required=True)
    args = parser.parse_args()
    output = ROOT / "build/motion"
    output.mkdir(parents=True, exist_ok=True)
    machine = Machine("frost_steps", args.rom.read_bytes())
    machine.action(5)
    lib.audio_peak(machine.p)
    frames, pcm = [], bytearray()
    frame_index = 0

    def run(count):
        nonlocal frame_index
        for _ in range(count):
            lib.frame(machine.p)
            size = lib.audio_size(machine.p)
            samples = (C.c_int16 * size)()
            lib.audio_copy(machine.p, samples)
            pcm.extend(bytes(samples))
            if frame_index % 2 == 0:
                pixels = C.create_string_buffer(256 * 192)
                lib.pixels(machine.p, pixels)
                image = Image.frombytes(
                    "L", (256, 192), bytes(255 if v else 0 for v in pixels.raw)
                )
                image = ImageOps.expand(
                    image.resize((768, 576), Image.Resampling.NEAREST),
                    border=24,
                    fill=0,
                )
                image.save(output / f"{len(frames):04}.png")
                frames.append(image)
            frame_index += 1

    run(30)
    route = json.loads((ROOT / "solutions.json").read_text())[0]
    for index, action in enumerate(route):
        lib.key(machine.p, *KEYS[action], 1)
        run(6)
        lib.key(machine.p, *KEYS[action], 0)
        run(234 if index == len(route) - 1 else 84)
        assert machine.get("MODE") == (2 if index == len(route) - 1 else 1)
    with wave.open(str(output / "sound.wav"), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(44100)
        wav.writeframes(pcm)
    frames[0].save(
        ROOT / "images/slide-clear.gif",
        save_all=True,
        append_images=frames[1:],
        duration=33,
        loop=0,
        optimize=True,
    )
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-loglevel",
            "error",
            "-framerate",
            "30",
            "-i",
            str(output / "%04d.png"),
            "-i",
            str(output / "sound.wav"),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-crf",
            "20",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            "-movflags",
            "+faststart",
            "-shortest",
            str(ROOT / "images/slide-clear.mp4"),
        ],
        check=True,
    )
    print(
        f"Captured {len(frames)} actual frames and {len(pcm) // 2} PCM samples; no state writes"
    )


if __name__ == "__main__":
    main()
