#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pulse-ZeroBaran | Collectors Base (Data Types + Politeness Contract)
====================================================================
طبقة الجلب والمسح الرقمي: عقد مشترك بين كل الجامعات.

⚠️ الالتزام: يُجمع فقط ما هو متاح **علنياً** وبإذن صاحبه، مع:
  - User-Agent واضح + انتظار بين الطلبات (Rate Limit)
  - احترام robots.txt للنطاق (عدم الزحف على الممنوع)
  - لا جمع بيانات شخصية حساسة (أسماء/إيميلات تُخفى في التخزين)

Author : Baran Avisat <baranavisat@gmail.com>
© 2026 Baran Avisat — All Rights Reserved.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional

USER_AGENT = ("Pulse-ZeroBaran/1.0 (+https://github.com/aoodiakdiro0001-ops/"
              "Pulse-ZeroBaran) respectful-monitor")
REQUEST_PAUSE = 1.5  # ثوانٍ بين طلبات كل جامع (مهذّب دائماً)


@dataclass
class Mention:
    """ذكر مرصود خام (قبل التحليل)."""
    text: str
    source: str = "web"           # rss | web | file | api
    author: str = "عميل مجهول"
    rating: Optional[int] = None  # تقييم بالنجوم إن وُجد (1..5)
    product: str = ""             # المنتج/العلامة المرتبطة
    url: str = ""
    created_at: str = ""          # ISO date أو timestamp
    extra: Dict = field(default_factory=dict)

    def as_dict(self) -> Dict:
        return asdict(self)


class BaseCollector:
    """جامع أساسي: يفرض pause لطيف وUser-Agent واضح."""

    name = "base"

    def __init__(self, pause: float = REQUEST_PAUSE):
        self.pause = pause
        self._last = 0.0

    def _throttle(self) -> None:
        elapsed = time.time() - self._last
        if elapsed < self.pause:
            time.sleep(self.pause - elapsed)
        self._last = time.time()

    def collect(self) -> List[Mention]:   # pragma: no cover - abstract
        raise NotImplementedError


def mask_author(name: str) -> str:
    """إخفاء هوية العميل جزئياً (خصوصية أولاً)."""
    name = (name or "").strip()
    if not name or len(name) < 2:
        return "عميل مجهول"
    return name[0] + "*" * max(2, len(name) - 2)
