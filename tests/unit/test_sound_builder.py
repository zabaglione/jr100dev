from __future__ import annotations

from io import BytesIO
from zipfile import ZipFile

import pytest

from tools.sound_editor.server import ProjectValidationError, build_package


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
                "included": True,
            },
            {
                "id": "not-included",
                "name": "Not Included",
                "notes": [25],
                "loopCell": 0,
                "included": False,
            }
        ],
        "effects": [
            {"id": "build-effect", "name": "Build Effect", "notes": [37, 0], "included": True},
            {"id": "not-included-sfx", "name": "Not Included SFX", "notes": [37], "included": False},
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
        assets = archive.read("sound_assets.inc")
        assert b"SOUND_BGM_BUILD_TRACK" in assets
        assert b"SOUND_BGM_NOT_INCLUDED" not in assets
        assert b"SOUND_SFX_NOT_INCLUDED_SFX" not in assets
        assert b"        .byte 4, $00" in assets
        assert b"        .byte $19, $06\n        .byte $19, $06" in assets
        assert archive.read("sound_demo.prg")
        assert b"SOUND_PLAY_BGM" in archive.read("sound_demo.map")


def test_builder_requires_a_selected_bgm_for_demo_prg() -> None:
    project = {
        "version": 1,
        "name": "SFX Only",
        "tickHz": 60,
        "gridTicks": 6,
        "tracks": [
            {
                "id": "music",
                "name": "Music",
                "notes": [25],
                "loopCell": 0,
                "included": False,
            }
        ],
        "effects": [{"id": "build-effect", "name": "Build Effect", "notes": [37], "included": True}],
    }

    with pytest.raises(ProjectValidationError, match="selected BGM"):
        build_package(project)


def test_builder_rejects_a_hand_edited_read_only_sample() -> None:
    project = {
        "version": 1,
        "name": "Changed Sample",
        "tickHz": 60,
        "gridTicks": 6,
        "tracks": [
            {
                "id": "ode-to-joy-opening",
                "name": "Ode To Joy Opening",
                "notes": [18, 17, 18, 20, 20, 18, 17, 15, 13, 13, 15, 17, 17, 15, 15, 0],
                "loopCell": 0,
                "origin": "sample",
                "included": True,
            }
        ],
        "effects": [],
    }

    with pytest.raises(ProjectValidationError, match="Sample assets"):
        build_package(project)


def test_builder_reserves_builtin_sample_ids_for_read_only_samples() -> None:
    project = {
        "version": 1,
        "name": "Changed Sample",
        "tickHz": 60,
        "gridTicks": 6,
        "tracks": [
            {
                "id": "ode-to-joy-opening",
                "name": "User Version",
                "notes": [25],
                "loopCell": 0,
                "origin": "user",
                "included": True,
            }
        ],
        "effects": [],
    }

    with pytest.raises(ProjectValidationError, match="reserved"):
        build_package(project)


def test_builder_accepts_an_unmodified_legacy_sample_without_origin() -> None:
    project = {
        "version": 1,
        "name": "Legacy Sample",
        "tickHz": 60,
        "gridTicks": 6,
        "tracks": [
            {
                "id": "ode-to-joy-opening",
                "name": "Ode To Joy Opening",
                "notes": [17, 17, 18, 20, 20, 18, 17, 15, 13, 13, 15, 17, 17, 15, 15, 0],
                "loopCell": 0,
                "included": True,
            }
        ],
        "effects": [],
    }

    assert build_package(project)


def test_builder_upgrades_a_previous_four_cell_sample() -> None:
    project = {
        "version": 1,
        "name": "Legacy Four Cell Sample",
        "tickHz": 60,
        "gridTicks": 6,
        "tracks": [
            {
                "id": "fur-elise-opening",
                "name": "Fur Elise Opening",
                "notes": [29, 28, 29, 28],
                "loopCell": 0,
                "origin": "sample",
                "included": True,
            }
        ],
        "effects": [],
    }

    payload = build_package(project)

    with ZipFile(BytesIO(payload)) as archive:
        assets = archive.read("sound_assets.inc")
    assert b".byte 16, $00" in assets
    assert b".byte $1D, $06\n        .byte $1C, $06" in assets
