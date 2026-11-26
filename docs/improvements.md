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

### 2026-11-22 — Final 26–28: ModernBERT, compression and Chinese NLU capstone
- Base main a1738f8f939dbc286def06312723b94144351f42 after PR #8; preserve published 21–25 each with two SVGs and two interactive labs rather than replacing with redundant parallel drafts.
- Add 26 ModernBERT RoPE/GeGLU/alternating local-global attention; 27 quantization/pruning/latency auditing; 28 Chinese NLU end-to-end data contract, masked metrics, validation, optional real BERT training and release checklist. Each independent article has accessible MathML, original diagram, offline teaching interaction and located research evidence.
- Executable 60-row synthetic Chinese classification example: stdlib character n-gram Naive Bayes, train/dev/test contracts, group/ID/text leakage gates, Macro F1 and export with unittest. Optional real Encoder script requires user-provided local pretrained checkpoint, pinned packages, and is not run in CI; the synthetic score is not an NLU benchmark.
- Canonical 28-chapter courses.json synchronized exactly with homepage file:// snapshot; 28 article cards, README, redirects and tests to 28. Fix chapter 25→26 navigation and MathML arithmetic formula denominator.
- Validation: pending CI browser+Node+Python and Pages workflow verification on final publication.

### 2026-11-22 — Dual-visualization parity for deep dives 26–28
- Scope: bring the final batch (26 ModernBERT, 27 compression/quantization, 28 Chinese NLU) up to the mechanism-first standard already applied to 21–25: two complementary original SVGs and two offline deterministic demos per page.
- Diagrams added: 26-unpadding-packing-budget.svg (token-slot vs token-pair ledger); 27-quantization-error-sparsity-ledger.svg (affine quantization error path, weight-only vs W+A INT8 kernels, dense-vs-sparse storage); 28-nlu-tensor-metric-ledger.svg (input_ids/Encoder/pooled/logits shapes plus a three-class confusion matrix and macro-F1 calculation).
- Demos added: 26 padding/unpadding/packing slot ledger; 27 FP32/INT8/80%-zeroed weight ledger; 28 tensor-contract / metric / split-isolation ledger. Each has three distinct states; all are toy arithmetic, not hardware measurements.
- Calculable examples: examples/modern_encoder_lab.py (padding_budget, attention_pair_budget, weight_bytes, linear_quantize/dequantize, macro_f1) with tests/test_modern_encoder_lab.py asserting explicit numbers (384/208/176, 20736/49152, 400MB/100MB, half-scale quantization error, macro-F1 zero-division convention).
- Gates fixed: tests/browser-qa.cjs demo loop clicked the already-active default button and would throw even on 21–25; it now clicks the first unpressed control, and the two-demo/two-figure/focus check covers indices 20–27 (through chapter 28). tests/quality.test.cjs adds a 26–28 dual-diagram/dual-demo assertion mirroring the 21–25 test.
- Validation: validate.py reports no new failures (the only remaining note is the skill validator's inline-SVG expectation versus this repo's standalone-<img> SVG convention, which all 28 pages share); node --test quality.test.cjs 14/14 pass; python unittest 70/70 pass; Playwright served over HTTP verified 2 demos respond, 2 figures load, no JS errors and no horizontal overflow at 1440/390/360 px for 26, 27, 28.
- Not verified here: `npm test`/`npm run test:browser` were not executed locally because node_modules is absent; the Playwright node suite must be read from the next GitHub Actions run before claiming browser acceptance.
- Rollback: revert the four commits on this branch to restore the single-diagram versions.

### 2026-11-25 — Correctness and mechanism-first pass over foundational deep dives 01–06
- Scope: chapters 01, 02, 03, 05, 06 gain a second, complementary inline SVG figure (mechanism/tensor-shape or sample-generation ledger) so each page pairs an orientation diagram with a computation/ledger view; chapter 01 and chapter 02 add a third deterministic demo state.
- Correctness fixes: chapter 13's language-sampling formula had a three-child `mfrac` (numerator `n_l^α`, a `munder` sum, and `n_j^α`) which is invalid MathML; the denominator is now wrapped in an `mrow`. A duplicated `tabindex` was removed from the same scroll region. Literal Markdown emphasis (`**…**`) in callouts in chapters 01, 05, 06, 07 now renders as `<strong>`.
- New figures: 01 static-vs-contextual representation functions; 02 encoder single-layer shape ledger ([B,T]→[B,T,d]→[B,h,T,dh]→[B,h,T,T]→[B,T,d]→FFN); 03 pre-training output-branch ledger (MLM on selected positions, NSP on [CLS]); 05 tokenizer/checkpoint pairing (same string, three vocabularies); 06 static vs dynamic masking sample-generation timing. All are original, self-contained inline SVGs with `viewBox`, `title`, `aria-labelledby`; the numeric values shown are labelled teaching examples, not checkpoint configs or benchmarks.
- Demos: chapter 01 distinguishes river/finance/verb senses of “bank”; chapter 02 adds a padding-mask state (k4 masked out of every query row) alongside bidirectional and causal masks.
- Engineering: shared `.article-body figure svg` CSS keeps inline SVG responsive; a new Node test asserts chapters 01/02/03/05/06 carry two figures with accessible inline SVG.
- Validation on this branch: validate.py passes for the five upgraded pages (the only remaining repo-wide note is the known inline-`<svg>` validator expectation versus the standalone-`<img>` convention shared by all 28 pages); `node --test tests/quality.test.cjs` 15/15; `python -m unittest discover -s tests` 70/70. HTTP-served Playwright (local Chromium, not committed) reports no JS errors, no broken images and no horizontal overflow at 1440/768/390/360 px for the changed pages.
- Not verified here: the repo's `tests/browser-qa.cjs` was not run because node_modules is absent; the bundled `scripts/browser_check.py` loads pages with `set_content`, so this repo's relative CSS/JS/images never load and its failures are tool artifacts, not page defects.
- Rollback: revert this batch of commits to restore the single-figure versions.

### 2026-11-26 — Mechanism-first parity for fine-tuning deep dive 07
- Scope: bring chapter 07 (BERT fine-tuning practice) up to the dual-figure/dual-demo standard already used by 01–06 and 21–28.
- New figure: an inline SVG label-alignment ledger showing how word-level tags (I / love / Beijing → O / O / B-LOC) map onto WordPiece sub-tokens ([CLS] I love Bei ##jing [SEP]) after `word_ids()`; the teaching split is labelled as an example, not a specific checkpoint's vocabulary.
- New demo: a three-state ledger for dynamic padding (288 slots / 136 effective / 152 empty), optimizer steps (ceil(3200/32)×3 = 300) and label alignment (-100 / O / O / B-LOC / -100 / -100). All numbers are labelled teaching arithmetic.
- Calculable example: examples/finetuning_contract_lab.py (`padding_budget`, `optimizer_steps`, `align_word_labels`) with tests/test_finetuning_contract_lab.py asserting the exact values (288/136/152, 300, ceil rounding, alignment list). Standard library only; not a training run or benchmark.
- Validation: validate.py passes chapter 07 (2 figures, inline SVG, 2 demos, MathML scroll regions); `node --test tests/quality.test.cjs` 15/15; `python -m unittest discover -s tests` 76/76; HTTP-served Chromium QA reports no JS errors, no broken images, nonzero inline-SVG geometry and no horizontal overflow at 1440/390/360 px, and both demos change output on click.
- Not verified here: the repo's Node `tests/browser-qa.cjs` was not run because node_modules is absent; the bundled `scripts/browser_check.py` loads pages via set_content, so its relative-asset failures are tool artifacts rather than page defects.

### 2026-11-26 — Dual-figure/dual-demo parity for RoBERTa deep dive 08
- New figure: an inline SVG comparing the four RoBERTa input organisations (SEGMENT-PAIR+NSP vs FULL-SENTENCES vs DOC-SENTENCES) at the token-sequence level, showing where the extra `[SEP]` and the document boundary fall. Teaching labels only; the comparison is attributed to RoBERTa §4.2 and Table 2.
- New demo: a three-state budget ledger for batch (256 vs 8K sequences), the Table 4 dev SQuAD 2.0 F1 staircase (87.3 → 87.7 → 88.7 → 89.4) and the 160GB corpus composition (16 + 76 + 38 + 31 GB). Every value is labelled as a paper-reported dev result.
- Calculable example: added `tokens_per_update` to examples/finetuning_contract_lab.py, with tests asserting 256×512 = 131,072, 8192×512 = 4,194,304 and the 32× ratio.
- Validation: validate.py passes chapter 08 (2 figures, inline SVG, 2 demos); quality tests 15/15; python unittest 77/77; HTTP-served Chromium QA shows no JS errors, no broken images, nonzero inline SVG and no horizontal overflow at 1440/390/360 px, both demos changing output.

### 2026-11-26 — Dual-figure/dual-demo parity for pretraining-data deep dive 09
- New figure: an inline SVG shingle-set ledger with a Jaccard example (A={A1..A5}, B={B1..B5}, three shared shingles, ∩=3, ∪=7, J=3/7≈0.43), explaining why MinHash/LSH is only a candidate-recall step before Jaccard confirmation.
- New demo: a three-state ledger for Jaccard (3/7, identical copies = 1, unrelated ≈ 0), the 80/10/10 MLM split with the selected-position denominator (100 → 80/10/10) and sequence packing utilisation (1000+300 tokens into 1024-length slots → 1300/2048 ≈ 63.5%). All labelled teaching arithmetic.
- Calculable example: added `jaccard`, `mlm_replace_counts` and `packing_utilization` to examples/finetuning_contract_lab.py with tests asserting 3/7, 1.0, the 80/10/10 and 12/1/2 splits, and 1300/2048.
- Validation: validate.py passes chapter 09 (2 figures, inline SVG, 2 demos); quality tests 15/15; python unittest 80/80; HTTP-served Chromium QA: no JS errors, no broken images, nonzero inline SVG, no overflow at 1440/390/360 px, both demos change output.

### 2026-11-26 — Dual-figure/dual-demo parity for optimization deep dive 10
- New figure: an inline SVG contrasting the correct vs incorrect placement of `optimizer.step()`/`scheduler.step()` under gradient accumulation A=4 — the scheduler must advance once per optimizer update, not once per micro-batch.
- New demo: a three-state ledger for effective batch (8×4×4=128, ceil(50000/128)=391 updates), linear warmup/decay (5e-5 at t=5,000; ≈5.05e-5 at t=500,000) and the AdamW per-step factor (1−1e-6 = 0.999999; ≈0.99990 over 100 steps). All labelled teaching arithmetic except the stated scheduler formula.
- Calculable example: added `effective_batch`, `linear_warmup_lr` and `adamw_decay_factor` to examples/finetuning_contract_lab.py with tests asserting 128/391, the two LR values and the decay factor.
- Validation: validate.py passes chapter 10 (2 figures, inline SVG, 2 demos, all display MathML in focusable scroll regions); quality tests 15/15; python unittest 83/83; HTTP-served Chromium QA: no JS errors, no broken images, nonzero inline SVG, no overflow at 1440/390/360 px, both demos change output.

### 2026-11-26 — Dual-figure/dual-demo parity for scaling deep dive 11
- New figure: an inline SVG units ledger showing that corpus bytes (13GB cleaned Books+Wiki), words (3.3B English words), WordPiece token count and D_seen (processed-token exposures) are four different quantities connected by three conversions, none of which is an equality.
- New demo: a three-state ledger for the compute order-of-magnitude C≈6ND (110M × 32.768B ≈ 2.162688e19), repeated-epoch D_seen vs D_unique (10B unique, 2 epochs → 20B seen) and equal-compute grid points (50M×20B and 200M×5B both ≈ 6e18). All labelled teaching estimates.
- Calculable example: added `flops_order` and `repeated_exposure` to examples/encoder_budget_lab.py, and referenced the existing `token_exposures`; tests/test_encoder_budget_lab.py asserts 2.162688e19, the equal-compute equality and 10B/20B.
- Validation: validate.py passes chapter 11 (2 figures, inline SVG, 2 demos); quality tests 15/15; python unittest 85/85; HTTP-served Chromium QA: no JS errors, no broken images, nonzero inline SVG, no overflow at 1440/390/360 px, both demos change output.

### 2026-11-26 — Dual-figure/dual-demo parity for stability deep dive 12
- New figure: an inline SVG memory ledger with two panels — per-parameter AdamW state (4+4+4+4 = 16 B, excluding activations/copies) and one-head attention score elements (T=512/1024/2048 → 262,144/1,048,576/4,194,304, ×4 per doubling).
- New demo: a three-state ledger for optimiser-state bytes (110M × 16 B ≈ 1.76 GB), the T² growth (×4 per doubling) and AMP loss scaling (1e-5 × 65536 = 0.65536, unscale before clipping). All labelled order-of-magnitude estimates.
- Calculable example: added `param_memory_bytes`, `attention_matrix_elements` and `scaled_gradient` to examples/encoder_budget_lab.py with tests asserting 1.76e9, the four element counts, the ×4 ratio and the scale round-trip.
- Validation: validate.py passes chapter 12 (2 figures, inline SVG, 2 demos, display MathML in focusable scroll regions); quality tests 15/15; python unittest 88/88; HTTP-served Chromium QA: no JS errors, no broken images, nonzero inline SVG, no overflow at 1440/390/360 px, both demos change output.

### 2026-11-26 — Dual-figure/dual-demo parity for multilingual deep dive 13
- New figure: an inline SVG comparing zero-shot, translate-train and translate-test data flow, showing which end (training or test) introduces the target language and that no protocol uses target-language labels.
- New demo: a three-state protocol ledger for zero-shot, translate-train and the XLM-R reported gains (XNLI +14.6 pts, MLQA F1 +13 pts, NER F1 +2.4 pts, all per the paper's protocol) plus the 2.5 TB-vs-tokens unit clarification. Also referenced the existing `language_sampling` helper in the temperature-sampling section.
- Calculable example: the sampling ratios (100:1, 25.12:1, 1:1) are computed by examples/encoder_budget_lab.py `language_sampling` and covered by tests/test_encoder_budget_lab.py.
- Validation: validate.py passes chapter 13 (2 figures, inline SVG, 2 demos); quality tests 15/15; python unittest 88/88; HTTP-served Chromium QA: no JS errors, no broken images, nonzero inline SVG, no overflow at 1440/390/360 px, both demos change output.

### 2026-11-26 — Dual-figure/dual-demo parity for model-selection deep dive 14
- New figure: an inline SVG Pareto diagram (macro-F1 vs p95 latency) with candidates A and B on the frontier and C dominated by B. Coordinates are explicitly labelled as schematic placeholders, not measured values.
- New demo: a three-state ledger for weight-only bytes (100M × 4 B = 400 MB FP32; ×1 B = 100 MB INT8; 4× ratio; excludes activations/workspace), steady-state throughput (1000/20 s = 50, 2000/20 s = 100 samples/s) and Pareto dominance for A/B/C. All labelled teaching arithmetic/schematic.
- Calculable example: added `throughput` and `dominates` to examples/encoder_budget_lab.py (reusing `param_memory_bytes`), with tests asserting 50/100 samples/s and the A/B/C dominance relations.
- Validation: validate.py passes chapter 14 (2 figures, inline SVG, 2 demos, display MathML in a focusable scroll region); quality tests 15/15; python unittest 90/90; HTTP-served Chromium QA: no JS errors, no broken images, nonzero inline SVG, no overflow at 1440/390/360 px, both demos change output.
