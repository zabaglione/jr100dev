function glyph(...rows) {
  if (rows.length !== 8 || rows.some((row) => typeof row !== "string" || row.length !== 8 || /[^.#]/.test(row))) {
    throw new TypeError("An 8x8 glyph requires eight dot rows");
  }
  return rows.map((row) => [...row].reduce((value, cell, index) => value | (cell === "#" ? 1 << (7 - index) : 0), 0));
}

function freezeGlyphs(glyphs) {
  return Object.freeze(glyphs.map((entry) => Object.freeze([...entry])));
}

function createPreset({ id, kind = "asset", name, category, tags, width, height, glyphs, slotNames }) {
  if (!id || !name || !category || !Array.isArray(tags) || !Number.isInteger(width) || !Number.isInteger(height)) {
    throw new TypeError("Preset metadata is invalid");
  }
  if (!Array.isArray(glyphs) || glyphs.length !== width * height || glyphs.some((entry) => !Array.isArray(entry) || entry.length !== 8 || entry.some((value) => !Number.isInteger(value) || value < 0 || value > 0xff))) {
    throw new TypeError("Preset glyph data is invalid");
  }
  if (!Array.isArray(slotNames) || slotNames.length !== glyphs.length || slotNames.some((entry) => typeof entry !== "string" || !entry)) {
    throw new TypeError("Preset slot names are invalid");
  }
  return Object.freeze({
    id,
    kind,
    name,
    category,
    tags: Object.freeze([...tags]),
    width,
    height,
    glyphs: freezeGlyphs(glyphs),
    slotNames: Object.freeze([...slotNames]),
  });
}

function tile(id, name, category, tags, rows) {
  return createPreset({
    id,
    name,
    category,
    tags,
    width: 1,
    height: 1,
    glyphs: [glyph(...rows)],
    slotNames: [name],
  });
}

function createMatrix() {
  return Array.from({ length: 16 }, () => Array(16).fill(0));
}

function setMatrixPixel(matrix, x, y, value = 1) {
  if (x >= 0 && x < 16 && y >= 0 && y < 16) {
    matrix[y][x] = value ? 1 : 0;
  }
}

function fillMatrixRect(matrix, x, y, width, height) {
  for (let row = y; row < y + height; row += 1) {
    for (let column = x; column < x + width; column += 1) {
      setMatrixPixel(matrix, column, row);
    }
  }
}

function drawMatrixLine(matrix, x0, y0, x1, y1) {
  let x = x0;
  let y = y0;
  const dx = Math.abs(x1 - x0);
  const sx = x0 < x1 ? 1 : -1;
  const dy = -Math.abs(y1 - y0);
  const sy = y0 < y1 ? 1 : -1;
  let error = dx + dy;
  while (true) {
    setMatrixPixel(matrix, x, y);
    if (x === x1 && y === y1) return;
    const twiceError = error * 2;
    if (twiceError >= dy) {
      error += dy;
      x += sx;
    }
    if (twiceError <= dx) {
      error += dx;
      y += sy;
    }
  }
}

function drawMatrixEllipse(matrix, centerX, centerY, radiusX, radiusY) {
  for (let y = Math.floor(centerY - radiusY); y <= Math.ceil(centerY + radiusY); y += 1) {
    for (let x = Math.floor(centerX - radiusX); x <= Math.ceil(centerX + radiusX); x += 1) {
      const distance = ((x - centerX) ** 2) / (radiusX ** 2) + ((y - centerY) ** 2) / (radiusY ** 2);
      if (distance <= 1) setMatrixPixel(matrix, x, y);
    }
  }
}

function matrixGlyphs(matrix) {
  return Array.from({ length: 4 }, (_, tile) => {
    const tileX = (tile % 2) * 8;
    const tileY = Math.floor(tile / 2) * 8;
    return Array.from({ length: 8 }, (_, row) =>
      matrix[tileY + row].reduce((value, cell, column) => value | (cell && column >= tileX && column < tileX + 8 ? 1 << (7 - (column - tileX)) : 0), 0),
    );
  });
}

function sprite(id, name, category, tags, painter) {
  const matrix = createMatrix();
  painter(matrix);
  return createPreset({
    id,
    name,
    category,
    tags,
    width: 2,
    height: 2,
    glyphs: matrixGlyphs(matrix),
    slotNames: ["TL", "TR", "BL", "BR"].map((corner) => `${name} ${corner}`),
  });
}

function vehiclePainter(kind) {
  return (matrix) => {
    if (kind === "propeller-plane") {
      drawMatrixLine(matrix, 1, 8, 14, 8);
      drawMatrixLine(matrix, 5, 8, 8, 3);
      drawMatrixLine(matrix, 7, 8, 11, 12);
      drawMatrixLine(matrix, 2, 6, 2, 10);
      drawMatrixLine(matrix, 0, 7, 3, 9);
    } else if (kind === "fighter-jet") {
      drawMatrixLine(matrix, 1, 8, 14, 8);
      drawMatrixLine(matrix, 5, 8, 9, 4);
      drawMatrixLine(matrix, 6, 8, 12, 12);
      fillMatrixRect(matrix, 8, 7, 3, 3);
      setMatrixPixel(matrix, 14, 7);
      setMatrixPixel(matrix, 14, 9);
    } else if (kind === "bomber") {
      fillMatrixRect(matrix, 3, 7, 10, 3);
      drawMatrixLine(matrix, 2, 8, 5, 4);
      drawMatrixLine(matrix, 5, 9, 8, 13);
      drawMatrixLine(matrix, 11, 7, 14, 5);
      drawMatrixLine(matrix, 1, 6, 1, 10);
    } else if (kind === "biplane") {
      drawMatrixLine(matrix, 2, 5, 12, 5);
      drawMatrixLine(matrix, 1, 10, 13, 10);
      drawMatrixLine(matrix, 4, 5, 4, 10);
      drawMatrixLine(matrix, 9, 5, 9, 10);
      fillMatrixRect(matrix, 6, 6, 4, 3);
      drawMatrixLine(matrix, 13, 7, 15, 8);
    } else if (kind === "helicopter") {
      fillMatrixRect(matrix, 3, 7, 8, 4);
      drawMatrixEllipse(matrix, 5, 8, 3, 3);
      drawMatrixLine(matrix, 10, 8, 15, 8);
      drawMatrixLine(matrix, 13, 5, 13, 11);
      drawMatrixLine(matrix, 6, 5, 6, 1);
      drawMatrixLine(matrix, 2, 1, 10, 1);
      drawMatrixLine(matrix, 3, 12, 8, 12);
    } else if (kind === "rocket") {
      drawMatrixLine(matrix, 8, 1, 4, 11);
      drawMatrixLine(matrix, 8, 1, 12, 11);
      fillMatrixRect(matrix, 6, 7, 5, 5);
      drawMatrixLine(matrix, 5, 11, 2, 14);
      drawMatrixLine(matrix, 11, 11, 14, 14);
      drawMatrixLine(matrix, 7, 13, 8, 15);
      drawMatrixLine(matrix, 9, 13, 8, 15);
    } else if (kind === "ufo") {
      drawMatrixEllipse(matrix, 8, 10, 7, 3);
      drawMatrixEllipse(matrix, 8, 6, 3, 3);
      fillMatrixRect(matrix, 3, 12, 10, 1);
      setMatrixPixel(matrix, 4, 13);
      setMatrixPixel(matrix, 8, 13);
      setMatrixPixel(matrix, 12, 13);
    } else if (kind === "airship") {
      drawMatrixEllipse(matrix, 8, 6, 7, 4);
      fillMatrixRect(matrix, 6, 10, 5, 3);
      drawMatrixLine(matrix, 11, 9, 15, 12);
      drawMatrixLine(matrix, 11, 4, 15, 1);
      drawMatrixLine(matrix, 5, 13, 11, 13);
    } else if (kind === "drone") {
      fillMatrixRect(matrix, 6, 6, 4, 4);
      drawMatrixLine(matrix, 6, 6, 2, 2);
      drawMatrixLine(matrix, 9, 6, 13, 2);
      drawMatrixLine(matrix, 6, 9, 2, 13);
      drawMatrixLine(matrix, 9, 9, 13, 13);
      drawMatrixEllipse(matrix, 2, 2, 2, 1);
      drawMatrixEllipse(matrix, 13, 2, 2, 1);
      drawMatrixEllipse(matrix, 2, 13, 2, 1);
      drawMatrixEllipse(matrix, 13, 13, 2, 1);
    } else if (kind === "tank") {
      fillMatrixRect(matrix, 2, 9, 12, 3);
      drawMatrixEllipse(matrix, 8, 12, 6, 2);
      fillMatrixRect(matrix, 6, 6, 5, 3);
      drawMatrixLine(matrix, 10, 7, 15, 4);
      setMatrixPixel(matrix, 14, 4);
    } else if (kind === "train") {
      fillMatrixRect(matrix, 3, 5, 8, 8);
      fillMatrixRect(matrix, 11, 8, 3, 5);
      drawMatrixLine(matrix, 4, 5, 4, 2);
      drawMatrixLine(matrix, 2, 13, 14, 13);
      drawMatrixEllipse(matrix, 5, 14, 2, 1);
      drawMatrixEllipse(matrix, 12, 14, 2, 1);
      setMatrixPixel(matrix, 12, 9);
    } else if (kind === "car") {
      fillMatrixRect(matrix, 2, 9, 12, 4);
      drawMatrixLine(matrix, 5, 9, 7, 5);
      drawMatrixLine(matrix, 7, 5, 11, 5);
      drawMatrixLine(matrix, 11, 5, 13, 9);
      drawMatrixEllipse(matrix, 5, 13, 2, 2);
      drawMatrixEllipse(matrix, 11, 13, 2, 2);
    } else if (kind === "motorcycle") {
      drawMatrixEllipse(matrix, 4, 12, 3, 3);
      drawMatrixEllipse(matrix, 12, 12, 3, 3);
      drawMatrixLine(matrix, 4, 11, 8, 7);
      drawMatrixLine(matrix, 8, 7, 12, 11);
      drawMatrixLine(matrix, 8, 7, 11, 5);
      drawMatrixLine(matrix, 11, 5, 13, 5);
      fillMatrixRect(matrix, 6, 8, 3, 2);
    } else if (kind === "sailboat") {
      drawMatrixLine(matrix, 2, 12, 14, 12);
      drawMatrixLine(matrix, 3, 12, 6, 14);
      drawMatrixLine(matrix, 13, 12, 10, 14);
      drawMatrixLine(matrix, 8, 11, 8, 2);
      drawMatrixLine(matrix, 8, 3, 3, 9);
      drawMatrixLine(matrix, 9, 4, 13, 10);
    } else if (kind === "submarine") {
      drawMatrixEllipse(matrix, 8, 9, 7, 4);
      fillMatrixRect(matrix, 6, 4, 4, 3);
      drawMatrixLine(matrix, 8, 4, 8, 2);
      drawMatrixLine(matrix, 8, 2, 12, 2);
      drawMatrixLine(matrix, 14, 9, 15, 7);
      setMatrixPixel(matrix, 4, 9);
      setMatrixPixel(matrix, 8, 9);
      setMatrixPixel(matrix, 12, 9);
    } else if (kind === "mech") {
      fillMatrixRect(matrix, 5, 3, 6, 4);
      fillMatrixRect(matrix, 4, 7, 8, 5);
      drawMatrixLine(matrix, 4, 8, 1, 12);
      drawMatrixLine(matrix, 11, 8, 14, 12);
      drawMatrixLine(matrix, 6, 12, 5, 15);
      drawMatrixLine(matrix, 10, 12, 11, 15);
      setMatrixPixel(matrix, 6, 5, 0);
      setMatrixPixel(matrix, 9, 5, 0);
    }
  };
}

function mammalPainter({ ears = "round", tail = "short", legs = 4, horn = false } = {}) {
  return (matrix) => {
    drawMatrixEllipse(matrix, 8, 10, 5, 4);
    drawMatrixEllipse(matrix, 5, 6, 3, 3);
    if (ears === "long") {
      drawMatrixLine(matrix, 3, 4, 2, 0);
      drawMatrixLine(matrix, 6, 4, 7, 0);
    } else if (ears === "point") {
      drawMatrixLine(matrix, 3, 4, 2, 1);
      drawMatrixLine(matrix, 6, 4, 7, 1);
    } else {
      drawMatrixEllipse(matrix, 3, 3, 2, 2);
      drawMatrixEllipse(matrix, 7, 3, 2, 2);
    }
    if (horn) {
      drawMatrixLine(matrix, 3, 4, 1, 1);
      drawMatrixLine(matrix, 6, 4, 8, 1);
    }
    if (tail === "long") drawMatrixLine(matrix, 12, 9, 15, 5);
    if (tail === "curled") {
      drawMatrixLine(matrix, 12, 9, 15, 9);
      drawMatrixLine(matrix, 15, 9, 15, 6);
      drawMatrixLine(matrix, 15, 6, 13, 6);
    }
    if (tail === "bushy") {
      drawMatrixLine(matrix, 12, 9, 15, 6);
      drawMatrixEllipse(matrix, 14, 5, 2, 2);
    }
    for (let index = 0; index < legs; index += 1) {
      const x = 5 + index * Math.max(1, Math.floor(6 / Math.max(1, legs - 1)));
      drawMatrixLine(matrix, x, 12, x, 15);
    }
    setMatrixPixel(matrix, 4, 6, 0);
    setMatrixPixel(matrix, 5, 6, 0);
  };
}

function birdPainter({ wing = "wide", crest = false, beak = true } = {}) {
  return (matrix) => {
    drawMatrixEllipse(matrix, 8, 9, 5, 4);
    drawMatrixEllipse(matrix, 6, 5, 3, 3);
    if (wing === "wide") {
      drawMatrixLine(matrix, 7, 8, 1, 3);
      drawMatrixLine(matrix, 1, 3, 2, 9);
      drawMatrixLine(matrix, 8, 8, 14, 3);
      drawMatrixLine(matrix, 14, 3, 13, 9);
    } else if (wing === "folded") {
      drawMatrixLine(matrix, 8, 8, 12, 12);
      drawMatrixLine(matrix, 12, 12, 7, 13);
    } else {
      drawMatrixLine(matrix, 7, 8, 3, 12);
      drawMatrixLine(matrix, 3, 12, 1, 8);
    }
    if (crest) drawMatrixLine(matrix, 6, 3, 5, 0);
    if (beak) drawMatrixLine(matrix, 3, 5, 0, 6);
    drawMatrixLine(matrix, 7, 12, 6, 15);
    drawMatrixLine(matrix, 9, 12, 10, 15);
  };
}

function aquaticPainter({ fins = "side", tentacles = false, longBody = false } = {}) {
  return (matrix) => {
    drawMatrixEllipse(matrix, longBody ? 8 : 7, 8, longBody ? 7 : 5, longBody ? 3 : 4);
    if (fins === "side") {
      drawMatrixLine(matrix, 7, 7, 10, 3);
      drawMatrixLine(matrix, 7, 9, 10, 13);
    } else if (fins === "top") {
      drawMatrixLine(matrix, 8, 5, 8, 1);
      drawMatrixLine(matrix, 7, 5, 11, 3);
    }
    drawMatrixLine(matrix, 13, 8, 15, 4);
    drawMatrixLine(matrix, 13, 8, 15, 12);
    setMatrixPixel(matrix, 4, 7, 0);
    if (tentacles) {
      drawMatrixEllipse(matrix, 8, 6, 4, 4);
      for (let x = 4; x <= 12; x += 2) {
        drawMatrixLine(matrix, x, 9, x + (x % 4 ? 1 : -1), 15);
      }
    }
  };
}

function reptilePainter({ shell = false, longBody = false, amphibian = false, teeth = false } = {}) {
  return (matrix) => {
    if (longBody) {
      drawMatrixLine(matrix, 1, 9, 12, 8);
      drawMatrixEllipse(matrix, 10, 8, 5, 2);
      drawMatrixLine(matrix, 4, 9, 1, 14);
    } else {
      drawMatrixEllipse(matrix, 8, 9, shell ? 6 : 5, 4);
      drawMatrixEllipse(matrix, 4, 6, 3, 3);
    }
    if (shell) {
      drawMatrixEllipse(matrix, 9, 8, 4, 3);
      drawMatrixLine(matrix, 5, 9, 12, 9);
      drawMatrixLine(matrix, 8, 5, 8, 12);
    }
    if (amphibian) {
      drawMatrixLine(matrix, 5, 11, 2, 14);
      drawMatrixLine(matrix, 11, 11, 14, 14);
      drawMatrixLine(matrix, 5, 12, 3, 15);
      drawMatrixLine(matrix, 11, 12, 13, 15);
    } else {
      drawMatrixLine(matrix, 6, 12, 5, 15);
      drawMatrixLine(matrix, 10, 12, 11, 15);
    }
    if (teeth) drawMatrixLine(matrix, 1, 8, 0, 11);
  };
}

const SIDE_VIEW_ASSETS = [
  tile("side-grass-top", "Grass Top", "side-view", ["terrain", "ground", "tileable"], ["........", "........", "########", ".#.#.#.#", "########", "........", "........", "........"]),
  tile("side-grass-fill", "Grass Fill", "side-view", ["terrain", "ground", "tileable"], [".#.#.#.#", "########", "#.#.#.#.", "########", ".#.#.#.#", "########", "#.#.#.#.", "########"]),
  tile("side-dirt-fill", "Dirt Fill", "side-view", ["terrain", "ground", "tileable"], ["#..#..#.", ".##..##.", "..#.#..#", "##...##.", ".#.##.#.", "#...#..#", ".##..##.", "#..#.#.."]),
  tile("side-stone-wall", "Stone Wall", "side-view", ["terrain", "wall", "tileable"], ["########", "#..##..#", "########", "##..##..", "########", "#..##..#", "########", "##..##.."]),
  tile("side-brick-wall", "Brick Wall", "side-view", ["terrain", "wall", "tileable"], ["########", "#...#...", "########", "...#...#", "########", "#...#...", "########", "...#...#"]),
  tile("side-metal-wall", "Metal Wall", "side-view", ["terrain", "wall", "metal"], ["########", "#......#", "#.#..#.#", "#......#", "#......#", "#.#..#.#", "#......#", "########"]),
  tile("side-ice-wall", "Ice Wall", "side-view", ["terrain", "wall", "ice"], ["##....##", "#.#..#.#", "..####..", ".##..##.", "##....##", "#.#..#.#", "..####..", ".##..##."]),
  tile("side-cloud-platform", "Cloud Platform", "side-view", ["platform", "cloud"], ["........", "........", "..##....", ".######.", "########", ".######.", "........", "........"]),
  tile("side-wood-platform", "Wood Platform", "side-view", ["platform", "wood"], ["........", "........", "########", "#..##..#", "########", "........", "........", "........"]),
  tile("side-rope-bridge", "Rope Bridge", "side-view", ["platform", "bridge", "rope"], ["........", "........", "#......#", ".##..##.", "..####..", ".##..##.", "#......#", "........"]),
  tile("side-ladder", "Ladder", "side-view", ["traversal", "ladder"], ["#......#", "#......#", "########", "#......#", "########", "#......#", "########", "#......#"]),
  tile("side-stairs-right", "Stairs Right", "side-view", ["traversal", "stairs"], [".......#", "......##", ".....###", "....####", "...#####", "..######", ".#######", "########"]),
  tile("side-stairs-left", "Stairs Left", "side-view", ["traversal", "stairs"], ["#.......", "##......", "###.....", "####....", "#####...", "######..", "#######.", "########"]),
  tile("side-jump-pad", "Jump Pad", "side-view", ["traversal", "jump"], ["........", "........", "..#..#..", ".#.##.#.", "########", "..#..#..", ".#....#.", "#......#"]),
  tile("side-conveyor-left", "Conveyor Left", "side-view", ["platform", "conveyor"], ["........", "########", "..##..##", ".##..##.", "##..##..", ".##..##.", "########", "........"]),
  tile("side-conveyor-right", "Conveyor Right", "side-view", ["platform", "conveyor"], ["........", "########", "##..##..", ".##..##.", "..##..##", ".##..##.", "########", "........"]),
  tile("side-floor-spikes", "Floor Spikes", "side-view", ["hazard", "trap"], ["........", "........", "........", ".#.#.#.#", "########", "########", "########", "########"]),
  tile("side-ceiling-spikes", "Ceiling Spikes", "side-view", ["hazard", "trap"], ["########", "########", "########", "########", ".#.#.#.#", "........", "........", "........"]),
  tile("side-flame-jet", "Flame Jet", "side-view", ["hazard", "fire"], ["...#....", "..###...", ".##.##..", "...#....", "..###...", ".##.##..", "########", "########"]),
  tile("side-door", "Door", "side-view", ["access", "door"], [".######.", ".#....#.", ".#....#.", ".#....#.", ".#..#.#.", ".#....#.", ".#....#.", ".######."]),
  tile("side-locked-door", "Locked Door", "side-view", ["access", "door", "lock"], [".######.", ".#....#.", ".#..#.#.", ".#.###.#", ".#.###.#", ".#..#.#.", ".#....#.", ".######."]),
  tile("side-water-surface", "Water Surface", "side-view", ["water", "tileable"], ["........", "........", ".##..##.", "#..##..#", ".##..##.", "........", "........", "........"]),
  tile("side-water-fill", "Water Fill", "side-view", ["water", "tileable"], [".##..##.", "#..##..#", ".##..##.", "#..##..#", ".##..##.", "#..##..#", ".##..##.", "#..##..#"]),
  tile("side-waterfall", "Waterfall", "side-view", ["water", "fall"], [".##..##.", "#..##..#", ".##..##.", "#..##..#", ".##..##.", "#..##..#", ".##..##.", "#..##..#"]),
  tile("side-lava-surface", "Lava Surface", "side-view", ["hazard", "lava"], ["........", ".#..#.#.", "########", "#.#..#.#", "########", "........", "........", "........"]),
  tile("side-lava-fill", "Lava Fill", "side-view", ["hazard", "lava", "tileable"], ["#.#..#.#", "########", ".##.##..", "########", "#..##..#", "########", ".#.##.#.", "########"]),
];

const TOP_VIEW_ASSETS = [
  tile("top-grass", "Grass", "top-view", ["terrain", "grass", "tileable"], [".#...#..", "...#...#", "#....#..", "..#...#.", ".#....#.", "...#...#", "#...#...", "..#....#"]),
  tile("top-tall-grass", "Tall Grass", "top-view", ["terrain", "grass", "obstacle"], [".#.#.#.#", ".#.#.#.#", "..#.#.#.", ".#.#.#.#", "#.#.#.#.", ".#.#.#.#", "..#.#.#.", ".#.#.#.#"]),
  tile("top-dirt", "Dirt", "top-view", ["terrain", "dirt", "tileable"], ["#...#...", ".##...#.", "...#..##", "#..#....", ".#...##.", "..##...#", "#....#..", ".#..#..."]),
  tile("top-sand", "Sand", "top-view", ["terrain", "sand", "tileable"], ["..#.....", ".....#..", "...#....", ".#....#.", "....#...", "#.....#.", "...#....", ".#....#."]),
  tile("top-shallow-water", "Shallow Water", "top-view", ["terrain", "water", "tileable"], [".##..##.", "..##..##", "##..##..", ".##..##.", "..##..##", "##..##..", ".##..##.", "..##..##"]),
  tile("top-deep-water", "Deep Water", "top-view", ["terrain", "water", "tileable"], ["##....##", "..####..", "....####", "####....", "##....##", "..####..", "....####", "####...."]),
  tile("top-road-horizontal", "Road Horizontal", "top-view", ["road", "tileable"], ["........", "........", "........", "########", "########", "........", "........", "........"]),
  tile("top-road-vertical", "Road Vertical", "top-view", ["road", "tileable"], ["...##...", "...##...", "...##...", "...##...", "...##...", "...##...", "...##...", "...##..."]),
  tile("top-road-corner-ne", "Road Corner NE", "top-view", ["road", "corner"], ["...##...", "...##...", "...##...", "...##...", "...##...", "...#####", "...#####", "........"]),
  tile("top-road-corner-nw", "Road Corner NW", "top-view", ["road", "corner"], ["...##...", "...##...", "...##...", "...##...", "...##...", "#####...", "#####...", "........"]),
  tile("top-road-corner-se", "Road Corner SE", "top-view", ["road", "corner"], ["........", "...#####", "...#####", "...##...", "...##...", "...##...", "...##...", "...##..."]),
  tile("top-road-corner-sw", "Road Corner SW", "top-view", ["road", "corner"], ["........", "#####...", "#####...", "...##...", "...##...", "...##...", "...##...", "...##..."]),
  tile("top-road-t-north", "Road T North", "top-view", ["road", "junction"], ["...##...", "...##...", "...##...", "...##...", "########", "########", "........", "........"]),
  tile("top-road-t-east", "Road T East", "top-view", ["road", "junction"], ["...##...", "...##...", "...##...", "...#####", "...#####", "...##...", "...##...", "...##..."]),
  tile("top-road-t-south", "Road T South", "top-view", ["road", "junction"], ["........", "........", "########", "########", "...##...", "...##...", "...##...", "...##..."]),
  tile("top-road-t-west", "Road T West", "top-view", ["road", "junction"], ["...##...", "...##...", "...##...", "#####...", "#####...", "...##...", "...##...", "...##..."]),
  tile("top-road-crossroad", "Road Crossroad", "top-view", ["road", "junction"], ["...##...", "...##...", "...##...", "########", "########", "...##...", "...##...", "...##..."]),
  tile("top-river-horizontal", "River Horizontal", "top-view", ["river", "water", "tileable"], ["........", ".##..##.", "##..##..", "########", "########", "..##..##", ".##..##.", "........"]),
  tile("top-river-vertical", "River Vertical", "top-view", ["river", "water", "tileable"], ["..####..", ".######.", ".##..##.", ".######.", ".######.", ".##..##.", ".######.", "..####.."]),
  tile("top-river-bend-ne", "River Bend NE", "top-view", ["river", "water", "corner"], ["....####", "...#####", "..######", ".####...", "####....", "###.....", "##......", "........"]),
  tile("top-river-bend-nw", "River Bend NW", "top-view", ["river", "water", "corner"], ["####....", "#####...", "######..", "...####.", "....####", ".....###", "......##", "........"]),
  tile("top-river-bend-se", "River Bend SE", "top-view", ["river", "water", "corner"], ["........", "##......", "###.....", "####....", ".####...", "..######", "...#####", "....####"]),
  tile("top-river-bend-sw", "River Bend SW", "top-view", ["river", "water", "corner"], ["........", "......##", ".....###", "....####", "...####.", "######..", "#####...", "####...."]),
  tile("top-shore-north", "Shore North", "top-view", ["shore", "water"], ["#..#..#.", ".#..#..#", "########", ".##..##.", "#..##..#", ".##..##.", "#..##..#", ".##..##."]),
  tile("top-shore-south", "Shore South", "top-view", ["shore", "water"], [".##..##.", "#..##..#", ".##..##.", "#..##..#", ".##..##.", "########", "#..#..#.", ".#..#..#"]),
  tile("top-shore-east", "Shore East", "top-view", ["shore", "water"], ["...##.#.", "...##.#.", "...##.#.", "...##.#.", "...##.#.", "...##.#.", "...##.#.", "...##.#."]),
  tile("top-shore-west", "Shore West", "top-view", ["shore", "water"], [".#.##...", ".#.##...", ".#.##...", ".#.##...", ".#.##...", ".#.##...", ".#.##...", ".#.##..."]),
  tile("top-bridge-horizontal", "Bridge Horizontal", "top-view", ["bridge", "road"], ["........", "########", "#.#..#.#", "########", "########", "#.#..#.#", "########", "........"]),
  tile("top-bridge-vertical", "Bridge Vertical", "top-view", ["bridge", "road"], [".######.", ".#.#..#.", ".######.", ".######.", ".#.#..#.", ".######.", ".######.", ".#.#..#."]),
  tile("top-fence-horizontal", "Fence Horizontal", "top-view", ["fence", "obstacle"], ["........", "########", "#.#.#.#.", "########", "........", "........", "........", "........"]),
  tile("top-fence-vertical", "Fence Vertical", "top-view", ["fence", "obstacle"], ["..##....", "..##....", "########", "..##....", "..##....", "..##....", "########", "..##...."]),
  tile("top-tree", "Tree", "top-view", ["nature", "tree", "obstacle"], ["...##...", ".######.", "########", "########", ".######.", "...##...", "...##...", "..####.."]),
  tile("top-bush", "Bush", "top-view", ["nature", "bush", "obstacle"], ["........", ".##..##.", "########", "########", ".######.", "..####..", "........", "........"]),
  tile("top-rock", "Rock", "top-view", ["nature", "rock", "obstacle"], ["........", "...##...", ".######.", "########", "########", ".######.", "........", "........"]),
];

const SYMBOL_ASSETS = [
  tile("symbol-arrow-up", "Arrow Up", "symbols", ["direction", "arrow"], ["...##...", ".####...", "##.##...", "...##...", "...##...", "...##...", "...##...", "........"]),
  tile("symbol-arrow-down", "Arrow Down", "symbols", ["direction", "arrow"], ["........", "...##...", "...##...", "...##...", "...##...", "##.##...", ".####...", "...##..."]),
  tile("symbol-arrow-left", "Arrow Left", "symbols", ["direction", "arrow"], ["........", "...#....", "..##....", ".#######", "########", ".#######", "..##....", "...#...."]),
  tile("symbol-arrow-right", "Arrow Right", "symbols", ["direction", "arrow"], ["........", "....#...", "....##..", "#######.", "########", "#######.", "....##..", "....#..."]),
  tile("symbol-passage", "Passage", "symbols", ["status", "access"], [".######.", ".#....#.", ".#.##.#.", ".#.##.#.", ".#....#.", ".#....#.", ".######.", "........"]),
  tile("symbol-no-passage", "No Passage", "symbols", ["status", "access"], [".######.", ".#....#.", ".#...##.", ".#..##..", ".#.##...", ".##....#", ".######.", "........"]),
  tile("symbol-check", "Check", "symbols", ["status", "confirm"], ["........", ".......#", "......##", "#....##.", ".#..##..", "..###...", "...#....", "........"]),
  tile("symbol-cross", "Cross", "symbols", ["status", "cancel"], ["........", "##....##", ".##..##.", "..####..", "..####..", ".##..##.", "##....##", "........"]),
  tile("symbol-warning", "Warning", "symbols", ["status", "warning"], ["...##...", "..####..", ".##..##.", ".##..##.", "....##..", "........", "....##..", "........"]),
  tile("symbol-question", "Question", "symbols", ["status", "question"], [".######.", "##....##", ".....##.", "...###..", "...##...", "........", "...##...", "........"]),
  tile("symbol-heart", "Heart", "symbols", ["status", "heart"], [".##..##.", "########", "########", ".######.", "..####..", "...##...", "....#...", "........"]),
  tile("symbol-star", "Star", "symbols", ["celestial", "star"], ["........", "...#....", "#.###.#.", ".#####..", "#######.", ".#####..", "#.###.#.", "...#...."]),
  tile("symbol-moon", "Moon", "symbols", ["celestial", "moon"], ["...###..", ".##..##.", ".#......", "##......", "##......", ".#......", ".##..##.", "...###.."]),
  tile("symbol-sun", "Sun", "symbols", ["celestial", "sun"], ["...#....", ".#.#.#..", "..###...", "#######.", "..###...", ".#.#.#..", "...#....", "........"]),
  tile("symbol-compass", "Compass", "symbols", ["navigation", "compass"], ["...#....", "..###...", ".##.##..", "##.#.##.", ".##.##..", "..###...", "...#....", "........"]),
  tile("symbol-target", "Target", "symbols", ["navigation", "target"], [".######.", "##....##", "#.####.#", "#.#..#.#", "#.#..#.#", "#.####.#", "##....##", ".######."]),
  tile("symbol-key", "Key", "symbols", ["access", "key"], ["........", ".####...", "##..##..", ".####...", "...##...", "...##...", "..##.##.", "........"]),
  tile("symbol-lock", "Lock", "symbols", ["access", "lock"], ["..####..", ".##..##.", ".##..##.", ".######.", ".##..##.", ".##..##.", ".######.", "........"]),
  tile("symbol-aries", "Aries", "symbols", ["constellation", "zodiac"], ["#......#", ".#....#.", "..#..#..", "...##...", "...##...", "...##...", "..####..", "........"]),
  tile("symbol-scorpius", "Scorpius", "symbols", ["constellation", "zodiac"], ["##......", ".##.....", "..##....", "...##...", "....##..", ".....##.", "...###..", "........"]),
  tile("symbol-ursa", "Ursa", "symbols", ["constellation", "zodiac"], ["#......#", ".#....#.", "..#..#..", "...##...", "....#...", "....##..", "...#..#.", "........"]),
  tile("symbol-rune-one", "Rune One", "symbols", ["rune", "magic"], ["...##...", "..####..", "...##...", "...##...", "...##...", ".######.", "........", "........"]),
  tile("symbol-rune-two", "Rune Two", "symbols", ["rune", "magic"], [".######.", "...##...", "...##...", "...##...", "...##...", ".######.", "........", "........"]),
  tile("symbol-rune-three", "Rune Three", "symbols", ["rune", "magic"], ["##....##", ".##..##.", "..####..", "...##...", "..####..", ".##..##.", "##....##", "........"]),
];

const STATIONERY_ASSETS = [
  tile("stationery-pencil", "Pencil", "stationery", ["tool", "writing"], ["......##", ".....##.", "....##..", "...##...", "..##....", ".##.....", "##......", "........"]),
  tile("stationery-pen", "Pen", "stationery", ["tool", "writing"], [".....##.", "....##..", "...##...", "..##....", ".##.....", "##......", "#.......", "........"]),
  tile("stationery-eraser", "Eraser", "stationery", ["tool"], ["........", ".######.", "########", "########", "########", ".######.", "........", "........"]),
  tile("stationery-ruler", "Ruler", "stationery", ["tool", "measure"], ["........", "########", "#.#.#.#.", "########", "........", "........", "........", "........"]),
  tile("stationery-set-square", "Set Square", "stationery", ["tool", "measure"], ["........", ".#......", ".##.....", ".#.#....", ".#..#...", ".#...#..", ".######.", "........"]),
  tile("stationery-compass", "Compass Tool", "stationery", ["tool", "measure"], ["...##...", "..####..", "...##...", "..#..#..", ".#....#.", "#......#", "........", "........"]),
  tile("stationery-notebook", "Notebook", "stationery", ["paper", "writing"], [".######.", ".#.#..#.", ".#.#..#.", ".#.#..#.", ".#.#..#.", ".#.#..#.", ".######.", "........"]),
  tile("stationery-paperclip", "Paperclip", "stationery", ["tool", "paper"], ["...##...", "..#..#..", "..#..#..", "..#..#..", "..#..#..", "..#..#..", "...##...", "........"]),
  tile("stationery-pushpin", "Pushpin", "stationery", ["tool", "pin"], ["...##...", ".######.", ".######.", "...##...", "...##...", "...##...", "..####..", "........"]),
  tile("stationery-scissors", "Scissors", "stationery", ["tool", "cut"], [".##..##.", "##....##", ".##..##.", "...##...", "..#..#..", ".#....#.", "#......#", "........"]),
  tile("stationery-tape", "Tape", "stationery", ["tool", "tape"], [".######.", "##....##", "#.####.#", "#.#..#.#", "#.####.#", "##....##", ".######.", "........"]),
  tile("stationery-stapler", "Stapler", "stationery", ["tool", "office"], ["........", ".######.", "########", ".....##.", ".######.", "########", "........", "........"]),
];

const VEHICLE_ASSETS = [
  sprite("vehicle-propeller-plane", "Propeller Plane", "vehicles", ["aircraft", "plane"], vehiclePainter("propeller-plane")),
  sprite("vehicle-fighter-jet", "Fighter Jet", "vehicles", ["aircraft", "fighter"], vehiclePainter("fighter-jet")),
  sprite("vehicle-bomber", "Bomber", "vehicles", ["aircraft", "plane"], vehiclePainter("bomber")),
  sprite("vehicle-biplane", "Biplane", "vehicles", ["aircraft", "plane"], vehiclePainter("biplane")),
  sprite("vehicle-helicopter", "Helicopter", "vehicles", ["aircraft", "rotor"], vehiclePainter("helicopter")),
  sprite("vehicle-rocket", "Rocket", "vehicles", ["space", "rocket"], vehiclePainter("rocket")),
  sprite("vehicle-ufo", "UFO", "vehicles", ["space", "ufo"], vehiclePainter("ufo")),
  sprite("vehicle-airship", "Airship", "vehicles", ["aircraft", "airship"], vehiclePainter("airship")),
  sprite("vehicle-drone", "Drone", "vehicles", ["aircraft", "drone"], vehiclePainter("drone")),
  sprite("vehicle-tank", "Tank", "vehicles", ["land", "tank"], vehiclePainter("tank")),
  sprite("vehicle-train", "Train Engine", "vehicles", ["land", "train"], vehiclePainter("train")),
  sprite("vehicle-car", "Car", "vehicles", ["land", "car"], vehiclePainter("car")),
  sprite("vehicle-motorcycle", "Motorcycle", "vehicles", ["land", "motorcycle"], vehiclePainter("motorcycle")),
  sprite("vehicle-sailboat", "Sailboat", "vehicles", ["sea", "boat"], vehiclePainter("sailboat")),
  sprite("vehicle-submarine", "Submarine", "vehicles", ["sea", "submarine"], vehiclePainter("submarine")),
  sprite("vehicle-mech", "Mech", "vehicles", ["machine", "mech"], vehiclePainter("mech")),
];

const CREATURE_ASSETS = [
  sprite("creature-cat", "Cat", "creatures", ["mammal", "animal"], mammalPainter({ ears: "point", tail: "long" })),
  sprite("creature-dog", "Dog", "creatures", ["mammal", "animal"], mammalPainter({ ears: "round", tail: "short" })),
  sprite("creature-rabbit", "Rabbit", "creatures", ["mammal", "animal"], mammalPainter({ ears: "long", tail: "short" })),
  sprite("creature-fox", "Fox", "creatures", ["mammal", "animal"], mammalPainter({ ears: "point", tail: "bushy" })),
  sprite("creature-bear", "Bear", "creatures", ["mammal", "animal"], mammalPainter({ ears: "round", tail: "short", legs: 2 })),
  sprite("creature-horse", "Horse", "creatures", ["mammal", "animal"], mammalPainter({ ears: "point", tail: "long", legs: 4 })),
  sprite("creature-cow", "Cow", "creatures", ["mammal", "animal"], mammalPainter({ ears: "round", tail: "long", legs: 4, horn: true })),
  sprite("creature-elephant", "Elephant", "creatures", ["mammal", "animal"], (matrix) => {
    drawMatrixEllipse(matrix, 9, 9, 6, 5);
    drawMatrixEllipse(matrix, 4, 6, 4, 4);
    drawMatrixEllipse(matrix, 3, 7, 3, 4);
    drawMatrixLine(matrix, 2, 8, 1, 14);
    drawMatrixLine(matrix, 6, 12, 5, 15);
    drawMatrixLine(matrix, 11, 12, 11, 15);
    setMatrixPixel(matrix, 3, 6, 0);
  }),
  sprite("creature-sparrow", "Sparrow", "creatures", ["bird", "animal"], birdPainter({ wing: "wide" })),
  sprite("creature-eagle", "Eagle", "creatures", ["bird", "animal"], birdPainter({ wing: "wide", crest: true })),
  sprite("creature-owl", "Owl", "creatures", ["bird", "animal"], birdPainter({ wing: "folded", crest: true, beak: false })),
  sprite("creature-penguin", "Penguin", "creatures", ["bird", "animal"], (matrix) => {
    drawMatrixEllipse(matrix, 8, 9, 5, 6);
    drawMatrixEllipse(matrix, 8, 4, 4, 3);
    drawMatrixLine(matrix, 3, 8, 1, 11);
    drawMatrixLine(matrix, 13, 8, 15, 11);
    drawMatrixLine(matrix, 6, 14, 4, 15);
    drawMatrixLine(matrix, 10, 14, 12, 15);
    setMatrixPixel(matrix, 6, 4, 0);
    setMatrixPixel(matrix, 10, 4, 0);
  }),
  sprite("creature-fish", "Fish", "creatures", ["fish", "aquatic"], aquaticPainter({ fins: "side" })),
  sprite("creature-shark", "Shark", "creatures", ["fish", "aquatic"], aquaticPainter({ fins: "top", longBody: true })),
  sprite("creature-whale", "Whale", "creatures", ["aquatic", "mammal"], (matrix) => {
    drawMatrixEllipse(matrix, 8, 9, 7, 4);
    drawMatrixLine(matrix, 11, 5, 13, 2);
    drawMatrixLine(matrix, 13, 2, 15, 3);
    drawMatrixLine(matrix, 13, 2, 14, 0);
    drawMatrixLine(matrix, 14, 9, 15, 6);
    drawMatrixLine(matrix, 14, 9, 15, 12);
    setMatrixPixel(matrix, 4, 8, 0);
  }),
  sprite("creature-octopus", "Octopus", "creatures", ["aquatic", "mollusk"], aquaticPainter({ tentacles: true })),
  sprite("creature-turtle", "Turtle", "creatures", ["reptile", "animal"], reptilePainter({ shell: true })),
  sprite("creature-snake", "Snake", "creatures", ["reptile", "animal"], reptilePainter({ longBody: true })),
  sprite("creature-lizard", "Lizard", "creatures", ["reptile", "animal"], reptilePainter({ longBody: true })),
  sprite("creature-crocodile", "Crocodile", "creatures", ["reptile", "animal"], reptilePainter({ longBody: true, teeth: true })),
  sprite("creature-frog", "Frog", "creatures", ["amphibian", "animal"], reptilePainter({ amphibian: true })),
  sprite("creature-salamander", "Salamander", "creatures", ["amphibian", "animal"], reptilePainter({ amphibian: true, longBody: true })),
  sprite("creature-dragon", "Dragon", "creatures", ["fantasy", "dragon"], (matrix) => {
    drawMatrixEllipse(matrix, 8, 9, 5, 4);
    drawMatrixLine(matrix, 6, 7, 2, 1);
    drawMatrixLine(matrix, 2, 1, 1, 8);
    drawMatrixLine(matrix, 9, 7, 15, 2);
    drawMatrixLine(matrix, 15, 2, 14, 9);
    drawMatrixLine(matrix, 4, 8, 1, 13);
    drawMatrixLine(matrix, 12, 10, 15, 14);
    drawMatrixLine(matrix, 7, 12, 6, 15);
    drawMatrixLine(matrix, 10, 12, 11, 15);
  }),
  sprite("creature-slime", "Slime", "creatures", ["fantasy", "slime"], (matrix) => {
    drawMatrixEllipse(matrix, 8, 10, 6, 4);
    drawMatrixLine(matrix, 2, 10, 3, 5);
    drawMatrixLine(matrix, 3, 5, 5, 7);
    drawMatrixLine(matrix, 13, 10, 12, 5);
    drawMatrixLine(matrix, 12, 5, 10, 7);
    setMatrixPixel(matrix, 6, 9, 0);
    setMatrixPixel(matrix, 10, 9, 0);
  }),
  sprite("creature-ghost", "Ghost", "creatures", ["fantasy", "ghost"], (matrix) => {
    drawMatrixEllipse(matrix, 8, 7, 5, 5);
    fillMatrixRect(matrix, 3, 7, 11, 6);
    drawMatrixLine(matrix, 3, 13, 5, 15);
    drawMatrixLine(matrix, 7, 13, 8, 15);
    drawMatrixLine(matrix, 11, 13, 13, 15);
    setMatrixPixel(matrix, 6, 7, 0);
    setMatrixPixel(matrix, 10, 7, 0);
  }),
  sprite("creature-goblin", "Goblin", "creatures", ["fantasy", "goblin"], (matrix) => {
    drawMatrixEllipse(matrix, 8, 5, 5, 4);
    fillMatrixRect(matrix, 5, 9, 7, 4);
    drawMatrixLine(matrix, 5, 5, 0, 7);
    drawMatrixLine(matrix, 11, 5, 15, 7);
    drawMatrixLine(matrix, 6, 13, 5, 15);
    drawMatrixLine(matrix, 10, 13, 11, 15);
    setMatrixPixel(matrix, 6, 5, 0);
    setMatrixPixel(matrix, 10, 5, 0);
  }),
  sprite("creature-robot", "Robot", "creatures", ["fantasy", "robot"], (matrix) => {
    fillMatrixRect(matrix, 4, 3, 8, 5);
    fillMatrixRect(matrix, 3, 8, 10, 5);
    drawMatrixLine(matrix, 4, 9, 1, 12);
    drawMatrixLine(matrix, 11, 9, 14, 12);
    drawMatrixLine(matrix, 6, 13, 5, 15);
    drawMatrixLine(matrix, 10, 13, 11, 15);
    setMatrixPixel(matrix, 6, 5, 0);
    setMatrixPixel(matrix, 10, 5, 0);
  }),
  sprite("creature-animal-hero", "Animal Hero", "creatures", ["fantasy", "anthro"], (matrix) => {
    drawMatrixEllipse(matrix, 8, 4, 4, 3);
    fillMatrixRect(matrix, 5, 8, 7, 5);
    drawMatrixLine(matrix, 5, 9, 1, 12);
    drawMatrixLine(matrix, 11, 9, 14, 7);
    drawMatrixLine(matrix, 6, 13, 5, 15);
    drawMatrixLine(matrix, 10, 13, 11, 15);
    drawMatrixLine(matrix, 5, 3, 3, 0);
    drawMatrixLine(matrix, 10, 3, 12, 0);
  }),
  sprite("creature-walking-mushroom", "Walking Mushroom", "creatures", ["plant", "fantasy"], (matrix) => {
    drawMatrixEllipse(matrix, 8, 5, 7, 4);
    fillMatrixRect(matrix, 6, 8, 5, 5);
    drawMatrixLine(matrix, 7, 13, 6, 15);
    drawMatrixLine(matrix, 10, 13, 11, 15);
    setMatrixPixel(matrix, 7, 10, 0);
    setMatrixPixel(matrix, 9, 10, 0);
  }),
  sprite("creature-flower-sprite", "Flower Sprite", "creatures", ["plant", "fantasy"], (matrix) => {
    drawMatrixEllipse(matrix, 8, 5, 3, 3);
    drawMatrixEllipse(matrix, 4, 5, 3, 2);
    drawMatrixEllipse(matrix, 12, 5, 3, 2);
    drawMatrixEllipse(matrix, 8, 1, 2, 3);
    drawMatrixLine(matrix, 8, 8, 8, 14);
    drawMatrixLine(matrix, 8, 11, 3, 13);
    drawMatrixLine(matrix, 8, 12, 13, 14);
  }),
  sprite("creature-tree-spirit", "Tree Spirit", "creatures", ["plant", "fantasy"], (matrix) => {
    drawMatrixEllipse(matrix, 8, 5, 7, 5);
    fillMatrixRect(matrix, 6, 9, 5, 6);
    drawMatrixLine(matrix, 6, 11, 2, 14);
    drawMatrixLine(matrix, 10, 11, 14, 14);
    setMatrixPixel(matrix, 6, 5, 0);
    setMatrixPixel(matrix, 10, 5, 0);
  }),
  sprite("creature-carnivorous-plant", "Carnivorous Plant", "creatures", ["plant", "fantasy"], (matrix) => {
    drawMatrixEllipse(matrix, 8, 5, 6, 4);
    drawMatrixLine(matrix, 3, 5, 13, 5);
    drawMatrixLine(matrix, 8, 9, 8, 14);
    drawMatrixLine(matrix, 8, 11, 3, 14);
    drawMatrixLine(matrix, 8, 12, 13, 15);
    drawMatrixLine(matrix, 4, 6, 6, 8);
    drawMatrixLine(matrix, 12, 6, 10, 8);
  }),
];

const ASSET_PRESETS = [
  ...SIDE_VIEW_ASSETS,
  ...TOP_VIEW_ASSETS,
  ...SYMBOL_ASSETS,
  ...STATIONERY_ASSETS,
  ...VEHICLE_ASSETS,
  ...CREATURE_ASSETS,
];

const ASSET_BY_ID = new Map(ASSET_PRESETS.map((preset) => [preset.id, preset]));

function rowSet(id, name, category, tags, memberIds) {
  const members = memberIds.map((memberId) => {
    const preset = ASSET_BY_ID.get(memberId);
    if (!preset || preset.width !== 1 || preset.height !== 1) throw new TypeError("Row sets require 8x8 members");
    return preset;
  });
  return createPreset({
    id,
    kind: "set",
    name,
    category,
    tags,
    width: members.length,
    height: 1,
    glyphs: members.map((preset) => preset.glyphs[0]),
    slotNames: members.map((preset) => preset.slotNames[0]),
  });
}

function spriteSet(id, name, category, tags, memberIds) {
  const members = memberIds.map((memberId) => {
    const preset = ASSET_BY_ID.get(memberId);
    if (!preset || preset.width !== 2 || preset.height !== 2) throw new TypeError("Sprite sets require 16x16 members");
    return preset;
  });
  if (members.length !== 4) throw new TypeError("Sprite sets require four members");
  const glyphs = Array.from({ length: 16 }, () => Array(8).fill(0));
  const slotNames = Array(16).fill("");
  members.forEach((preset, index) => {
    const baseX = (index % 2) * 2;
    const baseY = Math.floor(index / 2) * 2;
    preset.glyphs.forEach((entry, glyphIndex) => {
      const x = glyphIndex % 2;
      const y = Math.floor(glyphIndex / 2);
      const target = (baseY + y) * 4 + baseX + x;
      glyphs[target] = entry;
      slotNames[target] = preset.slotNames[glyphIndex];
    });
  });
  return createPreset({ id, kind: "set", name, category, tags, width: 4, height: 4, glyphs, slotNames });
}

const ARCADE_GLYPHS = [
  [0x3c, 0x66, 0x6e, 0x76, 0x66, 0x66, 0x3c, 0x00],
  [0x18, 0x38, 0x18, 0x18, 0x18, 0x18, 0x7e, 0x00],
  [0x3c, 0x66, 0x06, 0x0c, 0x18, 0x30, 0x7e, 0x00],
  [0x3c, 0x66, 0x06, 0x1c, 0x06, 0x66, 0x3c, 0x00],
  [0x0c, 0x1c, 0x3c, 0x6c, 0x7e, 0x0c, 0x0c, 0x00],
  [0x7e, 0x60, 0x7c, 0x06, 0x06, 0x66, 0x3c, 0x00],
  [0x1c, 0x30, 0x60, 0x7c, 0x66, 0x66, 0x3c, 0x00],
  [0x7e, 0x66, 0x06, 0x0c, 0x18, 0x18, 0x18, 0x00],
  [0x3c, 0x66, 0x66, 0x3c, 0x66, 0x66, 0x3c, 0x00],
  [0x3c, 0x66, 0x66, 0x3e, 0x06, 0x0c, 0x38, 0x00],
  [0x00, 0x18, 0x18, 0x00, 0x00, 0x18, 0x18, 0x00],
];

const ARCADE_SLOT_NAMES = [
  "Digit 0", "Digit 1", "Digit 2", "Digit 3", "Digit 4", "Digit 5", "Digit 6", "Digit 7", "Digit 8", "Digit 9", "Colon",
];

export const ARCADE_DIGITS = Object.freeze({
  ...createPreset({
    id: "arcade-digits",
    kind: "set",
    name: "Arcade Digits",
    category: "symbols",
    tags: ["digits", "arcade", "score"],
    width: 11,
    height: 1,
    glyphs: ARCADE_GLYPHS,
    slotNames: ARCADE_SLOT_NAMES,
  }),
  names: Object.freeze([...ARCADE_SLOT_NAMES]),
});

const SET_PRESETS = [
  rowSet("set-side-ground", "Side Ground", "side-view", ["set", "terrain"], ["side-grass-top", "side-grass-fill", "side-dirt-fill", "side-stone-wall", "side-brick-wall", "side-metal-wall", "side-ice-wall"]),
  rowSet("set-side-traversal", "Side Traversal", "side-view", ["set", "traversal"], ["side-cloud-platform", "side-wood-platform", "side-rope-bridge", "side-ladder", "side-stairs-right", "side-stairs-left", "side-jump-pad", "side-conveyor-left", "side-conveyor-right"]),
  rowSet("set-side-hazards", "Side Hazards", "side-view", ["set", "hazard"], ["side-floor-spikes", "side-ceiling-spikes", "side-flame-jet", "side-lava-surface", "side-lava-fill"]),
  rowSet("set-side-water-access", "Side Water Access", "side-view", ["set", "water", "access"], ["side-water-surface", "side-water-fill", "side-waterfall", "side-door", "side-locked-door"]),
  rowSet("set-top-roads", "Top Roads", "top-view", ["set", "road"], ["top-road-horizontal", "top-road-vertical", "top-road-corner-ne", "top-road-corner-nw", "top-road-corner-se", "top-road-corner-sw", "top-road-t-north", "top-road-t-east", "top-road-t-south", "top-road-t-west", "top-road-crossroad"]),
  rowSet("set-top-waters", "Top Waters", "top-view", ["set", "water"], ["top-shallow-water", "top-deep-water", "top-river-horizontal", "top-river-vertical", "top-river-bend-ne", "top-river-bend-nw", "top-river-bend-se", "top-river-bend-sw", "top-shore-north", "top-shore-south", "top-shore-east", "top-shore-west"]),
  rowSet("set-top-nature", "Top Nature", "top-view", ["set", "nature"], ["top-grass", "top-tall-grass", "top-dirt", "top-sand", "top-tree", "top-bush", "top-rock"]),
  rowSet("set-top-structures", "Top Structures", "top-view", ["set", "structure"], ["top-bridge-horizontal", "top-bridge-vertical", "top-fence-horizontal", "top-fence-vertical"]),
  rowSet("set-symbol-navigation", "Symbol Navigation", "symbols", ["set", "navigation"], ["symbol-arrow-up", "symbol-arrow-down", "symbol-arrow-left", "symbol-arrow-right", "symbol-passage", "symbol-no-passage", "symbol-check", "symbol-cross", "symbol-warning", "symbol-question", "symbol-compass", "symbol-target"]),
  rowSet("set-symbol-celestial", "Symbol Celestial", "symbols", ["set", "celestial", "rune"], ["symbol-heart", "symbol-star", "symbol-moon", "symbol-sun", "symbol-key", "symbol-lock", "symbol-aries", "symbol-scorpius", "symbol-ursa", "symbol-rune-one", "symbol-rune-two", "symbol-rune-three"]),
  rowSet("set-stationery-desk", "Stationery Desk", "stationery", ["set", "stationery"], STATIONERY_ASSETS.map(({ id }) => id)),
  spriteSet("set-aircraft", "Aircraft", "vehicles", ["set", "aircraft"], ["vehicle-propeller-plane", "vehicle-fighter-jet", "vehicle-bomber", "vehicle-biplane"]),
  spriteSet("set-sky-space", "Sky Space", "vehicles", ["set", "aircraft", "space"], ["vehicle-helicopter", "vehicle-rocket", "vehicle-ufo", "vehicle-airship"]),
  spriteSet("set-ground-transport", "Ground Transport", "vehicles", ["set", "land"], ["vehicle-drone", "vehicle-tank", "vehicle-train", "vehicle-car"]),
  spriteSet("set-mammals", "Mammals", "creatures", ["set", "mammal"], ["creature-cat", "creature-dog", "creature-rabbit", "creature-fox"]),
  ARCADE_DIGITS,
];

export const PCG_PRESETS = Object.freeze([...ASSET_PRESETS, ...SET_PRESETS]);

if (ASSET_PRESETS.length !== 144 || SET_PRESETS.length !== 16 || PCG_PRESETS.length !== 160 || new Set(PCG_PRESETS.map(({ id }) => id)).size !== PCG_PRESETS.length) {
  throw new Error("PCG preset catalog is incomplete");
}

const PRESET_BY_ID = new Map(PCG_PRESETS.map((preset) => [preset.id, preset]));

export const PCG_PRESET_CATEGORIES = Object.freeze([
  "side-view",
  "top-view",
  "symbols",
  "stationery",
  "vehicles",
  "creatures",
]);

export function getPcgPreset(id) {
  const preset = PRESET_BY_ID.get(id);
  if (!preset) throw new RangeError(`Unknown PCG preset: ${id}`);
  return preset;
}

export function filterPcgPresets({ category = "all", kind = "all", size = "all", query = "", ids = null } = {}) {
  const normalizedQuery = String(query).trim().toLowerCase();
  const orderedIds = ids === null ? null : Array.isArray(ids) ? ids : [];
  const allowedIds = orderedIds === null ? null : new Set(orderedIds);
  const matches = PCG_PRESETS.filter((preset) => {
    if (category !== "all" && preset.category !== category) return false;
    if (kind !== "all" && preset.kind !== kind) return false;
    if (size === "8x8" && !(preset.kind === "asset" && preset.width === 1 && preset.height === 1)) return false;
    if (size === "16x16" && !(preset.kind === "asset" && preset.width === 2 && preset.height === 2)) return false;
    if (size === "sets" && preset.kind !== "set") return false;
    if (allowedIds && !allowedIds.has(preset.id)) return false;
    if (!normalizedQuery) return true;
    return [preset.name, preset.category, preset.kind, ...preset.tags].join(" ").toLowerCase().includes(normalizedQuery);
  });
  if (!allowedIds) return matches;
  const matchesById = new Map(matches.map((preset) => [preset.id, preset]));
  return orderedIds.map((id) => matchesById.get(id)).filter(Boolean);
}
