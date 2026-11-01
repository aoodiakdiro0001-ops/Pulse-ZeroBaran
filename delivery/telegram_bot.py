#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pulse-ZeroBaran | Telegram Bot (Pulse Query Gateway)
=====================================================
بوت تفاعلي لاستعلام نبض السمعة من هاتفك:

  /start | /help   ترحيب
  /pulse           المؤشر العام + آخر الأزمات
  /report          تقرير أسبوعي مختصر
  /alert <id>      عرض تفاصيل أزمة + الرد المقترح

Author : Baran Avisat <baranavisat@gmail.com>
© 2026 Baran Avisat — All Rights Reserved.
"""
from __future__ import annotations

import json
import os
import sys
from typing import Dict, List, Optional

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from core.crisis import CrisisEngine                       # noqa: E402
from core.trends import (daily_scores, label_distribution,  # noqa: E402
                         overall_score, weekly_report)
from delivery.notifier import send_message                 # noqa: E402

try:
    import requests
except Exception:  # pragma: no cover
    requests = None

API = "https://api.telegram.org/bot{token}/{method}"
HELP = ("Pulse-ZeroBaran — رصد مشاعر العملاء\n"
        "/pulse   → المؤشر العام + آخر الأزمات\n"
        "/report  → تقرير أسبوعي\n"
        "/alert   → آخر أزمة مع الرد المقترح\n"
        "/help    → المساعدة")


def _load_records() -> List[Dict]:
    """قراءة آخر تحليلات محفوظة (output/ أو Supabase)."""
    path = os.path.join(ROOT, "output", "pulse_latest.json")
    if os.path.exists(path):
        try:
            d = json.load(open(path, encoding="utf-8"))
            return list(d.get("records") or d.get("mentions") or [])
        except Exception:
            return []
    try:
        from db import supabase_client as sb
        return sb.load_all()
    except Exception:
        return []


class PulseBot:
    """بوت نبض السمعة (polling خفيف)."""

    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        self.engine = CrisisEngine()

    # ------------------------------------------------------------------ #
    def handle(self, text: str) -> str:
        text = (text or "").strip()
        records = _load_records()
        if text in ("/start", "/help"):
            return HELP
        if text.startswith("/pulse"):
            if not records:
                return "لا توجد بيانات مرصودة بعد — شغّل: python scripts/scan_pulse.py"
            score = overall_score(records)
            dist = label_distribution(records)
            days = daily_scores(records)
            crises = [r for r in records
                      if r.get("crisis") or r.get("severity") in ("critical", "major")]
            last_day = list(days.items())[-3:] if days else []
            lines = ["🎯 نبض السمعة (Pulse)",
                     f"المؤشر العام: {score:+.2f}",
                     f"إيجابي {dist['positive']} · محايد {dist['neutral']} · سلبي {dist['negative']}",
                     f"أزمات مرصودة: {len(crises)}"]
            if last_day:
                lines.append("آخر الأيام: " + " · ".join(f"{d}:{s:+.2f}" for d, s in last_day))
            if crises:
                top = max(crises, key=lambda r: r.get("score", 0))
                lines.append("")
                lines.append(self.engine.alert_text(top))
            return "\n".join(lines)[:3800]
        if text.startswith("/report"):
            if not records:
                return "لا توجد بيانات — شغّل scan_pulse أولاً."
            return weekly_report(records)
        if text.startswith("/alert"):
            crises = [r for r in records
                      if r.get("crisis") or r.get("severity") in ("critical", "major")]
            if not crises:
                return "✅ لا أزمات مفتوحة — السمعة تحت السيطرة."
            return self.engine.alert_text(crises[0])
        return HELP

    # ------------------------------------------------------------------ #
    def poll_forever(self) -> None:
        if not self.token or requests is None:
            print("⚠️  ضع TELEGRAM_BOT_TOKEN في .env لتشغيل البوت.")
            return
        offset = 0
        print("📡 Pulse-ZeroBaran bot polling… (Ctrl+C للإيقاف)")
        while True:
            try:
                r = requests.get(API.format(token=self.token, method="getUpdates"),
                                 params={"offset": offset, "timeout": 30}, timeout=40)
                for upd in r.json().get("result", []):
                    offset = upd["update_id"] + 1
                    msg = upd.get("message") or {}
                    chat = str((msg.get("chat") or {}).get("id", ""))
                    if chat:
                        send_message(self.handle(msg.get("text", "")), chat_id=chat,
                                     token=self.token)
            except KeyboardInterrupt:
                print("\nتم إيقاف البوت.")
                return
            except Exception:
                continue


def main() -> None:
    PulseBot().poll_forever()


if __name__ == "__main__":
    main()
