"""Allowlisted release bundles and transactional local web deployment."""

import html
import json
import shutil
import tempfile
import zipfile
from pathlib import Path

from devkit.project import ROOT, digest, fingerprint, read_json, require
from devkit.scaffold import write_json


def package(directory):
    meta = read_json(directory / "game.json")
    build = directory / "build"
    test = read_json(build / "devkit/test.json")
    capture = read_json(build / "devkit/capture.json")
    current = fingerprint(directory)
    prg = build / (meta["id"] + ".prg")
    require(all(r.get("status") == "passed" and r.get("fingerprint") == current and r.get("prg_sha256") == digest(prg) for r in (test, capture)), "Test or capture evidence is stale.", hint="Rerun release; it builds, tests and captures the current sources.")
    require(capture["host_state_writes"] == 0, "Capture has host state writes.")
    for name, sha in capture["files"].items():
        require(digest(build / "media" / name) == sha, "Captured media changed after verification.")
    destination = build / "release"
    # A fresh directory prevents obsolete screenshots or unrelated files leaking in.
    with tempfile.TemporaryDirectory(prefix="release-", dir=build) as temporary:
        staging = Path(temporary)
        prg_name = f"games/{meta['id']}/{meta['version']}/{meta['id']}.prg"
        media_prefix = f"game-media/{meta['id']}"
        (staging / prg_name).parent.mkdir(parents=True)
        shutil.copyfile(prg, staging / prg_name)
        media = staging / media_prefix
        media.mkdir(parents=True)
        for name in capture["files"]:
            shutil.copyfile(build / "media" / name, media / name)
        source_files = ["game.json", "levels.json", meta["rulesSource"], meta["artSource"], "tests/replay.json", "README.md", "GAME_DESIGN.md", "Makefile", "AGENTS.md"]
        with zipfile.ZipFile(media / "source.zip", "w", zipfile.ZIP_DEFLATED) as archive:
            for name in source_files:
                path = (directory / name).resolve()
                require(path.is_relative_to(directory) and path.is_file(), "Source archive requires project-local files.", path)
                archive.write(path, arcname=name)
        shutil.copyfile(ROOT / "LICENSE", media / "LICENSE.txt")
        entry = {k: meta[k] for k in ("id", "title", "version", "ramKiB", "entry")}
        entry.update(path=prg_name, sha256=digest(prg))
        # The existing emulator validates repository URLs strictly. A standalone
        # project must not poison its shared catalog with an incompatible entry.
        if meta.get("sourceUrl"):
            entry["sourceUrl"] = meta["sourceUrl"]
            write_json(staging / "games/catalog.json", {"schemaVersion": 1, "games": [entry]})
        gallery_entry = {"id": meta["id"], "title": meta["title"], "genre": "Independent", "edited": False,
                         "outcome": capture["outcome"], "prg_sha256": digest(prg), "seconds": capture["seconds"],
                         "video": {"path": f"{media_prefix}/play.mp4", "sha256": capture["files"]["play.mp4"]},
                         "images": [{"path": f"{media_prefix}/{name}", "sha256": capture["files"][name]} for name in capture["images"]]}
        write_json(staging / "game-media/catalog.json", {"schemaVersion": 1, "games": [gallery_entry]})
        evidence = {key: capture[key] for key in ("evidence", "host_state_writes", "playback_speed", "edited", "outcome", "scenario", "seconds", "images", "events", "files", "prg_sha256", "fingerprint")}
        evidence["test_scenarios"] = test["scenarios"]
        write_json(media / "evidence.json", evidence)
        title = html.escape(meta["title"])
        images = "\n".join(f'<figure><img src="{name}" alt="{html.escape(Path(name).stem)}"><figcaption>{html.escape(Path(name).stem)}</figcaption></figure>' for name in capture["images"])
        (media / "index.html").write_text(f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>{title}</title>
<style>body{{max-width:960px;margin:2rem auto;padding:0 1rem;background:#151515;color:#eee;font:18px system-ui}}a{{color:#bde7ff}}img,video{{max-width:100%;image-rendering:pixelated}}video{{width:100%;max-width:816px;aspect-ratio:4/3}}figure{{margin:2rem 0}}figcaption{{color:#aaa}}</style>
<h1>{title}</h1><p>JR-100 / 16 KiB / {meta['version']}</p><p><a href="../../{prg_name}">Download PRG</a> · <a href="source.zip">Project source</a> · <a href="evidence.json">Verification evidence</a></p>
<video controls preload="metadata" src="play.mp4" poster="{capture['images'][0]}"></video>{images}
<p>Captured from a user-owned ROM in an emulator, with ordinary input only. Physical hardware has not been verified.</p><p><a href="LICENSE.txt">License</a></p></html>''', encoding="utf-8")
        manifest = {"schemaVersion": 1, "id": meta["id"], "version": meta["version"], "fingerprint": current,
                    "files": {str(p.relative_to(staging)): digest(p) for p in sorted(staging.rglob("*")) if p.is_file()}}
        write_json(media / "manifest.json", manifest)
        if destination.exists():
            shutil.rmtree(destination)
        shutil.move(str(staging), str(destination))
    return {"directory": str(destination), "preview": str(destination / media_prefix / "index.html"), "files": len(manifest["files"])+1,
            "emulator_catalog": "registered" if meta.get("sourceUrl") else "manual PRG loading; set sourceUrl for shared catalog registration"}


def deploy(bundle, destination):
    """Merge this project's catalogs, preserving every other catalog entry/file."""
    destination = Path(destination).resolve()
    require(not destination.is_relative_to(bundle.resolve()), "Deployment root must be outside the release bundle.")
    changes = {}
    for catalog in ("games/catalog.json", "game-media/catalog.json"):
        if not (bundle / catalog).is_file():
            continue
        new = read_json(bundle / catalog)
        old_path = destination / catalog
        old = read_json(old_path) if old_path.exists() else {"schemaVersion": 1, "games": []}
        require(isinstance(old, dict) and old.get("schemaVersion") == 1 and isinstance(old.get("games"), list), "Unsupported destination catalog; nothing was deployed.", old_path)
        require(all(isinstance(x, dict) and isinstance(x.get("id"), str) for x in old["games"]), "Malformed destination catalog; nothing was deployed.", old_path)
        ids = {g["id"] for g in new["games"]}
        merged = {**old, "games": [g for g in old["games"] if g["id"] not in ids] + new["games"]}
        changes[catalog] = (json.dumps(merged, indent=2) + "\n").encode()
    for path in sorted(bundle.rglob("*")):
        if path.is_file():
            name = str(path.relative_to(bundle))
            if name not in changes:
                changes[name] = path.read_bytes()
    # Catalogs are shared indexes; they cannot have per-game hashes after merging.
    for name in list(changes):
        if name.endswith("/manifest.json"):
            manifest = json.loads(changes[name])
            for catalog in ("games/catalog.json", "game-media/catalog.json"):
                manifest["files"].pop(catalog, None)
            changes[name] = (json.dumps(manifest, indent=2) + "\n").encode()
    for name in changes:
        target = destination / name
        require(target.resolve().is_relative_to(destination) and not target.is_symlink(), "Deployment path escapes web root or is a symlink.", target)
        require(not target.exists() or target.is_file(), "Deployment target is not a file.", target)
    destination.mkdir(parents=True, exist_ok=True)
    previous = {}
    try:
        order = sorted(changes, key=lambda name: (name in ("games/catalog.json", "game-media/catalog.json"), name))
        for name in order:
            data = changes[name]
            target = destination / name
            previous[name] = target.read_bytes() if target.exists() else None
            target.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as stream:
                staged = Path(stream.name)
                stream.write(data)
            try:
                staged.replace(target)
            finally:
                staged.unlink(missing_ok=True)
        for name, data in changes.items():
            require((destination / name).read_bytes() == data, "Post-deployment verification failed.")
    except Exception:
        for name, original in previous.items():
            target = destination / name
            if original is None:
                target.unlink(missing_ok=True)
            else:
                target.write_bytes(original)
        raise
    return {"web_root": str(destination), "files": len(changes), "verified": True}
