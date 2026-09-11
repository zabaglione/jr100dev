// Exercise the shipping WASM core directly; this does not automate a browser UI.
// Usage: node games/tests/wasm_launch.mjs <emulator checkout> <owned ROM>
import fs from 'node:fs';
import vm from 'node:vm';
import path from 'node:path';
import assert from 'node:assert/strict';
const [emulator, romFile] = process.argv.slice(2);
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
for(const game of catalog.games) {
  check(wasm._jr_create_core(transfer(fs.readFileSync(romFile)),0));
  frame(100);
  const data=fs.readFileSync(path.join(dist,game.path));
  check(wasm.ccall('jr_load_program','number',['number','string'],[transfer(data),`${game.id}.prg`]));
  frame(450);
  assert.equal(state().extendedRam,false);
  assert.equal(state().autotypeActive,false);
  assert.equal(peek(0x3340),0, `${game.id} did not reach its title`);
  assert(state().programCounter>=768 && state().programCounter<0x3000);
  const pixels=wasm.HEAPU8.slice(wasm._jr_frame_data(),wasm._jr_frame_data()+wasm._jr_frame_size());
  assert(pixels.some(n=>n===1));
  assert(wasm._jr_audio_size()>0);
  check(wasm._jr_clear_audio());
  check(wasm._jr_set_key(8,3,1));frame(6);check(wasm._jr_set_key(8,3,0));frame(50);
  assert.equal(peek(0x3340),1,`${game.id} did not begin play`);
  console.log(`PASS: ${game.id}, shipped WASM, BASIC autostart, 16KB, title, input and PCM`);
}
