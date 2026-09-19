"""Verify anonymously served release bytes against local evidence."""

import hashlib
from pathlib import PurePosixPath
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

from devkit.project import digest, fingerprint, read_json, require


def verify(directory, base_url):
    parsed = urlparse(base_url)
    require(parsed.scheme == "https" or parsed.scheme == "http" and parsed.hostname in ("localhost", "127.0.0.1", "::1"), "Use HTTPS, or HTTP on localhost for a local check.")
    require(not parsed.username and not parsed.password and not parsed.query and not parsed.fragment, "Use a public base URL without credentials, query or fragment.")
    base_url = base_url.rstrip("/") + "/"
    meta = read_json(directory / "game.json")
    bundle = directory / "build/release"
    manifest_path = f"game-media/{meta['id']}/manifest.json"
    manifest = read_json(bundle / manifest_path)
    require(manifest["fingerprint"] == fingerprint(directory), "Release does not match current sources.", hint="Rerun release and deploy its output.")
    checked = []
    for name, expected in manifest["files"].items():
        require(not PurePosixPath(name).is_absolute() and ".." not in PurePosixPath(name).parts, "Unsafe manifest path.")
        # Shared indexes change when other games are added. Check this entry below.
        if name in ("games/catalog.json", "game-media/catalog.json"):
            continue
        local = bundle / name
        require(digest(local) == expected, "Local bundle was modified after packaging.", local)
        url = urljoin(base_url, name)
        request = Request(url, headers={"Cache-Control": "no-cache"})
        with urlopen(request, timeout=30) as response:
            require(response.status == 200, f"HTTP {response.status}: {name}")
            require(urlparse(response.url).scheme == parsed.scheme, "Unexpected protocol change while fetching a public artifact.")
            data = response.read(local.stat().st_size + 1)
        require(hashlib.sha256(data).hexdigest() == expected, f"Published hash differs: {name}", hint="Wait for deployment, check the base URL, or replace the stale file.")
        checked.append(name)
    import json

    with urlopen(urljoin(base_url, manifest_path), timeout=30) as response:
        remote_manifest = json.loads(response.read(1_000_001))
    remote_files = remote_manifest.get("files", {})
    require(remote_manifest.get("fingerprint") == manifest["fingerprint"] and all(remote_files.get(name) == manifest["files"][name] for name in checked), "Published manifest is stale or incomplete.")
    for name in ("games/catalog.json", "game-media/catalog.json"):
        if not (bundle / name).is_file():
            continue
        with urlopen(urljoin(base_url, name), timeout=30) as response:
            remote = json.loads(response.read(4_000_001))
        expected = read_json(bundle / name)["games"][0]
        entries = [g for g in remote["games"] if g["id"] == meta["id"]]
        require(entries == [expected], f"Published catalog entry differs: {name}")
    return {"base_url": base_url, "verified_files": len(checked), "catalog_entries": "matched"}
