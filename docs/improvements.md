### 2026-11-06 12:22 UTC — ChatGPT Portfolio Iteration
- Run ID: portfolio-20261106T122245-b7e2
- Repo / Base SHA: 1998x-stack/Bert-tutorial / 37e22589fbb30dca81ab155032dc41174e3d5396
- Historical context: Default branch docs/improvements.md returned 404; no prior history. PR search returned none; two commits observed.
- Product problem & expected user value: README instructs opening index.html directly; file:// fetch of courses.json can fail, hiding all 28 chapters. Offline opening should show the complete catalog.
- Engineering diagnosis & evidence: index.html unconditionally fetched courses.json; browser file origin can block it. HTTP behavior must remain unchanged.
- Options & decision: P2 offline load (benefit 5, correctness 4, evidence 5, testability 3, cost 2, risk 2 = 13); P2 error recovery (3+2+4+3-2-2=8); P3 schema validation (2+3+3+3-2-2=7). Chose offline load.
- Changes: index.html embeds the canonical JSON snapshot and uses it only for file://; HTTP retains fetch. tests/offline-catalog.test.cjs checks data parity, chapter links, mode routing.
- Validation: C: source/JSON structural assertions run in connector JavaScript; D: Node tests written but not executed in project runtime; browser E2E not run. No A-grade behavior test or CI claim.
- Security & regression review: No credentials or deployment changes. Static embedded JSON uses script type application/json; HTTP path preserved. Risk of data drift mitigated by parity test.
- Risk & rollback: Offline JSON duplication requires parity on future updates; close Draft PR or revert commits to roll back.
- Follow-up: Run node --test tests/offline-catalog.test.cjs and Chrome file:// plus HTTP browser E2E before merging.
- Commit: 105ae74b46719100ba06ade4dec0374ae27109cf (pre-history-finalization HEAD)
- PR: https://github.com/1998x-stack/Bert-tutorial/pull/1


### 2026-11-21 — Olah-style BERT course upgrade (five-article batch)
- Repository / base: 1998x-stack/Bert-tutorial / cd86fe1987239b1b67071e3dca4915a803b7a668.
- Audit findings: the first five articles were short drafts with a repeated generic SVG, no runnable learning interactions, sparse technical derivations, generic evidence notes, and no browser E2E gate. The homepage exposed the old flat chapter list without a course route or progress model.
- Scope: keep the existing 28 chapter assets and PDF files; upgrade the first five deep reads, homepage, catalog metadata, evidence records, local assets, examples, tests, and CI. Root 01.html–05.html remain as redirect compatibility pages; 06.html–28.html retain their existing paths.
- Content changes:
  - 01: distinguish static embeddings, ELMo's independently trained directional LMs, GPT-1's causal LM, and BERT's deep bidirectional encoder.
  - 02: derive Q/K/V shapes, scaled attention, softmax axis, multi-head, FFN, post-LN, positional signals, masks, and sequence-length cost.
  - 03: define the 15% target set and 80/10/10 replacement denominator, MLM loss positions, NSP sampling, corpus sizes, and original training schedule.
  - 04: document classification, sentence-pair, NER and QA heads; qualify GLUE/SQuAD/SWAG numbers; include the original NSP ablation with table locator.
  - 05: distinguish WordPiece inference from vocabulary training, BPE from WordPiece, English normalization from Chinese character preprocessing, and IDs from input fields.
- Engineering changes: introduce assets/css, assets/js, assets/diagrams, examples, content evidence ledgers, Node/Python tests, Playwright browser checks, and a GitHub Actions workflow. The homepage has search, stage filters, local progress, and a file:// catalog fallback.
- Cross-check sources: BERT arXiv:1810.04805 Sections 1–5 and Appendices A.1–A.5; Transformer arXiv:1706.03762; ELMo arXiv:1802.05365; RoBERTa arXiv:1907.11692; Google Research BERT tokenizer implementation; Sennrich et al. arXiv:1508.07909; FlashAttention arXiv:2205.14135.
- Validation status at authoring time: source-level consistency checks and browser/Python test suites are added; actual CI results must be read from the new workflow run before claiming browser acceptance. No benchmark training run was performed.
- Deployment: keep GitHub Pages on the repository root; no custom domain, secret, permission, or deployment setting is changed.
- Follow-up: migrate chapters 06–28 in later batches, keeping the same standalone-article and evidence-ledger requirements.
