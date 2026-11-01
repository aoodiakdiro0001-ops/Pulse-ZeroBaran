#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pulse-ZeroBaran | AI Sentiment Core (Hybrid: Offline deterministic + Free AI)
=============================================================================
محلّل المشاعر:
  1) محرّك حتمي Offline (الافتراضي): قاموس ثنائي اللغة + نفي + تشديد +
     إشارة تقييم النجوم → درجة [-1 .. +1] + نبرة + جذر المشكلة.
  2) مسار AI اختياري (Gemini / Groq Free Tiers) لتحسين الصياغة عند توفر المفتاح.

لا ادعاءات دقة ممنوعة: الدرجات «تقديرية إرشادية» للرصد المبكر.

Author : Baran Avisat <baranavisat@gmail.com>
© 2026 Baran Avisat — All Rights Reserved.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple

from .lexicon import (CRISIS_KEYWORDS, INTENSIFIERS, NEGATION, NEGATIVE,
                      NEG_STEMS, POSITIVE, POS_STEMS)

try:
    import requests
except Exception:  # pragma: no cover
    requests = None

GEMINI_URL = ("https://generativelanguage.googleapis.com/v1beta/models/"
              "gemini-1.5-flash:generateContent?key={key}")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

_WORD_RE = re.compile(r"[A-Za-z']+|[^\W\d_]+", re.UNICODE)


@dataclass
class SentimentResult:
    """نتيجة تحليل مشاعر تعليق واحد."""
    label: str            # positive | neutral | negative
    score: float          # [-1 .. +1] تقديرية
    tone: str             # praise | technical-complaint | service-complaint |
                          # anger | suggestion | mixed | neutral
    root_cause: str       # product-quality | shipping | price | support | bug |
                          # privacy | none
    crisis: bool          # هل يستوجب تنبيهاً فورياً؟
    severity: str         # critical | major | minor | positive | neutral
    backend: str          # offline | gemini | groq
    reasons: List[str]    # إشارات مستخدمة (شفافية القرار)

    def as_dict(self) -> Dict:
        return asdict(self)


def _words(text: str) -> List[str]:
    return _WORD_RE.findall((text or "").lower())


def _rating_signal(rating: Optional[int]) -> Tuple[float, str]:
    """إشارة تقييم النجوم إن وُجدت: خفيفة الوزن (0.35 من القرار)."""
    if not rating:
        return 0.0, ""
    try:
        r = max(1, min(5, int(rating)))
    except (TypeError, ValueError):
        return 0.0, ""
    val = (r - 3) / 2.0          # 1★ → -1 · 3★ → 0 · 5★ → +1
    return round(val * 0.35, 4), f"rating:{r}★"


# ------------------------- تصنيف جذر المشكلة ------------------------- #
_CAUSE_RULES = [
    ("product-quality", ("تالف", "تالفة", "مكسور", "معطل", "عيب", "جودة",
                         "رديء", "بلاستيك", "تقطع", "تقطعت", "defect",
                         "broken", "damaged", "quality", "flimsy")),
    ("shipping", ("توصيل", "شحن", "وصل", "وصول", "توصيل", "الشحن", "البريد",
                 "مندوب", "تأخير", "متأخر", "late", "shipping", "delivery",
                 "arrived", "courier", "package")),
    ("price", ("غالي", "سعر", "تكلفة", "باهظ", "استغلال", "مبالغ", "overpriced",
               "expensive", "price", "cost", "value")),
    ("support", ("دعم", "خدمة", "خدمة العملاء", "رد", "استشارة", "اتصال",
                 "واتساب", "انتظار", "support", "service", "response",
                 "customer care", "contact")),
    ("bug", ("لا يعمل", "يعمل", "خطأ", "برمجي", "تطبيق", "هذا التطبيق",
             "crash", "bug", "error", "glitch", "freeze", "update", "login")),
    ("privacy", ("خصوصية", "بياناتي", "تسريب", "khososiya", "leak",
                 "privacy", "data breach", "compromised")),
]


def classify_root_cause(text: str) -> str:
    low = (text or "").lower()
    for cause, keys in _CAUSE_RULES:
        if any(k in low for k in keys):
            return cause
    return "none"


def classify_tone(text: str, score: float, root: str) -> str:
    low = (text or "").lower()
    anger_hits = sum(1 for k in ("احتيال", "نصاب", "حرام", "فاضح", "كارثة",
                                 "scam", "furious", "worst", "fraud") if k in low)
    if anger_hits >= 1 or score <= -0.6:
        return "anger"
    if root == "bug":
        return "technical-complaint"
    if root in ("support", "shipping", "price"):
        return "service-complaint"
    if any(k in low for k in ("اقترح", "نوعية", "أتمنى", "ارجوا", "ارجو",
                              "suggestion", "wish", "please add", "feature")):
        return "suggestion"
    if score >= 0.3:
        return "praise"
    if score <= -0.2:
        return "technical-complaint" if root != "none" else "service-complaint"
    return "neutral"


def severity_of(score: float, label: str, text: str) -> str:
    low = (text or "").lower()
    if label == "positive" or score >= 0.25:
        return "positive"
    crisis_hit = any(k in low for k in CRISIS_KEYWORDS)
    if score <= -0.6 or crisis_hit and score < 0:
        return "critical"
    if score <= -0.35:
        return "major"
    if score < -0.1:
        return "minor"
    return "neutral"


class SentimentAnalyzer:
    """محلّل المشاعر الهجين: Offline حتمي + مسار AI اختياري."""

    def __init__(self, gemini_key: Optional[str] = None,
                 groq_key: Optional[str] = None, timeout: int = 12):
        self.gemini_key = gemini_key or os.getenv("GEMINI_API_KEY", "").strip()
        self.groq_key = groq_key or os.getenv("GROQ_API_KEY", "").strip()
        self.timeout = timeout
        self.backend = "gemini" if self.gemini_key else (
            "groq" if self.groq_key else "offline")

    # ------------------------- المحرّك الحتمي ------------------------- #
    def analyze_offline(self, text: str, rating: Optional[int] = None
                        ) -> SentimentResult:
        words = _words(text)
        reasons: List[str] = []
        raw = 0.0
        neg_window = 0
        for i, w in enumerate(words):
            if w in NEGATION or w in {x.lower() for x in NEGATION}:
                neg_window = 2
                reasons.append(f"negation:{w}")
                continue
            weight = 0.0
            if w in {x.lower() for x in POSITIVE} or any(w.startswith(s) for s in POS_STEMS):
                weight = 0.22
            elif w in {x.lower() for x in NEGATIVE} or any(w.startswith(s) for s in NEG_STEMS):
                weight = -0.22
            if weight != 0.0:
                if i + 1 < len(words) and words[i + 1] in {x.lower() for x in INTENSIFIERS}:
                    weight *= 1.6
                    reasons.append("intensifier")
                if neg_window > 0:
                    weight *= -0.85   # «لا يعمل» ⇒ سلبي رغم اللفظ الإيجابي
                    neg_window -= 1
                raw += weight
        # تطبيع: قصّ الطرفين ثم دمج إشارة النجوم (إن وُجدت)
        raw = max(-1.0, min(1.0, raw * 0.75))
        r_sig, r_reason = _rating_signal(rating)
        if r_reason:
            reasons.append(r_reason)
        score = max(-1.0, min(1.0, 0.65 * raw + 0.35 * r_sig)) if rating \
            else max(-1.0, min(1.0, raw))

        if score >= 0.12:
            label = "positive"
        elif score <= -0.12:
            label = "negative"
        else:
            label = "neutral"
        root = classify_root_cause(text)
        if root != "none":
            reasons.append("root:" + root)
        tone = classify_tone(text, score, root)
        severity = severity_of(score, label, text)
        crisis = severity in ("critical", "major")
        return SentimentResult(label=label, score=round(score, 4), tone=tone,
                               root_cause=root, crisis=crisis,
                               severity=severity, backend="offline",
                               reasons=reasons[:8])

    # ------------------------- مسار الذكاء الاصطناعي ------------------------- #
    def _ai_analyze(self, text: str, rating: Optional[int]) -> Optional[SentimentResult]:
        if requests is None:
            return None
        prompt = ("حلّل مشاعر هذا التعليق بالعربية. أعد JSON فقط بالحقول: "
                  'label ("positive"|"neutral"|"negative"), score (-1..1), '
                  'tone (praise|technical-complaint|service-complaint|anger|'
                  'suggestion|mixed|neutral), root_cause (product-quality|'
                  'shipping|price|support|bug|privacy|none), crisis (true|'
                  'false).\nالتعليق: ' + (text or "")[:1200] +
                  (f"\nتقييم النجوم: {rating}/5" if rating else ""))
        try:
            if self.gemini_key:
                resp = requests.post(GEMINI_URL.format(key=self.gemini_key),
                                     json={"contents": [{"parts": [{"text": prompt}]}],
                                           "generationConfig": {"temperature": 0.2,
                                                                "responseMimeType": "application/json"}},
                                     timeout=self.timeout)
                if resp.ok:
                    return self._parse(resp.json()["candidates"][0]["content"]["parts"][0]["text"])
            if self.groq_key:
                resp = requests.post(GROQ_URL,
                                     headers={"Authorization": "Bearer " + self.groq_key},
                                     json={"model": "llama-3.1-8b-instant",
                                           "messages": [{"role": "user", "content": prompt}],
                                           "temperature": 0.2},
                                     timeout=self.timeout)
                if resp.ok:
                    return self._parse(resp.json()["choices"][0]["message"]["content"])
        except Exception:
            return None
        return None

    @staticmethod
    def _parse(blob: str) -> Optional[SentimentResult]:
        import json
        m = re.search(r"\{.*\}", blob or "", re.DOTALL)
        if not m:
            return None
        try:
            d = json.loads(m.group(0))
            label = str(d.get("label", "neutral")).lower()
            score = float(d.get("score", 0.0))
            return SentimentResult(label=label, score=max(-1.0, min(1.0, score)),
                                   tone=str(d.get("tone", "neutral")),
                                   root_cause=str(d.get("root_cause", "none")),
                                   crisis=bool(d.get("crisis", False)),
                                   severity=str(d.get("severity", "auto")),
                                   backend="ai", reasons=["ai-judge"])
        except Exception:
            return None

    # ------------------------- الواجهة الموحّدة ------------------------- #
    def analyze(self, text: str, rating: Optional[int] = None) -> SentimentResult:
        """تحليل تعليق واحد (AI إن توفر وإلا Offline الحتمي)."""
        offline = self.analyze_offline(text, rating)
        if self.backend in ("gemini", "groq"):
            ai = self._ai_analyze(text, rating)
            if ai is not None:
                # ندمج: درجة AI + تحقق أزمة من القاموس المحلي
                ai.severity = severity_of(ai.score, ai.label, text)
                ai.crisis = ai.crisis or ai.severity in ("critical", "major")
                ai.backend = self.backend
                ai.reasons = (ai.reasons or []) + offline.reasons[:3]
                return ai
        return offline

    def analyze_batch(self, items: List[Dict]) -> List[Dict]:
        """تحليل دفعة تعليقات [{text, rating?}] مع إرفاق النتائج."""
        out: List[Dict] = []
        for item in items:
            res = self.analyze(item.get("text", ""), item.get("rating"))
            row = dict(item)
            row.update(res.as_dict())
            out.append(row)
        return out
