const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
const html = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
const siteScript = fs.readFileSync(path.join(root, 'assets/js/site.js'), 'utf8');
const source = JSON.parse(fs.readFileSync(path.join(root, 'courses.json'), 'utf8'));
const match = html.match(/<script id="offline-courses" type="application\/json">\s*([\s\S]*?)<\/script>/);

test('offline catalog matches the canonical JSON exactly', () => {
  assert.ok(match, 'embedded offline catalog missing');
  assert.deepEqual(JSON.parse(match[1]), source);
});

test('all 28 chapter links point to existing files', () => {
  assert.equal(source.chapters.length, 28);
  for (const chapter of source.chapters) {
    assert.ok(chapter.file, 'chapter file path missing');
    assert.ok(fs.existsSync(path.join(root, chapter.file)), chapter.file);
    assert.ok(chapter.summary, 'summary missing for ' + chapter.num);
    assert.ok(chapter.stageId, 'stageId missing for ' + chapter.num);
  }
});

test('the all twenty-eight catalog entries link to the deep-reading articles', () => {
  const expected = [
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
    'articles/23-distilbert-tinybert-knowledge-distillation.html',
    'articles/24-mobilebert-edge-inference.html',
    'articles/25-lora-adalora-bitfit-parameter-efficient-tuning.html',
    'articles/26-modernbert-modern-encoder.html',
    'articles/27-model-compression-quantization.html',
    'articles/28-end-to-end-chinese-nlu-project.html',
  ];
  assert.deepEqual(source.chapters.slice(0, 28).map((chapter) => chapter.file), expected);
});

test('file mode uses the embedded snapshot and HTTP mode falls back to courses.json', () => {
  assert.match(siteScript, /location\.protocol\s*===\s*["']file:/);
  assert.match(html, /id="offline-courses"/);
  assert.match(siteScript, /fetch\(["']courses\.json["']\)/);
});
