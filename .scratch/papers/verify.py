#!/usr/bin/env python3
"""Check that each downloaded PDF actually contains the intended paper (title/DOI match)."""
import glob, json, os, re, sys, unicodedata
from pypdf import PdfReader

def norm(s):
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9 ]+", " ", s.lower()).strip()

def tokens(s):
    stop = {"of","the","a","an","in","and","for","to","on","with","from","by","as","is","are","its","their","new","via","into","based"}
    return [t for t in norm(s).split() if t not in stop and len(t) > 2]

jobs = json.load(open(".scratch/papers/jobs.json"))
man = {r["n"]: r for r in json.load(open(".scratch/papers/manifest.json"))}
out = []
for j in jobs:
    n = j["n"]
    p = glob.glob(f"papers/{n:02d} - *.pdf")
    rec = man.get(n, {})
    row = {"n": n, "status": rec.get("status"), "doi": rec.get("doi")}
    if not p:
        row["verdict"] = "MISSING"; out.append(row); continue
    path = p[0]
    try:
        rd = PdfReader(path)
        txt = "".join((pg.extract_text() or "") for pg in rd.pages[:3])
    except Exception as e:
        row["verdict"] = f"UNREADABLE {e}"; out.append(row); continue
    nt = norm(txt)
    toks = tokens(j["title"])
    got = sum(1 for t in toks if t in nt)
    frac = got / max(1, len(toks))
    doi_ok = bool(rec.get("doi")) and norm(rec["doi"]) in nt
    if rec.get("status") == "abstract-only":
        v = "ABSTRACT-RECORD" if frac >= 0.7 else f"ABSTRACT-RECORD(lowmatch {frac:.2f})"
    elif "checking your browser" in nt or "just a moment" in nt:
        v = "BLOCKED-PAGE"
    elif frac >= 0.7 or doi_ok:
        v = f"OK(title {frac:.2f}{' doi' if doi_ok else ''})"
    else:
        v = f"CONTENT-MISMATCH({frac:.2f})"
    row.update({"verdict": v, "file": os.path.basename(path),
                "first80": re.sub(r"\s+", " ", txt)[:95]})
    out.append(row)

for r in out:
    print(f"{r['n']:02d} {r.get('verdict','?'):<28} {r.get('doi')} :: {r.get('first80','')}")
json.dump(out, open(".scratch/papers/verify.json", "w"), indent=1)
