"""Title-only PCG finishes, assigned to complete logos in selected games."""

FINISH_GROUPS = {
    "stone": "hearth-zero glyph-shift five-forge stone-balance ruin-lexicon mirror-relic sand-rescue",
    "speed": "night-swarm gate-runner brick-pulse star-lance",
    "glass": "frost-steps prism-trace lumen-cross phase-pairs",
}
FINISH_FOR = {
    game: finish for finish, games in FINISH_GROUPS.items() for game in games.split()
}


def finish_bank(bank, finish):
    result = bank[:128]
    for mask in range(16):
        tile = bank[mask * 8 : mask * 8 + 8].copy()
        for quadrant in range(4):
            if not mask & (1 << quadrant):
                continue
            x, y = (quadrant % 2) * 4, (quadrant // 2) * 4
            if finish == "stone":
                tile[y + 2] &= ~(128 >> (x + 2))
                tile[y + 3] &= ~(128 >> (x + 3))
            elif finish == "glass":
                tile[y + 3] &= ~(128 >> (x + 3))
                tile[y + 2] &= ~(128 >> (x + 3))
                tile[y + 3] &= ~(128 >> (x + 2))
        if finish == "speed":
            tile[6] = 0
        result.extend(tile)
    return result
