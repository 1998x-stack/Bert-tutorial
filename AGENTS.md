# Repository instructions for coding agents

## Purpose
Maintain a rigorous, independently readable BERT/NLP learning resource. Follow the Olah-style-paper-posts Skill from https://github.com/1998x-stack/Olah-style-posts/tree/main/skills/olah-style-paper-posts for scientific storytelling, evidence, diagrams, MathML, teaching interactions and browser QA.

## Content rules
1. Every article must stand alone. Explain the problem, prior assumptions, mechanism, evidence and consequences; never rely on “the paper introduces...” as a substitute.
2. State inputs, shapes, transformations, outputs, loss positions, masks, normalization axes, train/inference differences and variant scope.
3. Separate original-paper facts, modern variants, implementation choices, derived calculations and toy demonstrations.
4. Every quantitative claim needs a primary source and exact locator. Never merge dev/test, EM/F1, single/ensemble, or leaderboard/table averages.
5. Keep tokenizer and checkpoint paired. Do not generalize English WordPiece behavior to every Chinese BERT checkpoint.
6. Every deep dive needs a matching evidence ledger with source URL, locator, status and verification note.
7. Use original SVGs with title, description, viewBox and meaningful captions. Never copy Colah or Annotated Transformer assets, prose or code.
8. Use native MathML for substantive equations; do not use raw LaTeX delimiters or CDN-rendered math.
9. Demos must work offline, expose an accessible output and clearly label toy data.
10. Do not claim browser acceptance, benchmark reproduction or Pages deployment unless it actually ran and passed.

## Engineering rules
- Preserve root URLs by redirecting upgraded chapters to articles/.
- Keep course metadata in courses.json; update the embedded offline snapshot in index.html in the same commit.
- Shared styles/scripts belong in assets/css and assets/js.
- Run npm test, Python unit tests and npm run test:browser.
- Browser QA must cover 1440, 768, 390 and 360 px; inspect local assets, MathML, interactions, keyboard focus and print.
- Keep CI and deployment claims tied to actual workflow/deployment status.

## Mechanism-first visualization standard (2026-11-22)
- For upgraded deep dives 21–25 and later, use two complementary original, static SVGs per page where beneficial: (a) architecture/attention/loss topology; (b) tensor shapes, propagation, numerical/computation budget or deployment pipeline. Every SVG must remain self-explanatory without JavaScript.
- A complex mechanism needs at least two distinct offline teaching demos, with three or more deterministic states and accessible live output. Interactive states must not alter or misstate the original paper's algorithm; toy inputs must be labeled.
- Include one calculable example with explicit numbers and a unit test, plus limits that distinguish theoretical complexity from measured runtime and source claims from hypothetical values.
- When naming a benchmark number: name model, evaluation metric, task/split, table/section and hardware when speed is involved. Avoid unqualified universal speedup, accuracy or memory claims.
- In CI, browser-check BOTH demos and BOTH figures for every deep dive in the upgraded 21–25 batch; do not silently skip mobile or math rendering.
