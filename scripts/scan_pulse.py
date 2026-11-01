#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pulse-ZeroBaran | Main Scan Pipeline (Collect → Analyze → Persist → Alert)
===========================================================================
المدخل الرئيسي للـ cron (GitHub Actions كل بضع ساعات):

  1) جمع الذكريات من المصادر (RSS · صفحات تقييمات · ملفات CSV/JSON)
  2) تحليل المشاعر (محرّك Offline حتمي · AI اختياري Gemini/Groq)
  3) إدارة الأزمات (مسودات ردود احترافية)
  4) التخزين (Supabase إن توفر · محلي دائماً output/pulse_latest.json)
  5) التنبيه الفوري (Telegram للأزمات)

يعمل دائماً بلا أي مفتاح (وضع Offline كامل) — المفاتيح تُضيف قوة فقط.

Usage:
    python scripts/scan_pulse.py                 # مسح كامل (افتراضي: data/*.csv)
    python scripts/scan_pulse.py --dry-run       # بلا إرسال تنبيهات
    python scripts/scan_pulse.py --file data/reviews_sample.csv

Author : Baran Avisat <baranavisat@gmail.com>
© 2026 Baran Avisat — All Rights Reserved.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from collectors.base import Mention, mask_author                # noqa: E402
from collectors.file_collector import FileCollector             # noqa: E402
from collectors.rss_collector import RssCollector               # noqa: E402
from collectors.web_collector import WebCollector               # noqa: E402
from config.settings import settings                            # noqa: E402
from core.crisis import CrisisEngine                            # noqa: E402
from core.sentiment import SentimentAnalyzer                    # noqa: E402
from core.trends import (crisis_count, daily_scores,            # noqa: E402
                         label_distribution, overall_score,
                         weekly_report)
from delivery import notifier                                   # noqa: E402


def _collect(cfg) -> list:
    mentions: list = []
    # 1) ملفات محلية (دائمة العمل)
    file_path = cfg["file_reviews"]
    if file_path and os.path.exists(file_path):
        mentions += FileCollector(file_path).collect()
    else:
        for name in ("reviews_sample.csv", "reviews_sample.json"):
            p = os.path.join(ROOT, "data", name)
            if os.path.exists(p):
                mentions += FileCollector(p).collect()
    # 2) RSS feeds
    if cfg["rss_feeds"]:
        mentions += RssCollector(cfg["rss_feeds"],
                                 brand_terms=[cfg["brand"]]).collect()
    # 3) صفحات تقييمات HTML
    if cfg["web_pages_json"]:
        try:
            pages = json.loads(cfg["web_pages_json"])
            mentions += WebCollector(pages).collect()
        except Exception:
            pass
    # إخفاء الهويات + قصّ النصوص
    for m in mentions:
        m.author = mask_author(m.author)
        m.text = (m.text or "")[:1200]
    return mentions


def run(dry_run: bool = False, brand: str = "") -> dict:
    cfg = settings()
    brand = brand or cfg["brand"]
    analyzer = SentimentAnalyzer()
    engine = CrisisEngine()

    mentions = _collect(cfg)
    if not mentions:
        print("⚠️ لا توجد ذكريات جديدة هذا المسح.")
        return {"records": [], "crises": 0}

    # تحليل دفعة
    records = []
    for m in mentions:
        res = analyzer.analyze(m.text, m.rating)
        row = m.as_dict()
        row.update(res.as_dict())
        row = engine.handle(row, author=m.author, product=m.product or brand)
        records.append(row)

    # إحصاءات
    dist = label_distribution(records)
    score = overall_score(records)
    crises = [r for r in records
              if r.get("crisis") or r.get("severity") in ("critical", "major")]
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    stats = {"avg_score": score, "positive": dist["positive"],
             "neutral": dist["neutral"], "negative": dist["negative"],
             "crises": len(crises)}

    # تخزين محلي دائماً + Supabase إن توفر
    os.makedirs(os.path.join(ROOT, "output"), exist_ok=True)
    out_path = os.path.join(ROOT, "output", "pulse_latest.json")
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump({"day": day, "brand": brand, "stats": stats,
                   "records": records, "report": weekly_report(records, brand)},
                  fh, ensure_ascii=False, indent=1)

    sb_note = "محلي"
    try:
        from db import supabase_client as sb
        if sb.available():
            n = sb.save_mentions(records)
            sb.save_analysis(records)
            sb.save_crises(crises)
            sb.save_daily(day, stats)
            sb_note = f"supabase:{n}"
    except Exception:
        pass

    # تنبيه فوري للأزمات
    sent = 0
    if crises and not dry_run:
        sent = notifier.send_crisis_batch(crises)

    print(f"✅ مسح مكتمل: {len(records)} ذكر · إيجابي {dist['positive']} · "
          f"محايد {dist['neutral']} · سلبي {dist['negative']} · أزمات {len(crises)}")
    print(f"   المؤشر العام: {score:+.2f} · التخزين: {sb_note} · "
          f"تنبيهات تليجرام: {sent}")
    return {"records": records, "crises": len(crises), "score": score,
            "stats": stats, "sent": sent}


def main() -> None:
    ap = argparse.ArgumentParser(description="Pulse-ZeroBaran main scan")
    ap.add_argument("--dry-run", action="store_true",
                    help="لا ترسل تنبيهات تليجرام")
    ap.add_argument("--file", default="", help="ملف تقييمات محدد (csv/json)")
    ap.add_argument("--brand", default="", help="اسم العلامة للتقارير")
    args = ap.parse_args()

    if args.file:
        os.environ["PULSE_FILE_REVIEWS"] = args.file
    run(dry_run=args.dry_run, brand=args.brand)


if __name__ == "__main__":
    main()
