import { mkdir, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";

import { ARCADE_DIGITS, SLOT_COUNT } from "../core.js";


const outputArgument = process.argv[2];
if (!outputArgument) {
  throw new Error("Output path is required");
}

const outputPath = resolve(outputArgument);
const lines = [
  "; Generated from tools/pcg_editor/core.js. Do not edit manually.",
  ...ARCADE_DIGITS.glyphs.map(
    (glyph) => `        .byte ${glyph.map((value) => `$${value.toString(16).toUpperCase().padStart(2, "0")}`).join(",")}`,
  ),
  `        .fill ${(SLOT_COUNT - ARCADE_DIGITS.glyphs.length) * 8}, $00`,
  "",
];

await mkdir(dirname(outputPath), { recursive: true });
await writeFile(outputPath, lines.join("\n"), "utf8");
