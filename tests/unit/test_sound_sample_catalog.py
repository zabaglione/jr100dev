"""Keep the browser and local-builder sample catalogs identical."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess

from tools.sound_editor.server import SAMPLE_EFFECTS, SAMPLE_TRACKS, validate_project


ROOT = Path(__file__).resolve().parents[2]


def test_browser_and_builder_sample_catalogs_match() -> None:
    script = """
        import { createProject } from './tools/sound_editor/core.js';
        const project = createProject();
        process.stdout.write(JSON.stringify({ tracks: project.tracks, effects: project.effects }));
    """
    result = subprocess.run(
        ["node", "--input-type=module", "--eval", script],
        cwd=ROOT,
        capture_output=True,
        check=True,
        text=True,
    )
    catalog = json.loads(result.stdout)
    browser_tracks = {
        track["id"]: (track["name"], tuple(track["notes"]), track["loopCell"])
        for track in catalog["tracks"]
    }
    browser_effects = {
        effect["id"]: (effect["name"], tuple(effect["notes"]))
        for effect in catalog["effects"]
    }

    assert browser_tracks == SAMPLE_TRACKS
    assert browser_effects == SAMPLE_EFFECTS
    assert validate_project({
        "version": 1,
        "name": "Sample Catalog",
        "tickHz": 60,
        "gridTicks": 6,
        "tracks": catalog["tracks"],
        "effects": catalog["effects"],
    })
