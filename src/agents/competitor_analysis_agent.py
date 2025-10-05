# competitor_analysis.py

import asyncio
from typing import List, Dict
import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from bs4 import BeautifulSoup
from readability import Document
from urllib.parse import urlparse
from src.models.state_models import OutlineState

# Constants
MAX_CONCURRENT = 5
REQUEST_TIMEOUT = 15
USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
              "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
COMMON_BRANDS = ["whey","casein","plant","pea","hemp","optimum","dymatize","isopure"]


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    retry=retry_if_exception_type(aiohttp.ClientError)
)
async def fetch_html(session: aiohttp.ClientSession, url: str) -> str:
    """Fetch page HTML with retry/backoff."""
    async with session.get(url, timeout=REQUEST_TIMEOUT) as resp:
        resp.raise_for_status()
        return await resp.text()


def parse_article(html: str, url: str) -> Dict:
    """Extract title, headings, topics, word count, products, and meta."""
    soup = BeautifulSoup(html, "html.parser")

    # Title or fallback to domain
    title_tag = soup.find("title")
    title = title_tag.get_text().strip() if title_tag else urlparse(url).netloc

    # Readability to get main content
    main_html = Document(html).summary(html_partial=True)
    text_only = BeautifulSoup(main_html, "html.parser").get_text()

    # Headings and topics
    headings = []
    topics = []
    for tag in BeautifulSoup(main_html, "html.parser").find_all(["h2","h3"]):
        txt = tag.get_text().strip()
        if txt:
            level = tag.name
            headings.append({"level": level, "text": txt})
            topics.append(txt)

    # Word count
    word_count = len(text_only.split())

    # Product mentions in headings
    products = [h["text"] for h in headings
                for b in COMMON_BRANDS if b in h["text"].lower()][:10]

    # Meta description fallback chain
    meta = (soup.find("meta", attrs={"name":"description"}) or
            soup.find("meta", attrs={"property":"og:description"}) or
            soup.find("meta", attrs={"name":"twitter:description"}))
    meta_desc = meta["content"].strip()[:160] if meta and meta.get("content") else ""

    return {
        "url": url,
        "title": title,
        "headings": headings,
        "topics_covered": topics,
        "word_count": word_count,
        "products_mentioned": products,
        "meta_description": meta_desc
    }


async def analyze_urls(urls: List[str]) -> List[Dict]:
    """Concurrent analysis of multiple competitor URLs."""
    connector = aiohttp.TCPConnector(limit=MAX_CONCURRENT)
    headers = {"User-Agent": USER_AGENT}
    async with aiohttp.ClientSession(connector=connector, headers=headers) as session:
        tasks = [fetch_html(session, url) for url in urls]
        html_list = await asyncio.gather(*tasks, return_exceptions=True)

    results = []
    for url, html in zip(urls, html_list):
        if isinstance(html, Exception):
            # Skip failed fetches
            continue
        results.append(parse_article(html, url))
    return results


def competitor_analysis(state: OutlineState) -> OutlineState:
    """Main entry: updates OutlineState with competitor insights."""
    serper = state.get("serper_results", [])
    if not serper:
        state["competitor_analysis"] = {"error":"No serper results available"}
        return state

    # Top 5 competitor URLs
    organic = serper[0].get("organic", [])[:5]
    urls = [c.get("link") for c in organic if c.get("link")]

    # Fetch & parse concurrently
    competitor_data = asyncio.run(analyze_urls(urls))

    # Aggregate topics
    all_topics = {topic.lower() for comp in competitor_data for topic in comp["topics_covered"]}

    # PAA-based gap detection
    paa = [p.get("question","") for p in serper[0].get("people_also_ask",[])]
    gaps = []
    for q in paa:
        keywords = set(q.lower().split()[:3])
        if not any(keywords & set(t.split()) for t in all_topics):
            gaps.append({
                "topic": q,
                "description": "PAA question not covered",
                "opportunity_score": 8
            })

    # Summary
    summary = {
        "competitors_analyzed": len(competitor_data),
        "competitor_data": competitor_data,
        "common_topics": list(all_topics),
        "content_gaps": gaps,
        "avg_word_count": (
            sum(c["word_count"] for c in competitor_data)//max(len(competitor_data),1)
        ),
        "avg_sections": (
            sum(len(c["headings"]) for c in competitor_data)//max(len(competitor_data),1)
        )
    }

    state["competitor_analysis"] = summary
    state["content_gaps"] = gaps
    state["confidence_scores"]["competitor_analysis"] = 0.8 if len(competitor_data)>=3 else 0.6
    return state
