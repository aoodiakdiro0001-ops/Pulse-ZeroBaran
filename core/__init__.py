# -*- coding: utf-8 -*-
"""Pulse-ZeroBaran | core package (Lexicon · Sentiment · Crisis · Trends).

© 2026 Baran Avisat — All Rights Reserved.
"""
from .sentiment import SentimentAnalyzer, SentimentResult
from .crisis import CrisisEngine, suggested_reply
from .trends import (daily_scores, overall_score, label_distribution,
                     crisis_count, delta_vs_previous, weekly_report)

__all__ = ["SentimentAnalyzer", "SentimentResult", "CrisisEngine",
           "suggested_reply", "daily_scores", "overall_score",
           "label_distribution", "crisis_count", "delta_vs_previous",
           "weekly_report"]
