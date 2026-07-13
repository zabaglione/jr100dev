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

function clearMatrixRect(matrix, x, y, width, height) {
  for (let row = y; row < y + height; row += 1) {
    for (let column = x; column < x + width; column += 1) {
      setMatrixPixel(matrix, column, row, 0);
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

function animationPreset({ id, name, category, tags, width, height, slotNames, frameDurationMs, frames }) {
  if (!Number.isInteger(frameDurationMs) || frameDurationMs < 16 || frameDurationMs > 60000) {
    throw new RangeError("Animation frame duration must be between 16 and 60000 ms");
  }
  if (!Array.isArray(frames) || frames.length < 2) {
    throw new TypeError("Animation presets require at least two frames");
  }
  const frameIds = new Set();
  const normalizedFrames = frames.map((frame) => {
    if (!frame || typeof frame.id !== "string" || !frame.id || frameIds.has(frame.id) || typeof frame.name !== "string" || !frame.name.trim()) {
      throw new TypeError("Animation frame metadata is invalid");
    }
    frameIds.add(frame.id);
    if (!Array.isArray(frame.glyphs) || frame.glyphs.length !== width * height || frame.glyphs.some((glyphData) => !Array.isArray(glyphData) || glyphData.length !== 8 || glyphData.some((value) => !Number.isInteger(value) || value < 0 || value > 0xff))) {
      throw new TypeError("Animation frame glyph data is invalid");
    }
    return Object.freeze({
      id: frame.id,
      name: frame.name,
      glyphs: freezeGlyphs(frame.glyphs),
    });
  });
  const preview = createPreset({
    id,
    kind: "animation",
    name,
    category,
    tags,
    width,
    height,
    glyphs: normalizedFrames[0].glyphs,
    slotNames,
  });
  return Object.freeze({
    ...preview,
    frameDurationMs,
    frames: Object.freeze(normalizedFrames),
  });
}

function animationTile(id, name, category, tags, frameDurationMs, frameRows) {
  return animationPreset({
    id,
    name,
    category,
    tags,
    width: 1,
    height: 1,
    slotNames: [name],
    frameDurationMs,
    frames: frameRows.map((rows, index) => ({
      id: `frame-${index}`,
      name: `Frame ${index + 1}`,
      glyphs: [glyph(...rows)],
    })),
  });
}

function animationSprite(id, name, category, tags, frameDurationMs, painters) {
  return animationPreset({
    id,
    name,
    category,
    tags,
    width: 2,
    height: 2,
    slotNames: ["TL", "TR", "BL", "BR"].map((corner) => `${name} ${corner}`),
    frameDurationMs,
    frames: painters.map((painter, index) => {
      const matrix = createMatrix();
      painter(matrix);
      return {
        id: `frame-${index}`,
        name: `Frame ${index + 1}`,
        glyphs: matrixGlyphs(matrix),
      };
    }),
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

function shapePainter({ rectangles = [], ellipses = [], lines = [], clearedPixels = [] } = {}) {
  return (matrix) => {
    rectangles.forEach(([x, y, width, height]) => fillMatrixRect(matrix, x, y, width, height));
    ellipses.forEach(([x, y, radiusX, radiusY]) => drawMatrixEllipse(matrix, x, y, radiusX, radiusY));
    lines.forEach(([x0, y0, x1, y1]) => drawMatrixLine(matrix, x0, y0, x1, y1));
    clearedPixels.forEach(([x, y]) => setMatrixPixel(matrix, x, y, 0));
  };
}

function chibiPainter({ hair = "short", accessory = "none", ears = "none", wings = false, tail = false } = {}) {
  return (matrix) => {
    drawMatrixEllipse(matrix, 8, 5, 5, 4);
    fillMatrixRect(matrix, 5, 9, 7, 4);
    drawMatrixLine(matrix, 6, 13, 5, 15);
    drawMatrixLine(matrix, 10, 13, 11, 15);
    drawMatrixLine(matrix, 5, 10, 2, 12);
    drawMatrixLine(matrix, 11, 10, 14, 12);
    if (hair === "long") {
      drawMatrixLine(matrix, 3, 5, 2, 10);
      drawMatrixLine(matrix, 13, 5, 14, 10);
    } else if (hair === "spiky") {
      drawMatrixLine(matrix, 4, 3, 3, 0);
      drawMatrixLine(matrix, 7, 2, 7, 0);
      drawMatrixLine(matrix, 10, 3, 12, 0);
    } else if (hair === "hood") {
      drawMatrixEllipse(matrix, 8, 5, 6, 5);
      drawMatrixEllipse(matrix, 8, 5, 4, 3);
      setMatrixPixel(matrix, 5, 5, 0);
      setMatrixPixel(matrix, 11, 5, 0);
    }
    if (ears === "point") {
      drawMatrixLine(matrix, 4, 3, 2, 0);
      drawMatrixLine(matrix, 12, 3, 14, 0);
    } else if (ears === "long") {
      drawMatrixLine(matrix, 4, 3, 3, 0);
      drawMatrixLine(matrix, 12, 3, 13, 0);
      drawMatrixLine(matrix, 3, 0, 2, 3);
      drawMatrixLine(matrix, 13, 0, 14, 3);
    }
    if (wings) {
      drawMatrixLine(matrix, 5, 9, 0, 6);
      drawMatrixLine(matrix, 0, 6, 1, 11);
      drawMatrixLine(matrix, 11, 9, 15, 6);
      drawMatrixLine(matrix, 15, 6, 14, 11);
    }
    if (tail) {
      drawMatrixLine(matrix, 11, 12, 15, 10);
      drawMatrixLine(matrix, 15, 10, 14, 13);
    }
    if (accessory === "sword") {
      drawMatrixLine(matrix, 13, 11, 15, 4);
      drawMatrixLine(matrix, 12, 8, 15, 9);
    } else if (accessory === "staff") {
      drawMatrixLine(matrix, 14, 4, 14, 15);
      drawMatrixEllipse(matrix, 14, 3, 2, 2);
    } else if (accessory === "helmet") {
      fillMatrixRect(matrix, 4, 1, 9, 2);
      drawMatrixLine(matrix, 8, 1, 8, 0);
    } else if (accessory === "visor") {
      fillMatrixRect(matrix, 4, 5, 9, 2);
      setMatrixPixel(matrix, 7, 5, 0);
      setMatrixPixel(matrix, 9, 5, 0);
    }
    setMatrixPixel(matrix, 6, 5, 0);
    setMatrixPixel(matrix, 10, 5, 0);
  };
}

function chibiWalkPainter(phase) {
  const legFrames = [
    [[6, 13, 4, 15], [10, 13, 11, 15]],
    [[6, 13, 6, 15], [10, 13, 13, 15]],
    [[6, 13, 8, 15], [10, 13, 10, 15]],
    [[6, 13, 3, 15], [10, 13, 10, 15]],
  ];
  return (matrix) => {
    chibiPainter({ accessory: "sword" })(matrix);
    clearMatrixRect(matrix, 3, 13, 11, 3);
    legFrames[phase % legFrames.length].forEach(([x0, y0, x1, y1]) => drawMatrixLine(matrix, x0, y0, x1, y1));
  };
}

function chibiKnightSlashPainter(phase) {
  const bladeFrames = [
    [[12, 10, 15, 8], [13, 9, 15, 10]],
    [[12, 9, 15, 4], [11, 8, 14, 7]],
    [[11, 10, 15, 12], [13, 11, 14, 14]],
    [[12, 11, 14, 15], [11, 12, 15, 13]],
  ];
  return (matrix) => {
    chibiPainter({ accessory: "helmet" })(matrix);
    bladeFrames[phase % bladeFrames.length].forEach(([x0, y0, x1, y1]) => drawMatrixLine(matrix, x0, y0, x1, y1));
  };
}

function chibiWizardCastPainter(phase) {
  const orbFrames = [[11, 3, 1], [12, 2, 2], [13, 1, 3], [12, 2, 2]];
  return (matrix) => {
    chibiPainter({ accessory: "staff", hair: "spiky" })(matrix);
    const [x, y, radius] = orbFrames[phase % orbFrames.length];
    drawMatrixEllipse(matrix, x, y, radius, radius);
  };
}

function fishSwimPainter(phase) {
  const tailFrames = [
    [[12, 8, 15, 4], [12, 8, 15, 12]],
    [[12, 8, 15, 6], [12, 8, 15, 10]],
    [[12, 8, 15, 2], [12, 8, 15, 14]],
    [[12, 8, 15, 6], [12, 8, 15, 10]],
  ];
  return (matrix) => {
    aquaticPainter({ fins: "side" })(matrix);
    clearMatrixRect(matrix, 12, 2, 4, 13);
    tailFrames[phase % tailFrames.length].forEach(([x0, y0, x1, y1]) => drawMatrixLine(matrix, x0, y0, x1, y1));
  };
}

function propellerPlanePainter(phase) {
  const propellerFrames = [
    [[2, 4, 2, 12]],
    [[0, 6, 4, 10]],
    [[0, 8, 4, 8]],
    [[0, 10, 4, 6]],
  ];
  return (matrix) => {
    drawMatrixLine(matrix, 2, 8, 14, 8);
    drawMatrixLine(matrix, 6, 8, 9, 3);
    drawMatrixLine(matrix, 7, 8, 11, 12);
    fillMatrixRect(matrix, 7, 7, 3, 3);
    drawMatrixLine(matrix, 12, 8, 15, 5);
    drawMatrixLine(matrix, 12, 8, 15, 11);
    propellerFrames[phase % propellerFrames.length].forEach(([x0, y0, x1, y1]) => drawMatrixLine(matrix, x0, y0, x1, y1));
  };
}

function excavatorDigPainter(phase) {
  const armFrames = [
    [[10, 7, 14, 3], [14, 3, 15, 6]],
    [[10, 7, 14, 5], [14, 5, 15, 9]],
    [[10, 7, 13, 9], [13, 9, 14, 13]],
    [[10, 7, 12, 6], [12, 6, 15, 4]],
  ];
  return (matrix) => {
    fillMatrixRect(matrix, 2, 10, 10, 3);
    fillMatrixRect(matrix, 6, 6, 5, 4);
    drawMatrixEllipse(matrix, 7, 13, 6, 2);
    armFrames[phase % armFrames.length].forEach(([x0, y0, x1, y1]) => drawMatrixLine(matrix, x0, y0, x1, y1));
  };
}

function mineCartRollPainter(phase) {
  const wheelOffsets = [0, 1, 0, -1];
  return (matrix) => {
    const offset = wheelOffsets[phase % wheelOffsets.length];
    fillMatrixRect(matrix, 3, 8, 10, 4);
    drawMatrixLine(matrix, 3, 8, 5, 4);
    drawMatrixLine(matrix, 5, 4, 11, 4);
    drawMatrixLine(matrix, 11, 4, 13, 8);
    drawMatrixEllipse(matrix, 5 + offset, 13, 2, 2);
    drawMatrixEllipse(matrix, 11 + offset, 13, 2, 2);
    drawMatrixLine(matrix, 1, 15, 15, 15);
  };
}

function windmillTurnPainter(phase) {
  const bladeFrames = [
    [[8, 4, 8, 0], [8, 4, 12, 4], [8, 4, 8, 8], [8, 4, 4, 4]],
    [[8, 4, 11, 1], [8, 4, 11, 7], [8, 4, 5, 7], [8, 4, 5, 1]],
    [[8, 4, 12, 4], [8, 4, 8, 8], [8, 4, 4, 4], [8, 4, 8, 0]],
    [[8, 4, 11, 7], [8, 4, 5, 7], [8, 4, 5, 1], [8, 4, 11, 1]],
  ];
  return (matrix) => {
    fillMatrixRect(matrix, 5, 7, 7, 8);
    drawMatrixLine(matrix, 4, 15, 13, 15);
    bladeFrames[phase % bladeFrames.length].forEach(([x0, y0, x1, y1]) => drawMatrixLine(matrix, x0, y0, x1, y1));
    drawMatrixEllipse(matrix, 8, 4, 1, 1);
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

const EXTENDED_EXISTING_ASSETS = [
  sprite("side-wooden-bridge", "Wooden Bridge", "side-view", ["platform", "bridge", "large"], shapePainter({
    rectangles: [[1, 9, 14, 2]],
    lines: [[2, 9, 4, 14], [6, 9, 6, 14], [10, 9, 10, 14], [14, 9, 12, 14]],
  })),
  sprite("side-stone-arch", "Stone Arch", "side-view", ["terrain", "arch", "large"], shapePainter({
    rectangles: [[1, 7, 14, 8]],
    ellipses: [[8, 8, 5, 5]],
    clearedPixels: [[5, 8], [6, 8], [7, 8], [8, 8], [9, 8], [10, 8], [11, 8], [5, 9], [6, 9], [7, 9], [8, 9], [9, 9], [10, 9], [11, 9], [5, 10], [6, 10], [7, 10], [8, 10], [9, 10], [10, 10], [11, 10], [5, 11], [6, 11], [7, 11], [8, 11], [9, 11], [10, 11], [11, 11], [5, 12], [6, 12], [7, 12], [8, 12], [9, 12], [10, 12], [11, 12], [5, 13], [6, 13], [7, 13], [8, 13], [9, 13], [10, 13], [11, 13], [5, 14], [6, 14], [7, 14], [8, 14], [9, 14], [10, 14], [11, 14]],
  })),
  sprite("side-watermill", "Watermill", "side-view", ["structure", "water", "large"], shapePainter({
    rectangles: [[2, 6, 7, 8]],
    ellipses: [[11, 10, 4, 4]],
    lines: [[11, 6, 11, 14], [7, 10, 15, 10], [8, 7, 14, 13], [14, 7, 8, 13]],
  })),
  sprite("side-boss-door", "Boss Door", "side-view", ["access", "door", "large"], shapePainter({
    rectangles: [[2, 3, 12, 12]],
    ellipses: [[8, 8, 4, 5]],
    clearedPixels: [[6, 7], [7, 7], [8, 7], [9, 7], [10, 7], [6, 8], [7, 8], [8, 8], [9, 8], [10, 8], [6, 9], [7, 9], [8, 9], [9, 9], [10, 9], [6, 10], [7, 10], [8, 10], [9, 10], [10, 10], [6, 11], [7, 11], [8, 11], [9, 11], [10, 11], [6, 12], [7, 12], [8, 12], [9, 12], [10, 12], [6, 13], [7, 13], [8, 13], [9, 13], [10, 13]],
  })),
  sprite("top-house", "Top House", "top-view", ["building", "house", "large"], shapePainter({
    rectangles: [[3, 6, 10, 8]],
    lines: [[2, 6, 8, 1], [8, 1, 14, 6]],
    clearedPixels: [[7, 10], [8, 10], [7, 11], [8, 11], [7, 12], [8, 12], [7, 13], [8, 13]],
  })),
  sprite("top-castle", "Top Castle", "top-view", ["building", "castle", "large"], shapePainter({
    rectangles: [[2, 5, 12, 10], [1, 2, 3, 4], [6, 1, 4, 5], [12, 2, 3, 4]],
    clearedPixels: [[7, 11], [8, 11], [7, 12], [8, 12], [7, 13], [8, 13], [7, 14], [8, 14]],
  })),
  sprite("top-pond", "Top Pond", "top-view", ["water", "pond", "large"], shapePainter({
    ellipses: [[8, 8, 7, 5]],
    lines: [[3, 8, 6, 6], [10, 10, 13, 8]],
  })),
  sprite("top-dock", "Top Dock", "top-view", ["water", "dock", "large"], shapePainter({
    rectangles: [[3, 1, 4, 14], [7, 9, 8, 3]],
    lines: [[3, 4, 6, 4], [3, 7, 6, 7], [9, 9, 9, 11], [12, 9, 12, 11]],
  })),
  sprite("symbol-compass-rose", "Compass Rose", "symbols", ["symbol", "navigation", "large"], shapePainter({
    lines: [[8, 0, 8, 15], [0, 8, 15, 8], [2, 2, 14, 14], [14, 2, 2, 14]],
    ellipses: [[8, 8, 3, 3]],
  })),
  sprite("symbol-magic-circle", "Magic Circle", "symbols", ["symbol", "magic", "large"], shapePainter({
    ellipses: [[8, 8, 7, 7], [8, 8, 4, 4]],
    lines: [[8, 1, 13, 12], [13, 12, 2, 12], [2, 12, 8, 1]],
  })),
  sprite("symbol-rune-gate", "Rune Gate", "symbols", ["symbol", "rune", "large"], shapePainter({
    rectangles: [[2, 2, 3, 12], [11, 2, 3, 12], [5, 2, 6, 2]],
    lines: [[6, 5, 10, 11], [10, 5, 6, 11]],
  })),
  sprite("symbol-quest-marker", "Quest Marker", "symbols", ["symbol", "quest", "large"], shapePainter({
    ellipses: [[8, 6, 5, 5]],
    lines: [[4, 10, 8, 15], [12, 10, 8, 15]],
    clearedPixels: [[7, 5], [8, 5], [9, 5], [7, 6], [8, 6], [9, 6]],
  })),
  sprite("vehicle-glider", "Glider", "vehicles", ["aircraft", "glider", "large"], shapePainter({
    lines: [[1, 8, 14, 8], [6, 8, 9, 3], [7, 8, 11, 12], [2, 7, 0, 9]],
  })),
  sprite("vehicle-seaplane", "Seaplane", "vehicles", ["aircraft", "sea", "large"], shapePainter({
    rectangles: [[4, 7, 8, 3], [3, 12, 4, 2], [9, 12, 4, 2]],
    lines: [[5, 8, 8, 3], [8, 8, 13, 11], [2, 7, 0, 9]],
  })),
  sprite("vehicle-fire-engine", "Fire Engine", "vehicles", ["land", "emergency", "large"], shapePainter({
    rectangles: [[2, 8, 12, 5], [4, 5, 6, 3]],
    ellipses: [[5, 13, 2, 2], [11, 13, 2, 2]],
    lines: [[9, 7, 14, 4]],
  })),
  sprite("vehicle-hovercraft", "Hovercraft", "vehicles", ["sea", "hovercraft", "large"], shapePainter({
    ellipses: [[8, 10, 7, 4]],
    rectangles: [[5, 5, 6, 4]],
    lines: [[8, 5, 8, 1], [4, 14, 12, 14]],
  })),
  sprite("creature-bat", "Bat", "creatures", ["animal", "bat", "large"], shapePainter({
    ellipses: [[8, 8, 3, 4]],
    lines: [[6, 7, 0, 3], [0, 3, 2, 11], [10, 7, 15, 3], [15, 3, 13, 11], [7, 11, 8, 14], [9, 11, 8, 14]],
  })),
  sprite("creature-butterfly", "Butterfly", "creatures", ["animal", "insect", "large"], shapePainter({
    ellipses: [[4, 6, 4, 5], [12, 6, 4, 5], [4, 11, 4, 3], [12, 11, 4, 3]],
    rectangles: [[7, 4, 2, 10]],
    lines: [[7, 4, 5, 1], [9, 4, 11, 1]],
  })),
  sprite("creature-crab", "Crab", "creatures", ["animal", "crab", "large"], shapePainter({
    ellipses: [[8, 9, 5, 4]],
    lines: [[4, 9, 0, 5], [0, 5, 1, 2], [12, 9, 15, 5], [15, 5, 14, 2], [5, 12, 3, 15], [7, 12, 6, 15], [9, 12, 10, 15], [11, 12, 13, 15]],
    clearedPixels: [[6, 8], [10, 8]],
  })),
  sprite("creature-unicorn", "Unicorn", "creatures", ["animal", "fantasy", "large"], (matrix) => {
    mammalPainter({ ears: "point", tail: "long", legs: 4 })(matrix);
    drawMatrixLine(matrix, 5, 3, 8, 0);
  }),
];

const CONSTRUCTION_ASSETS = [
  tile("construction-caution-stripe", "Caution Stripe", "construction", ["construction", "warning", "tileable"], ["##....##", ".##..##.", "..####..", "...##...", "..####..", ".##..##.", "##....##", "........"]),
  tile("construction-traffic-cone", "Traffic Cone", "construction", ["construction", "traffic"], ["...##...", "..####..", "...##...", "..####..", ".##..##.", ".######.", "########", "........"]),
  tile("construction-safety-barrier", "Safety Barrier", "construction", ["construction", "barrier"], ["........", "########", "#..##..#", "########", "..#..#..", ".#....#.", "#......#", "........"]),
  tile("construction-site-fence", "Site Fence", "construction", ["construction", "fence"], ["#......#", "##....##", "########", "#..##..#", "########", "##....##", "#......#", "........"]),
  tile("construction-scaffold", "Scaffold", "construction", ["construction", "platform"], ["#..##..#", "########", "#..##..#", "########", "#..##..#", "########", "#..##..#", "........"]),
  tile("construction-steel-beam", "Steel Beam", "construction", ["construction", "metal"], ["########", "#......#", "##....##", "########", "##....##", "#......#", "########", "........"]),
  tile("construction-oil-drum", "Oil Drum", "construction", ["construction", "prop"], ["..####..", ".######.", ".#....#.", ".######.", ".#....#.", ".######.", "..####..", "........"]),
  tile("construction-cargo-crate", "Cargo Crate", "construction", ["construction", "prop"], ["########", "##....##", "#.####.#", "#.#..#.#", "#.####.#", "##....##", "########", "........"]),
  sprite("construction-excavator", "Excavator", "construction", ["construction", "machine", "large"], shapePainter({
    rectangles: [[2, 10, 10, 3], [6, 6, 5, 4]],
    ellipses: [[7, 13, 6, 2]],
    lines: [[10, 7, 14, 3], [14, 3, 15, 6]],
  })),
  sprite("construction-bulldozer", "Bulldozer", "construction", ["construction", "machine", "large"], shapePainter({
    rectangles: [[3, 8, 9, 5], [6, 5, 4, 3]],
    ellipses: [[7, 13, 6, 2]],
    lines: [[2, 10, 0, 12], [0, 12, 2, 14]],
  })),
  sprite("construction-crane", "Tower Crane", "construction", ["construction", "machine", "large"], shapePainter({
    rectangles: [[6, 3, 3, 12]],
    lines: [[7, 3, 15, 3], [13, 3, 13, 11], [2, 15, 13, 15]],
  })),
  sprite("construction-dump-truck", "Dump Truck", "construction", ["construction", "machine", "large"], shapePainter({
    rectangles: [[2, 9, 12, 4], [4, 5, 7, 4]],
    ellipses: [[5, 13, 2, 2], [11, 13, 2, 2]],
    lines: [[4, 5, 11, 3]],
  })),
  sprite("construction-cement-mixer", "Cement Mixer", "construction", ["construction", "machine", "large"], shapePainter({
    rectangles: [[2, 10, 12, 3], [3, 7, 3, 3]],
    ellipses: [[9, 7, 4, 4], [5, 13, 2, 2], [11, 13, 2, 2]],
  })),
  sprite("construction-forklift", "Forklift", "construction", ["construction", "machine", "large"], shapePainter({
    rectangles: [[3, 9, 7, 4], [5, 5, 4, 4]],
    ellipses: [[5, 13, 2, 2], [10, 13, 2, 2]],
    lines: [[11, 5, 11, 15], [12, 5, 12, 15], [11, 5, 15, 5]],
  })),
];

const CAVE_ASSETS = [
  tile("cave-rock-wall", "Rock Wall", "cave", ["cave", "rock", "tileable"], ["##..##..", ".####..#", "#..##.##", "##..##..", ".##..###", "#..##..#", "###..##.", ".##..##."]),
  tile("cave-crystal-wall", "Crystal Wall", "cave", ["cave", "crystal"], ["..#..#..", ".###.###", "##.#.#.#", ".##.###.", "..#.#...", ".###.##.", "##.#.###", "........"]),
  tile("cave-floor", "Cave Floor", "cave", ["cave", "ground"], ["........", "........", "........", "........", ".#..#..#", "########", "########", "########"]),
  tile("cave-stalactite", "Stalactite", "cave", ["cave", "hazard"], ["########", "########", ".#.#.#.#", "..#.#.#.", "...#.#..", "....#...", "........", "........"]),
  tile("cave-stalagmite", "Stalagmite", "cave", ["cave", "hazard"], ["........", "........", "....#...", "...#.#..", "..#.#.#.", ".#.#.#.#", "########", "########"]),
  tile("cave-mine-track", "Mine Track", "cave", ["cave", "track"], ["........", "........", "#......#", "########", ".#.#.#.#", "########", "#......#", "........"]),
  tile("cave-torch", "Torch", "cave", ["cave", "light"], ["...#....", "..###...", ".##.##..", "...#....", "...#....", "..###...", "..###...", "........"]),
  sprite("cave-entrance", "Cave Entrance", "cave", ["cave", "entrance", "large"], shapePainter({
    ellipses: [[8, 9, 7, 7]],
    rectangles: [[1, 9, 14, 7]],
    clearedPixels: [[5, 7], [6, 7], [7, 7], [8, 7], [9, 7], [10, 7], [11, 7], [4, 8], [5, 8], [6, 8], [7, 8], [8, 8], [9, 8], [10, 8], [11, 8], [12, 8], [4, 9], [5, 9], [6, 9], [7, 9], [8, 9], [9, 9], [10, 9], [11, 9], [12, 9], [4, 10], [5, 10], [6, 10], [7, 10], [8, 10], [9, 10], [10, 10], [11, 10], [12, 10], [4, 11], [5, 11], [6, 11], [7, 11], [8, 11], [9, 11], [10, 11], [11, 11], [12, 11], [4, 12], [5, 12], [6, 12], [7, 12], [8, 12], [9, 12], [10, 12], [11, 12], [12, 12], [4, 13], [5, 13], [6, 13], [7, 13], [8, 13], [9, 13], [10, 13], [11, 13], [12, 13], [4, 14], [5, 14], [6, 14], [7, 14], [8, 14], [9, 14], [10, 14], [11, 14], [12, 14], [4, 15], [5, 15], [6, 15], [7, 15], [8, 15], [9, 15], [10, 15], [11, 15], [12, 15]],
  })),
  sprite("cave-crystal-cluster", "Crystal Cluster", "cave", ["cave", "crystal", "large"], shapePainter({
    lines: [[3, 15, 5, 3], [5, 3, 7, 15], [7, 15, 10, 1], [10, 1, 13, 15], [1, 15, 3, 7], [13, 15, 15, 6]],
  })),
  sprite("cave-mine-cart", "Cave Mine Cart", "cave", ["cave", "cart", "large"], shapePainter({
    rectangles: [[3, 8, 10, 4]],
    ellipses: [[5, 13, 2, 2], [11, 13, 2, 2]],
    lines: [[3, 8, 5, 4], [5, 4, 11, 4], [11, 4, 13, 8]],
  })),
  sprite("cave-underground-lake", "Underground Lake", "cave", ["cave", "water", "large"], shapePainter({
    ellipses: [[8, 11, 7, 3]],
    lines: [[2, 8, 5, 2], [5, 2, 7, 8], [12, 8, 10, 1], [10, 1, 8, 8]],
  })),
  sprite("cave-treasure-chest", "Cave Treasure Chest", "cave", ["cave", "treasure", "large"], shapePainter({
    rectangles: [[3, 8, 10, 6]],
    ellipses: [[8, 8, 5, 3]],
    lines: [[8, 7, 8, 14]],
  })),
];

const FOREST_ASSETS = [
  tile("forest-leaf-canopy", "Leaf Canopy", "forest", ["forest", "leaves", "tileable"], [".##..##.", "########", "##.##.##", ".######.", "########", "##.##.##", ".######.", "........"]),
  tile("forest-tree-trunk", "Tree Trunk", "forest", ["forest", "tree"], ["...##...", "...##...", "..####..", "...##...", "...##...", "..####..", "...##...", "...##..."]),
  tile("forest-tree-stump", "Tree Stump", "forest", ["forest", "tree"], ["........", "........", ".######.", "##....##", "##.##.##", "##....##", ".######.", "........"]),
  tile("forest-fern", "Fern", "forest", ["forest", "plant"], ["...#....", "..###...", ".##.##..", "...#....", ".##.##..", "##...##.", "........", "........"]),
  tile("forest-mossy-rock", "Mossy Rock", "forest", ["forest", "rock"], ["........", ".##.##..", "########", "##.####.", ".######.", "..####..", "........", "........"]),
  tile("forest-vine", "Vine", "forest", ["forest", "plant"], ["..##....", "...##...", "....##..", "...##...", "..##....", ".##.....", "##......", "........"]),
  tile("forest-mushroom", "Forest Mushroom", "forest", ["forest", "mushroom"], ["........", ".######.", "########", ".#.#..#.", "...##...", "...##...", "..####..", "........"]),
  tile("forest-fallen-leaf", "Fallen Leaf", "forest", ["forest", "leaf"], ["........", "...#....", ".#####..", "##.####.", ".#####..", "...#....", "........", "........"]),
  sprite("forest-oak-tree", "Oak Tree", "forest", ["forest", "tree", "large"], shapePainter({
    ellipses: [[8, 5, 7, 5], [4, 7, 4, 4], [12, 7, 4, 4]],
    rectangles: [[6, 9, 5, 7]],
  })),
  sprite("forest-pine-tree", "Pine Tree", "forest", ["forest", "tree", "large"], shapePainter({
    lines: [[8, 0, 1, 11], [8, 0, 15, 11], [8, 4, 2, 13], [8, 4, 14, 13]],
    rectangles: [[7, 10, 3, 6]],
  })),
  sprite("forest-fallen-log", "Fallen Log", "forest", ["forest", "log", "large"], shapePainter({
    ellipses: [[4, 10, 3, 3]],
    rectangles: [[4, 7, 11, 6]],
    lines: [[7, 7, 10, 13], [10, 7, 13, 13]],
  })),
  sprite("forest-waterfall", "Forest Waterfall", "forest", ["forest", "water", "large"], shapePainter({
    rectangles: [[5, 1, 6, 14]],
    lines: [[2, 3, 5, 1], [11, 1, 14, 4], [5, 14, 2, 15], [11, 14, 14, 15]],
  })),
];

const UNDERWATER_ASSETS = [
  tile("underwater-sand", "Underwater Sand", "underwater", ["underwater", "sand", "tileable"], ["...#....", ".#....#.", "....#...", "..#.....", "#....#..", "...#....", ".#....#.", "....#..."]),
  tile("underwater-coral", "Coral", "underwater", ["underwater", "coral"], ["...#....", ".#.#.#..", "..###...", ".#.###..", "...#.#..", "..#.#...", ".#####..", "........"]),
  tile("underwater-seaweed", "Seaweed", "underwater", ["underwater", "plant"], ["..#.....", "...#....", "..#.....", ".#......", "..#.....", "...#....", "..#.....", ".#......"]),
  tile("underwater-kelp", "Kelp", "underwater", ["underwater", "plant"], [".#......", "..#.....", "...#....", "..#.....", ".#......", "..#.....", "...#....", "..#....."]),
  tile("underwater-shell", "Shell", "underwater", ["underwater", "shell"], ["........", "...##...", ".######.", "##.##.##", "########", ".######.", "........", "........"]),
  tile("underwater-bubble", "Bubble", "underwater", ["underwater", "bubble"], ["...##...", "..#..#..", "...##...", "........", ".....#..", "......#.", ".....#..", "........"]),
  tile("underwater-reef-wall", "Reef Wall", "underwater", ["underwater", "reef", "tileable"], ["##..##..", "########", ".##.####", "##.##.##", "########", "##.####.", ".##.##..", "########"]),
  sprite("underwater-coral-reef", "Coral Reef", "underwater", ["underwater", "coral", "large"], shapePainter({
    ellipses: [[4, 11, 4, 4], [8, 8, 3, 6], [12, 11, 4, 4]],
    lines: [[2, 13, 1, 5], [6, 11, 5, 2], [10, 11, 11, 3], [14, 13, 15, 6]],
  })),
  sprite("underwater-shipwreck", "Shipwreck", "underwater", ["underwater", "wreck", "large"], shapePainter({
    rectangles: [[2, 10, 12, 3]],
    lines: [[3, 10, 6, 14], [13, 10, 10, 14], [8, 10, 8, 1], [8, 2, 13, 7]],
  })),
  sprite("underwater-treasure-chest", "Underwater Treasure", "underwater", ["underwater", "treasure", "large"], shapePainter({
    rectangles: [[3, 9, 10, 5]],
    ellipses: [[8, 9, 5, 3]],
    lines: [[8, 8, 8, 14]],
  })),
  sprite("underwater-diver", "Diver", "underwater", ["underwater", "character", "large"], shapePainter({
    ellipses: [[8, 4, 4, 3]],
    rectangles: [[5, 8, 6, 5]],
    lines: [[5, 10, 1, 12], [11, 10, 15, 8], [6, 13, 4, 15], [10, 13, 12, 15], [12, 4, 15, 4]],
  })),
  sprite("underwater-jellyfish", "Jellyfish", "underwater", ["underwater", "jellyfish", "large"], shapePainter({
    ellipses: [[8, 6, 6, 5]],
    lines: [[4, 10, 3, 15], [6, 11, 6, 15], [8, 11, 9, 15], [10, 11, 11, 15], [12, 10, 13, 14]],
  })),
];

const VILLAGE_ASSETS = [
  tile("village-cobblestone", "Village Cobblestone", "village", ["village", "road", "tileable"], [".##..##.", "##..##..", "..##..##", ".##..##.", "##..##..", "..##..##", ".##..##.", "##..##.."]),
  tile("village-fence", "Village Fence", "village", ["village", "fence"], ["#......#", "########", "#..##..#", "########", "#......#", "........", "........", "........"]),
  tile("village-signpost", "Village Signpost", "village", ["village", "sign"], [".######.", "########", "...##...", "...##...", "...##...", "..####..", "........", "........"]),
  tile("village-hay-bale", "Hay Bale", "village", ["village", "prop"], [".######.", "########", "##....##", "########", "##....##", "########", ".######.", "........"]),
  tile("village-barrel", "Village Barrel", "village", ["village", "prop"], ["..####..", ".######.", ".#....#.", ".######.", ".#....#.", ".######.", "..####..", "........"]),
  tile("village-lamp-post", "Village Lamp Post", "village", ["village", "light"], ["...##...", ".######.", ".######.", "...##...", "...##...", "...##...", "..####..", "........"]),
  tile("village-well", "Village Well", "village", ["village", "well"], ["..####..", ".#....#.", "########", "##....##", "########", ".######.", "........", "........"]),
  tile("village-crop-field", "Crop Field", "village", ["village", "farm", "tileable"], ["#.#.#.#.", ".#.#.#.#", "#.#.#.#.", ".#.#.#.#", "#.#.#.#.", ".#.#.#.#", "#.#.#.#.", ".#.#.#.#"]),
  sprite("village-cottage", "Village Cottage", "village", ["village", "house", "large"], shapePainter({
    rectangles: [[3, 7, 10, 8]],
    lines: [[2, 7, 8, 2], [8, 2, 14, 7]],
    clearedPixels: [[7, 11], [8, 11], [7, 12], [8, 12], [7, 13], [8, 13], [7, 14], [8, 14]],
  })),
  sprite("village-shop", "Village Shop", "village", ["village", "shop", "large"], shapePainter({
    rectangles: [[2, 7, 12, 8], [1, 5, 14, 2]],
    lines: [[3, 5, 5, 7], [7, 5, 9, 7], [11, 5, 13, 7]],
    clearedPixels: [[4, 10], [5, 10], [10, 10], [11, 10], [4, 11], [5, 11], [10, 11], [11, 11]],
  })),
  sprite("village-inn", "Village Inn", "village", ["village", "inn", "large"], shapePainter({
    rectangles: [[2, 6, 12, 9]],
    lines: [[1, 6, 8, 1], [8, 1, 15, 6]],
    clearedPixels: [[7, 10], [8, 10], [7, 11], [8, 11], [7, 12], [8, 12], [7, 13], [8, 13], [7, 14], [8, 14]],
  })),
  sprite("village-windmill", "Village Windmill", "village", ["village", "windmill", "large"], shapePainter({
    rectangles: [[6, 8, 5, 7]],
    ellipses: [[8, 6, 3, 3]],
    lines: [[8, 3, 8, 10], [5, 6, 11, 6], [6, 4, 10, 8], [10, 4, 6, 8]],
  })),
];

const CITY_ASSETS = [
  tile("city-asphalt", "City Asphalt", "city", ["city", "road", "tileable"], ["#...#...", "...#...#", ".#...#..", "....#...", "..#....#", "#...#...", "...#...#", ".#...#.."]),
  tile("city-sidewalk", "City Sidewalk", "city", ["city", "sidewalk", "tileable"], ["########", "#..##..#", "########", "##....##", "########", "#..##..#", "########", "##....##"]),
  tile("city-crosswalk", "Crosswalk", "city", ["city", "road"], ["........", "########", "........", "########", "........", "########", "........", "########"]),
  tile("city-road-marking", "Road Marking", "city", ["city", "road"], ["...##...", "...##...", "........", "........", "...##...", "...##...", "........", "........"]),
  tile("city-traffic-light", "Traffic Light", "city", ["city", "traffic"], ["...##...", "..####..", "..#..#..", "..####..", "..#..#..", "..####..", "...##...", "..####.."]),
  tile("city-hydrant", "Hydrant", "city", ["city", "prop"], ["...##...", ".######.", ".##..##.", ".######.", "...##...", ".##..##.", ".######.", "........"]),
  tile("city-mailbox", "Mailbox", "city", ["city", "prop"], [".######.", "##....##", "########", "##....##", ".######.", "...##...", "...##...", "........"]),
  tile("city-bench", "City Bench", "city", ["city", "prop"], ["........", ".######.", "########", "........", ".#....#.", ".#....#.", "#......#", "........"]),
  sprite("city-apartment", "City Apartment", "city", ["city", "building", "large"], shapePainter({
    rectangles: [[3, 1, 10, 15]],
    clearedPixels: [[5, 3], [6, 3], [9, 3], [10, 3], [5, 6], [6, 6], [9, 6], [10, 6], [5, 9], [6, 9], [9, 9], [10, 9], [5, 12], [6, 12], [9, 12], [10, 12]],
  })),
  sprite("city-office-tower", "Office Tower", "city", ["city", "building", "large"], shapePainter({
    rectangles: [[4, 0, 8, 16]],
    clearedPixels: [[6, 2], [7, 2], [9, 2], [6, 5], [7, 5], [9, 5], [6, 8], [7, 8], [9, 8], [6, 11], [7, 11], [9, 11], [6, 14], [7, 14], [9, 14]],
  })),
  sprite("city-storefront", "City Storefront", "city", ["city", "shop", "large"], shapePainter({
    rectangles: [[2, 6, 12, 9], [1, 4, 14, 2]],
    lines: [[3, 4, 5, 6], [7, 4, 9, 6], [11, 4, 13, 6]],
    clearedPixels: [[4, 10], [5, 10], [10, 10], [11, 10], [4, 11], [5, 11], [10, 11], [11, 11]],
  })),
  sprite("city-cafe", "City Cafe", "city", ["city", "cafe", "large"], shapePainter({
    rectangles: [[3, 7, 10, 7]],
    ellipses: [[8, 5, 5, 2]],
    lines: [[8, 7, 8, 14], [5, 14, 5, 15], [11, 14, 11, 15]],
  })),
];

const STATIONERY_EXPANSION_ASSETS = [
  tile("stationery-marker", "Marker", "stationery", ["stationery", "writing"], [".....##.", "....##..", "...##...", "..##....", ".##.....", "##......", "#.......", "........"]),
  tile("stationery-ink-bottle", "Ink Bottle", "stationery", ["stationery", "ink"], ["...##...", ".######.", ".#....#.", ".######.", ".######.", ".#....#.", ".######.", "........"]),
  tile("stationery-envelope", "Envelope", "stationery", ["stationery", "paper"], [".######.", "##....##", "#.####.#", "#.#..#.#", "#..##..#", "##....##", ".######.", "........"]),
  tile("stationery-sticky-note", "Sticky Note", "stationery", ["stationery", "paper"], [".######.", ".#....#.", ".#....#.", ".#....#.", ".#....#.", ".#####..", "........", "........"]),
  tile("stationery-folder", "Folder", "stationery", ["stationery", "paper"], [".###....", ".######.", "########", "########", "########", ".######.", "........", "........"]),
  tile("stationery-protractor", "Protractor", "stationery", ["stationery", "measure"], ["...##...", ".##..##.", "##....##", "########", "#.#..#.#", "########", "........", "........"]),
  sprite("stationery-pencil-cup", "Pencil Cup", "stationery", ["stationery", "desk", "large"], shapePainter({
    rectangles: [[5, 9, 6, 6]],
    lines: [[5, 9, 3, 1], [7, 9, 7, 0], [9, 9, 12, 2], [5, 15, 11, 15]],
  })),
  sprite("stationery-open-notebook", "Open Notebook", "stationery", ["stationery", "paper", "large"], shapePainter({
    rectangles: [[1, 3, 6, 11], [9, 3, 6, 11]],
    lines: [[8, 2, 8, 15], [3, 6, 5, 6], [11, 6, 13, 6], [3, 9, 5, 9], [11, 9, 13, 9]],
  })),
  sprite("stationery-desk-lamp", "Desk Lamp", "stationery", ["stationery", "desk", "large"], shapePainter({
    ellipses: [[8, 4, 5, 3]],
    lines: [[8, 7, 6, 12], [6, 12, 10, 14], [3, 14, 13, 14]],
  })),
  sprite("stationery-calculator", "Calculator", "stationery", ["stationery", "calculator", "large"], shapePainter({
    rectangles: [[3, 1, 10, 14]],
    clearedPixels: [[5, 3], [6, 3], [7, 3], [8, 3], [9, 3], [10, 3], [5, 7], [7, 7], [9, 7], [11, 7], [5, 10], [7, 10], [9, 10], [11, 10], [5, 13], [7, 13], [9, 13], [11, 13]],
  })),
];

const ELECTRONICS_ASSETS = [
  tile("electronics-chip", "Chip", "electronics", ["electronics", "chip"], ["..####..", ".######.", "##....##", "##.##.##", "##.##.##", "##....##", ".######.", "..####.."]),
  tile("electronics-circuit-board", "Circuit Board", "electronics", ["electronics", "circuit", "tileable"], ["#..#..#.", ".##.##..", "..#.#.##", "##.#.#..", ".##.##.#", "#..#..##", "##.##...", "..#..#.#"]),
  tile("electronics-resistor", "Resistor", "electronics", ["electronics", "component"], ["........", "........", "#..####.", ".##....#", "#..####.", "........", "........", "........"]),
  tile("electronics-capacitor", "Capacitor", "electronics", ["electronics", "component"], ["........", "...##...", "...##...", "########", "...##...", "...##...", "........", "........"]),
  tile("electronics-diode", "Diode", "electronics", ["electronics", "component"], ["........", "........", "##..##..", ".#####..", "##..##..", "........", "........", "........"]),
  tile("electronics-led", "LED", "electronics", ["electronics", "component"], ["...##...", ".######.", "##....##", ".######.", "...##...", "...##...", "..####..", "........"]),
  tile("electronics-switch", "Switch", "electronics", ["electronics", "component"], ["........", ".######.", "########", "...##...", "....##..", ".....##.", "........", "........"]),
  tile("electronics-battery", "Battery", "electronics", ["electronics", "power"], ["...##...", ".######.", "##....##", "##.##.##", "##.##.##", "##....##", ".######.", "........"]),
  tile("electronics-plug", "Plug", "electronics", ["electronics", "power"], ["..#..#..", "..#..#..", ".######.", ".######.", "...##...", "...##...", "..####..", "........"]),
  sprite("electronics-desktop-pc", "Desktop PC", "electronics", ["electronics", "computer", "large"], shapePainter({
    rectangles: [[2, 2, 10, 8], [5, 11, 4, 2], [3, 14, 8, 1]],
    lines: [[12, 5, 15, 5], [12, 8, 15, 8]],
  })),
  sprite("electronics-laptop", "Laptop", "electronics", ["electronics", "computer", "large"], shapePainter({
    rectangles: [[3, 3, 10, 7], [1, 11, 14, 3]],
    lines: [[4, 12, 12, 12]],
  })),
  sprite("electronics-crt-monitor", "CRT Monitor", "electronics", ["electronics", "monitor", "large"], shapePainter({
    ellipses: [[8, 6, 6, 5]],
    rectangles: [[5, 10, 6, 3], [3, 14, 10, 1]],
  })),
  sprite("electronics-keyboard", "Keyboard", "electronics", ["electronics", "keyboard", "large"], shapePainter({
    rectangles: [[1, 6, 14, 7]],
    clearedPixels: [[3, 8], [5, 8], [7, 8], [9, 8], [11, 8], [13, 8], [3, 10], [5, 10], [7, 10], [9, 10], [11, 10], [13, 10]],
  })),
  sprite("electronics-gamepad", "Gamepad", "electronics", ["electronics", "game", "large"], shapePainter({
    ellipses: [[8, 9, 7, 4]],
    lines: [[4, 9, 8, 9], [6, 7, 6, 11]],
    clearedPixels: [[11, 8], [13, 10]],
  })),
];

const CHIBI_ASSETS = [
  sprite("chibi-hero", "Chibi Hero", "chibi", ["chibi", "character", "hero"], chibiPainter({ accessory: "sword" })),
  sprite("chibi-heroine", "Chibi Heroine", "chibi", ["chibi", "character", "hero"], chibiPainter({ hair: "long" })),
  sprite("chibi-knight", "Chibi Knight", "chibi", ["chibi", "character", "knight"], chibiPainter({ accessory: "helmet" })),
  sprite("chibi-wizard", "Chibi Wizard", "chibi", ["chibi", "character", "wizard"], chibiPainter({ accessory: "staff", hair: "spiky" })),
  sprite("chibi-ninja", "Chibi Ninja", "chibi", ["chibi", "character", "ninja"], chibiPainter({ hair: "hood" })),
  sprite("chibi-astronaut", "Chibi Astronaut", "chibi", ["chibi", "character", "space"], chibiPainter({ accessory: "visor" })),
  sprite("chibi-cat", "Chibi Cat", "chibi", ["chibi", "animal", "cat"], chibiPainter({ ears: "point", tail: true })),
  sprite("chibi-dog", "Chibi Dog", "chibi", ["chibi", "animal", "dog"], chibiPainter({ tail: true })),
  sprite("chibi-rabbit", "Chibi Rabbit", "chibi", ["chibi", "animal", "rabbit"], chibiPainter({ ears: "long" })),
  sprite("chibi-fox", "Chibi Fox", "chibi", ["chibi", "animal", "fox"], chibiPainter({ ears: "point", tail: true })),
  sprite("chibi-slime", "Chibi Slime", "chibi", ["chibi", "fantasy", "slime"], (matrix) => {
    drawMatrixEllipse(matrix, 8, 9, 6, 5);
    drawMatrixLine(matrix, 3, 9, 5, 3);
    drawMatrixLine(matrix, 13, 9, 11, 3);
    setMatrixPixel(matrix, 6, 9, 0);
    setMatrixPixel(matrix, 10, 9, 0);
  }),
  sprite("chibi-dragon", "Chibi Dragon", "chibi", ["chibi", "fantasy", "dragon"], chibiPainter({ ears: "point", wings: true, tail: true })),
];

const FLORA_ASSETS = [
  tile("flora-grass-clump", "Grass Clump", "flora", ["flora", "grass"], ["........", ".#..#...", "..##....", ".#..#...", "#....#..", ".#..#...", "........", "........"]),
  tile("flora-tall-grass", "Tall Grass", "flora", ["flora", "grass"], [".#.#.#.#", ".#.#.#.#", "..#.#.#.", ".#.#.#.#", "#.#.#.#.", ".#.#.#.#", "........", "........"]),
  tile("flora-tulip", "Tulip", "flora", ["flora", "flower"], ["...##...", ".######.", ".######.", "...##...", "...##...", "...##...", "..####..", "........"]),
  tile("flora-sunflower", "Sunflower", "flora", ["flora", "flower"], ["...##...", ".######.", "##.##.##", ".######.", "...##...", "...##...", "..####..", "........"]),
  tile("flora-rose", "Rose", "flora", ["flora", "flower"], ["...##...", ".######.", ".##.##..", "..###...", "...##...", "...##...", "..####..", "........"]),
  tile("flora-lily-pad", "Lily Pad", "flora", ["flora", "water"], ["........", ".######.", "########", "###..###", "########", ".######.", "........", "........"]),
  tile("flora-mushroom", "Flora Mushroom", "flora", ["flora", "mushroom"], ["........", ".######.", "########", ".#.#..#.", "...##...", "...##...", "..####..", "........"]),
  tile("flora-cactus", "Cactus", "flora", ["flora", "cactus"], ["...##...", "...##...", ".#.##.#.", ".#.##.#.", "...##...", "...##...", "..####..", "........"]),
  tile("flora-bamboo", "Bamboo", "flora", ["flora", "bamboo"], ["..##....", "..##....", "..##....", "..##....", "..##....", "..##....", "..##....", "..##...."]),
  sprite("flora-palm-tree", "Palm Tree", "flora", ["flora", "tree", "large"], shapePainter({
    lines: [[8, 14, 8, 5], [8, 5, 1, 2], [8, 5, 15, 2], [8, 5, 3, 7], [8, 5, 13, 7]],
    rectangles: [[7, 12, 3, 4]],
  })),
  sprite("flora-cherry-tree", "Cherry Tree", "flora", ["flora", "tree", "large"], shapePainter({
    ellipses: [[8, 5, 7, 5], [4, 8, 4, 4], [12, 8, 4, 4]],
    rectangles: [[6, 9, 5, 7]],
  })),
  sprite("flora-cactus-tall", "Tall Cactus", "flora", ["flora", "cactus", "large"], shapePainter({
    rectangles: [[6, 2, 4, 13]],
    lines: [[6, 7, 2, 7], [2, 7, 2, 11], [10, 9, 14, 9], [14, 9, 14, 5]],
  })),
  sprite("flora-rose-bush", "Rose Bush", "flora", ["flora", "flower", "large"], shapePainter({
    ellipses: [[8, 10, 7, 4], [4, 6, 3, 3], [8, 4, 3, 3], [12, 6, 3, 3]],
  })),
  sprite("flora-giant-flower", "Giant Flower", "flora", ["flora", "flower", "large"], shapePainter({
    ellipses: [[8, 5, 3, 3], [4, 5, 3, 3], [12, 5, 3, 3], [8, 1, 2, 3], [8, 9, 2, 3]],
    lines: [[8, 9, 8, 15], [8, 12, 3, 14], [8, 12, 13, 14]],
  })),
];

const ANIMATION_PRESETS = [
  animationTile("anim-water-ripple", "Water Ripple", "top-view", ["animation", "water", "ripple"], 160, [
    ["........", "..##....", "........", "....##..", "........", ".##.....", "........", "........"],
    ["...##...", "........", ".##.....", "........", ".....##.", "........", "..##....", "........"],
    ["........", ".##.....", "........", ".....##.", "........", "...##...", "........", ".##....."],
    [".....##.", "........", "...##...", "........", ".##.....", "........", ".....##.", "........"],
  ]),
  animationTile("anim-waterfall-flow", "Waterfall Flow", "side-view", ["animation", "water", "fall"], 100, [
    [".##..##.", "#..##..#", ".##..##.", "#..##..#", ".##..##.", "#..##..#", ".##..##.", "#..##..#"],
    ["#..##..#", ".##..##.", "#..##..#", ".##..##.", "#..##..#", ".##..##.", "#..##..#", ".##..##."],
    ["..##..##", ".#..##..", "##..##..", "..##..##", ".#..##..", "##..##..", "..##..##", ".#..##.."],
    ["##..##..", ".##..##.", "..##..##", "##..##..", ".##..##.", "..##..##", "##..##..", ".##..##."],
  ]),
  animationTile("anim-lava-bubble", "Lava Bubble", "side-view", ["animation", "lava", "hazard"], 140, [
    ["........", "........", "...##...", "........", "########", "#.##.##.", "########", "########"],
    ["........", "...##...", "..####..", "...##...", "########", "##.##.##", "########", "########"],
    ["...##...", "..####..", ".######.", "..####..", "########", "#.##.##.", "########", "########"],
    ["........", "..####..", "...##...", "........", "########", "##.##.##", "########", "########"],
  ]),
  animationTile("anim-torch-flame", "Torch Flame", "cave", ["animation", "fire", "torch"], 120, [
    ["...#....", "..###...", ".##.##..", "...#....", "...#....", "..###...", "..###...", "........"],
    ["....#...", "...###..", "..##.##.", "...###..", "....#...", "...###..", "...###..", "........"],
    ["...#....", ".#####..", "..###...", "...#....", "...#....", "..###...", "..###...", "........"],
    ["..#.....", ".###....", ".##.##..", "...##...", "...#....", "..###...", "..###...", "........"],
  ]),
  animationTile("anim-construction-beacon", "Construction Beacon", "construction", ["animation", "construction", "warning"], 320, [
    ["........", "...##...", "..####..", "...##...", "...##...", "..####..", ".######.", "########"],
    ["........", "........", "...##...", "...##...", "...##...", "...##...", ".######.", "########"],
  ]),
  animationTile("anim-traffic-light", "Traffic Light", "city", ["animation", "city", "traffic"], 600, [
    ["..####..", ".##..##.", ".##..##.", ".##..##.", ".##..##.", ".##..##.", "..####..", "...##..."],
    ["..####..", ".##..##.", ".##..##.", ".######.", ".##..##.", ".##..##.", "..####..", "...##..."],
    ["..####..", ".##..##.", ".##..##.", ".##..##.", ".##..##.", ".######.", "..####..", "...##..."],
  ]),
  animationTile("anim-led-pulse", "LED Pulse", "electronics", ["animation", "electronics", "led"], 120, [
    ["........", "........", "........", "...##...", "...##...", "........", "........", "........"],
    ["........", "........", "..####..", ".######.", ".######.", "..####..", "........", "........"],
    ["........", ".######.", "########", "########", "########", "########", ".######.", "........"],
    ["........", "........", "..####..", ".######.", ".######.", "..####..", "........", "........"],
  ]),
  animationTile("anim-bubble-rise", "Bubble Rise", "underwater", ["animation", "underwater", "bubble"], 140, [
    ["........", "........", "........", "........", "........", ".....##.", ".....##.", "........"],
    ["........", "........", "........", "....##..", "....##..", "........", "........", "........"],
    ["........", "...##...", "...##...", "........", "........", "........", "........", "........"],
    ["..##....", "..##....", "........", "........", "........", "........", "........", "........"],
  ]),
  animationTile("anim-leaf-rustle", "Leaf Rustle", "forest", ["animation", "forest", "leaf"], 180, [
    ["........", "...#....", ".#####..", "##.####.", ".#####..", "...#....", "........", "........"],
    ["........", "....#...", "..#####.", ".####.##", "..#####.", "....#...", "........", "........"],
    ["........", ".....#..", "...#####", "##.####.", "...#####", ".....#..", "........", "........"],
    ["........", "....#...", ".####.##", "..#####.", ".####.##", "....#...", "........", "........"],
  ]),
  animationTile("anim-flower-bloom", "Flower Bloom", "flora", ["animation", "flora", "flower"], 180, [
    ["........", "........", "...##...", "...##...", "...##...", "..####..", "...##...", "........"],
    ["........", "...##...", ".######.", "...##...", ".######.", "..####..", "...##...", "........"],
    ["...##...", ".######.", "##.##.##", ".######.", "##.##.##", "..####..", "...##...", "........"],
    ["........", ".######.", "##.##.##", ".######.", ".######.", "..####..", "...##...", "........"],
  ]),
  animationTile("anim-pencil-write", "Pencil Write", "stationery", ["animation", "stationery", "writing"], 130, [
    ["......##", ".....##.", "....##..", "...##...", "..##....", ".##.....", "........", "........"],
    ["......##", ".....##.", "....##..", "...##...", "..##....", ".######.", "........", "........"],
    ["......##", ".....##.", "....##..", "...##...", "..##....", ".######.", "########", "........"],
  ]),
  animationTile("anim-village-lamp", "Village Lamp", "village", ["animation", "village", "light"], 280, [
    ["...##...", "..####..", "...##...", "...##...", "...##...", "...##...", "...##...", "..####.."],
    ["..####..", ".######.", "..####..", "...##...", "...##...", "...##...", "...##...", "..####.."],
    [".######.", "########", ".######.", "...##...", "...##...", "...##...", "...##...", "..####.."],
    ["..####..", ".######.", "..####..", "...##...", "...##...", "...##...", "...##...", "..####.."],
  ]),
  animationSprite("anim-chibi-hero-walk", "Chibi Hero Walk", "chibi", ["animation", "chibi", "walk"], 120, [
    chibiWalkPainter(0), chibiWalkPainter(1), chibiWalkPainter(2), chibiWalkPainter(3),
  ]),
  animationSprite("anim-chibi-knight-slash", "Chibi Knight Slash", "chibi", ["animation", "chibi", "action"], 100, [
    chibiKnightSlashPainter(0), chibiKnightSlashPainter(1), chibiKnightSlashPainter(2), chibiKnightSlashPainter(3),
  ]),
  animationSprite("anim-chibi-wizard-cast", "Chibi Wizard Cast", "chibi", ["animation", "chibi", "magic"], 110, [
    chibiWizardCastPainter(0), chibiWizardCastPainter(1), chibiWizardCastPainter(2), chibiWizardCastPainter(3),
  ]),
  animationSprite("anim-fish-swim", "Fish Swim", "creatures", ["animation", "fish", "underwater"], 130, [
    fishSwimPainter(0), fishSwimPainter(1), fishSwimPainter(2), fishSwimPainter(3),
  ]),
  animationSprite("anim-propeller-plane", "Propeller Plane", "vehicles", ["animation", "aircraft", "propeller"], 80, [
    propellerPlanePainter(0), propellerPlanePainter(1), propellerPlanePainter(2), propellerPlanePainter(3),
  ]),
  animationSprite("anim-excavator-dig", "Excavator Dig", "construction", ["animation", "construction", "machine"], 140, [
    excavatorDigPainter(0), excavatorDigPainter(1), excavatorDigPainter(2), excavatorDigPainter(3),
  ]),
  animationSprite("anim-mine-cart-roll", "Mine Cart Roll", "cave", ["animation", "cave", "cart"], 120, [
    mineCartRollPainter(0), mineCartRollPainter(1), mineCartRollPainter(2), mineCartRollPainter(3),
  ]),
  animationSprite("anim-windmill-turn", "Windmill Turn", "village", ["animation", "village", "windmill"], 150, [
    windmillTurnPainter(0), windmillTurnPainter(1), windmillTurnPainter(2), windmillTurnPainter(3),
  ]),
];

const ASSET_PRESETS = [
  ...SIDE_VIEW_ASSETS,
  ...TOP_VIEW_ASSETS,
  ...SYMBOL_ASSETS,
  ...STATIONERY_ASSETS,
  ...VEHICLE_ASSETS,
  ...CREATURE_ASSETS,
  ...EXTENDED_EXISTING_ASSETS,
  ...CONSTRUCTION_ASSETS,
  ...CAVE_ASSETS,
  ...FOREST_ASSETS,
  ...UNDERWATER_ASSETS,
  ...VILLAGE_ASSETS,
  ...CITY_ASSETS,
  ...STATIONERY_EXPANSION_ASSETS,
  ...ELECTRONICS_ASSETS,
  ...CHIBI_ASSETS,
  ...FLORA_ASSETS,
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
  rowSet("set-stationery-desk", "Stationery Desk", "stationery", ["set", "stationery"], [...STATIONERY_ASSETS, ...STATIONERY_EXPANSION_ASSETS]
    .filter(({ width, height }) => width === 1 && height === 1)
    .map(({ id }) => id)),
  spriteSet("set-aircraft", "Aircraft", "vehicles", ["set", "aircraft"], ["vehicle-propeller-plane", "vehicle-fighter-jet", "vehicle-bomber", "vehicle-biplane"]),
  spriteSet("set-sky-space", "Sky Space", "vehicles", ["set", "aircraft", "space"], ["vehicle-helicopter", "vehicle-rocket", "vehicle-ufo", "vehicle-airship"]),
  spriteSet("set-ground-transport", "Ground Transport", "vehicles", ["set", "land"], ["vehicle-drone", "vehicle-tank", "vehicle-train", "vehicle-car"]),
  spriteSet("set-mammals", "Mammals", "creatures", ["set", "mammal"], ["creature-cat", "creature-dog", "creature-rabbit", "creature-fox"]),
  ARCADE_DIGITS,
  rowSet("set-construction-site", "Construction Site", "construction", ["set", "construction"], ["construction-caution-stripe", "construction-traffic-cone", "construction-safety-barrier", "construction-site-fence", "construction-scaffold", "construction-steel-beam", "construction-oil-drum", "construction-cargo-crate"]),
  spriteSet("set-construction-machines", "Construction Machines", "construction", ["set", "construction"], ["construction-excavator", "construction-bulldozer", "construction-crane", "construction-dump-truck"]),
  rowSet("set-cave-tiles", "Cave Tiles", "cave", ["set", "cave"], ["cave-rock-wall", "cave-crystal-wall", "cave-floor", "cave-stalactite", "cave-stalagmite", "cave-mine-track", "cave-torch"]),
  spriteSet("set-cave-landmarks", "Cave Landmarks", "cave", ["set", "cave"], ["cave-entrance", "cave-crystal-cluster", "cave-mine-cart", "cave-treasure-chest"]),
  rowSet("set-forest-ground", "Forest Ground", "forest", ["set", "forest"], ["forest-leaf-canopy", "forest-tree-trunk", "forest-tree-stump", "forest-fern", "forest-mossy-rock", "forest-vine", "forest-mushroom", "forest-fallen-leaf"]),
  spriteSet("set-forest-landmarks", "Forest Landmarks", "forest", ["set", "forest"], ["forest-oak-tree", "forest-pine-tree", "forest-fallen-log", "forest-waterfall"]),
  rowSet("set-underwater-floor", "Underwater Floor", "underwater", ["set", "underwater"], ["underwater-sand", "underwater-coral", "underwater-seaweed", "underwater-kelp", "underwater-shell", "underwater-bubble", "underwater-reef-wall"]),
  spriteSet("set-underwater-scenes", "Underwater Scenes", "underwater", ["set", "underwater"], ["underwater-coral-reef", "underwater-shipwreck", "underwater-diver", "underwater-jellyfish"]),
  rowSet("set-village-props", "Village Props", "village", ["set", "village"], ["village-cobblestone", "village-fence", "village-signpost", "village-hay-bale", "village-barrel", "village-lamp-post", "village-well", "village-crop-field"]),
  spriteSet("set-village-buildings", "Village Buildings", "village", ["set", "village"], ["village-cottage", "village-shop", "village-inn", "village-windmill"]),
  rowSet("set-city-streets", "City Streets", "city", ["set", "city"], ["city-asphalt", "city-sidewalk", "city-crosswalk", "city-road-marking", "city-traffic-light", "city-hydrant", "city-mailbox", "city-bench"]),
  spriteSet("set-city-buildings", "City Buildings", "city", ["set", "city"], ["city-apartment", "city-office-tower", "city-storefront", "city-cafe"]),
  rowSet("set-electronics-parts", "Electronics Parts", "electronics", ["set", "electronics"], ["electronics-chip", "electronics-circuit-board", "electronics-resistor", "electronics-capacitor", "electronics-diode", "electronics-led", "electronics-switch", "electronics-battery", "electronics-plug"]),
  spriteSet("set-electronics-devices", "Electronics Devices", "electronics", ["set", "electronics"], ["electronics-desktop-pc", "electronics-laptop", "electronics-crt-monitor", "electronics-keyboard"]),
  spriteSet("set-chibi-party", "Chibi Party", "chibi", ["set", "chibi"], ["chibi-hero", "chibi-heroine", "chibi-knight", "chibi-wizard"]),
  spriteSet("set-flora-garden", "Flora Garden", "flora", ["set", "flora"], ["flora-palm-tree", "flora-cherry-tree", "flora-cactus-tall", "flora-rose-bush"]),
];

export const PCG_PRESETS = Object.freeze([...ASSET_PRESETS, ...SET_PRESETS, ...ANIMATION_PRESETS]);

if (ASSET_PRESETS.length !== 288 || SET_PRESETS.length !== 32 || ANIMATION_PRESETS.length !== 20 || PCG_PRESETS.length !== 340 || new Set(PCG_PRESETS.map(({ id }) => id)).size !== PCG_PRESETS.length) {
  throw new Error("PCG preset catalog is incomplete");
}

const PRESET_BY_ID = new Map(PCG_PRESETS.map((preset) => [preset.id, preset]));

export const PCG_PRESET_CATEGORY_OPTIONS = Object.freeze([
  { id: "side-view", label: "Side view" },
  { id: "top-view", label: "Top view" },
  { id: "symbols", label: "Symbols" },
  { id: "stationery", label: "Stationery" },
  { id: "vehicles", label: "Vehicles" },
  { id: "creatures", label: "Creatures" },
  { id: "construction", label: "Construction" },
  { id: "cave", label: "Cave" },
  { id: "forest", label: "Forest" },
  { id: "underwater", label: "Underwater" },
  { id: "village", label: "Village" },
  { id: "city", label: "City" },
  { id: "electronics", label: "Electronics" },
  { id: "chibi", label: "Chibi" },
  { id: "flora", label: "Flora" },
].map((option) => Object.freeze(option)));

export const PCG_PRESET_CATEGORIES = Object.freeze(PCG_PRESET_CATEGORY_OPTIONS.map(({ id }) => id));

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
    if (size === "8x8" && !(["asset", "animation"].includes(preset.kind) && preset.width === 1 && preset.height === 1)) return false;
    if (size === "16x16" && !(["asset", "animation"].includes(preset.kind) && preset.width === 2 && preset.height === 2)) return false;
    if (size === "sets" && preset.kind !== "set") return false;
    if (allowedIds && !allowedIds.has(preset.id)) return false;
    if (!normalizedQuery) return true;
    return [preset.name, preset.category, preset.kind, ...preset.tags].join(" ").toLowerCase().includes(normalizedQuery);
  });
  if (!allowedIds) return matches;
  const matchesById = new Map(matches.map((preset) => [preset.id, preset]));
  return orderedIds.map((id) => matchesById.get(id)).filter(Boolean);
}
