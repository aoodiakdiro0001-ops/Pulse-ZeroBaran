#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pulse-ZeroBaran | Telegram Alerts Channel (Instant + Weekly)
=============================================================
قناة التنبيه الفوري: إرسال إنذارات الأزمات (مع الرد المقترح) وحصيلة
أسبوعية عبر Telegram Bot API (مجانية).

Author : Baran Avisat <baranavisat@gmail.com>
© 2026 Baran Avisat — All Rights Reserved.
"""
from __future__ import annotations

import os
from typing import Dict, List, Optional, Sequence

try:
    import requests
except Exception:  # pragma: no cover
    requests = None

API = "https://api.telegram.org/bot{token}/{method}"
MAX_LEN = 3900


def _esc(t: str) -> str:
    for ch in ("_", "*", "`", "["):
        t = (t or "").replace(ch, "\\" + ch)
    return t


def send_message(text: str, chat_id: Optional[str] = None,
                 token: Optional[str] = None, timeout: int = 15) -> bool:
    """إرسال رسالة عبر تليجرام (يتجاهل بصمت إن لم يُضبط — وضع Offline)."""
    if requests is None:
        return False
    token = (token or os.getenv("TELEGRAM_BOT_TOKEN", "")).strip()
    chat_id = (chat_id or os.getenv("TELEGRAM_CHAT_ID", "")).strip()
    if not token or not chat_id:
        return False
    try:
        r = requests.post(API.format(token=token, method="sendMessage"),
                          json={"chat_id": chat_id, "text": (text or "")[:MAX_LEN],
                                "disable_web_page_preview": True},
                          timeout=timeout)
        return bool(r.ok and r.json().get("ok"))
    except Exception:
        return False


def format_alert(crisis: Dict) -> str:
    """تنسيق إنذار أزمة فوري (بنموذج الطلب: نص + رد مقترح)."""
    sev = crisis.get("severity", "minor")
    icon = "🚨" if sev == "critical" else "⚠️"
    lines = [f"{icon} *تنبيه رصد تعليق سلبي* — خطورة: `{_esc(str(sev))}`"]
    if crisis.get("rating"):
        lines.append(f"⭐ تقييم: {crisis['rating']}/5")
    lines.append(f"💬 *نص الشكوى:* {_esc(str(crisis.get('text', ''))[:300])}")
    if crisis.get("root_cause") and crisis.get("root_cause") != "none":
        lines.append(f"🧩 جذر المشكلة: `{_esc(str(crisis['root_cause']))}`")
    if crisis.get("product"):
        lines.append(f"📦 المنتج: {_esc(str(crisis['product']))}")
    if crisis.get("suggested_reply"):
        lines.append(f"💡 *الرد المقترح:* {_esc(str(crisis['suggested_reply'])[:600])}")
    lines.append("_تقديرات إرشادية · © 2026 Baran Avisat_")
    return "\n".join(lines)[:MAX_LEN]


def send_alert(crisis: Dict, token: Optional[str] = None,
               chat_id: Optional[str] = None) -> bool:
    """إرسال إنذار أزمة واحد فوراً."""
    return send_message(format_alert(crisis), token=token, chat_id=chat_id)


def format_weekly(report_text: str, brand: str = "علامتك التجارية") -> str:
    """إطار تقرير أسبوعي جاهز للإرسال."""
    return (f"📊 *Pulse-ZeroBaran — تقرير أسبوعي*\n"
            f"{report_text}\n\n"
            f"_المصدر: {brand} · © 2026 Baran Avisat_")[:MAX_LEN]


def send_crisis_batch(crises: Sequence[Dict],
                      token: Optional[str] = None,
                      chat_id: Optional[str] = None) -> int:
    """إرسال دفعة إنذارات (بحد أقصى 4 رسائل لتفادي الازدحام)."""
    sent = 0
    for crisis in list(crises)[:4]:
        if send_alert(crisis, token=token, chat_id=chat_id):
            sent += 1
    return sent
