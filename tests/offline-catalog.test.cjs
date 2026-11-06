const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const html = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
const source = JSON.parse(fs.readFileSync(path.join(root, 'courses.json'), 'utf8'));
const match = html.match(/<script id="offline-courses" type="application\/json">\s*([\s\S]*?)<\/script>/);

test('offline catalog matches the canonical JSON', () => {
  assert.ok(match, 'embedded offline catalog missing');
  assert.deepEqual(JSON.parse(match[1]), source);
});
test('all offline chapter links point to existing files', () => {
  for (const chapter of source.chapters) {
    assert.match(chapter.file, /^\d{2}\.html$/);
    assert.ok(fs.existsSync(path.join(root, chapter.file)), chapter.file);
  }
});
test('file mode uses embedded data and HTTP mode retains fetch', () => {
  assert.match(html, /window\.location\.protocol === 'file:'/);
  assert.match(html, /Promise\.resolve\(JSON\.parse\(localData\.textContent\)\)/);
  assert.match(html, /fetch\('courses\.json'\)/);
});
