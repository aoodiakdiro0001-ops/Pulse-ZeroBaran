# Changelog — Pulse-ZeroBaran

All notable changes to this project are documented in this file.
Format follows Keep a Changelog · Versioning: Semantic.

## [1.0.0] — 2026-11-01

### Added
- **Bilingual sentiment core** (`core/lexicon.py`, `core/sentiment.py`):
  deterministic Offline engine (Arabic + English lexicon, negation,
  intensifiers, star-rating signal) with optional Gemini/Groq AI path.
- **Crisis engine** (`core/crisis.py`): severity ranking (critical/major/
  minor), root-cause classification (product-quality · shipping · price ·
  support · bug · privacy) and professional Arabic reply drafts.
- **Trends layer** (`core/trends.py`): daily sentiment scores, overall
  brand-pulse indicator, label distribution, crisis breakdown, period-over-
  period delta and weekly report text.
- **Polite collectors** (`collectors/`): RSS/Atom (stdlib XML), HTML review
  pages (BeautifulSoup with raw fallback), CSV/JSON file importer; clear
  User-Agent, throttling and author masking by default.
- **Persistence** (`db/`): Supabase schema (mentions, sentiment_analysis,
  crises, sentiment_daily + RLS + `brand_pulse()` helper) and client with
  fingerprint dedup, local JSON export fallback.
- **Delivery** (`delivery/`): Telegram instant alerts (crisis + suggested
  reply), weekly report sender and interactive PulseBot (`/pulse`, `/report`,
  `/alert`).
- **Pipeline** (`scripts/`): `seed_sample_data.py`, `scan_pulse.py`
  (collect → analyze → persist → alert), `weekly_report.py`.
- **Dashboard** (`dashboard/app.py`): Streamlit reputation control room
  (metrics, daily curve, crisis table with reply drafts, weekly report).
- **Automation** (`.github/workflows/`): `pulse-scan.yml` runs every 6 hours
  with snapshot artifacts + history commits; `tests.yml` runs the suite.
- **Tests** (`tests/test_pulse.py`): 10 deterministic tests, runnable
  directly without pytest.
- Docs: `docs/ARCHITECTURE.md`, `docs/DEPLOYMENT.md`, README, MIT LICENSE,
  AUTHOR_INFO, requirements, `.env.example`, `.gitignore`.

### Notes
- All sentiment scores are **indicative estimates for early monitoring** —
  no accuracy claims are made or implied.
- 100% free-tier stack; every component works with zero keys in Offline
  mode.

---
© 2026 Baran Avisat — All Rights Reserved.
