#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pulse-ZeroBaran | Supabase Persistence Client
=============================================
طبقة الأرشيف والمتابعة التاريخية على Supabase (PostgreSQL Free Tier).
كل الدوال اختيارية: إن غاب المفتاح يعمل النظام محلياً بلا توقف.

Author : Baran Avisat <baranavisat@gmail.com>
© 2026 Baran Avisat — All Rights Reserved.
"""
from __future__ import annotations

import hashlib
import json
import os
from typing import Dict, List, Optional


def _client():
    url = os.getenv("SUPABASE_URL", "").strip()
    key = os.getenv("SUPABASE_KEY", "").strip()
    if not url or not key:
        return None
    try:
        from supabase import create_client  # type: ignore
        return create_client(url, key)
    except Exception:
        return None


def available() -> bool:
    return _client() is not None


def fingerprint(text: str, source: str = "", url: str = "") -> str:
    """بصمة فريدة لمنع تخزين الذكر مرتين."""
    blob = ((text or "").strip().lower() + "|" + (source or "") + "|" +
            (url or "").strip())
    return hashlib.sha1(blob.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------- #
# Writers
# ---------------------------------------------------------------------- #
def save_mentions(rows: List[Dict]) -> int:
    """حفظ ذكريات جديدة (upsert بالبصمة لمنع التكرار)."""
    client = _client()
    if client is None or not rows:
        return 0
    payload = [{
        "text": r.get("text", ""),
        "source": r.get("source", "web"),
        "author": r.get("author", "عميل مجهول"),
        "rating": r.get("rating"),
        "product": r.get("product") or None,
        "url": r.get("url") or None,
        "created_at": r.get("created_at") or None,
        "fingerprint": r.get("fingerprint") or fingerprint(
            r.get("text", ""), r.get("source", ""), r.get("url", "")),
    } for r in rows if r.get("text")]
    try:
        client.table("mentions").upsert(payload, on_conflict="fingerprint").execute()
        return len(payload)
    except Exception:
        return 0


def save_analysis(analysis_rows: List[Dict]) -> int:
    """حفظ نتائج تحليل المشاعر المرتبطة بالذكر."""
    client = _client()
    if client is None or not analysis_rows:
        return 0
    payload = [{
        "mention_id": r.get("mention_id"),
        "label": r.get("label", "neutral"),
        "score": float(r.get("score") or 0.0),
        "tone": r.get("tone"),
        "root_cause": r.get("root_cause"),
        "severity": r.get("severity"),
        "crisis": bool(r.get("crisis")),
        "backend": r.get("backend", "offline"),
    } for r in analysis_rows if r.get("mention_id") is not None]
    try:
        client.table("sentiment_analysis").insert(payload).execute()
        return len(payload)
    except Exception:
        return 0


def save_crises(crises: List[Dict]) -> int:
    """حفظ سجل الأزمات مع مسودات الردود."""
    client = _client()
    if client is None or not crises:
        return 0
    payload = [{
        "mention_id": r.get("mention_id"),
        "severity": r.get("severity"),
        "root_cause": r.get("root_cause"),
        "suggested_reply": r.get("suggested_reply"),
        "needs_action": bool(r.get("needs_action")),
    } for r in crises if r.get("mention_id") is not None]
    try:
        client.table("crises").upsert(payload, on_conflict="mention_id").execute()
        return len(payload)
    except Exception:
        return 0


def save_daily(day: str, stats: Dict) -> int:
    """حفظ مؤشر السمعة اليومي (لرسم المنحنى التاريخي)."""
    client = _client()
    if client is None:
        return 0
    payload = {"day": day,
               "avg_score": float(stats.get("avg_score") or 0.0),
               "positive": int(stats.get("positive") or 0),
               "neutral": int(stats.get("neutral") or 0),
               "negative": int(stats.get("negative") or 0),
               "crises": int(stats.get("crises") or 0)}
    try:
        client.table("sentiment_daily").upsert(payload, on_conflict="day").execute()
        return 1
    except Exception:
        return 0


# ---------------------------------------------------------------------- #
# Readers
# ---------------------------------------------------------------------- #
def load_all(limit: int = 5000) -> List[Dict]:
    """دمج آخر الذكريات مع تحليلاتها (للوحة/التقارير)."""
    client = _client()
    if client is None:
        return []
    try:
        mentions = (client.table("mentions").select("*")
                    .order("collected_at", desc=True).limit(limit).execute()).data or []
        ids = {m["id"]: m for m in mentions}
        if not ids:
            return []
        analysis = (client.table("sentiment_analysis").select("*")
                    .order("analyzed_at", desc=True).limit(limit * 2).execute()).data or []
        merged: List[Dict] = []
        for a in analysis:
            m = ids.get(a.get("mention_id"))
            if not m:
                continue
            merged.append({**{k: m.get(k) for k in
                              ("text", "source", "author", "rating", "product",
                               "url", "created_at")},
                           "score": a.get("score"), "label": a.get("label"),
                           "tone": a.get("tone"), "root_cause": a.get("root_cause"),
                           "severity": a.get("severity"), "crisis": a.get("crisis")})
        return merged
    except Exception:
        return []


def export_local(payload, path: str) -> str:
    """نسخة احتياطية محلية (JSON) — تعمل دائماً بلا سحابة."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    return path
