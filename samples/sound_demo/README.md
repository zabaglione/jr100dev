# Cooperative Sound Demo

This sample demonstrates the Timer 1 PB7 sound driver without using a BGM
interrupt. It starts with `ODE_TO_JOY_OPENING` and proves that PB7 sound, PB5
PCG selection, and keyboard input coexist. It writes two PCG glyphs to
`$C000-$C00F`, displays codes `$80` and `$81` in VRAM, and scans keyboard row
0 without changing PB5 or PB7.

| Row 0 bit | Action |
| --- | --- |
| 0 | Play the blocking `BLIP` effect and toggle the displayed PCG glyph. |
| 1 | Immediately switch to `AH_VOUS_DIRAIJE_OPENING`. |
| 2 | Immediately switch back to `ODE_TO_JOY_OPENING`. |
| 3 | Stop BGM. |

Build it with:

```sh
make -C samples/sound_demo
```

The BGM data is updated once per approximate 60Hz game tick. The effect uses
10ms blocking units and resumes the BGM note and remaining duration that were
active before it began.
