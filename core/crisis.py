#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pulse-ZeroBaran | Crisis Detection & Response Suggestions
==========================================================
طبقة الأزمات: تحديد التعليقات التي تستوجب تدخلاً سريعاً + صياغة رد
احترافي مقترح (اعتذار + آلية تعويض) بناءً على جذر المشكلة والنبرة.

الردود المقترحة قوالب حتمية Offline (عربية مهنية) + إعادة صياغة اختيارية
عبر Gemini/Groq إن توفر المفتاح.

Author : Baran Avisat <baranavisat@gmail.com>
© 2026 Baran Avisat — All Rights Reserved.
"""
from __future__ import annotations

import os
import re
from typing import Dict, List, Optional

try:
    import requests
except Exception:  # pragma: no cover
    requests = None

GEMINI_URL = ("https://generativelanguage.googleapis.com/v1beta/models/"
              "gemini-1.5-flash:generateContent?key={key}")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# ---------------- قوالب الردود المقترحة (حتمية · Offline) ---------------- #
_REPLIES = {
    "product-quality": (
        "أهلاً {author}، نعتذر بصدق عن تجربتك مع {product}. هذه ليست "
        "المعيار الذي نعمل عليه. سنقوم فوراً بفحص طلبك واستبدال المنتج "
        "التالف أو رد المبلغ كاملاً خلال 48 ساعة. يسعدنا متابعتك شخصياً "
        "حتى نتأكد من رضاك التام."),
    "shipping": (
        "أهلاً {author}، نأسف على تأخر شحنتك ({product}). تواصلنا الآن مع "
        "شركة الشحن لمعرفة موضعها الدقيق، وسنعيد إرسال الطلب مجاناً إن لم "
        "يصل خلال 3 أيام عمل. سنوافيك بالتحديث اليوم."),
    "price": (
        "أهلاً {author}، شكرًا لمشاركتنا رأيك في سعر {product}. نراجع "
        "تسعيرتنا باستمرار، وسنرسل لك كود خصم خاص بطلبك القادم كنوع من "
        "تقديرنا لانطباعك."),
    "support": (
        "أهلاً {author}، نعتذر عن تأخّر الرد على استفسارك ({product}). "
        "أولوية قصوى لدينا الآن: تم تحويل طلبك لمختص وسيصلك رد شامل خلال "
        "ساعتين كحد أقصى، مع متابعة خاصة حتى الحل."),
    "bug": (
        "أهلاً {author}، شكرًا لإبلاغنا بالخطأ في {product}. فريقنا يراجع "
        "البلاغ الآن، وسننشر تحديثاً يعالج المشكلة. سنعلمك فور نشر الإصلاح، "
        "ونقدّر صبرك وتعاونك."),
    "privacy": (
        "أهلاً {author}، نأخذ خصوصيتك على محمل الجد. تم تفعيل فريق الأمن "
        "للتحقيق الفوري في تقريرك ({product}). سنوافيك بنتائج التحقيق خلال "
        "24 ساعة، ولن نشارك بياناتك مع أي طرف ثالث."),
    "none": (
        "أهلاً {author}، شكرًا لمراسلتنا بخصوص {product}. نأخذ ملاحظتك بعين "
        "الاعتبار وسنعود إليك برد شامل خلال 24 ساعة."),
}
_PRaise = ("أهلاً {author}! شكرًا جزيلاً لثقتك في {product} — سعداء جداً "
           "بانطباعك، ونسعد بخدمتك دوماً. ❤️")


def _clean(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip()


def suggested_reply(result: Dict, product: str = "منتجنا", author: str = "عميلنا",
                    lang: str = "ar") -> str:
    """مسودة رد احترافية حسب النبرة وجذر المشكلة (Offline حتمي)."""
    product = _clean(str(product)) or "منتجنا"
    author = _clean(str(author)) or "عميلنا"
    if result.get("label") == "positive" or result.get("severity") == "positive":
        return _PRaise.format(author=author, product=product)
    root = result.get("root_cause", "none")
    tpl = _REPLIES.get(root, _REPLIES["none"])
    return tpl.format(author=author, product=product)


class CrisisEngine:
    """محرّك إدارة الأزمات: ترتيب خطورة التعليقات + مسودات الردود."""

    def __init__(self, gemini_key: Optional[str] = None,
                 groq_key: Optional[str] = None, timeout: int = 12):
        self.gemini_key = gemini_key or os.getenv("GEMINI_API_KEY", "").strip()
        self.groq_key = groq_key or os.getenv("GROQ_API_KEY", "").strip()
        self.timeout = timeout

    # ------------------------------------------------------------------ #
    def _ai_rephrase(self, draft: str, severity: str) -> Optional[str]:
        if requests is None or not (self.gemini_key or self.groq_key):
            return None
        prompt = ("أعد صياغة مسودة رد احترافية على شكوى عميل بخطورة "
                  f"{severity} بنبرة متعاطفة ومقنعة، 3-5 جمل، العربية فقط:\n" + draft)
        try:
            if self.gemini_key:
                r = requests.post(GEMINI_URL.format(key=self.gemini_key),
                                  json={"contents": [{"parts": [{"text": prompt}]}],
                                        "generationConfig": {"maxOutputTokens": 220,
                                                             "temperature": 0.6}},
                                  timeout=self.timeout)
                if r.ok:
                    txt = r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                    return _clean(txt)[:700] or None
            if self.groq_key:
                r = requests.post(GROQ_URL,
                                  headers={"Authorization": "Bearer " + self.groq_key},
                                  json={"model": "llama-3.1-8b-instant",
                                        "messages": [{"role": "user", "content": prompt}],
                                        "max_tokens": 220, "temperature": 0.6},
                                  timeout=self.timeout)
                if r.ok:
                    txt = r.json()["choices"][0]["message"]["content"].strip()
                    return _clean(txt)[:700] or None
        except Exception:
            return None
        return None

    # ------------------------------------------------------------------ #
    def handle(self, mention: Dict, author: str = "عميلنا",
               product: str = "منتجنا") -> Dict:
        """إرفاق مسودة رد + مؤشرات أزمة بسجل ذكر مُحلَّل."""
        severity = mention.get("severity", "neutral")
        draft = suggested_reply(mention, product=product, author=author)
        used = "offline"
        ai = self._ai_rephrase(draft, severity)
        if ai:
            draft, used = ai, "ai"
        out = dict(mention)
        out["suggested_reply"] = draft
        out["reply_backend"] = used
        out["needs_action"] = bool(mention.get("crisis") or
                                   severity in ("critical", "major"))
        out["priority"] = {"critical": 1, "major": 2, "minor": 3,
                           "neutral": 4, "positive": 5}.get(severity, 4)
        return out

    # ------------------------------------------------------------------ #
    def alert_text(self, mention: Dict, product: str = "منتجنا") -> str:
        """نص تنبيه تليجرام جاهز للإرسال لأي ذكر سلبي/أزمة."""
        sev = mention.get("severity", "minor")
        icon = "🚨" if sev == "critical" else "⚠️"
        lines = [f"{icon} تنبيه رصد مشاعر — خطورة: {sev}",
                 f"💬 النص: {(mention.get('text') or '')[:240]}",
                 f"📦 المنتج: {product} · المصدر: {mention.get('source', 'web')}"]
        if mention.get("root_cause", "none") != "none":
            lines.append(f"🧩 جذر المشكلة: {mention.get('root_cause')}")
        if mention.get("suggested_reply"):
            lines.append(f"💡 الرد المقترح: {mention['suggested_reply']}")
        lines.append("_تقديرات إرشادية للرصد المبكر · © 2026 Baran Avisat_")
        return "\n".join(lines)[:3800]
