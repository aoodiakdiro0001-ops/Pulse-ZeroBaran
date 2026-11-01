# DEPLOYMENT — Pulse-ZeroBaran

© 2026 Baran Avisat — MIT License (attribution required)

Everything below uses **100% free tiers**. Every step is optional: the
system runs fully Offline with zero configuration.

## 0. Local run (zero keys)

```bash
python scripts/seed_sample_data.py     # 20 bilingual demo mentions
python scripts/scan_pulse.py --dry-run # collect → analyze → local JSON
python scripts/weekly_report.py        # weekly summary to terminal
python tests/test_pulse.py             # 10/10 tests
streamlit run dashboard/app.py         # control room
```

## 1. Telegram instant alerts (free)

1. Open `@BotFather` → `/newbot` → copy the token.
2. Get your chat id from `@userinfobot`.
3. `.env`:
   ```
   TELEGRAM_BOT_TOKEN=123456:ABC...
   TELEGRAM_CHAT_ID=987654321
   ```
4. Interactive bot: `python delivery/telegram_bot.py`
   (`/pulse` · `/report` · `/alert` · `/help`).

## 2. Supabase persistence (free tier)

1. Create a project at https://supabase.com.
2. SQL Editor → run `db/schema.sql` (creates 4 tables + RLS + `brand_pulse()`).
3. `.env`:
   ```
   SUPABASE_URL=https://xxxx.supabase.co
   SUPABASE_KEY=eyJ...
   ```
4. Next `scan_pulse.py` writes to Supabase **and** keeps the local JSON copy.

## 3. AI upgrade (optional, free tiers)

```
GEMINI_API_KEY=...     # https://aistudio.google.com/apikey
GROQ_API_KEY=...       # https://console.groq.com/keys
```
Without keys the deterministic bilingual engine handles everything.

## 4. Scheduled monitoring on GitHub Actions (free)

1. Push the project to GitHub (`aoodiakdiro0001-ops/Pulse-ZeroBaran`).
2. Repo → Settings → Secrets and variables → **Actions**:
   - Secrets: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `SUPABASE_URL`,
     `SUPABASE_KEY`, `GEMINI_API_KEY`, `GROQ_API_KEY` (any subset).
   - Variables: `PULSE_RSS_FEEDS` (comma-separated), `PULSE_WEB_PAGES`
     (JSON array of `{url, item, text, rating, product}`).
3. The workflow `pulse-scan.yml` runs every 6 hours:
   collect → analyze → persist → alert → artifact + history commit.

## 5. Connecting your own store reviews

- **CSV/JSON export** from your store dashboard → `data/reviews.csv` with
  columns `text,author,rating,product,created_at,url` → set
  `PULSE_FILE_REVIEWS=data/reviews.csv`.
- **RSS/Atom feed** of your blog or review feed → `PULSE_RSS_FEEDS`.
- **Public review page** → `PULSE_WEB_PAGES` JSON with CSS selectors.

Only collect publicly available content you are allowed to monitor.

## Troubleshooting

| Symptom | Fix |
|---|---|
| "لا توجد ذكريات" | run `seed_sample_data.py` first, or check your feed URLs |
| No Telegram messages | verify token + chat id; bot must have received `/start` once |
| Supabase writes = 0 | run `db/schema.sql`; check `SUPABASE_KEY` (service role) |
| bs4 warnings | `pip install beautifulsoup4` (raw fallback still works) |

---
© 2026 Baran Avisat — baranavisat@gmail.com — +90 531 326 37 22
