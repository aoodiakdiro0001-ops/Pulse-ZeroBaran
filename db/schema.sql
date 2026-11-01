-- ============================================================
-- Pulse-ZeroBaran | Database Schema (Supabase · PostgreSQL Free)
-- ============================================================
-- نفّذ هذا الملف في Supabase SQL Editor مرة واحدة قبل أول مسح.
-- يخزّن الذكريات الخام + تحليلات المشاعر + سجل الأزمات عبر الزمن.
--
-- المؤلف: Baran Avisat <baranavisat@gmail.com>
-- © 2026 Baran Avisat — All Rights Reserved.
-- ============================================================

-- 1) الذكريات المرصودة (خام)
create table if not exists mentions (
    id            bigserial primary key,
    text          text not null,
    source        text default 'web',        -- rss | web | file | api
    author        text default 'عميل مجهول',
    rating        int,                        -- 1..5 إن وُجد
    product       text,
    url           text,
    created_at    timestamptz,                -- وقت النشر الأصلي إن عُرف
    collected_at  timestamptz default now(),
    fingerprint   text unique                 -- بصمة ضد التكرار (hash)
);

-- 2) تحليلات المشاعر المرتبطة بالذكر
create table if not exists sentiment_analysis (
    id            bigserial primary key,
    mention_id    bigint references mentions(id) on delete cascade,
    label         text not null,              -- positive | neutral | negative
    score         double precision not null,  -- [-1 .. +1] تقديرية
    tone          text,
    root_cause    text,
    severity      text,                       -- critical | major | minor | ...
    crisis        boolean default false,
    backend       text default 'offline',     -- offline | gemini | groq
    analyzed_at   timestamptz default now()
);
create index if not exists idx_analysis_sev on sentiment_analysis (severity);
create index if not exists idx_analysis_day on sentiment_analysis (analyzed_at);

-- 3) الأزمات والردود المقترحة
create table if not exists crises (
    id                bigserial primary key,
    mention_id        bigint references mentions(id) on delete cascade,
    severity          text not null,
    root_cause        text,
    suggested_reply   text,
    needs_action      boolean default true,
    resolved          boolean default false,
    created_at        timestamptz default now()
);

-- 4) مؤشر السمعة اليومي (يُحسب في cron ويخزن للتاريخ)
create table if not exists sentiment_daily (
    day             date primary key,
    avg_score       double precision,
    positive        int,
    neutral         int,
    negative        int,
    crises          int
);

-- 5) حماية البيانات (خصوصية أولاً)
alter table mentions enable row level security;
alter table sentiment_analysis enable row level security;
alter table crises enable row level security;
alter table sentiment_daily enable row level security;

create policy "service manages mentions" on mentions
    for all using (true) with check (true);
create policy "service manages analysis" on sentiment_analysis
    for all using (true) with check (true);
create policy "service manages crises" on crises
    for all using (true) with check (true);

-- 6) دالة مساعدة: مؤشر السمعة لآخر N يوم
create or replace function brand_pulse(days int)
returns table (day date, avg_score double precision, crises int) as $$
    select day, avg_score, crises
    from sentiment_daily
    where day >= (current_date - days)
    order by day desc;
$$ language sql stable;

-- ============================================================
-- © 2026 Baran Avisat — Pulse-ZeroBaran v1.0.0 — All Rights Reserved.
-- ============================================================
