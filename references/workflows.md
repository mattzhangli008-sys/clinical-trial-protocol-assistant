# Workflows

## Create Workflow

Hard gate: after the user confirms necessary/recommended/optional sections, do not draft the whole protocol. Build and show an execution plan, then process one section at a time through a section information gate. If the user asks for fast-track full drafting, state that section-by-section confirmation will be skipped and mark unresolved items with `[待确认]`.

1. Global P0 intake:
   - task: full protocol, outline, specific section, Word output
   - title or clinical question
   - broad study nature: interventional, observational/RWE, or unknown
   - source materials available: ask explicitly whether the user has Word/Excel/PPT/PDF/text materials. If files are provided, extract them before asking further non-blocking questions.
2. Infer study profile from available information.
3. Propose outline:
   - necessary sections
   - recommended sections
   - optional sections
   - not recommended now
4. User confirms section scope.
5. Build execution plan and create or identify the protocol Markdown source file (`protocol_md_path`).
6. For each section:
   - check whether uploaded materials answer this section's P0/P1/P2 questions
   - run section information gate
   - resolve P0
   - confirm P1 assumptions
   - mark P2 placeholders
   - retrieve required/recommended evidence
   - draft with Chinese numeric headings (`一、二、三、四`) and inline citation markers for retrieved evidence
   - user confirms/revises
   - immediately write the confirmed section into the protocol Markdown source file
7. Cross-section consistency check using the complete protocol Markdown source file.
8. Generate DOCX from the complete protocol Markdown source file if delivering Word, then run style unification.

## Review Workflow

Hard gate: after extracting a document, do not immediately produce final findings. First show the extracted document profile and section coverage review, then ask the user to confirm missing necessary/recommended/optional sections for the review plan.

1. Extract document text, headings, and tables.
2. Extract global P0/P1/P2 from the document.
3. Ask user only for missing blocking items.
4. Map document sections to the section map.
5. Check missing necessary sections and candidate recommended/optional sections.
6. Ask user which sections to include in review plan.
7. For each section:
   - extract section P0/P1/P2 answers from text
   - consult any additional uploaded materials before asking the user
   - ask about missing or unclear blocking items
   - retrieve external evidence when needed
   - generate findings with inline citation markers when retrieved evidence supports a finding
   - keep suggested edits small
8. Deliver chat report, Word report, or commented/redlined Word as requested.

## Always Available Actions

- Add a section.
- Upload or add supporting materials.
- Re-extract uploaded materials and update the material index.
- Skip or postpone a section.
- Reopen a prior section.
- Re-run outline/coverage check.
- Change output format.
- Run Word style unification.
