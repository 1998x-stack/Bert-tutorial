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
  'articles/06-mlm-nsp-masking-objectives.html',
  'articles/07-bert-finetuning-practice.html',
  'articles/08-roberta-training-recipe.html',
  'articles/09-pretraining-data-engineering.html',
  'articles/10-bert-optimization-hyperparameters.html',
  'articles/11-encoder-scaling-compute.html',
  'articles/12-numerical-stability-attention.html',
  'articles/13-multilingual-transfer.html',
  'articles/14-encoder-model-selection.html',
  'articles/15-electra-replaced-token-detection.html',
  'articles/16-xlnet-permutation-language-model.html',
  'articles/17-mpnet-masked-permuted.html',
  'articles/18-albert-factorized-sharing.html',
  'articles/19-deberta-disentangled-attention.html',
  'articles/20-chinese-bert-whole-word-masking.html',
  'articles/21-longformer-bigbird-sparse-attention.html',
  'articles/22-simcse-contrastive-sentence-embeddings.html',
  'articles/23-distilbert-tinybert-distillation.html',
  'articles/24-mobilebert-on-device-deployment.html',
  'articles/25-lora-adalora-bitfit.html',
  'articles/26-modernbert-modern-encoder.html',
  'articles/27-model-compression-quantization.html',
  'articles/28-end-to-end-chinese-nlu-project.html',
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
    assert.match(html, /class="skip-link"/i, pagePath);
    assert.doesNotMatch(html, /\\\(|\\\)/, pagePath + ': raw LaTeX delimiters are not rendered offline');
    for (const formula of [...html.matchAll(/<math\b([^>]*)>/gi)]) assert.match(formula[1], /aria-label=/, pagePath + ': MathML needs an accessible label');
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

test('twenty-eight articles use twenty-eight different subject-specific diagrams', () => {
  const diagramPaths = articles.map((pagePath) => {
    const html = read(pagePath);
    const match = html.match(/<img[^>]+src="([^"]+\.svg)"/i);
    assert.ok(match, pagePath + ': diagram path missing');
    return match[1];
  });
  assert.equal(new Set(diagramPaths).size, 28);
});

test('each article has an evidence ledger with verified source locators', () => {
  for (let index = 1; index <= 28; index += 1) {
    const articleId = String(index).padStart(2, '0');
    const ledgerPath = 'articles/evidence-' + articleId + '.json';
    const ledger = JSON.parse(read(ledgerPath));
    assert.ok(ledger.article_id.startsWith(articleId), ledgerPath);
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
  for (const pagePath of articles) {
    const html = read(pagePath);
    if (pagePath.endsWith('05-wordpiece-inputs.html')) {
      assert.match(html, /data-wordpiece-input/, pagePath);
      assert.match(html, /data-wordpiece-run/, pagePath);
    } else {
      assert.match(html, /data-demo-action=/, pagePath);
      assert.match(html, /data-demo-states/, pagePath);
    }
  }
});

test('legacy chapter entry points 01–28 redirect to the new article pages', () => {
  const targets = [
    'articles/01-pretraining-evolution.html',
    'articles/02-transformer-encoder.html',
    'articles/03-bert-pretraining.html',
    'articles/04-bert-finetuning-evidence.html',
    'articles/05-wordpiece-inputs.html',
    'articles/06-mlm-nsp-masking-objectives.html',
    'articles/07-bert-finetuning-practice.html',
    'articles/08-roberta-training-recipe.html',
    'articles/09-pretraining-data-engineering.html',
    'articles/10-bert-optimization-hyperparameters.html',
    'articles/11-encoder-scaling-compute.html',
    'articles/12-numerical-stability-attention.html',
    'articles/13-multilingual-transfer.html',
    'articles/14-encoder-model-selection.html',
    'articles/15-electra-replaced-token-detection.html',
    'articles/16-xlnet-permutation-language-model.html',
    'articles/17-mpnet-masked-permuted.html',
    'articles/18-albert-factorized-sharing.html',
    'articles/19-deberta-disentangled-attention.html',
    'articles/20-chinese-bert-whole-word-masking.html',
    'articles/21-longformer-bigbird-sparse-attention.html',
    'articles/22-simcse-contrastive-sentence-embeddings.html',
    'articles/23-distilbert-tinybert-distillation.html',
    'articles/24-mobilebert-on-device-deployment.html',
    'articles/25-lora-adalora-bitfit.html',
    'articles/26-modernbert-modern-encoder.html',
    'articles/27-model-compression-quantization.html',
    'articles/28-end-to-end-chinese-nlu-project.html',
  ];
  targets.forEach((target, index) => {
    const html = read(String(index + 1).padStart(2, '0') + '.html');
    assert.ok(html.includes(target), target);
    assert.match(html, /http-equiv="refresh"/i);
  });
});


test('all declared teaching states parse and have distinct outputs', () => {
  for (const pagePath of articles) {
    const html = read(pagePath);
    const matches = [...html.matchAll(/<script type="application\/json" data-demo-states>([\s\S]*?)<\/script>/g)];
    if (pagePath.endsWith('05-wordpiece-inputs.html')) continue;
    assert.ok(matches.length >= 1, pagePath + ': demo states missing');
    for (const [, raw] of matches) {
      const states = JSON.parse(raw);
      assert.ok(Object.keys(states).length >= 2);
      assert.ok(new Set(Object.values(states)).size >= 2);
    }
  }
});

test('shared local stylesheet and script exist', () => {
  assert.ok(fs.existsSync(path.join(root, 'assets/css/course.css')));
  assert.ok(fs.existsSync(path.join(root, 'assets/js/site.js')));
});


test('five variant articles explain distinct mechanisms with rendered MathML', () => {
  const terms = [
    ['articles/16-xlnet-permutation-language-model.html', /Query stream/, /Transformer-XL/],
    ['articles/17-mpnet-masked-permuted.html', /位置补偿/, /MPNet/],
    ['articles/18-albert-factorized-sharing.html', /SOP/, /FLOPs/],
    ['articles/19-deberta-disentangled-attention.html', /c2p/, /p2c/],
    ['articles/20-chinese-bert-whole-word-masking.html', /WWM/, /MacBERT/],
  ];
  for (const [page, ...patterns] of terms) {
    const html = read(page);
    assert.match(html, /<math display="block"/, page);
    for (const pattern of patterns) assert.match(html, pattern, page);
  }
});

test('new SVG diagrams include title, description and viewBox', () => {
  const names = [
    '16-xlnet-two-stream.svg', '17-mpnet-position-compensation.svg',
    '18-albert-factorization-sharing.svg', '19-deberta-disentangled.svg',
    '20-chinese-wwm-pipeline.svg',
  ];
  for (const name of names) {
    const svg = read('assets/diagrams/' + name);
    assert.match(svg, /<svg[^>]+viewBox=/);
    assert.match(svg, /<title id=/);
    assert.match(svg, /<desc id=/);
    assert.match(svg, /aria-labelledby=/);
  }
});


test('final eight standalone tutorials include real MathML, independent SVG and source narrative', () => {
  const parts = [
  {
    "num": "21",
    "file": "articles/21-longformer-bigbird-sparse-attention.html"
  },
  {
    "num": "22",
    "file": "articles/22-simcse-contrastive-sentence-embeddings.html"
  },
  {
    "num": "23",
    "file": "articles/23-distilbert-tinybert-distillation.html"
  },
  {
    "num": "24",
    "file": "articles/24-mobilebert-on-device-deployment.html"
  },
  {
    "num": "25",
    "file": "articles/25-lora-adalora-bitfit.html"
  },
  {
    "num": "26",
    "file": "articles/26-modernbert-modern-encoder.html"
  },
  {
    "num": "27",
    "file": "articles/27-model-compression-quantization.html"
  },
  {
    "num": "28",
    "file": "articles/28-end-to-end-chinese-nlu-project.html"
  }
];
  const diagrams = new Set();
  for (const {num,file} of parts) {
    const html = read(file);
    assert.ok((html.match(/<section id=/g) || []).length >= 7, file);
    assert.match(html, /<math display="block" aria-label=/, file);
    assert.match(html, /data-demo-states/, file);
    const img = html.match(/src="\.\.\/(assets\/diagrams\/[0-9]+-[^"]+\.svg)"/);
    assert.ok(img, file);
    diagrams.add(img[1]);
    const svg = read(img[1]);
    assert.match(svg, /<title id=/);
    assert.match(svg, /<desc id=/);
    assert.match(svg, /viewBox=/);
    assert.equal(JSON.parse(read('articles/evidence-' + num + '.json')).article_id, num);
  }
  assert.equal(diagrams.size, 8);
});
