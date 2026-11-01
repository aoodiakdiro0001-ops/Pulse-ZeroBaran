#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pulse-ZeroBaran | Reputation Trends (Sentiment Score Over Time)
===============================================================
طبقة المتابعة التاريخية: مؤشر عام للسمعة (Sentiment Score) عبر الأيام،
نسب المشاعر، عدّ الأزمات، والتغير مقارنة بالفترة السابقة — لتعرف هل
سمعة علامتك تتراجع أم تتحسن.

المؤشر: متوسط درجات المشاعر [-1..+1] لكل يوم (مُطبّع).

Author : Baran Avisat <baranavisat@gmail.com>
© 2026 Baran Avisat — All Rights Reserved.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Optional, Tuple


def _day_of(rec: Dict) -> str:
    ts = rec.get("created_at") or rec.get("day") or ""
    return str(ts)[:10] if ts else "unknown"


def daily_scores(records: List[Dict]) -> Dict[str, float]:
    """متوسط درجة المشاعر لكل يوم."""
    buckets: Dict[str, List[float]] = defaultdict(list)
    for r in records:
        buckets[_day_of(r)].append(float(r.get("score") or 0.0))
    return {d: round(sum(v) / len(v), 4) for d, v in sorted(buckets.items())}


def overall_score(records: List[Dict]) -> float:
    """المؤشر العام للسمعة عبر كل السجلات (متوسط موزون بسيط)."""
    if not records:
        return 0.0
    total = sum(float(r.get("score") or 0.0) for r in records)
    return round(total / len(records), 4)


def label_distribution(records: List[Dict]) -> Dict[str, int]:
    """توزيع المشاعر: إيجابي / محايد / سلبي."""
    out = {"positive": 0, "neutral": 0, "negative": 0}
    for r in records:
        lab = r.get("label", "neutral")
        out[lab] = out.get(lab, 0) + 1
    return out


def crisis_count(records: List[Dict], severity: Optional[str] = None) -> int:
    """عدد الأزمات (كل السجلات أزمة إن حددنا خطورة معينة)."""
    n = 0
    for r in records:
        if severity:
            if r.get("severity") == severity:
                n += 1
        elif r.get("crisis") or r.get("severity") in ("critical", "major"):
            n += 1
    return n


def delta_vs_previous(records: List[Dict], split_ratio: float = 0.33
                      ) -> Tuple[float, str]:
    """
    مقارنة الفترة الأخيرة بالفترة السابقة (تقدير اتجاه السمعة).
    يرجع: (التغير, وصف الاتجاه).
    """
    if len(records) < 6:
        return 0.0, "insufficient-data"
    ordered = sorted(records, key=_day_of)
    cut = max(1, int(len(ordered) * split_ratio))
    prev, curr = ordered[:-cut], ordered[-cut:]
    if not prev or not curr:
        return 0.0, "insufficient-data"
    avg = lambda rs: sum(float(r.get("score") or 0.0) for r in rs) / len(rs)
    d = round(avg(curr) - avg(prev), 4)
    trend = "improving" if d >= 0.05 else ("declining" if d <= -0.05 else "stable")
    return d, trend


def crisis_breakdown(records: List[Dict]) -> Dict[str, int]:
    """توزيع الأزمات حسب جذر المشكلة (لتحديد الأولويات)."""
    out: Dict[str, int] = defaultdict(int)
    for r in records:
        if r.get("crisis") or r.get("severity") in ("critical", "major"):
            out[r.get("root_cause") or "none"] += 1
    return dict(sorted(out.items(), key=lambda kv: -kv[1]))


def weekly_report(records: List[Dict], brand: str = "علامتك التجارية") -> str:
    """تقرير أسبوعي عربي مختصر جاهز للتليجرام/اللوحة."""
    if not records:
        return f"📊 {brand}: لا توجد ذكريات مرصودة هذه الفترة."
    dist = label_distribution(records)
    total = sum(dist.values()) or 1
    score = overall_score(records)
    d, trend = delta_vs_previous(records)
    crises = crisis_count(records)
    trend_icon = {"improving": "📈 تتحسن", "declining": "📉 تتراجع",
                  "stable": "➡️ مستقرة", "insufficient-data": "؟ بيانات قليلة"}
    lines = [
        f"📊 تقرير نبض السمعة — {brand}",
        f"المؤشر العام: {score:+.2f} ({trend_icon.get(trend, trend)})",
        f"الذكريات: {total} — إيجابي {dist['positive']} · محايد {dist['neutral']} · سلبي {dist['negative']}",
        f"الأزمات المفتوحة: {crises}",
    ]
    breakdown = crisis_breakdown(records)
    if breakdown:
        top = " · ".join(f"{k}:{v}" for k, v in list(breakdown.items())[:3])
        lines.append(f"أهم أسباب الشكاوى: {top}")
    lines.append("التغير عن الفترة السابقة: " + f"{d:+.2f}")
    lines.append("_تقديرات إرشادية · © 2026 Baran Avisat_")
    return "\n".join(lines)[:3800]
