const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
const articles = [
  'articles/01-pretraining-evolution.html',
  'articles/02-transformer-encoder.html',
  'articles/03-bert-pretraining.html',
  'articles/04-bert-finetuning-evidence.html',
  'articles/05-wordpiece-inputs.html',
];

function read(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), 'utf8');
}

function existsFrom(pagePath, href) {
  const clean = href.split('#')[0].split('?')[0];
  if (!clean) return true;
  return fs.existsSync(path.resolve(root, path.dirname(pagePath), clean));
}

test('each deep-reading page has one semantic H1 and a complete document shell', () => {
  for (const pagePath of articles) {
    const html = read(pagePath);
    assert.match(html, /<html lang="zh-CN">/i, pagePath);
    assert.match(html, /<meta name="viewport"/i, pagePath);
    assert.equal((html.match(/<h1\b/gi) || []).length, 1, pagePath);
    assert.match(html, /<main\b[^>]*class="article-main"/i, pagePath);
    assert.match(html, /<article\b[^>]*class="article-body"/i, pagePath);
    assert.match(html, /<section[^>]*class="article-summary"/i, pagePath);
    assert.match(html, /id="references"/i, pagePath);
    assert.match(html, /data-mark-complete/i, pagePath);
    assert.match(html, /assets\/js\/site\.js/i, pagePath);
  }
});

test('article table-of-contents anchors resolve to unique section IDs', () => {
  for (const pagePath of articles) {
    const html = read(pagePath);
    const ids = [...html.matchAll(/\bid="([^"]+)"/g)].map((match) => match[1]);
    assert.equal(new Set(ids).size, ids.length, pagePath + ': duplicate id');
    const links = [...html.matchAll(/href="#([^"]+)"/g)].map((match) => match[1]);
    for (const target of links) {
      assert.ok(ids.includes(target), pagePath + ': missing #' + target);
    }
  }
});

test('all article assets and local links resolve inside the repository', () => {
  for (const pagePath of articles) {
    const html = read(pagePath);
    const localHrefs = [...html.matchAll(/(?:href|src)="([^"]+)"/g)]
      .map((match) => match[1])
      .filter((href) => !/^(?:https?:|mailto:|tel:|data:)/i.test(href));
    for (const href of localHrefs) {
      assert.ok(existsFrom(pagePath, href), pagePath + ': broken local link ' + href);
    }
    const imageTags = [...html.matchAll(/<img\b[^>]*>/gi)].map((match) => match[0]);
    assert.ok(imageTags.length >= 1, pagePath + ': missing diagram');
    for (const image of imageTags) assert.match(image, /\balt="[^"]+"/i, pagePath);
  }
});

test('five articles use five different subject-specific diagrams', () => {
  const diagramPaths = articles.map((pagePath) => {
    const html = read(pagePath);
    const match = html.match(/<img[^>]+src="([^"]+\.svg)"/i);
    assert.ok(match, pagePath + ': diagram path missing');
    return match[1];
  });
  assert.equal(new Set(diagramPaths).size, 5);
});

test('each article has an evidence ledger with verified source locators', () => {
  for (let index = 1; index <= 5; index += 1) {
    const ledgerPath = 'articles/evidence-0' + index + '.json';
    const ledger = JSON.parse(read(ledgerPath));
    assert.equal(ledger.article_id, '0' + index);
    assert.ok(ledger.claims.length >= 4, ledgerPath);
    for (const claim of ledger.claims) {
      assert.equal(claim.status, 'verified', ledgerPath + ': ' + claim.id);
      assert.match(claim.source_url, /^https:\/\//);
      assert.ok(claim.locator);
      assert.ok(claim.verification_note);
    }
  }
});

test('each article includes a meaningful interaction or tokenizer experiment', () => {
  for (const pagePath of articles.slice(0, 4)) {
    const html = read(pagePath);
    assert.match(html, /data-demo-action=/, pagePath);
    assert.match(html, /data-demo-states/, pagePath);
  }
  const fifth = read(articles[4]);
  assert.match(fifth, /data-wordpiece-input/, articles[4]);
  assert.match(fifth, /data-wordpiece-run/, articles[4]);
});

test('legacy chapter entry points 01–05 redirect to the new article pages', () => {
  const targets = [
    'articles/01-pretraining-evolution.html',
    'articles/02-transformer-encoder.html',
    'articles/03-bert-pretraining.html',
    'articles/04-bert-finetuning-evidence.html',
    'articles/05-wordpiece-inputs.html',
  ];
  targets.forEach((target, index) => {
    const html = read(String(index + 1).padStart(2, '0') + '.html');
    assert.ok(html.includes(target), target);
    assert.match(html, /http-equiv="refresh"/i);
  });
});

test('shared local stylesheet and script exist', () => {
  assert.ok(fs.existsSync(path.join(root, 'assets/css/course.css')));
  assert.ok(fs.existsSync(path.join(root, 'assets/js/site.js')));
});
