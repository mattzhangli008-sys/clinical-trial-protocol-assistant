# Materials and Word Processing

## Materials Intake

At first intake and whenever new files are uploaded, extract them into a material index before continuing.

Supported first-pass formats:

- `.docx`
- `.xlsx`, `.xlsm`
- `.csv`, `.tsv`
- `.pptx`
- `.pdf`
- `.txt`, `.md`

Use `scripts/extract_materials.py` for multi-file extraction. The index should preserve:

- source file path
- file type
- paragraphs/sheets/slides/pages/tables
- source location labels
- extracted text

Use the material index to answer P0/P1/P2 questions before asking the user. If the material gives a likely answer, present it as an assumption to confirm.

For published installs, install the skill dependencies first:

```bash
python -m pip install -r requirements.txt
```

The extractor prefers stronger format-specific libraries when available:

- `python-docx` for DOCX paragraphs and tables, with zip/XML fallback.
- `openpyxl` for XLSX/XLSM sheets.
- `python-pptx` for PPTX slide text and tables, with zip/XML fallback.
- `pdfplumber` for PDF text and tables, then `PyMuPDF`, then `pypdf`.
- `markitdown` for an optional whole-document Markdown view.

## Reading Word

Use `scripts/extract_docx.py` for first-pass extraction of:

- paragraphs
- headings
- tables
- rough character counts
- source locations

For advanced comments/redlines/render QA, use the built-in `documents` skill/plugin.

## Editing Word

Preserve original files. Always write to a new output file.

Review mode:

- Preserve source structure.
- Prefer comments or small suggested edits.
- Do not accept/reject existing tracked changes unless user asks.

Create mode:

- Generate clean protocol DOCX only after section content is confirmed and saved into the protocol Markdown source file.
- Use the complete protocol Markdown file as the only content source for DOCX generation. Do not ask the model to recreate, expand, summarize, or reinterpret confirmed sections while building Word.
- If the Markdown file is incomplete or missing confirmed sections, stop and update the Markdown source before creating DOCX.
- Keep `[待确认]`, `[TBD]`, and unresolved placeholders visible.

## Style Unification

Use `scripts/style_unify_docx.py` for baseline style cleanup.

Minimum style scope:

- page size/margins
- title and heading styles
- body font/spacing
- tables
- placeholders
- comments/review report severity labels where possible

Style unification must not change professional content.
