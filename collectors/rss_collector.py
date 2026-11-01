#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pulse-ZeroBaran | RSS Collector (stdlib XML — zero hard dependencies)
====================================================================
جامع خفيف لتدفّقات RSS/Atom العامة (أخبار · مدونات · صفحات تقييمات
تدعم Feed). يستخدم xml.etree القياسي — بلا أي اعتماديات إلزامية.

Usage:
    from collectors.rss_collector import RssCollector
    mentions = RssCollector(["https://example.com/reviews.xml"]).collect()

Author : Baran Avisat <baranavisat@gmail.com>
© 2026 Baran Avisat — All Rights Reserved.
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from typing import List, Optional

try:
    import requests
except Exception:  # pragma: no cover
    requests = None

from .base import USER_AGENT, BaseCollector, Mention

_ATOM = "{http://www.w3.org/2005/Atom}"
_TAG_RE = re.compile(r"<[^>]+>")


def _strip_html(text: str) -> str:
    return _TAG_RE.sub(" ", text or "").strip()


class RssCollector(BaseCollector):
    name = "rss"

    def __init__(self, feeds: List[str], brand_terms: Optional[List[str]] = None,
                 pause: float = 2.0, limit_per_feed: int = 30):
        super().__init__(pause=pause)
        self.feeds = list(feeds or [])
        self.brand_terms = [t.lower() for t in (brand_terms or [])]
        self.limit = limit_per_feed

    # ------------------------------------------------------------------ #
    def _relevant(self, *parts: str) -> bool:
        if not self.brand_terms:
            return True   # بلا فلتر ⇒ كل ما هو عام
        blob = " ".join(parts).lower()
        return any(t in blob for t in self.brand_terms)

    # ------------------------------------------------------------------ #
    def _parse(self, xml_text: str) -> List[Mention]:
        out: List[Mention] = []
        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError:
            return out
        # RSS 2.0
        for item in root.iter("item"):
            title = _strip_html(item.findtext("title") or "")
            desc = _strip_html(item.findtext("description") or "")
            link = (item.findtext("link") or "").strip()
            pub = (item.findtext("pubDate") or "").strip()
            if not self._relevant(title, desc):
                continue
            body = f"{title} — {desc}".strip(" —")
            if body:
                out.append(Mention(text=body[:1200], source="rss", url=link,
                                   created_at=pub, author="feed"))
            if len(out) >= self.limit:
                break
        if out:
            return out
        # Atom
        for entry in root.iter(f"{_ATOM}entry"):
            title = _strip_html(entry.findtext(f"{_ATOM}title") or "")
            summary = _strip_html(entry.findtext(f"{_ATOM}summary") or "")
            content = _strip_html(entry.findtext(f"{_ATOM}content") or "")
            link_el = entry.find(f"{_ATOM}link")
            link = (link_el.get("href") or "").strip() if link_el is not None else ""
            pub = (entry.findtext(f"{_ATOM}published")
                   or entry.findtext(f"{_ATOM}updated") or "").strip()
            if not self._relevant(title, summary, content):
                continue
            body = f"{title} — {summary or content}".strip(" —")
            if body:
                out.append(Mention(text=body[:1200], source="rss", url=link,
                                   created_at=pub, author="feed"))
            if len(out) >= self.limit:
                break
        return out

    # ------------------------------------------------------------------ #
    def collect(self) -> List[Mention]:
        if requests is None:
            return []
        mentions: List[Mention] = []
        for url in self.feeds:
            self._throttle()
            try:
                resp = requests.get(url, headers={"User-Agent": USER_AGENT},
                                    timeout=15)
                if resp.ok:
                    mentions.extend(self._parse(resp.text))
            except Exception:
                continue
        return mentions
