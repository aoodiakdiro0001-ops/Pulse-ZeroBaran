# ARCHITECTURE — Pulse-ZeroBaran v1.0.0

© 2026 Baran Avisat — MIT License (attribution required)

## Overview

Pulse-ZeroBaran is a self-hosted brand-reputation monitoring system with four
layers that work together as a never-sleeping sentiment radar:

```
[Ingestion & Scraping]  →  [Sentiment Core]  →  [Persistence]  →  [Delivery]
   collectors/               core/                db/              delivery/
   GitHub Actions cron       Offline + AI         Supabase/JSON    Telegram + Streamlit
```

## Layer 1 — Ingestion & Scraping (`collectors/`)

| Collector | Source | Dependency |
|---|---|---|
| `RssCollector` | RSS 2.0 / Atom feeds | stdlib `xml.etree` |
| `WebCollector` | HTML review pages (CSS selectors) | BeautifulSoup (raw `<p>` fallback) |
| `FileCollector` | local CSV / JSON exports | stdlib |

Politeness contract (enforced in `BaseCollector`):
- clear User-Agent identifying the project,
- `REQUEST_PAUSE` throttle between requests (1.5–2.5 s),
- author masking (`mask_author`) — privacy first,
- only publicly available text is collected.

## Layer 2 — Sentiment Core (`core/`)

- `lexicon.py` — bilingual lexicon: positive/negative sets (Fusha + common
  dialect + English), negation window, intensifiers, crisis keywords, stems.
- `sentiment.py` — `SentimentAnalyzer`:
  - **Offline deterministic path (default):** token window scan → weighted
    score [-1..+1] with negation flip (`-0.85`), intensifier boost (`×1.6`),
    optional star-rating fusion (`0.65·text + 0.35·rating`).
  - **AI path (optional):** Gemini 1.5 Flash or Groq `llama-3.1-8b-instant`
    returns JSON; result is merged with local crisis validation.
  - Outputs: `label`, `score`, `tone`, `root_cause`, `severity`, `crisis`,
    `backend`, `reasons` (decision transparency).
- `crisis.py` — `CrisisEngine`: severity → priority (critical=1 … positive=5),
  professional Arabic reply drafts per root cause (7 templates), optional AI
  rephrasing, ready-to-send Telegram alert text.
- `trends.py` — daily averages, overall brand pulse, label distribution,
  crisis breakdown, period delta + trend word, weekly report formatter.

## Layer 3 — Persistence (`db/`)

- `schema.sql` — 4 tables (`mentions`, `sentiment_analysis`, `crises`,
  `sentiment_daily`), unique `fingerprint` for dedup, RLS enabled, helper
  function `brand_pulse(days)`.
- `supabase_client.py` — upsert writers with graceful `0`-return on any
  failure; `load_all()` merges mentions with analysis; `export_local()`
  JSON backup. Everything optional: with no keys the pipeline writes
  `output/pulse_latest.json` only.

## Layer 4 — Delivery (`delivery/`, `dashboard/`)

- `notifier.py` — `format_alert` / `send_alert` / `send_crisis_batch`
  (max 4 per run) / `format_weekly`; silent no-op without tokens.
- `telegram_bot.py` — `PulseBot` polling: `/pulse` (indicator + worst
  crisis), `/report` (weekly), `/alert` (draft reply), `/help`.
- `dashboard/app.py` — Streamlit control room: metric row, daily line
  chart, crisis expanders with reply drafts, root-cause bars, weekly text.

## Automation (`.github/workflows/`)

- `pulse-scan.yml` — cron `17 */6 * * *` (every 6 h): install → scan →
  upload `pulse_latest.json` artifact → commit dated snapshot to `history/`.
- `tests.yml` — on push/PR: `compileall` + `python tests/test_pulse.py`.

## Data flow for one mention

1. Collector emits `Mention(text, source, author, rating, product, url)`.
2. `SentimentAnalyzer.analyze` → `SentimentResult`.
3. `CrisisEngine.handle` adds `suggested_reply`, `needs_action`, `priority`.
4. Pipeline writes local JSON (+ Supabase when configured).
5. Crises → Telegram alert immediately; trends → weekly report.

## Design principles

- **Zero mandatory dependencies** — core runs on Python 3.8+ stdlib.
- **Offline-first** — no key, no network: still fully functional.
- **Indicative estimates only** — scores support early monitoring; no
  accuracy claims are made.
- **Privacy** — author masking, public text only, RLS on tables.
- **Attribution** — author name "Baran Avisat" kept in README, LICENSE and
  interface captions.

---
© 2026 Baran Avisat — Pulse-ZeroBaran v1.0.0
