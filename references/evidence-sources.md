# Evidence Sources

Use evidence by section. Do not search everything at the start.

## Sources

- PubMed / MEDLINE: background, disease, endpoints, safety literature.
- ClinicalTrials.gov: similar trial design, criteria, endpoints, sample size, duration.
- WHO ICTRP / ChiCTR: additional trial registration coverage.
- Drug labels / NMPA labels / FDA labels: indication, dosage, contraindications, warnings, adverse reactions.
- Drugs@FDA / Orange Book / Purple Book: regulatory status and reference products.
- openFDA / FAERS / PV sources: safety signals.
- FDA 510(k), PMA, De Novo and device registries: device predicates, classification, evidence.
- Guidelines: standard of care, diagnostic criteria, endpoints.
- RWE data dictionaries: variable availability, exposure/outcome definitions, missingness.
- Internal KB: historical protocols, SAP, CSR, IB, PV updates.

## Section Triggers

| Section | Evidence need |
|---|---|
| Background | PubMed/guidelines recommended |
| Risk-benefit | label/IB/safety sources required for interventional studies |
| Objectives/endpoints | ClinicalTrials.gov/PubMed/guidelines recommended; required for pivotal claims |
| Study design/comparator | ClinicalTrials.gov and methods literature recommended; required for external controls |
| Population/criteria | ClinicalTrials.gov, labels, guidelines recommended |
| Intervention/exposure | label/IB/IFU/regulatory data required for drug/device |
| Safety/AE | label/IB/PV/PubMed required for interventional studies |
| Sample size/statistics | similar trials and prior studies recommended; required for final sample-size justification |
| RWE bias/confounding | data dictionary and RWE methods required |
| Ethics/regulatory | applicable regulations/guidance required for submission-facing work |

## Evidence Record

Record:

- source
- query
- retrieval date
- records used
- citation number used in generated text, if cited
- key extracted points
- limitations
- user confirmation needed

## Citation Markers

When retrieved literature, trial records, labels, guidelines, or other external records are used to support generated content:

- Number cited sources in order of first use: `[1]`, `[2]`, `[3]`.
- Put the marker immediately after the supported sentence or paragraph, not only at the end of the whole section.
- Keep the same number for repeated use of the same source.
- Provide a matching references list or evidence record with enough information to identify the source, such as title, registry ID, label/source name, year/date, URL or PMID/NCT number when available, and retrieval date.
- Do not cite sources that were not actually retrieved or provided by the user.
