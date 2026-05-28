# Clinical Trial Protocol Assistant

A Codex skill for creating and reviewing clinical trial protocols. It is designed for IITs, pre-market drug/device studies, phase IV/post-marketing studies, and RWS/RWE protocols.

The skill uses a gated workflow: it collects only the minimum necessary information first, proposes a protocol section outline, asks the user to confirm included sections, then drafts or reviews section by section.

## Capabilities

- Create new clinical trial protocol outlines and drafts.
- Review existing protocol documents without wholesale rewriting.
- Classify protocol sections as necessary, recommended, optional, or not recommended now.
- Use P0/P1/P2 information gates at the global and section levels.
- Extract user-provided materials from Word, Excel, PowerPoint, PDF, CSV/TSV, text, and Markdown files.
- Use uploaded materials to answer later questions and guide drafting.
- Retrieve supporting evidence from PubMed, ClinicalTrials.gov, and openFDA labels.
- Unify Word document styles for protocol outputs.

## Installation

Install this skill from the GitHub repository:

```bash
codex skills install https://github.com/mattzhangli008-sys/clinical-trial-protocol-assistant.git
```

For heavy file extraction, install Python dependencies from the skill directory:

```bash
python -m pip install -r requirements.txt
```

## Typical Workflow

### Create Mode

1. The skill asks for the research title/question, broad study nature, and whether existing materials are available.
2. It extracts any uploaded materials into a material index.
3. It proposes necessary, recommended, optional, and currently not recommended sections.
4. After the user confirms the section scope, it creates an execution plan.
5. It collects section-level P0/P1/P2 information and drafts one section at a time.
6. After all confirmed sections are complete, it runs cross-section consistency checks and can produce a styled Word document.

### Review Mode

1. The skill extracts the existing protocol and any supporting materials.
2. It builds a document profile and checks section coverage.
3. It identifies missing necessary sections and asks whether to include recommended or optional sections.
4. It creates a review execution plan.
5. It reviews each section using extracted information, external evidence when needed, and restrained suggested edits.

## Material Extraction

The main extraction script is:

```bash
python scripts/extract_materials.py file1.docx file2.xlsx file3.pdf --out material_index.json
```

Optional Markdown view:

```bash
python scripts/extract_materials.py protocol.docx --include-markdown --out material_index.json
```

The extractor prefers stronger libraries when available:

- `python-docx` for DOCX paragraphs and tables.
- `openpyxl` for XLSX/XLSM sheets.
- `python-pptx` for PPTX slide text and tables.
- `pdfplumber`, `PyMuPDF`, then `pypdf` for PDF extraction.
- `markitdown` for optional whole-document Markdown conversion.

If a dependency is unavailable, the script records the fallback or error in the output index.

## Important Notes

This skill is intended to support clinical protocol drafting and review. It does not replace medical, statistical, ethical, regulatory, or legal review by qualified professionals.

For medical, regulatory, endpoint, safety, sample-size, or RWE claims, the skill should use external evidence or user-provided materials instead of relying only on model memory.
