// Exercise the shipping WASM core directly; this does not automate a browser UI.
// Usage: node games/tests/wasm_launch.mjs <emulator checkout> <owned ROM> [game id]
import fs from 'node:fs';
import vm from 'node:vm';
import path from 'node:path';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
const [emulator, romFile, gameId] = process.argv.slice(2);
const gamesRoot = fileURLToPath(new URL('../', import.meta.url));
const dist = path.join(emulator, 'web/dist');
const context = vm.createContext({console, URL, TextDecoder, TextEncoder, WebAssembly,
  performance, self:{location:{href:'https://local.test/wasm/jr100-core.js'}}});
vm.runInContext(fs.readFileSync(path.join(dist,'wasm/jr100-core.js'),'utf8'),context);
const binary = new WebAssembly.Module(fs.readFileSync(path.join(dist,'wasm/jr100-core.wasm')));
const wasm = await context.createJR100Module({instantiateWasm(imports, receive) {
  receive(new WebAssembly.Instance(binary, imports));
}});
const check = value => assert.equal(value, 0, wasm.UTF8ToString(wasm._jr_last_error()));
function transfer(bytes) {const pointer=wasm._jr_input_resize(bytes.length);wasm.HEAPU8.set(bytes,pointer);return bytes.length;}
function state() {return JSON.parse(wasm.UTF8ToString(wasm._jr_state_json()));}
function frame(count) {for(let i=0;i<count;i++)check(wasm._jr_run_frame(14900));}
function peek(address) {return wasm.HEAPU8[wasm._jr_read_memory(address,1)];}
const catalog=JSON.parse(fs.readFileSync(path.join(dist,'games/catalog.json'),'utf8'));
const selected = catalog.games.filter(game => !gameId || game.id === gameId);
assert(selected.length, `Unknown game: ${gameId}`);
for(const game of selected) {
  const metadata = JSON.parse(fs.readFileSync(path.join(gamesRoot, game.id.replaceAll('-', '_'), 'game.json'), 'utf8'));
  const symbolsPath = path.join(gamesRoot, game.id.replaceAll('-', '_'), 'build/symbols.json');
  const presentationSymbols = fs.existsSync(symbolsPath) ? JSON.parse(fs.readFileSync(symbolsPath, 'utf8')) : {};
  function waitForPresentation() {
    if (!('PACE_ACTIVE' in presentationSymbols)) return;
    const pending = () => peek(presentationSymbols.INTRO_PENDING) || peek(presentationSymbols.PACE_ACTIVE);
    for (let i = 0; i < 240 && pending(); i++) frame(1);
    assert.equal(pending(), 0, `${game.id} presentation did not finish`);
    frame(6);
  }
  const {modeAddress = 0x3340, startFrames = 50} = metadata.launchCheck ?? {};
  check(wasm._jr_create_core(transfer(fs.readFileSync(romFile)),0));
  frame(100);
  const data=fs.readFileSync(path.join(dist,game.path));
  check(wasm.ccall('jr_load_program','number',['number','string'],[transfer(data),`${game.id}.prg`]));
  frame(450);
  assert.equal(state().extendedRam,false);
  assert.equal(state().autotypeActive,false);
  assert.equal(peek(modeAddress),0, `${game.id} did not reach its title`);
  assert(state().programCounter>=768 && state().programCounter<0x3000);
  const pixels=wasm.HEAPU8.slice(wasm._jr_frame_data(),wasm._jr_frame_data()+wasm._jr_frame_size());
  assert(pixels.some(n=>n===1));
  function checkFont(scene) {
    const directory = path.join(gamesRoot, game.id.replaceAll('-', '_'));
    const fontPath = path.join(directory, 'build/fonts.json');
    if (!fs.existsSync(fontPath)) return;
    const fonts = JSON.parse(fs.readFileSync(fontPath, 'utf8'));
    const symbols = JSON.parse(fs.readFileSync(path.join(directory, 'build/symbols.json'), 'utf8'));
    const chars = Object.values(fonts[scene].characters);
    const bankAddress = symbols[`${scene.toUpperCase()}_PCG`];
    for (const slot of chars) {
      for (let row = 0; row < 8; row++) {
        assert.equal(peek(0xc000 + slot * 8 + row), peek(bankAddress + slot * 8 + row),
          `${game.id} ${scene} font bank differs`);
      }
    }
    if (chars.length) {
      const screen = Array.from({length:768}, (_, i) => peek(0xc100 + i));
      assert(screen.some(code => chars.includes(code - 128)), `${game.id} ${scene} font not displayed`);
    }
  }
  checkFont('title');
  if (metadata.launchCheck?.titleAnimation) {
    const {address, size, frames} = metadata.launchCheck.titleAnimation;
    const bank = () => Array.from({length: 256}, (_, i) => peek(0xc000 + i));
    const original = bank();
    const offset = address - 0xc000;
    const seen = new Set();
    for (let i = 0; i < frames; i++) {
      frame(1);
      const current = bank();
      assert.deepEqual(current.slice(0, offset), original.slice(0, offset));
      assert.deepEqual(current.slice(offset + size), original.slice(offset + size));
      seen.add(current.slice(offset, offset + size).join(','));
    }
    assert(seen.size >= 2, `${game.id} title did not animate`);
    assert.equal(peek(modeAddress), 0);
  }
  assert(wasm._jr_audio_size()>0);
  check(wasm._jr_clear_audio());
  check(wasm._jr_set_key(8,3,1));frame(6);check(wasm._jr_set_key(8,3,0));frame(startFrames);
  waitForPresentation();
  // DICE RELIC finishes its opening roll after the start presentation.
  for (let i = 0; i < 240 && peek(modeAddress) !== 1; i++) frame(1);
  assert.equal(peek(modeAddress),1,`${game.id} did not begin play`);
  checkFont('game');
  if (game.id === 'brick-pulse') {
    const directory = path.join(gamesRoot, 'brick_pulse');
    const slots = JSON.parse(fs.readFileSync(path.join(directory, 'build/state_slots.json'), 'utf8'));
    const symbols = JSON.parse(fs.readFileSync(path.join(directory, 'build/symbols.json'), 'utf8'));
    const value = field => peek(symbols[slots[`s.${field}`]]);
    for (const pad of [false, true]) {
      if (pad) {
        check(wasm._jr_create_core(transfer(fs.readFileSync(romFile)),0)); frame(100);
        check(wasm.ccall('jr_load_program','number',['number','string'],[transfer(data),`${game.id}.prg`])); frame(450);
        check(wasm._jr_set_key(8,3,1)); frame(6); check(wasm._jr_set_key(8,3,0)); frame(30);
        waitForPresentation();
      }
      check(wasm._jr_set_key(8, 1, 1)); frame(6);
      check(wasm._jr_set_key(8, 1, 0)); frame(6);
      assert.equal(peek(symbols.CN_ACTIVE), 0, 'SPACE must not open a reset');
      const direction = (right, down) => pad
        ? check(wasm._jr_set_joystick(down ? (right ? 1 : 2) : 0))
        : check(wasm._jr_set_key(1, right ? 2 : 0, down ? 1 : 0));
      const before = value('clock');
      direction(false, true); frame(95);
      assert.equal(value('paddle'), 0, 'Held left must reach the boundary');
      assert(((value('clock') - before) & 255) >= 4, 'Holding must not stall physics');
      direction(false, false); direction(true, true); frame(180);
      assert.equal(value('paddle'), 24, 'Held right must reach the boundary');
      direction(true, false); direction(false, true); frame(15);
      direction(false, false); frame(3);
      const stopped = value('paddle');
      assert(stopped > 0 && stopped < 24);
      frame(12);
      assert.equal(value('paddle'), stopped, 'Paddle moves after key release');
      assert.equal(peek(modeAddress), 1);
      console.log(`PASS: brick-pulse, shipping WASM ${pad ? 'pad' : 'keyboard'} hold, reversal, release and active ball`);
    }
  }
  if (metadata.nativeRules && !metadata.disableSpaceReset && !metadata.rankedCampaign) {
    const symbols = JSON.parse(fs.readFileSync(path.join(gamesRoot, game.id.replaceAll('-', '_'), 'build/symbols.json'), 'utf8'));
    const press = (row, bit) => {
      check(wasm._jr_set_key(row,bit,1)); frame(6);
      check(wasm._jr_set_key(row,bit,0)); frame(30);
      waitForPresentation();
    };
    press(8,1);
    assert.equal(peek(symbols.CN_ACTIVE), 1);
    assert.equal(peek(symbols.CN_CHOICE), 0);
    const snapshot = () => Array.from({length:1024}, (_,i)=>peek(0x3400+i));
    const paused = snapshot(); frame(120);
    assert.deepEqual(snapshot(), paused, `${game.id} advances during reset question`);
    press(8,3);
    assert.equal(peek(symbols.CN_ACTIVE), 0);
    press(8,1); press(1,2); press(8,3);
    assert.equal(peek(symbols.CN_ACTIVE), 0);
    assert.equal(peek(modeAddress), 1);
  }
  if (metadata.rankedCampaign) {
    const directory = path.join(gamesRoot, game.id.replaceAll('-', '_'));
    const slots = JSON.parse(fs.readFileSync(path.join(directory, 'build/state_slots.json'), 'utf8'));
    const symbols = JSON.parse(fs.readFileSync(path.join(directory, 'build/symbols.json'), 'utf8'));
    const proof = JSON.parse(fs.readFileSync(path.join(directory, 'challenges.json'), 'utf8'))[0];
    const keys = {1:[2,1],2:[1,1],3:[1,0],4:[1,2],5:[8,3],6:[8,1],7:[0,3],8:[1,3]};
    const letterKeys = [[1,0],[0,4],[1,2],[2,2],[1,3],[1,4],[6,0],[6,1],
      [6,2],[7,3],[7,2],[5,4],[2,0],[2,3],[2,4],[2,1]];
    const value = field => peek(symbols[slots[`s.${field}`]]);
    let slideObserved = false;
    let clearObserved = false;
    const press = action => {
      const [row, bit] = keys[action];
      check(wasm._jr_set_key(row, bit, 1)); frame(6);
      check(wasm._jr_set_key(row, bit, 0));
      const positions = new Set();
      let clearFrames = 0;
      let resultScreen;
      // Allow the CPU to draw each cell, then finish the victory phrase.
      for (let i = 0; i < 300; i++) {
        frame(1);
        if (game.id !== 'frost-steps') continue;
        positions.add(value('pos'));
        if (peek(symbols.RESULT_ACTIVE)) {
          clearFrames++;
          const screen = Array.from({length:768}, (_,j)=>peek(0xc100+j));
          if (resultScreen) assert.deepEqual(screen, resultScreen, 'Clear board must stay visible');
          resultScreen = screen;
        }
      }
      slideObserved ||= positions.size >= 3;
      clearObserved ||= clearFrames >= 85;
    };
    for (const action of proof.bonus) {
      assert.equal(peek(modeAddress), 1);
      press(action);
    }
    assert.equal(peek(modeAddress), 2);
    assert.equal(value('stars'), 3);
    assert.equal(value('runes'), 3);
    assert.equal(value('moves'), value('par'));
    assert.equal(peek(symbols.BEST), 3);
    if (game.id === 'frost-steps') {
      assert(slideObserved, 'FROST STEPS must display intermediate positions');
      assert(clearObserved, 'FROST STEPS must hold the completed board through its jingle');
      console.log('PASS: frost-steps, shipping WASM intermediate slide and stable clear hold');
    }
    press(6);
    assert.equal(peek(symbols.CN_ACTIVE), 1);
    press(4); press(5);
    assert.equal(peek(modeAddress), 1);
    assert.equal(value('moves'), 0);
    assert.equal(peek(symbols.BEST), 3);
    press(8);
    assert.equal(peek(symbols.CN_ACTIVE), 1);
    press(4); press(5);
    assert.equal(peek(modeAddress), 6);
    press(4);
    press(5);
    assert.equal(peek(modeAddress), 1);
    assert.equal(peek(symbols.LEVEL), 1);
    console.log(`PASS: ${game.id}, shipping WASM three-star clear, retry and stage selection`);
    press(8);
    press(4); press(5);
    const password = Array.from({length:peek(symbols.P_LEN)}, (_,i)=>peek(symbols.P_BUFFER+i));
    const ratings = Array.from({length:40}, (_,i)=>peek(symbols.BEST+i));
    check(wasm._jr_create_core(transfer(fs.readFileSync(romFile)),0));
    frame(100);
    check(wasm.ccall('jr_load_program','number',['number','string'],[transfer(data),`${game.id}.prg`]));
    frame(450);
    assert.equal(peek(modeAddress), 0);
    assert.equal(peek(symbols.BEST), 0);
    press(7);
    assert.equal(peek(modeAddress), 7);
    for (const letter of password) {
      const [row,bit] = letterKeys[letter];
      check(wasm._jr_set_key(row,bit,1)); frame(6);
      check(wasm._jr_set_key(row,bit,0)); frame(60);
    }
    assert(Array.from({length:768}, (_, i) => peek(0xc100 + i)).every(code => code < 128),
      `${game.id} password entry must use only the ordinary font`);
    press(5);
    assert.equal(peek(modeAddress), 6);
    assert.equal(peek(symbols.LEVEL), 1);
    assert.deepEqual(Array.from({length:40},(_,i)=>peek(symbols.BEST+i)), ratings);
    press(5);
    assert.equal(peek(modeAddress), 1);
    assert.equal(value('moves'), 0);
    console.log(`PASS: ${game.id}, shipping WASM fresh-boot password restores stage and all ratings`);
  }
  console.log(`PASS: ${game.id}, shipped WASM, BASIC autostart, 16KB, title, input and PCM`);
}
