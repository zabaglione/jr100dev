from __future__ import annotations

from io import BytesIO
from zipfile import ZipFile

from tools.sound_editor.server import build_package


def test_builder_returns_demo_prg_and_include_without_writing_project_files() -> None:
    project = {
        "version": 1,
        "name": "Build Test",
        "tickHz": 60,
        "gridTicks": 6,
        "tracks": [
            {
                "id": "build-track",
                "name": "Build Track",
                "notes": [25, 25, 0, 29],
                "loopCell": 0,
            }
        ],
        "effects": [
            {"id": "blip", "name": "Blip", "notes": [37, 0]},
        ],
    }

    payload = build_package(project)

    with ZipFile(BytesIO(payload)) as archive:
        assert set(archive.namelist()) == {
            "sound_assets.inc",
            "sound_demo.prg",
            "sound_demo.bin",
            "sound_demo.map",
        }
        assert b"SOUND_BGM_BUILD_TRACK" in archive.read("sound_assets.inc")
        assert archive.read("sound_demo.prg")
        assert b"SOUND_PLAY_BGM" in archive.read("sound_demo.map")
