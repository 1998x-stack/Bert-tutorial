# BERT mechanics examples

These examples are deliberately small and dependency-free. They are designed to
make input construction and attention math inspectable, not to reproduce a
pretrained checkpoint.

Run the unit tests from the repository root:

\`\`\`bash
python -m unittest discover -s tests -p "test_*.py"
\`\`\`

Scope and limitations:

- wordpiece_tokenize implements longest-match-first for one already-normalized
  word and a supplied vocabulary. It does not implement the official BasicTokenizer,
  language-specific normalization, or WordPiece vocabulary training.
- build_bert_inputs creates the familiar special-token layout and aligned
  arrays from already-tokenized inputs. The vocabulary is supplied by the caller.
- scaled_dot_product_attention demonstrates one query and one head using Python
  lists. It is not a high-performance tensor kernel.
