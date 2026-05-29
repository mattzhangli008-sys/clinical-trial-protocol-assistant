---
name: clinical-trial-protocol-assistant
description: Create or review clinical trial protocols, including IIT, pre-market drug/device studies, phase IV/post-marketing studies, and RWS/RWE protocols. Use for protocol generation, protocol review, section planning, evidence-backed drafting, Word DOCX reading/editing, and Word style unification.
---

# Clinical Trial Protocol Assistant

## Purpose

Use this skill to create or review clinical trial protocols. It supports two workflows:

- **Create mode:** collect minimal P0 information, propose a section outline, get user confirmation, then generate sections one by one.
- **Review mode:** extract information from an existing document, check section coverage, get user confirmation on missing/recommended/optional sections, then review sections one by one.

Use external evidence and Word tooling when needed. Do not rely only on model memory for medical, safety, regulatory, endpoint, trial-design, sample-size, or RWE claims.

## Output Style

- When drafting protocol content in Chinese, use Chinese numeric section headings such as `一、二、三、四` for generated protocol sections and subsections. Do not use `A、B、C、D` as generated section numbering. Internal module IDs such as `A1`, `B1`, and `C2` may be used only in planning tables or workflow status blocks.
- If generated content uses literature or external records retrieved during the task, add citation markers immediately after the supported sentence or paragraph, using bracketed numeric markers such as `[1]`, `[2]`. Include a matching references list or evidence record in the same response or final document section. Do not add citation markers for unsupported claims, and do not fabricate citations.

## First Decision

Determine the mode:

1. **Create:** user wants a new protocol, outline, or section draft.
2. **Review:** user provides an existing protocol and asks for review, audit, optimization, comments, or suggestions.
3. **Word only:** user only asks to extract, restyle, comment, redline, or format a protocol document.

Read references as needed:

- `references/workflows.md` for create/review workflow details.
- `references/section-map.md` for section modules and priority rules.
- `references/information-gates.md` for global and section-level P0/P1/P2 rules.
- `references/evidence-sources.md` for PubMed, ClinicalTrials.gov, labels, regulatory, RWE, and internal evidence triggers.
- `references/word-processing.md` for DOCX extraction, editing, commenting, redlining, and style unification.

## User Materials Intake

On the first user-facing question in create mode, explicitly ask whether the user has existing materials that can support the protocol, including Word, Excel, PowerPoint, PDF, text/Markdown, images, drug labels, investigator brochures, prior protocols, SAPs, ethics templates, visit schedules, CRFs, or data dictionaries.

User materials are not a one-time input. If the user uploads or mentions new files at any later point, pause the current drafting/review step, extract the materials, update the material index, and then resume. Use uploaded materials to:

1. answer global and section-level P0/P1/P2 questions when possible;
2. support section drafting, review findings, and Word outputs;
3. reduce repeated questions to the user.

Prefer `scripts/extract_materials.py` for multi-file extraction. Preserve source paths and locations so later claims can cite the supporting material.

For published installs, install Python dependencies from `requirements.txt` before heavy material extraction:

```bash
python -m pip install -r requirements.txt
```

The extractor uses stronger libraries when available (`pdfplumber`, `PyMuPDF`, `python-pptx`, `python-docx`, `openpyxl`, `markitdown`) and records fallbacks or missing dependencies in the material index.

## Create Mode

Do not generate a full protocol immediately after the user confirms the outline. After outline confirmation, the next response must build an execution plan and open the first section information gate. A full-document draft is only allowed after all included sections have passed their section gates, unless the user explicitly requests fast-track full drafting and accepts skipped section confirmations.

1. Ask only global P0 questions: task, research title/question, broad study nature, and whether source materials exist.
2. Infer P1/P2 items from the title/materials when possible; ask only if the inference changes the outline.
3. Propose an outline grouped as **necessary**, **recommended**, **optional**, and **not recommended now**.
4. Ask the user to confirm which sections to include.
5. Build an execution plan and show it to the user. Adding sections must always remain available.
6. For each section, run a section information gate:
   - If section P0 is missing, ask before drafting.
   - If P1 is inferred, confirm with the user.
   - If P2 is missing, draft with `[待确认]` only if acceptable.
7. Check `external_data_needs` for the section. Retrieve evidence when required or recommended.
8. Draft the section with citation markers for any searched literature or external records used, then ask the user to confirm, revise, or regenerate.
9. After all included sections are confirmed, run cross-section consistency checks.
10. If delivering Word, run Word style unification.

## Review Mode

Do not jump from a document to final review findings. After extraction, first show the document profile and section coverage review; after user confirms the review scope, build a review execution plan and open the first section review gate.

1. Extract the document structure and text. Use `scripts/extract_docx.py` for `.docx`.
2. Extract global P0/P1/P2 information from the document. Ask the user only for missing or unclear items that block review.
3. Map document headings to the section map.
4. Identify missing necessary sections; ask whether to add recommended or optional sections.
5. Build a review execution plan. Adding review sections/dimensions must always remain available.
6. For each section, extract section P0/P1/P2 answers from the source text:
   - Ask the user only for missing or unclear answers that affect the section review.
   - If P2 is missing, do not block review; flag it as a recommendation.
   - If P0 is missing and user cannot answer, provide a limited review with limitations.
7. Use external evidence to verify claims where needed; cite searched literature or external records with inline markers when they support review findings; do not rewrite the user's text wholesale.
8. Output findings as issue, source evidence, risk, recommendation, and small suggested edit.
9. If delivering Word, preserve the user's structure and run style unification or comments/redlines only as requested.

## Word Capabilities

This skill can read and edit Word documents. Prefer scripts for repeatable document operations:

- `scripts/extract_materials.py`: extract text/tables from docx, xlsx, csv, pdf, pptx, txt, and md into one material index.
- `scripts/extract_docx.py`: extract headings, paragraphs, tables, comments/tracked-change text where available.
- `scripts/style_unify_docx.py`: apply baseline protocol/report styles to a DOCX.

For advanced Word creation, rendering, comments, or redlines, also use the built-in `documents` skill/plugin instructions. Preserve original documents; write modified files to a new output path.

When running these scripts in Codex Desktop, prefer the bundled workspace Python from `load_workspace_dependencies`; system Python may not include all requirements. For published or external installs, create an environment and install `requirements.txt`.

## External Data Scripts

Use `scripts/evidence_search.py` for first-pass external data retrieval:

- `pubmed` for PubMed / NCBI E-utilities.
- `clinicaltrials` for ClinicalTrials.gov v2.
- `openfda-label` for openFDA drug labels.

Network failures or missing results should not halt work unless the section requires evidence. Mark evidence as unavailable and ask whether to continue with a limited draft/review.

## Required Structured Outputs

Use these compact blocks to keep the workflow gated.

After outline confirmation in create mode:

```yaml
execution_plan:
  sections:
    - id: ""
      title: ""
      priority: necessary | recommended | optional
      status: pending
      next_action: section_info_gate
  always_available_actions: [add_section, skip_section, revise_previous_section, unify_word_style]
```

Before drafting each section:

```yaml
section_info_gate:
  section_id: ""
  section_title: ""
  can_generate_now: true | false
  p0_questions: []
  p1_assumptions_to_confirm: []
  p2_placeholders: []
  external_data_needs:
    required: []
    recommended: []
    optional: []
  proposed_action: ask_p0 | confirm_assumptions | retrieve_evidence | generate_with_placeholders
```

After document extraction in review mode:

```yaml
section_coverage_review:
  missing_necessary_sections: []
  recommended_sections_to_consider: []
  optional_sections_to_consider: []
  user_decision_needed: []
```

## Safety Boundaries

- This skill generates drafts and review suggestions only; it does not provide regulatory approval, medical advice, legal advice, or biostatistical sign-off.
- Require professional review for final protocols: PI/clinical expert, statistician, regulatory/ethics, pharmacovigilance, legal, and sponsor review as applicable.
- Do not fabricate citations, trial IDs, labels, sample sizes, or regulatory facts.
- In review mode, keep edits small and traceable unless the user explicitly asks for rewriting.
