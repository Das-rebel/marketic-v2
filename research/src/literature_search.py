#!/usr/bin/env python3
"""
Literature search for MAIS research bootstrap.
Queries Semantic Scholar and arXiv with rate-limiting and retries.
Falls back gracefully on 429s.
"""
import urllib.request
import urllib.parse
import json
import time
import sys
import os
import xml.etree.ElementTree as ET

OUT_DIR = os.path.expanduser("~/marketic-v2/research/literature")
os.makedirs(OUT_DIR, exist_ok=True)

QUERIES = [
    # (topic_key, query_string)
    ("rlhf_marketing", "RLHF marketing content generation advertising"),
    ("causal_inference_ads", "causal inference digital advertising uplift modeling"),
    ("tool_use_ecommerce", "tool use agents e-commerce shopping assistant"),
    ("reward_model_personalization", "reward model marketing personalization LLM"),
    ("multi_task_marketing", "multi-task learning marketing prediction conversion"),
    ("marketing_mix_causal", "marketing mix modeling causal inference Bayesian"),
    ("uplift_modeling", "uplift modeling treatment effect estimation advertising"),
    ("llm_agents_marketing", "LLM agents marketing campaign optimization"),
    ("rlhf_reward_hacking", "RLHF reward hacking reward model robustness"),
    ("bandit_advertising", "contextual bandit advertising real-time bidding"),
    ("causal_forest_uplift", "causal forest uplift randomized experiment"),
    ("mmoe_multi_task", "mixture of experts multi-task learning recommendation"),
]

HEADERS = {"User-Agent": "MAIS-Research/1.0 (academic research; mailto:research@mais.local)"}


def http_get(url, timeout=25, retries=4):
    """GET with exponential backoff on 429."""
    last_err = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            r = urllib.request.urlopen(req, timeout=timeout)
            return r.read().decode("utf-8", errors="ignore")
        except urllib.error.HTTPError as e:
            last_err = e
            if e.code == 429:
                wait = 5 * (2 ** attempt)  # 5, 10, 20, 40
                print(f"    429 rate-limited, backing off {wait}s...", flush=True)
                time.sleep(wait)
                continue
            else:
                return None
        except Exception as e:
            last_err = e
            time.sleep(3 * (attempt + 1))
    print(f"    FAILED after retries: {last_err}", flush=True)
    return None


def search_semantic_scholar(query, limit=6):
    """Search Semantic Scholar Graph API."""
    q = urllib.parse.quote(query)
    fields = "title,year,abstract,citationCount,url,authors,venue,externalIds"
    url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={q}&limit={limit}&fields={fields}&year=2022-2026"
    raw = http_get(url)
    if not raw:
        return []
    try:
        data = json.loads(raw)
    except Exception:
        return []
    out = []
    for p in data.get("data", []):
        authors = ", ".join(a.get("name", "") for a in (p.get("authors") or [])[:4])
        out.append({
            "title": p.get("title", ""),
            "year": p.get("year"),
            "authors": authors,
            "venue": p.get("venue") or "",
            "citations": p.get("citationCount", 0),
            "url": p.get("url", ""),
            "doi": (p.get("externalIds") or {}).get("DOI", ""),
            "abstract": (p.get("abstract") or "")[:600],
            "source": "semantic_scholar",
        })
    return out


def search_arxiv(query, max_results=6):
    """Search arXiv API (ATOM XML)."""
    q = urllib.parse.quote(query)
    url = (
        f"http://export.arxiv.org/api/query?search_query=all:{q}"
        f"&max_results={max_results}&sortBy=submittedDate&sortOrder=descending"
    )
    raw = http_get(url, timeout=30)
    if not raw:
        return []
    out = []
    try:
        ns = {"a": "http://www.w3.org/2005/Atom"}
        root = ET.fromstring(raw)
        for entry in root.findall("a:entry", ns):
            title = entry.findtext("a:title", "", ns).strip().replace("\n", " ")
            published = entry.findtext("a:published", "", ns)[:4]
            link = entry.findtext("a:id", "", ns)
            summary = entry.findtext("a:summary", "", ns).strip().replace("\n", " ")[:600]
            authors = ", ".join(
                e.findtext("a:name", "", ns) for e in entry.findall("a:author", ns)[:4]
            )
            out.append({
                "title": title,
                "year": published,
                "authors": authors,
                "venue": "arXiv",
                "citations": 0,
                "url": link,
                "doi": "",
                "abstract": summary,
                "source": "arxiv",
            })
    except Exception as e:
        print(f"    arxiv parse error: {e}", flush=True)
    return out


def main():
    all_results = {}
    total_papers = 0
    for i, (key, query) in enumerate(QUERIES):
        print(f"\n[{i+1}/{len(QUERIES)}] Searching: {query}", flush=True)
        results = []
        # Try arxiv first (more lenient on separate host), then semantic scholar
        time.sleep(2)
        ax = search_arxiv(query)
        results.extend(ax)
        print(f"    arxiv: {len(ax)} results", flush=True)
        time.sleep(4)
        ss = search_semantic_scholar(query)
        # dedupe by title
        seen = {r["title"].lower()[:80] for r in results}
        for r in ss:
            t = r["title"].lower()[:80]
            if t not in seen:
                results.append(r)
                seen.add(t)
        print(f"    semantic scholar: {len(ss)} results (total {len(results)})", flush=True)
        all_results[key] = results
        total_papers += len(results)
        # write per-topic file
        fname = os.path.join(OUT_DIR, f"search_{key}.json")
        with open(fname, "w") as f:
            json.dump(results, f, indent=2)
        # be polite between queries
        time.sleep(3)

    print(f"\n=== TOTAL: {total_papers} papers across {len(QUERIES)} topics ===", flush=True)

    # Write combined survey.md
    survey_path = os.path.join(OUT_DIR, "survey.md")
    with open(survey_path, "w") as f:
        f.write("# Literature Survey — MAIS Research Bootstrap\n\n")
        f.write("Auto-generated from Semantic Scholar + arXiv searches.\n")
        f.write(f"Total papers collected: **{total_papers}** across {len(QUERIES)} topics.\n\n")
        f.write("---\n\n")
        for key, query in QUERIES:
            papers = all_results.get(key, [])
            f.write(f"## Topic: {key}\n")
            f.write(f"*Query: `{query}`* — {len(papers)} papers\n\n")
            # sort by year desc then citations
            papers_sorted = sorted(
                papers, key=lambda p: (p.get("year") or 0, p.get("citations") or 0), reverse=True
            )
            for p in papers_sorted:
                yr = p.get("year") or "?"
                cite = p.get("citations") or 0
                f.write(f"### {p['title']}\n")
                f.write(f"- **Year:** {yr} | **Citations:** {cite} | **Venue:** {p.get('venue','')} | **Source:** {p.get('source','')}\n")
                f.write(f"- **Authors:** {p.get('authors','')}\n")
                f.write(f"- **URL:** {p.get('url','')}\n")
                if p.get("abstract"):
                    f.write(f"- **Abstract:** {p['abstract']}\n")
                f.write("\n")
            f.write("---\n\n")
    print(f"Wrote survey to {survey_path}", flush=True)


if __name__ == "__main__":
    main()
