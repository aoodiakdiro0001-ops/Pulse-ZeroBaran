#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pulse-ZeroBaran | Weekly Reputation Report
===========================================
يقرأ آخر نتائج المسح المحفوظة ويولّد تقريراً أسبوعياً عربياً:
المؤشر العام · توزيع المشاعر · الاتجاه · الأزمات وأسبابها — جاهز
للإرسال عبر تليجرام أو حفظه في output/.

Usage:
    python scripts/weekly_report.py            # طباعة التقرير
    python scripts/weekly_report.py --send     # إرساله لتليجرام (إن مُضبط)

Author : Baran Avisat <baranavisat@gmail.com>
© 2026 Baran Avisat — All Rights Reserved.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Dict, List

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from core.trends import weekly_report            # noqa: E402
from delivery import notifier                    # noqa: E402

LATEST = os.path.join(ROOT, "output", "pulse_latest.json")


def _load() -> Dict:
    if not os.path.exists(LATEST):
        return {}
    try:
        return json.load(open(LATEST, encoding="utf-8"))
    except Exception:
        return {}


def main() -> None:
    ap = argparse.ArgumentParser(description="Pulse weekly report")
    ap.add_argument("--send", action="store_true", help="إرسال عبر تليجرام")
    args = ap.parse_args()

    data = _load()
    records: List[Dict] = list(data.get("records") or [])
    brand = data.get("brand", "علامتك التجارية")
    if not records:
        print("⚠️ لا توجد بيانات محفوظة — شغّل scan_pulse.py أولاً.")
        return

    report = weekly_report(records, brand)
    print(report)

    if args.send:
        ok = notifier.send_message(notifier.format_weekly(report, brand))
        print("\n✅ أُرسل التقرير إلى تليجرام." if ok
              else "\n⚠️ تعذّر الإرسال (اضبط TELEGRAM_BOT_TOKEN / CHAT_ID).")


if __name__ == "__main__":
    main()
