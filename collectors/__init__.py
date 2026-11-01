# -*- coding: utf-8 -*-
"""Pulse-ZeroBaran | collectors package (RSS · Web · File — polite scraping).

© 2026 Baran Avisat — All Rights Reserved.
"""
from .base import BaseCollector, Mention, mask_author, USER_AGENT
from .rss_collector import RssCollector
from .web_collector import WebCollector
from .file_collector import FileCollector

__all__ = ["BaseCollector", "Mention", "mask_author", "USER_AGENT",
           "RssCollector", "WebCollector", "FileCollector"]
