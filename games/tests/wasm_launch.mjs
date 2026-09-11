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
  assert.equal(peek(modeAddress),1,`${game.id} did not begin play`);
  checkFont('game');
  if (metadata.rankedCampaign) {
    const directory = path.join(gamesRoot, game.id.replaceAll('-', '_'));
    const slots = JSON.parse(fs.readFileSync(path.join(directory, 'build/state_slots.json'), 'utf8'));
    const symbols = JSON.parse(fs.readFileSync(path.join(directory, 'build/symbols.json'), 'utf8'));
    const proof = JSON.parse(fs.readFileSync(path.join(directory, 'challenges.json'), 'utf8'))[0];
    const keys = {1:[2,1],2:[1,1],3:[1,0],4:[1,2],5:[8,3],6:[8,1],7:[0,3],8:[1,3]};
    const letterKeys = [[1,0],[0,4],[1,2],[2,2],[1,3],[1,4],[6,0],[6,1],
      [6,2],[7,3],[7,2],[5,4],[2,0],[2,3],[2,4],[2,1]];
    const value = field => peek(symbols[slots[`s.${field}`]]);
    const press = action => {
      const [row, bit] = keys[action];
      check(wasm._jr_set_key(row, bit, 1)); frame(6);
      check(wasm._jr_set_key(row, bit, 0)); frame(60);
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
    press(6);
    assert.equal(peek(modeAddress), 1);
    assert.equal(value('moves'), 0);
    assert.equal(peek(symbols.BEST), 3);
    press(8);
    assert.equal(peek(modeAddress), 6);
    press(4);
    press(5);
    assert.equal(peek(modeAddress), 1);
    assert.equal(peek(symbols.LEVEL), 1);
    console.log(`PASS: ${game.id}, shipping WASM three-star clear, retry and stage selection`);
    press(8);
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
