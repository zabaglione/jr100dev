"""Input replays with both independent assertions and native/model comparison."""

import re
import sys

from devkit.project import Problem, ROOT, read_json, require

KEYS = {"W": 1, "S": 2, "A": 3, "D": 4, "RETURN": 5, "SPACE": 6}


def load_replay(directory):
    path = directory / "tests/replay.json"
    data = read_json(path)
    require(isinstance(data, dict) and data.get("schemaVersion") == 1, "Unsupported replay schema.", path)
    scenarios = data.get("scenarios")
    require(isinstance(scenarios, list) and 1 <= len(scenarios) <= 100, "Provide 1-100 replay scenarios.", path)
    names = set()
    for scenario in scenarios:
        require(isinstance(scenario, dict), "Each scenario must be an object.", path)
        name = scenario.get("name")
        require(isinstance(name, str) and re.fullmatch(r"[a-z][a-z0-9-]*", name) and name not in names, "Use unique lowercase scenario names.", path)
        names.add(name)
        steps = scenario.get("steps")
        require(isinstance(steps, list) and 1 <= len(steps) <= 1000, f"{name}: provide 1-1000 steps.", path)
        require(any(isinstance(s, dict) and s.get("expect") for s in steps), f"{name}: add independent expected values.", path)
        captures = set()
        for step in steps:
            require(isinstance(step, dict) and bool(step) and not set(step) - {"press", "ticks", "repeat", "expect", "confirm", "capture"}, f"{name}: unknown or empty replay step.", path)
            require(not ("press" in step and "ticks" in step), "Use either press or ticks in one step.", path)
            if "press" in step:
                require(step["press"] in KEYS, "press must be W/S/A/D/RETURN/SPACE.", path)
            require(type(step.get("repeat", 1)) is int and 1 <= step.get("repeat", 1) <= 255, "repeat must be 1-255.", path)
            if "repeat" in step:
                require("press" in step, "repeat requires press.", path)
            if "ticks" in step:
                require(type(step["ticks"]) is int and 1 <= step["ticks"] <= 255, "ticks must be 1-255.", path)
            if "confirm" in step:
                require(type(step["confirm"]) is bool and step.get("press") in ("RETURN", "SPACE"), "confirm requires RETURN/SPACE and a boolean.", path)
            if "expect" in step:
                require(isinstance(step["expect"], dict) and bool(step["expect"]), "expect must contain state or array values.", path)
                for key, value in step["expect"].items():
                    require(re.fullmatch(r"s\.[a-zA-Z_][a-zA-Z_0-9]*|[bcd]\[(?:[0-9]|[1-9][0-9]|1[01][0-9]|12[0-7])\]", key) and type(value) is int and 0 <= value <= 255, "expect uses s.name or b/c/d[0..127] with byte values.", path)
            if "capture" in step:
                value = step["capture"]
                require(isinstance(value, str) and re.fullmatch(r"[a-z][a-z0-9-]*", value) and value != "title" and value not in captures, "Use unique capture names (title is reserved).", path)
                captures.add(value)
    require(data.get("demo") in names, "demo must name a scenario.", path)
    return data


def harness():
    sys.path[:0] = [str(ROOT / "tests"), str(ROOT / "native"), str(ROOT / "common")]
    import checks

    return checks


def expect(machine, expected):
    slots = read_json(machine.directory / "build/state_slots.json")
    for key, value in expected.items():
        if key.startswith("s."):
            require(key in slots, f"Expected field is absent from generated state: {key}")
            actual = machine.get(slots[key])
        else:
            actual = machine.get(machine.sym[key[0].upper() + "_ARRAY"] + int(key[2:-1]))
        assert actual == value, f"{key}: expected {value}, actual {actual}"


def test(directory):
    data = load_replay(directory)
    checks = harness()
    results = []
    for scenario in data["scenarios"]:
        for pad in (False, True):
            m, model = checks.begin(str(directory))
            index = -1
            try:
                for index, step in enumerate(scenario["steps"]):
                    if "press" in step:
                        key = KEYS[step["press"]]
                        for _ in range(step.get("repeat", 1)):
                            checks.action(m, model, key, pad=pad and key != 6, confirm=step.get("confirm"))
                    elif "ticks" in step:
                        for _ in range(step["ticks"]):
                            require(m.get("MODE") == 1, "ticks requires active gameplay.")
                            checks.tick(m, model)
                    expect(m, step.get("expect", {}))
                results.append({"scenario": scenario["name"], "input": "pad+keyboard-reset" if pad else "keyboard", "steps": len(scenario["steps"]), "pass": True})
            except (AssertionError, ValueError, IndexError, KeyError, ZeroDivisionError) as exc:
                raise Problem("REPLAY", f"{scenario['name']} / {'pad' if pad else 'keyboard'} / step {index+1}: {exc}", "Fix the rule or independently justified expectation, then rerun test. Do not remove the failing check.", directory / "tests/replay.json") from exc
            finally:
                m.__del__()
    from check_rules import check

    check(str(directory))
    return {"evidence": "synthetic-ROM emulator + byte-model; not hardware", "scenarios": results, "mixed_inputs": 160}
