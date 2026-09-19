"""Fail-fast, machine-readable development pipeline."""

import argparse
import contextlib
import importlib.util
import io
import json
import os
import shutil
import sys
import traceback
from pathlib import Path

from devkit.project import Problem, ROOT, digest, fingerprint, require, validate
from devkit.scaffold import create, write_json


def doctor(capture=False, rom=None):
    emu = Path(os.environ.get("JR100EMU_ROOT", str(Path.home() / "jr100emu"))).expanduser()
    checks = [{"name": "Python >= 3.9", "ok": sys.version_info >= (3, 9)},
              {"name": "C++20 compiler", "ok": bool(shutil.which("c++")), "fix": "Install Xcode command line tools or a C++20 compiler."},
              {"name": "emulator C++ sources", "ok": all((emu / p).is_file() for p in ("cpp/src/core.cpp", "cpp/src/cpu.cpp", "cpp/src/via.cpp")) and (emu / "cpp/include").is_dir(), "fix": "Set JR100EMU_ROOT to your jr100emu checkout."}]
    if capture:
        checks += [{"name": "Pillow", "ok": importlib.util.find_spec("PIL") is not None, "fix": "Install this SDK with pip install -e '.[test,media]'."}]
        checks += [{"name": name, "ok": bool(shutil.which(name)), "fix": "Install ffmpeg (including ffprobe)."} for name in ("ffmpeg", "ffprobe")]
        checks += [{"name": "user-owned ROM", "ok": rom is not None and rom.is_file(), "fix": "Pass --rom /path/to/owned-rom.prg or set JR100_ROM."}]
    return {"checks": checks, "ready": all(c["ok"] for c in checks)}


def preflight(capture, rom):
    result = doctor(capture, rom)
    missing = [c for c in result["checks"] if not c["ok"]]
    if missing:
        raise Problem("DEPENDENCY", "; ".join(c["name"] for c in missing), " ".join(c.get("fix", "Use a supported Python version.") for c in missing))
    return result


def parser():
    p = argparse.ArgumentParser(description="Create, check, test, capture and deploy JR-100 Python games.")
    p.add_argument("--json", action="store_true", help="emit a single JSON result for an AI/CI caller")
    subs = p.add_subparsers(dest="command", required=True)
    init = subs.add_parser("init", help="create a playable project; never overwrite")
    init.add_argument("project", type=Path)
    init.add_argument("--id", required=True)
    init.add_argument("--title", default="CRYSTAL TRAIL")
    for name in ("doctor", "check", "build", "test", "capture", "release", "deploy"):
        sub = subs.add_parser(name)
        if name != "doctor":
            sub.add_argument("project", type=Path)
        if name in ("doctor", "test", "capture", "release", "deploy"):
            sub.add_argument("--emu-root", type=Path, help="emulator source checkout (or JR100EMU_ROOT)")
        if name in ("doctor", "capture", "release", "deploy"):
            sub.add_argument("--rom", type=Path, default=os.environ.get("JR100_ROM"), help="user-owned ROM for genuine captures")
        if name == "doctor":
            sub.add_argument("--capture", action="store_true", help="also check media dependencies and ROM")
        if name in ("release", "deploy"):
            sub.add_argument("--web-root", type=Path, required=name == "deploy", help="merge release into this local web directory and verify it")
    published = subs.add_parser("verify-published", help="compare served artifacts with this project's release manifest")
    published.add_argument("project", type=Path)
    published.add_argument("--base-url", required=True)
    return p


def execute(args):
    if getattr(args, "emu_root", None):
        os.environ["JR100EMU_ROOT"] = str(args.emu_root.expanduser().resolve())
    rom = getattr(args, "rom", None)
    rom = Path(rom).expanduser().resolve() if rom else None
    if args.command == "doctor":
        result = doctor(args.capture, rom)
        return {"status": "passed" if result["ready"] else "failed", "stage": "doctor", **result}
    if args.command == "init":
        return {"status": "passed", "stage": "init", **create(args.project, args.id, args.title)}
    if args.command == "verify-published":
        from devkit.published import verify

        return {"status": "passed", "stage": "verify-published", **verify(args.project.expanduser().resolve(), args.base_url)}
    directory = args.project.expanduser().resolve()
    require(directory.is_dir(), "Project directory does not exist.", directory, "Run init first, or correct the project path.")
    output = directory / "build/devkit"
    output.mkdir(parents=True, exist_ok=True)
    report = {"status": "running", "stage": "check", "stages": []}
    write_json(output / "report.json", report)
    log = io.StringIO()
    built_fingerprint = None
    built_prg_sha256 = None

    def stage(name, operation):
        report["stage"] = name
        write_json(output / "report.json", report)
        if not args.json:
            print(f"[{name}]", file=sys.stderr, flush=True)
        with contextlib.redirect_stdout(log):
            value = operation()
        if name in ("test", "capture"):
            require(fingerprint(directory) == built_fingerprint and digest(directory / "build" / (meta["id"] + ".prg")) == built_prg_sha256,
                    "Sources or PRG changed during verification.", hint="Finish editing, then rerun the command from the build stage.")
            value.update(status="passed", fingerprint=built_fingerprint, prg_sha256=built_prg_sha256)
            write_json(output / (name + ".json"), value)
        report["stages"].append({"stage": name, "status": "passed", "result": value})
        return value

    try:
        # Starting a new build invalidates previous downstream evidence even on failure.
        if args.command != "check":
            for name in ("test.json", "capture.json"):
                (output / name).unlink(missing_ok=True)
        from devkit.verify import load_replay

        def check():
            metadata = validate(directory)
            load_replay(directory)
            return metadata
        meta = stage("check", check)
        if args.command != "check":
            from build_game import build

            built_fingerprint = fingerprint(directory)
            stage("build", lambda: build(directory))
            require(fingerprint(directory) == built_fingerprint, "Sources changed during the build.", hint="Finish editing and rerun build.")
            built_prg_sha256 = digest(directory / "build" / (meta["id"] + ".prg"))
        if args.command in ("test", "capture", "release", "deploy"):
            stage("environment", lambda: preflight(args.command != "test", rom))
            from devkit.verify import test

            stage("test", lambda: test(directory))
        if args.command in ("capture", "release", "deploy"):
            from devkit.media import capture

            stage("capture", lambda: capture(directory, rom))
        if args.command in ("release", "deploy"):
            from devkit.release import deploy, package

            packed = stage("package", lambda: package(directory))
            if args.web_root:
                stage("deploy", lambda: deploy(Path(packed["directory"]), args.web_root))
        report["status"] = "passed"
        return report
    except Exception as exc:
        report["status"] = "failed"
        report["error"] = exc.detail if isinstance(exc, Problem) else {
            "code": "PIPELINE", "message": f"{type(exc).__name__}: {exc}",
            "hint": "Read build/devkit/run.log, fix authored sources or the reported dependency, and rerun the same command."}
        log.write(traceback.format_exc())
        return report
    finally:
        write_json(output / "report.json", report)
        (output / "run.log").write_text(log.getvalue(), encoding="utf-8")


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        result = execute(args)
    except Problem as exc:
        result = {"status": "failed", "stage": args.command, "error": exc.detail}
    except OSError as exc:
        result = {"status": "failed", "stage": args.command, "error": {"code": "IO", "message": str(exc), "hint": "Check file paths and filesystem permissions."}}
    except Exception as exc:
        result = {"status": "failed", "stage": args.command, "error": {"code": "PIPELINE", "message": f"{type(exc).__name__}: {exc}", "hint": "Check the input format and the failed command; do not treat this run as passed."}}
    if args.json:
        print(json.dumps(result, ensure_ascii=True))
    elif result["status"] == "failed":
        error = result.get("error", {})
        print(f"FAIL [{result['stage']}] {error.get('code', 'DEPENDENCY')}: {error.get('message', 'See dependency checks below.')}")
        if "file" in error:
            print(f"  {error['file']}:{error.get('line', 1)}")
        if error.get("hint"):
            print("  Fix: " + error["hint"])
        for item in result.get("checks", []):
            print(f"  {'OK' if item['ok'] else 'MISSING'}: {item['name']}" + (" - " + item.get("fix", "") if not item["ok"] else ""))
    else:
        print(f"PASS [{result['stage']}]")
        if "project" in result:
            print(result["project"])
        for item in result.get("stages", []):
            value = item.get("result")
            if isinstance(value, dict) and value.get("preview"):
                print("Preview: " + value["preview"])
                print("Emulator catalog: " + value["emulator_catalog"])
        if args.command == "doctor":
            for item in result["checks"]:
                print("  OK: " + item["name"])
    return 0 if result["status"] == "passed" else 1
