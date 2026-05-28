#!/usr/bin/env python3
"""Extract text/tables from protocol support materials into one JSON index.

The script prefers richer extraction libraries when they are installed, while
keeping lightweight fallbacks so the skill remains usable in constrained
environments.
"""

import argparse
import csv
import importlib
import json
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def item(kind, location, text, extra=None):
    out = {"kind": kind, "location": location, "text": clean(text)}
    if extra:
        out.update(extra)
    return out


def optional_import(module_name: str):
    try:
        return importlib.import_module(module_name), None
    except Exception as exc:
        return None, exc


def truncate_items(items, max_chars_per_item):
    if not max_chars_per_item:
        return items
    out = []
    for entry in items:
        text = entry.get("text", "")
        if len(text) <= max_chars_per_item:
            out.append(entry)
            continue
        truncated = dict(entry)
        truncated["text"] = text[:max_chars_per_item].rstrip()
        truncated["truncated"] = True
        truncated["original_char_count"] = len(text)
        out.append(truncated)
    return out


def extract_markdown_view(path: Path):
    markitdown, _ = optional_import("markitdown")
    if markitdown is None:
        return None
    markdown_cls = getattr(markitdown, "MarkItDown", None)
    if markdown_cls is None:
        return None
    result = markdown_cls().convert(str(path))
    text = clean(getattr(result, "text_content", "") or "")
    if not text:
        return None
    return item("markdown_view", "markitdown", text, {"method": "markitdown"})


def extract_docx_fallback(path: Path):
    items = []
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    with zipfile.ZipFile(path) as zf:
        root = ET.fromstring(zf.read("word/document.xml"))
        for i, para in enumerate(root.findall(".//w:p", ns), 1):
            texts = [node.text or "" for node in para.findall(".//w:t", ns)]
            text = clean("".join(texts))
            if text:
                items.append(item("paragraph", f"P{i:04d}", text, {"method": "zip-xml"}))
    return items


def extract_docx(path: Path):
    docx, err = optional_import("docx")
    if docx is None:
        return extract_docx_fallback(path), [f"python-docx unavailable; used zip XML fallback: {err}"]

    doc = docx.Document(str(path))
    items = []
    for i, para in enumerate(doc.paragraphs, 1):
        text = clean(para.text)
        if text:
            style = para.style.name if para.style is not None else ""
            items.append(item("paragraph", f"P{i:04d}", text, {"style": style, "method": "python-docx"}))
    for ti, table in enumerate(doc.tables, 1):
        for ri, row in enumerate(table.rows, 1):
            row_text = " | ".join(clean(cell.text) for cell in row.cells)
            if clean(row_text):
                items.append(item("table_row", f"T{ti}:R{ri}", row_text, {"method": "python-docx"}))
    return items, []


def extract_xlsx(path: Path):
    openpyxl, err = optional_import("openpyxl")
    if openpyxl is None:
        raise RuntimeError(f"openpyxl is required for Excel extraction: {err}")

    wb = openpyxl.load_workbook(str(path), read_only=True, data_only=True)
    items = []
    for ws in wb.worksheets:
        for ri, row in enumerate(ws.iter_rows(values_only=True), 1):
            values = [clean(str(v)) if v is not None else "" for v in row]
            if any(values):
                items.append(item("sheet_row", f"{ws.title}!R{ri}", " | ".join(values), {"method": "openpyxl"}))
    return items, []


def extract_csv(path: Path, delimiter=None):
    if delimiter is None:
        delimiter = "\t" if path.suffix.lower() == ".tsv" else ","
    items = []
    with path.open("r", encoding="utf-8-sig", newline="", errors="ignore") as f:
        reader = csv.reader(f, delimiter=delimiter)
        for ri, row in enumerate(reader, 1):
            row_text = " | ".join(clean(c) for c in row)
            if clean(row_text):
                items.append(item("table_row", f"R{ri}", row_text, {"method": "csv"}))
    return items, []


def extract_pdf_with_pdfplumber(path: Path):
    pdfplumber, err = optional_import("pdfplumber")
    if pdfplumber is None:
        return None, err

    items = []
    with pdfplumber.open(str(path)) as pdf:
        for pi, page in enumerate(pdf.pages, 1):
            text = clean(page.extract_text() or "")
            if text:
                items.append(item("page", f"page-{pi}", text, {"method": "pdfplumber"}))
            for ti, table in enumerate(page.extract_tables() or [], 1):
                for ri, row in enumerate(table or [], 1):
                    values = [clean(str(v)) if v is not None else "" for v in row]
                    if any(values):
                        items.append(item("table_row", f"page-{pi}:T{ti}:R{ri}", " | ".join(values), {"method": "pdfplumber"}))
    return items, None


def extract_pdf_with_pymupdf(path: Path):
    fitz, err = optional_import("fitz")
    if fitz is None:
        return None, err

    items = []
    with fitz.open(str(path)) as doc:
        for pi, page in enumerate(doc, 1):
            text = clean(page.get_text("text") or "")
            if text:
                items.append(item("page", f"page-{pi}", text, {"method": "pymupdf"}))
    return items, None


def extract_pdf_with_pypdf(path: Path):
    pypdf, err = optional_import("pypdf")
    if pypdf is None:
        return None, err

    reader = pypdf.PdfReader(str(path))
    items = []
    for pi, page in enumerate(reader.pages, 1):
        text = clean(page.extract_text() or "")
        if text:
            items.append(item("page", f"page-{pi}", text, {"method": "pypdf"}))
    return items, None


def extract_pdf(path: Path):
    notes = []
    for label, extractor in [
        ("pdfplumber", extract_pdf_with_pdfplumber),
        ("pymupdf", extract_pdf_with_pymupdf),
        ("pypdf", extract_pdf_with_pypdf),
    ]:
        items, err = extractor(path)
        if items:
            return items, notes
        if err:
            notes.append(f"{label} unavailable or failed: {err}")
    raise RuntimeError("No PDF text could be extracted. Install pdfplumber, PyMuPDF, or pypdf; scanned PDFs may require OCR.")


def extract_pptx_with_python_pptx(path: Path):
    pptx, err = optional_import("pptx")
    if pptx is None:
        return None, err

    prs = pptx.Presentation(str(path))
    items = []
    for slide_idx, slide in enumerate(prs.slides, 1):
        text_parts = []
        for shape_idx, shape in enumerate(slide.shapes, 1):
            if getattr(shape, "has_text_frame", False):
                text = clean(shape.text)
                if text:
                    text_parts.append(text)
            if getattr(shape, "has_table", False):
                table = shape.table
                for ri, row in enumerate(table.rows, 1):
                    values = [clean(cell.text) for cell in row.cells]
                    if any(values):
                        items.append(item("table_row", f"slide-{slide_idx}:shape-{shape_idx}:R{ri}", " | ".join(values), {"method": "python-pptx"}))
        text = clean(" ".join(text_parts))
        if text:
            items.append(item("slide", f"slide-{slide_idx}", text, {"method": "python-pptx"}))
    return items, None


def extract_pptx_zip(path: Path):
    items = []
    ns = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
    with zipfile.ZipFile(path) as zf:
        slide_names = sorted(
            [n for n in zf.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n)],
            key=lambda n: int(re.search(r"slide(\d+)\.xml", n).group(1)),
        )
        for slide_idx, name in enumerate(slide_names, 1):
            root = ET.fromstring(zf.read(name))
            texts = [clean(t.text or "") for t in root.findall(".//a:t", ns)]
            text = clean(" ".join(t for t in texts if t))
            if text:
                items.append(item("slide", f"slide-{slide_idx}", text, {"method": "zip-xml"}))
    return items, None


def extract_pptx(path: Path):
    items, err = extract_pptx_with_python_pptx(path)
    if items:
        return items, []
    fallback_items, fallback_err = extract_pptx_zip(path)
    notes = []
    if err:
        notes.append(f"python-pptx unavailable or failed; used zip XML fallback: {err}")
    if fallback_err:
        notes.append(f"zip XML fallback failed: {fallback_err}")
    return fallback_items, notes


def extract_text(path: Path):
    raw = path.read_bytes()
    charset_normalizer, _ = optional_import("charset_normalizer")
    if charset_normalizer is not None:
        detected = charset_normalizer.from_bytes(raw).best()
        text = str(detected) if detected is not None else raw.decode("utf-8", errors="ignore")
    else:
        text = raw.decode("utf-8", errors="ignore")
    items = []
    for i, para in enumerate(re.split(r"\n\s*\n", text), 1):
        para = clean(para)
        if para:
            items.append(item("paragraph", f"P{i:04d}", para, {"method": "text"}))
    return items, []


def extract_file(path: Path, include_markdown=False, max_chars_per_item=None):
    suffix = path.suffix.lower()
    notes = []
    if suffix == ".docx":
        items, notes = extract_docx(path)
    elif suffix in {".xlsx", ".xlsm"}:
        items, notes = extract_xlsx(path)
    elif suffix in {".csv", ".tsv"}:
        items, notes = extract_csv(path)
    elif suffix == ".pdf":
        items, notes = extract_pdf(path)
    elif suffix == ".pptx":
        items, notes = extract_pptx(path)
    elif suffix in {".txt", ".md"}:
        items, notes = extract_text(path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")
    if include_markdown:
        markdown_item = extract_markdown_view(path)
        if markdown_item:
            items.append(markdown_item)
        else:
            notes.append("markitdown unavailable or produced no markdown view")
    items = truncate_items(items, max_chars_per_item)
    return {
        "source": str(path),
        "file_name": path.name,
        "file_type": suffix.lstrip("."),
        "item_count": len(items),
        "char_count": sum(len(x["text"]) for x in items),
        "notes": notes,
        "items": items,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+")
    parser.add_argument("--out")
    parser.add_argument("--include-markdown", action="store_true", help="Add a MarkItDown whole-document view when available.")
    parser.add_argument("--max-chars-per-item", type=int, default=0, help="Truncate very long extracted items for compact indexes.")
    args = parser.parse_args()

    records = []
    for raw in args.files:
        path = Path(raw).expanduser()
        try:
            records.append(extract_file(path, include_markdown=args.include_markdown, max_chars_per_item=args.max_chars_per_item))
        except Exception as exc:
            records.append({
                "source": str(path),
                "file_name": path.name,
                "error": str(exc),
                "items": [],
            })
    result = {"materials": records}
    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(output, encoding="utf-8")
    else:
        sys.stdout.write(output + "\n")


if __name__ == "__main__":
    main()
