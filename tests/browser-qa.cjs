const fs = require('node:fs');
const http = require('node:http');
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const { chromium } = require('playwright');

const root = path.resolve(__dirname, '..');
const artifacts = path.join(root, 'artifacts', 'browser-qa');
fs.mkdirSync(artifacts, { recursive: true });

const mimeTypes = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.md': 'text/markdown; charset=utf-8',
};

function startServer() {
  const server = http.createServer((request, response) => {
    const pathname = decodeURIComponent(new URL(request.url, 'http://127.0.0.1').pathname);
    const relative = pathname === '/' ? 'index.html' : pathname.replace(/^\/+/, '');
    const filePath = path.resolve(root, relative);
    if (filePath !== root && !filePath.startsWith(root + path.sep)) {
      response.writeHead(403).end('Forbidden');
      return;
    }
    fs.readFile(filePath, (error, content) => {
      if (error) {
        response.writeHead(404).end('Not found');
        return;
      }
      response.writeHead(200, {
        'Content-Type': mimeTypes[path.extname(filePath)] || 'application/octet-stream',
        'Cache-Control': 'no-store',
      });
      response.end(content);
    });
  });
  return new Promise((resolve) => server.listen(0, '127.0.0.1', () => {
    const address = server.address();
    resolve({ server, baseUrl: 'http://127.0.0.1:' + address.port });
  }));
}

async function main() {
  const serverInfo = await startServer();
  const server = serverInfo.server;
  const baseUrl = serverInfo.baseUrl;
  const browser = await chromium.launch({ headless: true });
  const errors = [];
  try {
    const context = await browser.newContext();
    const page = await context.newPage();
    page.on('pageerror', (error) => errors.push('pageerror: ' + error.message));
    page.on('console', (message) => {
      if (message.type() === 'error') errors.push('console: ' + message.text());
    });

    await page.goto(baseUrl + '/', { waitUntil: 'networkidle' });
    await page.locator('#chapter-grid .chapter-card').first().waitFor();
    const initialCount = await page.locator('#chapter-grid .chapter-card').count();
    if (initialCount !== 28) throw new Error('homepage rendered ' + initialCount + ' chapters, expected 28');

    await page.locator('#chapter-search').fill('WordPiece');
    await page.waitForFunction(() => document.querySelectorAll('#chapter-grid .chapter-card').length > 0);
    const searchCount = await page.locator('#chapter-grid .chapter-card').count();
    if (searchCount >= 28) throw new Error('catalog search did not filter results');

    await page.locator('#reset-filters').click();
    await page.locator('#stage-filter').selectOption('bert-core');
    const stageCount = await page.locator('#chapter-grid .chapter-card').count();
    if (stageCount !== 4) throw new Error('BERT core stage rendered ' + stageCount + ' chapters, expected 4');

    await page.locator('#reset-filters').click();
    const firstToggle = page.locator('#chapter-grid .completion-toggle').first();
    await firstToggle.click();
    if (await firstToggle.getAttribute('aria-pressed') !== 'true') {
      throw new Error('chapter completion toggle did not update');
    }
    await page.screenshot({ path: path.join(artifacts, 'homepage-desktop.png'), fullPage: true });

    const articlePages = [
      'articles/01-pretraining-evolution.html',
      'articles/02-transformer-encoder.html',
      'articles/03-bert-pretraining.html',
      'articles/04-bert-finetuning-evidence.html',
      'articles/05-wordpiece-inputs.html',
    ];
    for (const articlePath of articlePages) {
      await page.goto(baseUrl + '/' + articlePath, { waitUntil: 'networkidle' });
      await page.locator('.article-main h1').waitFor();
      const h1Count = await page.locator('.article-main h1').count();
      if (h1Count !== 1) throw new Error(articlePath + ': expected exactly one H1');
      const mathCount = await page.locator('math').count();
      if (articlePath !== articlePages[0] && mathCount === 0) {
        throw new Error(articlePath + ': expected a rendered MathML formula');
      }

      if (articlePath === articlePages[4]) {
        await page.locator('[data-wordpiece-input]').fill('playing');
        await page.locator('[data-wordpiece-run]').click();
        const output = await page.locator('[data-wordpiece-output]').textContent();
        if (!output.includes('##ing')) throw new Error('WordPiece toy tokenizer did not segment playing');
      } else {
        const demoOutput = page.locator('[data-demo-output]');
        const buttons = page.locator('[data-demo-action]');
        const before = await demoOutput.textContent();
        await buttons.nth(1).click();
        const after = await demoOutput.textContent();
        if (before === after) throw new Error(articlePath + ': demo interaction did not change output');
      }

      for (const width of [1440, 768, 390, 360]) {
        await page.setViewportSize({ width, height: 900 });
        const dimensions = await page.evaluate(() => ({
          viewport: document.documentElement.clientWidth,
          content: document.documentElement.scrollWidth,
        }));
        if (dimensions.content > dimensions.viewport + 1) {
          throw new Error(articlePath + ': horizontal overflow at ' + width + 'px (' + dimensions.content + 'px)');
        }
        await page.screenshot({
          path: path.join(artifacts, path.basename(articlePath, '.html') + '-' + width + '.png'),
          fullPage: true,
        });
      }
    }

    const offlinePage = await context.newPage();
    offlinePage.on('pageerror', (error) => errors.push('file pageerror: ' + error.message));
    await offlinePage.goto(pathToFileURL(path.join(root, 'index.html')).href, { waitUntil: 'load' });
    await offlinePage.locator('#chapter-grid .chapter-card').first().waitFor();
    const offlineCount = await offlinePage.locator('#chapter-grid .chapter-card').count();
    if (offlineCount !== 28) throw new Error('file:// homepage rendered ' + offlineCount + ' chapters, expected 28');

    if (errors.length) throw new Error(errors.join('\n'));
    console.log('Browser QA passed: homepage HTTP + file://, search/filter/progress, five article interactions, MathML, and 1440/768/390/360px layouts.');
  } finally {
    await browser.close();
    await new Promise((resolve) => server.close(resolve));
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
