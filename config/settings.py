#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pulse-ZeroBaran | Settings (100% Free-Tier Configuration)
==========================================================
إعدادات centralisée عبر .env مع قيم افتراضية تعمل بلا أي مفاتيح.

© 2026 Baran Avisat — All Rights Reserved.
"""
from __future__ import annotations

import os
from typing import Dict

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:  # pragma: no cover
    pass


def _f(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


PROJECT = "Pulse-ZeroBaran"
VERSION = "1.0.0"
AUTHOR = "Baran Avisat"
EMAIL = "baranavisat@gmail.com"
COPYRIGHT = "© 2026 Baran Avisat — All Rights Reserved."


def settings() -> Dict:
    return {
        "project": PROJECT,
        "version": VERSION,
        "brand": os.getenv("PULSE_BRAND", "ZeroBaran Store").strip() or "ZeroBaran Store",
        # الذكاء الاصطناعي (مجاني)
        "gemini_key": os.getenv("GEMINI_API_KEY", "").strip(),
        "groq_key": os.getenv("GROQ_API_KEY", "").strip(),
        # التسليم
        "telegram_token": os.getenv("TELEGRAM_BOT_TOKEN", "").strip(),
        "telegram_chat_id": os.getenv("TELEGRAM_CHAT_ID", "").strip(),
        # قاعدة البيانات
        "supabase_url": os.getenv("SUPABASE_URL", "").strip(),
        "supabase_key": os.getenv("SUPABASE_KEY", "").strip(),
        # المصادر (RSS feeds · صفحات تقييمات)
        "rss_feeds": [u.strip() for u in os.getenv("PULSE_RSS_FEEDS", "").split(",")
                      if u.strip()],
        "web_pages_json": os.getenv("PULSE_WEB_PAGES", "").strip(),
        "file_reviews": os.getenv("PULSE_FILE_REVIEWS", "").strip(),
        # المسارات
        "data_dir": os.getenv("PULSE_DATA_DIR", "data").strip() or "data",
        "output_dir": os.getenv("PULSE_OUTPUT_DIR", "output").strip() or "output",
        # حدّ الإرسال
        "alert_threshold": _f("PULSE_ALERT_THRESHOLD", -0.2),
    }
