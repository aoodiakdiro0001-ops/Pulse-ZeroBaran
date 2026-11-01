#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pulse-ZeroBaran | Test Suite (10 tests — run directly, no pytest needed)
=========================================================================
python tests/test_pulse.py   ·   كل الاختبارات حتمية Offline بلا شبكة.

Author : Baran Avisat <baranavisat@gmail.com>
© 2026 Baran Avisat — All Rights Reserved.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from collectors.base import Mention, mask_author               # noqa: E402
from collectors.file_collector import FileCollector            # noqa: E402
from collectors.rss_collector import RssCollector             # noqa: E402
from core.crisis import CrisisEngine, suggested_reply          # noqa: E402
from core.sentiment import SentimentAnalyzer                  # noqa: E402
from core.trends import (crisis_count, daily_scores,          # noqa: E402
                         delta_vs_previous, label_distribution,
                         overall_score, weekly_report)

PASS = 0
FAIL = 0


def check(name: str, cond: bool, detail: str = "") -> None:
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✓ {name}")
    else:
        FAIL += 1
        print(f"  ✗ {name} {detail}")


def test_sentiment_positive_ar() -> None:
    a = SentimentAnalyzer()
    r = a.analyze("المنتج ممتاز جداً وأنصح به الجميع")
    check("sentiment: عربي إيجابي → positive",
          r.label == "positive" and r.score > 0.12, f"got {r.label}/{r.score}")


def test_sentiment_negative_ar_with_rating() -> None:
    a = SentimentAnalyzer()
    r = a.analyze("وصل تالفاً ولم يعمل، أشعر بخيبة أمل", rating=1)
    check("sentiment: عربي سلبي + نجمة 1 → negative/أزمة",
          r.label == "negative" and r.score < -0.12 and r.crisis,
          f"got {r.label}/{r.score}/crisis={r.crisis}")


def test_sentiment_negation() -> None:
    a = SentimentAnalyzer()
    r = a.analyze("هذا ليس رائعاً على الإطلاق")
    check("sentiment: النفي يقلب الاتجاه (لا رائعاً → سلبي/محايد)",
          r.score <= 0.12, f"got {r.score}")


def test_sentiment_english() -> None:
    a = SentimentAnalyzer()
    pos = a.analyze("Great product, fast shipping, love it!")
    neg = a.analyze("Terrible broken item, worst ever, want refund")
    check("sentiment: إنجليزي إيجابي/سلبي",
          pos.label == "positive" and neg.label == "negative",
          f"{pos.label}/{neg.label}")


def test_crisis_detection_and_reply() -> None:
    a = SentimentAnalyzer()
    e = CrisisEngine()
    r = a.analyze("احتيال! لم يصل الطلب ويرفضون رد المبلغ", rating=1)
    handled = e.handle(r.as_dict(), author="عميل", product="ZB-Kit")
    reply = handled.get("suggested_reply", "")
    check("crisis: اكتشاف أزمة + رد مقترح عربي",
          handled["needs_action"] and len(reply) > 40 and " " in reply,
          f"reply={reply[:40]}")


def test_reply_templates_all_roots() -> None:
    ok = True
    for root in ("product-quality", "shipping", "price", "support",
                 "bug", "privacy", "none"):
        txt = suggested_reply({"label": "negative", "root_cause": root},
                              product="X", author="A")
        ok = ok and len(txt) > 30
    check("crisis: كل قوالب الردود (7 جذور) مولّدة", ok)


def test_trends_pipeline() -> None:
    recs = [
        {"score": 0.5, "label": "positive", "created_at": "2026-01-01"},
        {"score": -0.7, "label": "negative", "created_at": "2026-01-01",
         "crisis": True, "severity": "critical", "root_cause": "shipping"},
        {"score": 0.2, "label": "positive", "created_at": "2026-01-02"},
        {"score": -0.3, "label": "negative", "created_at": "2026-01-02"},
        {"score": 0.4, "label": "positive", "created_at": "2026-01-03"},
        {"score": -0.1, "label": "neutral", "created_at": "2026-01-03"},
        {"score": 0.6, "label": "positive", "created_at": "2026-01-04"},
    ]
    days = daily_scores(recs)
    dist = label_distribution(recs)
    check("trends: متوسط يومي + توزيع + أزمات + اتجاه",
          len(days) == 4 and dist["positive"] == 4 and
          crisis_count(recs) == 1 and
          delta_vs_previous(recs)[1] in
          ("improving", "declining", "stable", "insufficient-data") and
          "المؤشر" in weekly_report(recs, "TestBrand"))


def test_file_collector_csv_json() -> None:
    with tempfile.TemporaryDirectory() as td:
        csv_p = os.path.join(td, "r.csv")
        with open(csv_p, "w", encoding="utf-8") as fh:
            fh.write("text,author,rating\n"
                     "\"منتج جميل\",سارة,5\n"
                     "\"منتج سيء\",علي,1\n")
        js_p = os.path.join(td, "r.json")
        json.dump([{"text": "ok product", "rating": 4}],
                  open(js_p, "w", encoding="utf-8"))
        n1 = FileCollector(csv_p).collect()
        n2 = FileCollector(js_p).collect()
        check("collectors: CSV + JSON (2 + 1 ذكر)",
              len(n1) == 2 and len(n2) == 1 and n1[0].rating == 5,
              f"{len(n1)}/{len(n2)}")


def test_rss_collector_parse() -> None:
    xml = """<?xml version="1.0"?><rss version="2.0"><channel>
<title>Reviews</title><item>
<title>زبون يشتكي من تأخر الشحن</title>
<description>المنتج ممتاز لكن التوصيل بطيء جداً</description>
<link>https://x.test/1</link><pubDate>Mon, 05 Jan 2026</pubDate>
</item></channel></rss>"""
    m = RssCollector([], brand_terms=[""])._parse(xml)
    check("collectors: RSS parse (stdlib)",
          len(m) == 1 and "يشتكي" in m[0].text and m[0].source == "rss",
          f"{len(m)}")


def test_privacy_mask_and_mention() -> None:
    m = Mention(text="hi", author="Mohammed")
    m.author = mask_author(m.author)
    d = m.as_dict()
    check("privacy: إخفاء الهوية + dataclass",
          d["author"].startswith("M") and "*" in d["author"] and
          d["source"] == "web", f"{d['author']}")


def main() -> int:
    print("Pulse-ZeroBaran · test suite")
    tests = [
        test_sentiment_positive_ar, test_sentiment_negative_ar_with_rating,
        test_sentiment_negation, test_sentiment_english,
        test_crisis_detection_and_reply, test_reply_templates_all_roots,
        test_trends_pipeline, test_file_collector_csv_json,
        test_rss_collector_parse, test_privacy_mask_and_mention,
    ]
    for t in tests:
        try:
            t()
        except Exception as exc:  # pragma: no cover
            global FAIL
            FAIL += 1
            print(f"  ✗ {t.__name__} raised {exc!r}")
    print(f"\n{PASS}/{PASS + FAIL} passed")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
