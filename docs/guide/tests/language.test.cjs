const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '../assets/language.js'), 'utf8');

function visit(preferred, saved, search = '', blocked = false) {
  let stored = saved;
  const page = { document: { documentElement: { lang: 'en' } }, navigator: { language: preferred },
    location: { search }, URLSearchParams, localStorage: {
      getItem() { if (blocked) throw new Error('Storage blocked'); return stored; },
      setItem(key, value) { if (blocked) throw new Error('Storage blocked'); stored = value; },
    } };
  vm.runInNewContext(source, page);
  return [page.document.documentElement.lang, stored];
}
test('Japanese primary language only; all other and missing languages default to English', () => {
  for (const language of ['ja', 'ja-JP', 'ja-jp', 'JA']) assert.equal(visit(language)[0], 'ja');
  for (const language of ['en', 'en-US', 'fr-FR', 'zh-CN', 'jargon', '', undefined]) assert.equal(visit(language)[0], 'en');
});
test('explicit choice is persisted and overrides the browser on subsequent pages', () => {
  assert.deepEqual(visit('ja-JP', undefined, '?lang=en'), ['en', 'en']);
  assert.deepEqual(visit('ja-JP', 'en'), ['en', 'en']);
  assert.deepEqual(visit('en-US', 'en', '?lang=ja'), ['ja', 'ja']);
});
test('invalid preferences are ignored and denied storage does not break a guide', () => {
  assert.equal(visit('ja-JP', 'fr', '?lang=fr')[0], 'ja');
  assert.equal(visit('en-US', undefined, '?lang=ja', true)[0], 'ja');
  assert.equal(visit('ja-JP', undefined, '', true)[0], 'ja');
});
