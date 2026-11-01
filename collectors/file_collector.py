#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pulse-ZeroBaran | File Collector (CSV/JSON review import)
==========================================================
جامع الملفات: يستورد تقييمات متجرك من CSV/JSON المحلي (مثلاً تصدير من
لوحة تحكم متجرك أو ملف مجمّع يدوياً) — يعمل دائماً بلا شبكة.

الصيغ المدعومة:
  CSV : text,author,rating,product,created_at,url   (الحد الأدنى: text)
  JSON: [{"text": "...", "rating": 5, ...}, ...]

Author : Baran Avisat <baranavisat@gmail.com>
© 2026 Baran Avisat — All Rights Reserved.
"""
from __future__ import annotations

import csv
import json
import os
from typing import List

from .base import BaseCollector, Mention, mask_author


class FileCollector(BaseCollector):
    name = "file"

    def __init__(self, path: str):
        super().__init__(pause=0.0)
        self.path = path

    def collect(self) -> List[Mention]:
        if not os.path.exists(self.path):
            return []
        mentions: List[Mention] = []
        if self.path.lower().endswith(".json"):
            try:
                data = json.load(open(self.path, encoding="utf-8"))
            except Exception:
                return []
            if isinstance(data, dict):
                data = data.get("reviews") or data.get("mentions") or []
            for row in data:
                if not isinstance(row, dict) or not row.get("text"):
                    continue
                mentions.append(self._to_mention(row))
            return mentions
        with open(self.path, newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                if not row.get("text"):
                    continue
                mentions.append(self._to_mention(row))
        return mentions

    @staticmethod
    def _to_mention(row: dict) -> Mention:
        rating = row.get("rating")
        try:
            rating = int(str(rating).strip()) if rating not in (None, "") else None
        except (TypeError, ValueError):
            rating = None
        return Mention(
            text=str(row.get("text", "")).strip()[:1200],
            source=str(row.get("source") or "file"),
            author=mask_author(str(row.get("author", "") or "")),
            rating=rating,
            product=str(row.get("product", "") or ""),
            url=str(row.get("url", "") or ""),
            created_at=str(row.get("created_at", "") or ""),
        )
