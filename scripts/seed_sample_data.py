#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pulse-ZeroBaran | Sample Data Seed (demos + tests — offline, deterministic)
===========================================================================
يولّد مجموعة ذكريات تجريبية ثنائية اللغة (مديح · شكاوى · أزمات) لتجربة
المحرّك واللوحة والتقارير فوراً — بلا شبكة وبلا مفاتيح.

Usage:
    python scripts/seed_sample_data.py            # → data/reviews_sample.csv
    python scripts/seed_sample_data.py --json     # → data/reviews_sample.json

Author : Baran Avisat <baranavisat@gmail.com>
© 2026 Baran Avisat — All Rights Reserved.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

DATA_DIR = os.path.join(ROOT, "data")

SAMPLE = [
    # إيجابي
    {"text": "المنتج ممتاز جداً ووصل بسرعة، أنصح به الجميع!", "author": "سارة",
     "rating": 5, "product": "ZB-Kit", "source": "store", "created_at": "2026-01-03"},
    {"text": "جودة ممتازة وخدمة عملاء متعاونة، شكرًا لكم.",
     "author": "أحمد", "rating": 5, "product": "ZB-Kit", "source": "store",
     "created_at": "2026-01-04"},
    {"text": "Great quality and fast shipping, highly recommend!",
     "author": "Omar", "rating": 5, "product": "ZB-Kit", "source": "web",
     "created_at": "2026-01-05"},
    {"text": "تطبيق سهل الاستخدام وتصميم جميل، أعجبني كثيراً.",
     "author": "Lina", "rating": 4, "product": "App", "source": "store",
     "created_at": "2026-01-06"},
    {"text": "Excellent customer service, they solved my issue in minutes.",
     "author": "Sara", "rating": 5, "product": "App", "source": "web",
     "created_at": "2026-01-07"},
    {"text": "سعر مناسب مقارنة بالجودة، أرشحه لمن يبحث عن قيمة حقيقية.",
     "author": "خالد", "rating": 4, "product": "ZB-Kit", "source": "file",
     "created_at": "2026-01-08"},
    # محايد
    {"text": "المنتج وصل، لم أجرّبه بعد لأحكم عليه لاحقاً.",
     "author": "Mona", "rating": 3, "product": "ZB-Kit", "source": "store",
     "created_at": "2026-01-09"},
    {"text": "It's okay, nothing special but works as described.",
     "author": "Ali", "rating": 3, "product": "App", "source": "web",
     "created_at": "2026-01-10"},
    # سلبي
    {"text": "المنتج وصل تالفاً ولم يعمل معي، أشعر بخيبة أمل كبيرة.",
     "author": "فاطمة", "rating": 1, "product": "ZB-Kit", "source": "store",
     "created_at": "2026-01-11"},
    {"text": "التوصيل تأخر أكثر من أسبوع والدعم لا يرد على اتصالي.",
     "author": "يوسف", "rating": 2, "product": "ZB-Kit", "source": "store",
     "created_at": "2026-01-12"},
    {"text": "The app crashes every time I open it after the update. Worst update ever.",
     "author": "Karim", "rating": 1, "product": "App", "source": "web",
     "created_at": "2026-01-13"},
    {"text": "السعر مرتفع جداً مقابل الجودة المقدمة، أشعر أنني استُغليت.",
     "author": "Huda", "rating": 2, "product": "ZB-Kit", "source": "file",
     "created_at": "2026-01-14"},
    {"text": "خدمة العملاء بطيئة جداً ولم تحل مشكلتي، غير مرضٍ على الإطلاق.",
     "author": "سامي", "rating": 2, "product": "App", "source": "store",
     "created_at": "2026-01-15"},
    # أزمات
    {"text": "احتيال! لم يصل الطلب ويرفضون رد المبلغ، سأبلغ الجهات المختصة.",
     "author": "منى", "rating": 1, "product": "ZB-Kit", "source": "web",
     "created_at": "2026-01-16"},
    {"text": "Scam company, my package was broken and support is ignoring me, worst ever!",
     "author": "Rami", "rating": 1, "product": "ZB-Kit", "source": "web",
     "created_at": "2026-01-17"},
    {"text": "منتج مكسور ورقم الطلب لا يرد، أطالب باسترداد فوري لمعاناتي.",
     "author": "ليلى", "rating": 1, "product": "ZB-Kit", "source": "store",
     "created_at": "2026-01-18"},
    {"text": "Refund request ignored for 2 weeks, furious about this broken item.",
     "author": "Nour", "rating": 1, "product": "App", "source": "file",
     "created_at": "2026-01-19"},
    # إيجابي متأخر (لتتبع الاتجاه)
    {"text": "بعد التحديث الجديد أصبح كل شيء يعمل بسلاسة، ممتاز!",
     "author": "طارق", "rating": 5, "product": "App", "source": "store",
     "created_at": "2026-01-20"},
    {"text": "They replaced my broken unit immediately. Very professional team.",
     "author": "Dina", "rating": 5, "product": "ZB-Kit", "source": "web",
     "created_at": "2026-01-21"},
]

FIELDS = ["text", "author", "rating", "product", "source", "created_at", "url"]


def main() -> None:
    ap = argparse.ArgumentParser(description="Pulse seed sample data")
    ap.add_argument("--json", action="store_true", help="JSON instead of CSV")
    args = ap.parse_args()

    os.makedirs(DATA_DIR, exist_ok=True)
    if args.json:
        path = os.path.join(DATA_DIR, "reviews_sample.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(SAMPLE, fh, ensure_ascii=False, indent=1)
    else:
        path = os.path.join(DATA_DIR, "reviews_sample.csv")
        with open(path, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=FIELDS, extrasaction="ignore")
            w.writeheader()
            w.writerows(SAMPLE)

    print(f"✓ {len(SAMPLE)} ذكر تجريبي → {path}")


if __name__ == "__main__":
    main()
