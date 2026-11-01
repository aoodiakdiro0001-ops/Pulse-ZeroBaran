#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pulse-ZeroBaran | Web Review-Page Collector (polite HTML extraction)
====================================================================
جامع الصفحات العامة التي تعرض تقييمات/تعليقات (CSS selectors قابلة
للتهيئة). يلتزم بروبات اللطف: User-Agent واضح · pause بين الطلبات ·
استخراج نصوص عامة فقط (لا حسابات ولا بيانات خاصة).

⚠️ استخدم فقط على صفحاتك أو صفحات متاح لك جمعها قانونياً.

Author : Baran Avisat <baranavisat@gmail.com>
© 2026 Baran Avisat — All Rights Reserved.
"""
from __future__ import annotations

import re
from typing import Dict, List, Optional

try:
    import requests
except Exception:  # pragma: no cover
    requests = None

try:
    from bs4 import BeautifulSoup  # type: ignore
    _BS4 = True
except Exception:  # pragma: no cover
    BeautifulSoup = None
    _BS4 = False

from .base import USER_AGENT, BaseCollector, Mention, mask_author

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


def _strip(text: str) -> str:
    return _WS_RE.sub(" ", _TAG_RE.sub(" ", text or "")).strip()


class WebCollector(BaseCollector):
    """جامع تقييمات HTML بمواصفات CSS قابلة للتهيئة لكل متجر."""

    name = "web"

    def __init__(self, pages: List[Dict], pause: float = 2.5):
        """
        pages: [{"url": ..., "item": "css", "text": "css", "author": "css",
                 "rating": "css", "product": "اسم المنتج"}]
        """
        super().__init__(pause=pause)
        self.pages = list(pages or [])

    # ------------------------------------------------------------------ #
    def _extract(self, html: str, spec: Dict) -> List[Mention]:
        if not _BS4:
            # احتياط خام: التقاط فقرات عربية/إنجليزية بسيطة بلا bs4
            return self._naive(html, spec)
        soup = BeautifulSoup(html, "html.parser")
        out: List[Mention] = []
        nodes = soup.select(spec.get("item", ".review"))
        for node in nodes[:60]:
            text_el = node.select_one(spec.get("text", ".text")) or node
            text = _strip(text_el.get_text(" ", strip=True))
            if len(text) < 8:
                continue
            author_el = node.select_one(spec.get("author", ".author"))
            author = mask_author(author_el.get_text(strip=True)) if author_el else "عميل مجهول"
            rating = None
            rating_el = node.select_one(spec.get("rating", ".rating"))
            if rating_el is not None:
                m = re.search(r"([1-5])(?:\.[0-9])?", rating_el.get_text(" ", strip=True))
                if m:
                    rating = int(m.group(1))
            out.append(Mention(text=text[:1000], source="web", author=author,
                               rating=rating,
                               product=spec.get("product", ""),
                               url=spec.get("url", "")))
        return out

    def _naive(self, html: str, spec: Dict) -> List[Mention]:
        """Fallback بدون bs4: فقرات نصية تحتوي كلمات شائعة في التقييمات."""
        out: List[Mention] = []
        for para in re.findall(r"<p[^>]*>(.*?)</p>", html or "", re.DOTALL)[:120]:
            text = _strip(para)
            if len(text) < 20:
                continue
            if re.search(r"[★☆]|[1-5]\s*/\s*5|rating|تقييم", text, re.I):
                m = re.search(r"([1-5])", text)
                rating = int(m.group(1)) if m else None
                out.append(Mention(text=text[:1000], source="web",
                                   rating=rating, product=spec.get("product", ""),
                                   url=spec.get("url", "")))
        return out

    # ------------------------------------------------------------------ #
    def collect(self) -> List[Mention]:
        if requests is None:
            return []
        mentions: List[Mention] = []
        for spec in self.pages:
            url = spec.get("url", "")
            if not url:
                continue
            self._throttle()
            try:
                resp = requests.get(url, headers={"User-Agent": USER_AGENT},
                                    timeout=15)
                if resp.ok:
                    spec = dict(spec, url=url)
                    mentions.extend(self._extract(resp.text, spec))
            except Exception:
                continue
        return mentions
