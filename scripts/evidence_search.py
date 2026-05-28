#!/usr/bin/env python3
"""Small evidence-search helper for PubMed, ClinicalTrials.gov, and openFDA labels."""

import argparse
import json
import sys
import urllib.parse
import urllib.request
from datetime import date


def get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "clinical-trial-protocol-assistant/0.1"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def pubmed(query: str, limit: int) -> dict:
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = urllib.parse.urlencode({"db": "pubmed", "term": query, "retmode": "json", "retmax": limit})
    data = get_json(f"{base}?{params}")
    ids = data.get("esearchresult", {}).get("idlist", [])
    return {"source": "PubMed", "query": query, "retrieval_date": str(date.today()), "ids": ids}


def clinicaltrials(query: str, limit: int) -> dict:
    base = "https://clinicaltrials.gov/api/v2/studies"
    params = urllib.parse.urlencode({"query.term": query, "pageSize": limit, "format": "json"})
    data = get_json(f"{base}?{params}")
    records = []
    for study in data.get("studies", [])[:limit]:
        proto = study.get("protocolSection", {})
        ident = proto.get("identificationModule", {})
        status = proto.get("statusModule", {})
        design = proto.get("designModule", {})
        records.append({
            "nctId": ident.get("nctId"),
            "briefTitle": ident.get("briefTitle"),
            "overallStatus": status.get("overallStatus"),
            "phases": design.get("phases"),
        })
    return {"source": "ClinicalTrials.gov", "query": query, "retrieval_date": str(date.today()), "records": records}


def openfda_label(query: str, limit: int) -> dict:
    base = "https://api.fda.gov/drug/label.json"
    search = f'openfda.brand_name:"{query}" OR openfda.generic_name:"{query}"'
    params = urllib.parse.urlencode({"search": search, "limit": limit})
    data = get_json(f"{base}?{params}")
    records = []
    for item in data.get("results", [])[:limit]:
        openfda = item.get("openfda", {})
        records.append({
            "brand_name": openfda.get("brand_name"),
            "generic_name": openfda.get("generic_name"),
            "indications_and_usage": item.get("indications_and_usage", [])[:1],
            "warnings": item.get("warnings", [])[:1],
            "adverse_reactions": item.get("adverse_reactions", [])[:1],
        })
    return {"source": "openFDA drug label", "query": query, "retrieval_date": str(date.today()), "records": records}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", choices=["pubmed", "clinicaltrials", "openfda-label"])
    parser.add_argument("query")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--out")
    args = parser.parse_args()

    try:
        if args.source == "pubmed":
            result = pubmed(args.query, args.limit)
        elif args.source == "clinicaltrials":
            result = clinicaltrials(args.query, args.limit)
        else:
            result = openfda_label(args.query, args.limit)
    except Exception as exc:
        result = {"source": args.source, "query": args.query, "retrieval_date": str(date.today()), "error": str(exc)}

    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(output)
    else:
        sys.stdout.write(output + "\n")


if __name__ == "__main__":
    main()

