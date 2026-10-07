#!/usr/bin/env python3
"""Probe which download endpoints actually work from the GitHub runner."""
import sys, time, urllib.parse, urllib.request

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/126.0.0.0 Safari/537.36")
try:
    from curl_cffi import requests as cffi
    HAVE_CFFI = True
except Exception as e:  # noqa: BLE001
    cffi = None
    HAVE_CFFI = False
    print("curl_cffi import failed:", e)

URLS = [
    # Europe PMC REST
    ("epmc-search-lite", "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:%2210.3390/pharmaceutics15030718%22&format=json&resultType=lite&pageSize=5"),
    ("epmc-search-core", "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:%2210.3390/pharmaceutics15030718%22&format=json&resultType=core&pageSize=5"),
    ("epmc-jats-PMC11671129", "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11671129/fullTextXML"),
    ("epmc-jats-PMC11097067", "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11097067/fullTextXML"),
    ("epmc-jats-PMC4809755", "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC4809755/fullTextXML"),
    ("epmc-render-PMC11671129", "https://europepmc.org/articles/PMC11671129?pdf=render"),
    ("epmc-fulltextrepo", "https://europepmc.org/api/fulltextRepo?pprId=PMC11671129&type=FILE&fileName=EMS.pdf&mimeType=application/pdf"),
    # NCBI
    ("ncbi-oa-fcgi-PMC11999318", "https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id=PMC11999318"),
    ("ncbi-oa-fcgi-PMC11097067", "https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id=PMC11097067"),
    ("ncbi-oa-fcgi-PMC4809755", "https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id=PMC4809755"),
    ("ncbi-pmc-pdf", "https://pmc.ncbi.nlm.nih.gov/articles/PMC11671129/pdf/"),
    # MDPI
    ("mdpi-web-processes", "https://www.mdpi.com/2227-9717/9/2/356/pdf"),
    ("mdpi-cdn-processes", "https://mdpi-res.com/d_attachment/processes/processes-09-00356/article_deploy/processes-09-00356.pdf"),
    ("mdpi-web-ijms", "https://www.mdpi.com/1422-0067/25/6/3439/pdf"),
    ("mdpi-cdn-ijms", "https://mdpi-res.com/d_attachment/ijms/ijms-25-03439/article_deploy/ijms-25-03439.pdf"),
    ("mdpi-web-pharmaceutics", "https://www.mdpi.com/1999-4923/15/3/718/pdf"),
    # Wiley
    ("wiley-medcomm", "https://onlinelibrary.wiley.com/doi/pdfdirect/10.1002/mco2.70386?download=true"),
    ("wiley-adhm", "https://onlinelibrary.wiley.com/doi/pdfdirect/10.1002/adhm.202100047?download=true"),
    ("wiley-jex2", "https://onlinelibrary.wiley.com/doi/pdfdirect/10.1002/jex2.156?download=true"),
    # Elsevier OA
    ("sd-vesic-pdfft", "https://www.sciencedirect.com/science/article/pii/S2773041724000254/pdfft?isDNToken="),
    ("sd-jsps", "https://www.sciencedirect.com/science/article/pii/S1319016424001781/pdfft"),
    # Frontiers / Nature sanity
    ("frontiers-pdf", "https://www.frontiersin.org/journals/cell-and-developmental-biology/articles/10.3389/fcell.2025.1655623/pdf"),
    ("nature-pdf", "https://www.nature.com/articles/s41419-022-05034-x.pdf"),
]


def probe(name, url, engine):
    t0 = time.time()
    try:
        if engine == "cffi" and HAVE_CFFI:
            r = cffi.get(url, impersonate="chrome", timeout=45, allow_redirects=True,
                         headers={"Accept": "*/*", "Referer": "https://" + urllib.parse.urlparse(url).netloc + "/"})
            data, status, ctype = r.content, r.status_code, r.headers.get("content-type", "")
        else:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
            with urllib.request.urlopen(req, timeout=45) as resp:
                data, status, ctype = resp.read(), resp.status, resp.headers.get("content-type", "")
    except Exception as e:  # noqa: BLE001
        return f"{engine:<5} {name:<26} FAIL {type(e).__name__}: {str(e)[:80]}"
    kind = "PDF" if data[:5].startswith(b"%PDF") else ("xml" if b"<" in data[:200] else "other")
    head = data[:110].decode("utf-8", "replace").replace("\n", " ")
    return (f"{engine:<5} {name:<26} {status} {len(data):>8}B {ctype[:24]:<24} {kind} "
            f"{time.time()-t0:4.1f}s :: {head}")


out = []
for name, url in URLS:
    parts = []
    if HAVE_CFFI:
        parts.append(probe(name, url, "cffi"))
    parts.append(probe(name, url, "urllib"))
    line = "\n".join(parts)
    print(line, flush=True)
    out.append(line)
    time.sleep(0.6)

with open(".scratch/papers/diag.txt", "w", encoding="utf-8") as fh:
    fh.write("\n".join(out) + "\n")
print("\nwrote .scratch/papers/diag.txt")
