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


### 2026-11-21 — Olah-style BERT course upgrade (articles 06–10)
- Scope: replace legacy 06–10 chapter entry pages with compatibility redirects to five standalone articles; keep the 28-chapter catalogue and old root URLs working.
- Article 06: compare BERT pre-generated mask examples and dupe_factor, RoBERTa dynamic masking, whole-word masking, SpanBERT geometric spans and SBO, BERT NSP, ALBERT SOP, and RoBERTa no-NSP sentence packing.
- Article 07: define task data contracts and leakage-safe splits; add a version-pinned Transformers 4.46.3 classification workflow, fast-tokenizer NER alignment, QA offsets/overflow windows, effective batch math and evaluation protocol.
- Article 08: cross-check RoBERTa Tables 1–6 and Appendices B–C; separate dynamic-mask ablation, NSP/input-format changes, data scale, batch/steps, byte-level BPE, dev metrics and leaderboard test ensemble.
- Article 09: document provenance/licensing, cleaning, exact and near-duplicate detection, document-level split, FULL-SENTENCES/DOC-SENTENCES packing and dynamic MLM collators.
- Article 10: derive Adam/AdamW and warmup/linear decay; compare BERT and RoBERTa Base/Large pretraining hyperparameters and fine-tuning search spaces.
- Engineering: add five article-specific SVGs, five evidence ledgers, ten-article directory, root compatibility redirects, catalogue and offline snapshot updates, and extend static/browser test coverage.
- Cross-check sources: BERT arXiv:1810.04805 and official preprocessing/optimizer code; RoBERTa arXiv:1907.11692; ALBERT arXiv:1909.11942; SpanBERT arXiv:1907.10529; Adam arXiv:1412.6980; AdamW arXiv:1711.05101; versioned Transformers 4.46.3 docs.
- Validation: GitHub Actions run 9 passed the Node catalog/content tests, 12 Python reference tests, and HTTP/file:// Playwright checks across all ten article pages and 1440/768/390/360 px viewports; 41 screenshots were uploaded. The first CI run caught a missing Article 07 diagram, which was added before the final passing run. GitHub Pages refresh is checked after merge. No new pretraining or benchmark run is claimed.
- Compatibility: root 06.html–10.html redirect to articles; chapter metadata points to articles; original legacy page bodies remain available in Git history.


### 2026-11-22 — Olah-style deep reading expansion, 11–15
- Scope: standalone articles 11–15, five original SVG diagrams, five evidence ledgers, and root compatibility redirects for 11.html–15.html; preserve 16–28 legacy URLs.
- Chapter 11: distinguish GB/words/token IDs/token exposures; explain Chinchilla's autoregressive compute-optimal evidence without applying its approximate 20:1 ratio mechanically to MLM Encoders.
- Chapter 12: compare FP16/BF16/FP32 precision, AMP unscale-before-clipping, accumulation, optimizer state and activation memory, and distinguish FlashAttention IO complexity from dense arithmetic complexity.
- Chapter 13: compare mBERT cased 104-language checkpoint, smoothed sampling alpha=0.7 and XLM-R 100-language CC-100 corpus; distinguish 2.5TB raw text from training tokens; define zero-shot/translate-train/test protocols.
- Chapter 14: replace unsupported cross-paper latency/throughput and GLUE scoreboard claims with a measurement protocol covering task, tokenizer, split, hardware, batch, latency and Pareto comparison.
- Chapter 15: distinguish generator-masked positions from actual sampled replacements; reproduce RTD label semantics from the official ELECTRA implementation; explain combined objectives, data efficiency and downstream discriminator use.
- New reference implementation: examples/encoder_budget_lab.py and tests/test_encoder_budget_lab.py use Python stdlib for token arithmetic, language sampling, RTD identity labels and masked softmax. They are not a complete neural network or benchmark reproduction.
- Editorial source policy: primary papers and official code are linked per article; evidence-11.json through evidence-15.json record source locators and verification notes.
- Engineering: expand 28-chapter catalog with 15 article URLs; synchronized offline JSON snapshot, articles/index.html, README, article interactions and browser test list.
- Validation: pending CI and browser checks for this branch. Do not claim deployment or QA success before inspecting run results.

### 2026-11-22 — Olah-style deep dives 16–20 (XLNet / MPNet / ALBERT / DeBERTa / Chinese WWM)
- Scope: replace legacy root chapters 16–20 with redirects to independently readable technical articles in articles/; preserve 21–28 legacy paths and existing links.
- Scientific story: XLNet permutation and two-stream attention prevent target-content leakage; MPNet predicts conditionally with complete masked-position clues; ALBERT factorizes embeddings, shares layer weights and uses SOP; DeBERTa disentangles c2c/c2p/p2c with directed relative offsets; Chinese WWM aligns word segmentation with token-level MLM labels and distinguishes ERNIE, MacBERT and glyph/pinyin signals.
- Evidence: original papers and official reference implementations linked with locators in evidence-16.json through evidence-20.json. All toy-demo scores and parameter counts labeled as calculations, not reproduced benchmarks. ALBERT Table 4 data explicitly scoped to the original table.
- Information architecture: 28-chapter canonical courses.json kept synchronized with the file:// embedded index.html catalog; updated course homepage, 20-card article reading directory, README and compatibility redirects.
- Technical artifacts: five standalone SVG diagrams with title/description, five offline deterministic demos, standard-library Python implementation examples and tests for prediction masks, parameter decomposition, relative offsets and whole-word label groups.
- Validation policy: CI for Node, Python and Chromium at widths 1440/768/390/360 remains the release gate; do not claim success without workflow evidence. Verify GitHub Pages workflow after merging.
- Rollback: revert the final squash merge to restore prior chapters and catalogue routes if a regression is detected.

### 2026-11-22 — Olah-style deep dives 21–25, visual-first second-round expansion
- Scope: new standalone Chinese analyses for Longformer/BigBird, SimCSE, DistilBERT/TinyBERT, MobileBERT and LoRA/AdaLoRA/BitFit; 21.html–25.html become backward-compatible redirects. Other 26–28 legacy paths remain.
- Why: previous short drafts lacked deep attention graph topology, explicit tensor/loss semantics, numerical budgets, and individual data/hardware limits. Each replacement is independently readable: question → mechanism → shapes/formula → example → evidence → limits.
- Visualization: two independent original SVGs per article (ten total), showing attention matrices and distance propagation; SimCSE positive/negative matrix and vector geometry; KD paths and temperature/layer mapping; MobileBERT internal bottleneck and deployment flow; PEFT weight update and rank/merge budget.
- Interactivity: two offline deterministic 3-state demos per article (ten demos total). Results are toy examples, not trained model output. Shared assets/css/course.css and assets/js/site.js handle focus and progress; no CDN.
- Reproducibility: examples/efficient_encoder_lab.py (standard library) and tests/test_efficient_encoder_lab.py exercise mask adjacency, stable softmax and InfoNCE, KL distillation, bottleneck projections, INT8, LoRA parameter counts and fixed rank allocation. Tests are mechanism checks, not actual benchmark training.
- Evidence: articles/evidence-21.json…25.json include at least six claim-to-primary-source mappings per chapter. Original Longformer, BigBird, SimCSE, DistilBERT, TinyBERT, MobileBERT, LoRA, AdaLoRA and BitFit papers cross-checked with research repository/implementation docs. Do not generalize paper results to different hardware or task metrics.
- Integration: 28-chapter courses.json and index.html file:// snapshot kept identical, 25 cards in articles/index.html, README and AGENTS updated. Automated checks expand to 25 article pages, two diagrams and both demos in the newest five; Playwright at 1440, 768, 390, 360 px.
- Release policy: passing GitHub Actions CI and subsequent GitHub Pages deployment required before claiming publication; site HTTP reachability must be independently checked where possible. Revert squash merge to roll back.
