#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pulse-ZeroBaran | Streamlit Dashboard (Reputation Control Room)
===============================================================
لوحة نبض السمعة: المؤشر العام · منحنى الأيام · توزيع المشاعر · جدول
الأزمات مع مسودات الردود · تقرير أسبوعي — تعمل محلياً على الملف
output/pulse_latest.json (أو Supabase إن مُضبط).

Run:
    streamlit run dashboard/app.py

Author : Baran Avisat <baranavisat@gmail.com>
© 2026 Baran Avisat — All Rights Reserved.
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from core.trends import (crisis_breakdown, daily_scores,        # noqa: E402
                         crisis_count, delta_vs_previous,
                         label_distribution, overall_score,
                         weekly_report)

try:
    import streamlit as st
    _ST = True
except Exception:  # pragma: no cover
    _ST = False


def _load() -> dict:
    path = os.path.join(ROOT, "output", "pulse_latest.json")
    if os.path.exists(path):
        try:
            return json.load(open(path, encoding="utf-8"))
        except Exception:
            return {}
    try:
        from db import supabase_client as sb
        rows = sb.load_all()
        return {"records": rows, "brand": "علامتك التجارية"} if rows else {}
    except Exception:
        return {}


def main() -> None:
    if not _ST:
        print("pip install streamlit  ثم:  streamlit run dashboard/app.py")
        return

    st.set_page_config(page_title="Pulse-ZeroBaran · نبض السمعة",
                       page_icon="📡", layout="wide")
    st.title("📡 Pulse-ZeroBaran — غرفة تحكّم نبض السمعة")
    st.caption("رصد مشاعر العملاء · تحليل السمعة · إنذارات فورية — © 2026 Baran Avisat")

    data = _load()
    records = data.get("records") or []
    brand = data.get("brand", "علامتك التجارية")

    if not records:
        st.info("لا توجد بيانات بعد — شغّل: `python scripts/seed_sample_data.py` ثم "
                "`python scripts/scan_pulse.py`")
        return

    score = overall_score(records)
    dist = label_distribution(records)
    crises_n = crisis_count(records)
    delta, trend = delta_vs_previous(records)
    trend_txt = {"improving": "📈 تتحسن", "declining": "📉 تتراجع",
                 "stable": "➡️ مستقرة"}.get(trend, trend)

    # ---- المؤشرات العلوية ---- #
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("🎯 المؤشر العام", f"{score:+.2f}")
    c2.metric("💚 إيجابي", dist["positive"])
    c3.metric("⚪ محايد", dist["neutral"])
    c4.metric("❤️ سلبي", dist["negative"])
    c5.metric("🚨 أزمات", crises_n)
    st.markdown(f"**الاتجاه:** {trend_txt} · التغير {delta:+.2f} عن الفترة السابقة")

    # ---- منحنى الأيام ---- #
    days = daily_scores(records)
    if days:
        st.subheader("📈 منحنى نبض السمعة (يومي)")
        st.line_chart(days)

    # ---- الأزمات والردود ---- #
    st.subheader("🚨 الأزمات ومسوحات الردود")
    hot = [r for r in records
           if r.get("crisis") or r.get("severity") in ("critical", "major")]
    if not hot:
        st.success("✅ لا أزمات مفتوحة — السمعة تحت السيطرة.")
    else:
        for r in sorted(hot, key=lambda x: {"critical": 0, "major": 1}.get(
                x.get("severity"), 2))[:8]:
            with st.expander(
                    f"{'🚨' if r.get('severity') == 'critical' else '⚠️'} "
                    f"[{r.get('severity')}] {(r.get('text') or '')[:70]}…"):
                st.write("**النص:**", r.get("text"))
                st.write("**النبرة:**", r.get("tone"),
                         "· **الجذر:**", r.get("root_cause"),
                         "· **الدرجة:**", r.get("score"))
                st.code(r.get("suggested_reply") or "—", language=None)

    # ---- توزيع الأسباب + التقرير ---- #
    left, right = st.columns(2)
    with left:
        st.subheader("🧩 أسباب الشكاوى")
        bd = crisis_breakdown(records)
        if bd:
            st.bar_chart(bd)
        else:
            st.caption("لا توجد أزمات مصنّفة.")
    with right:
        st.subheader("📊 التقرير الأسبوعي")
        st.text(weekly_report(records, brand))

    st.divider()
    st.caption("تقديرات إرشادية للرصد المبكر · © 2026 Baran Avisat · "
               "Pulse-ZeroBaran v1.0.0")


if __name__ == "__main__":
    main()
