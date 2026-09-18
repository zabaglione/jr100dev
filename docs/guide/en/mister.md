## Choose one game or take the whole collection

Every card in [All games](Home) has a **Download .prg (MiSTer)** button. It saves the game directly; no source checkout or build is needed.

For all 51 games, download the ZIP above and extract it. Copy its **JR100** folder into **games/** on your MiSTer's SD card. The individual downloads and the ZIP contain the same games, with autostart hints already included. The ZIP also includes these instructions and the MIT license.

## First-time setup

Use the [JR-100 core](https://github.com/MiSTer-devel/JR100_MiSTer) and your own BASIC ROM. The core's [ROM setup instructions](https://github.com/MiSTer-devel/JR100_MiSTer#rom) explain how to prepare **games/JR100/boot.rom**. The game downloads include neither the ROM nor a core binary.

Start the JR-100 core and wait for **READY**. In its on-screen menu, set **Autostart loaded program** to **Yes**, then choose **Load PRG** and select a downloaded game. It starts at its title; press **RETURN** to play. The games use standard 16 KB RAM, so leave **Extended RAM (reset)** off.

If autostart is off or the machine remains at READY after loading, type `A=USR($0300)` and press RETURN. You do not need `RUN` for these machine-code games. Use the current core if automatic typing is incomplete.

## SuperStation One and USB storage

Put the files in the **games/JR100/** folder on the storage device MiSTer is actually using. On SuperStation One this may be USB storage rather than the SD card.

The steps above use the JR-100 core's own **Load PRG** menu. SuperStation One's **Console Mode → Load Game** needs an MGL launcher; a plain .prg is not that launcher. Follow the core's [Console Mode setup guide](https://github.com/MiSTer-devel/JR100_MiSTer/blob/main/docs/SS1_FW12_CONSOLE_MODE.md) for that interface.

## Controls, credits, and verification

See each game's guide for its rules and [Getting started](Controls) for keyboard and pad controls.

RELIC DIVE is co-developed with **JR-800 Web Emulator contributors**. Their credit is retained in the collection's [MIT license](LICENSE.txt).

Tested on MiSTer (SuperStation One) on 18 September 2026, using `JR100_20260801.rbf`. With standard 16 KB RAM, the four downloads below autostarted and reached gameplay. Their checks cover:

| Game | Confirmed on SS1 |
| --- | --- |
| FROST STEPS | Starting, movement, and collecting a crystal |
| GATE RUNNER | Starting, obstacle progression, and the pit-failure display |
| STAR LANCE | Starting, movement, and normal/heavy shots |
| NIGHT SWARM | Starting, movement, and pulse attacks |

The device owner also confirmed STAR LANCE's physical pad controls and sound effects. Sound and physical pad input for the other three games, all stages, and the remaining 47 games have not been tested on SS1. Original JR-100 hardware remains untested.
