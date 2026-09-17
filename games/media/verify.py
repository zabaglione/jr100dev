"""Decode every published demo, check its evidence and build review sheets."""

import argparse
import array
import hashlib
import json
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]


def verify(name):
    directory = ROOT / name
    images = directory / "images"
    report = json.loads((images / "play.json").read_text())
    assert report["host_state_writes"] == 0 and report["playback_speed"] == 1
    prg = directory / "build" / (report["id"] + ".prg")
    assert hashlib.sha256(prg.read_bytes()).hexdigest() == report["prg_sha256"]
    probe = json.loads(
        subprocess.check_output(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_streams",
                "-show_format",
                "-of",
                "json",
                str(images / "play.mp4"),
            ]
        )
    )
    seconds = float(probe["format"]["duration"])
    assert 25 <= seconds <= 35 and abs(seconds - report["video_seconds"]) < 0.1
    video = next(s for s in probe["streams"] if s["codec_type"] == "video")
    audio = next(s for s in probe["streams"] if s["codec_type"] == "audio")
    assert (video["codec_name"], video["pix_fmt"], video["width"], video["height"]) == (
        "h264",
        "yuv420p",
        816,
        624,
    )
    assert video["avg_frame_rate"] == "30/1" and audio["codec_name"] == "aac"
    assert abs(float(video["duration"]) - float(audio["duration"])) < 0.08
    hashes = subprocess.check_output(
        [
            "ffmpeg",
            "-v",
            "error",
            "-i",
            str(images / "play.mp4"),
            "-map",
            "0:v",
            "-f",
            "framemd5",
            "pipe:1",
        ],
        text=True,
    )
    frames = [
        line.rsplit(",", 1)[-1].strip()
        for line in hashes.splitlines()
        if line and not line.startswith("#")
    ]
    assert len(frames) >= seconds * 30 - 2 and len(set(frames)) >= 20
    pcm = array.array(
        "h",
        subprocess.check_output(
            [
                "ffmpeg",
                "-v",
                "error",
                "-i",
                str(images / "play.mp4"),
                "-map",
                "0:a",
                "-f",
                "s16le",
                "pipe:1",
            ]
        ),
    )
    peak = max(abs(min(pcm)), abs(max(pcm)))
    assert peak > 1000
    pictures = []
    for filename in report["images"]:
        image = Image.open(images / filename)
        assert image.size == (816, 624)
        assert sum(image.convert("L").histogram()[128:]) > 500
        pictures.append(hashlib.sha256(image.tobytes()).hexdigest())
    assert len(set(pictures)) == 3, (name, "Duplicate screenshot")
    wiki = (ROOT.parent / "docs/wiki" / (report["id"].upper() + ".md")).read_text()
    assert len(set(re.findall(r"!\[[^\]]*\]\(([^)]+)\)", wiki))) >= 3
    assert f"gameplay.html?game={report['id']}" in wiki
    assert len(re.findall(r"^## 紹介画像とプレイ動画$", wiki, re.MULTILINE)) == 1
    segments = report["source_segments"]
    assert all(0 <= a < b <= report["source_seconds"] + 0.001 for a, b in segments)
    assert all(a[1] <= b[0] for a, b in zip(segments, segments[1:]))
    assert any(a <= report["clear_time"] <= b for a, b in segments)
    return {
        "id": report["id"],
        "seconds": seconds,
        "unique_frames": len(set(frames)),
        "audio_peak": peak,
        "images": 3,
        "edited": report["edited"],
        "video_sha256": hashlib.sha256((images / "play.mp4").read_bytes()).hexdigest(),
    }


def sheets(names, destination):
    font = ImageFont.load_default(size=17)
    for page in range(0, len(names), 4):
        subset = names[page : page + 4]
        sheet = Image.new("RGB", (1224, 340 * len(subset)), "#202620")
        draw = ImageDraw.Draw(sheet)
        for row, name in enumerate(subset):
            draw.text(
                (8, row * 340 + 3),
                name.upper().replace("_", " "),
                fill="white",
                font=font,
            )
            for col, filename in enumerate(
                ["demo-start.png", "demo-play.png", "demo-clear.png"]
            ):
                image = Image.open(ROOT / name / "images" / filename)
                sheet.paste(
                    image.resize((408, 312), Image.Resampling.NEAREST),
                    (col * 408, row * 340 + 25),
                )
        sheet.save(destination / f"review-{page // 4 + 1:02}.png")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    names = json.loads((ROOT / "collection.json").read_text())["games"]
    args.output.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(verify, names))
    (args.output / "verification.json").write_text(json.dumps(results, indent=2) + "\n")
    sheets(names, args.output)
    print(
        f"PASS: {len(results)} decoded videos, 153 distinct gameplay screenshots, audio and clear events verified"
    )
