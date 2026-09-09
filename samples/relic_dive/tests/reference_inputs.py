"""Check local reference programs without redistributing their bytes."""

import hashlib
import json

from machine import EMU, ROOT


def check():
    reports = []
    # ASCEND's input reader tests bits 0..4 and sets action bits on nonzero.
    ascend = EMU / "datas/inufuto/ascend_0300.prg"
    if ascend.exists():
        data = ascend.read_bytes()
        signature = bytes.fromhex(
            "b6 cc 02 85 01 27 02 ca 02 85 02 27 02 ca 01 85 04 27 02 ca 04 85 08 27 02 ca 08 85 10 27 02 ca 10"
        )
        offset = data.find(signature)
        assert offset >= 0, "ASCEND joystick reader differs from inspected reference"
        presence = data.find(bytes.fromhex("b6 cc 02 43 27 02 86 01"))
        assert presence >= 0, "ASCEND absent-port detection differs"
        reports.append(
            {
                "program": ascend.name,
                "sha256": hashlib.sha256(data).hexdigest(),
                "input_file_offset": offset,
                "presence_file_offset": presence,
                "contract": "CC02 bits 0..4 active-high; FF absent",
            }
        )
    starfire = EMU / "datas/STARFIRE_0D00.prg"
    if starfire.exists():
        data = starfire.read_bytes()
        address = data.find(bytes.fromhex("ce cc 02 df 94"))
        reader = data.find(bytes.fromhex("de 94 a6 00 5f 36 37 86 1f"))
        assert min(address, reader) >= 0, "STARFIRE indirect joystick reader differs"
        reports.append(
            {
                "program": starfire.name,
                "sha256": hashlib.sha256(data).hexdigest(),
                "address_file_offset": address,
                "input_file_offset": reader,
                "contract": "CC02 via direct-page pointer 94; mask 1F",
            }
        )
    (ROOT / "build/reference-inputs.json").write_text(
        json.dumps(reports, indent=2) + "\n"
    )
    return {
        "references_checked": len(reports),
        "physical_test": "not performed on this port",
    }


if __name__ == "__main__":
    print(check())
