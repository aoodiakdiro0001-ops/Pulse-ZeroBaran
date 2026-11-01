<div dir="rtl">

# 📡 Pulse-ZeroBaran
### المنظومة الذاتية الذكية لرصد مشاعر العملاء، تحليل السمعة، وتتبع ردود الفعل الرقمية

**نظام ذكي متكامل ومستقل لرصد التعليقات والتقييمات والمنشورات التي تتحدث عن علامتك التجارية عبر الويب والمتاجر، تحليل مشاعرها (إيجابية/محايدة/سلبية)، واكتشاف الأزمات أو الشكاوى فور وقوعها — مع إنذار فوري ومسودة رد احترافية.** يعمل بموارد مجانية بالكامل و**دون دفع دولار واحد لأي أداة رصد مدفوعة.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-green.svg)](https://www.python.org/)
[![Free Tier](https://img.shields.io/badge/Cost-100%25%20Free-success.svg)](#)
[![Tests](https://img.shields.io/badge/tests-10%2F10%20passing-brightgreen.svg)](#)

---

## 🌟 لماذا تتمنى كل شركة وكل صاحب مشروع الحصول عليه؟

| الميزة | الوصف |
|---|---|
| 💰 **توفير مال فلكي** | اشتراكات أدوات رصد السمعة وتحليل المشاعر تكلف الشركات ثروات طائلة سنوياً؛ هذا النظام يؤدي نفس الغرض باحترافية عسكرية وبتكلفة صفر. |
| ⚡ **الاستباقية وإخماد الأزمات (Zero Crisis Latency)** | يخبرك فوراً إذا اشتكى عميل من منتجك، مما يتيح لك حل مشكلته قبل أن تنتشر أو تؤثر على مبيعاتك. |
| 📈 **فهم نبض السوق الحقيقي** | تقارير دورية عن شعور العملاء تجاه منتجاتك الجديدة وما يفضلونه، بمؤشر سمعة يوضّح هل السمعة تتراجع أم تتحسن يوماً بيوم. |

---

## 🛠️ الموارد المجانية البحتة المستخدمة في البناء (The Free Tech Stack)

| المكون الأساسي | الخدمة / التقنية المجانية | دورها في المشروع |
|---|---|---|
| محرك التشغيل والمراقبة المجدولة (Cron) | **GitHub Actions** | خادم مجاني لتنفيذ عمليات جلب التعليقات والتقييمات دورياً كل بضعة ساعات. |
| محرك الجلب واستخراج البيانات (Scraping Core) | **Python + BeautifulSoup / XML قياسي** | جمع التقييمات والتعليقات العامة من متاجرك وصفحاتك بأسلوب مهذّب ومحترم لروبات. |
| محرك تحليل المشاعر (Sentiment Brain) | **محرّك Offline حتمي ثنائي اللغة + Google Gemini / Groq (Free Tiers)** | قراءة التعليقات، تحديد النبرة العاطفية، واستخراج جذر المشكلة — والمسار الذكي اختياري لتحسين الصياغة. |
| قاعدة البيانات وسجلات السمعة | **Supabase (PostgreSQL Free Tier)** | تخزين آراء العملاء ودرجات المشاعر وسجلات الأزمات عبر الزمن لتتبع الأداء. |
| قناة التنبيهات الفورية (Gateway & UI) | **Telegram Bot API / Streamlit Dashboard** | إرسال إنذار عاجل على هاتفك فور رصد تعليق سلبي مع اقتراح الرد المناسب. |

---

## 📐 البنية البرمجية والتصميم الهندسي (Software Architecture)

```
[تجميع التقييمات والتعليقات الجديدة من المتاجر أو الويب (GitHub Actions + Python)]
                                      │
                                      ▼
[محرّك تحليل المشاعر — Offline حتمي ثنائي اللغة · Gemini/Groq اختياري]
                                      │
                                      ▼
[تخزين التحليل في Supabase ──► إرسال إنذار فوري للتعليقات السلبية أو تقرير أسبوعي إلى تليجرام]
```

### تفصيل الطبقات برمجياً:

| # | الطبقة | التقنية | الملفات |
|---|---|---|---|
| 1 | **طبقة الجلب والمسح الرقمي** (Ingestion & Scraping) | Python · RSS/XML · BeautifulSoup | `collectors/rss_collector.py` · `collectors/web_collector.py` · `collectors/file_collector.py` |
| 2 | **العقل الذكي لتحليل المشاعر** (Sentiment Core) | قاموس ثنائي اللغة حتمي + Gemini/Groq اختياري | `core/lexicon.py` · `core/sentiment.py` · `core/crisis.py` |
| 3 | **الأرشيف والمتابعة التاريخية** (Persistence) | Supabase (PostgreSQL) + JSON محلي | `db/supabase_client.py` · `db/schema.sql` · `core/trends.py` |
| 4 | **التوصيل والتنبيه الفوري** (Delivery & Control) | Telegram Bot + Streamlit | `delivery/notifier.py` · `delivery/telegram_bot.py` · `dashboard/app.py` |

> **ملاحظة هندسية:** محرّك المشاعر الاحتياطي **حتمي Offline** (قاموس عربي/إنجليزي + نفي + تشديد + إشارة النجوم) يعمل دائماً بلا أي مفتاح أو شبكة؛ مسارات Gemini/Groq تُضاف لتحسين الصياغة عند توفرها فقط.

---

## ⚙️ طريقة العمل خطوة بخطوة (End-to-End Workflow)

1. **الحدث:** في أوقات مجدولة، يستيقظ خادم GitHub Actions ليمسح أحدث التقييمات والتعليقات الخاصة بعلامتك التجارية.
2. **التحليل والتصنيف:** يمرر النظام التعليقات على محرّك المشاعر لفحص النبرة واستخراج جذر المشكلة (جودة · شحن · سعر · دعم · خصوصية).
3. **الإنذار والتنبيه:** إذا رصد النظام شكوى حرجة، يجهّز مسودة رد احترافية ويرسل تنبيهاً فورياً لهاتفك:
   > ⚠️ تنبيه رصد تعليق سلبي — خطورة: critical
   > 💬 نص الشكوى: "المنتج وصل تالفاً ولم يعمل معي."
   > 🧩 جذر المشكلة: product-quality
   > 💡 الرد المقترح: (رسالة اعتذار احترافية مع آلية لتعويض العميل فوراً)
4. **النتيجة الفورية:** تسيطر على أي أزمة محتملة في مهدها، وبقيّة السجلات تُبنى لمنحنى نبض السمعة عبر الأيام.

---

## 🚀 التشغيل السريع (Quickstart — 3 أوامر)

```bash
# 1) توليد بيانات تجريبية ثنائية اللغة (20 ذكر تجريبي)
python scripts/seed_sample_data.py

# 2) المسح الكامل: جمع → تحليل → تخزين → تنبيه (يعمل بلا أي مفاتيح)
python scripts/scan_pulse.py --dry-run

# 3) تقرير أسبوعي من الطرفية
python scripts/weekly_report.py
```

مع لوحة التحكم:
```bash
pip install -r requirements.txt
streamlit run dashboard/app.py        # نبض السمعة · منحنى الأيام · الأزمات والردود
```

مع البوت:
```bash
export TELEGRAM_BOT_TOKEN=...         # من @BotFather مجاناً
python delivery/telegram_bot.py       # /pulse  ·  /report  ·  /alert
```

### الاختبارات
```bash
python tests/test_pulse.py    # 10/10 — بلا pytest أيضاً
# أو: pytest tests/ -q
```

---

## 🗄️ النشر على Supabase (اختياري · مجاني)

1. أنشئ مشروعاً في [supabase.com](https://supabase.com) (Free Tier).
2. نفّذ ملف `db/schema.sql` في SQL Editor.
3. ضع في `.env`:
   ```
   SUPABASE_URL=https://xxxx.supabase.co
   SUPABASE_KEY=eyJ...
   ```
4. شغّل `python scripts/scan_pulse.py` — يحفظ السجلات تلقائياً عند توفر المفاتيح (وينسخها محلياً دائماً في `output/pulse_latest.json`).

### التنبيهات الفورية (تليجرام · مجاني)
```
TELEGRAM_BOT_TOKEN=123...    # من @BotFather
TELEGRAM_CHAT_ID=456...      # من @userinfobot
```

---

## 📂 بنية المشروع

```
Pulse-ZeroBaran/
├── core/                    # العقل الذكي
│   ├── lexicon.py           #   قاموس مشاعر عربي/إنجليزي + نفي + تشديد + أزمات
│   ├── sentiment.py         #   محرك تحليل هجين (Offline حتمي + AI اختياري)
│   ├── crisis.py            #   اكتشاف الأزمات + مسودات ردود احترافية
│   └── trends.py            #   مؤشر السمعة اليومي + التغير + التقارير
├── collectors/              # طبقة الجلب المهذبة (RSS · Web · CSV/JSON)
├── db/                      # Supabase client + schema.sql (4 جداول + RLS)
├── delivery/                # تنبيهات تليجرام + بوت استعلام /pulse /report
├── dashboard/app.py         # لوحة Streamlit (غرفة تحكّم السمعة)
├── scripts/                 # seed · scan_pipeline · weekly_report
├── tests/test_pulse.py      # 10 اختبارات (pytest أو مباشر)
├── .github/workflows/       # مسح كل 6 ساعات + اختبارات (GitHub Actions مجاناً)
└── docs/                    # ARCHITECTURE · DEPLOYMENT
```

---

## 🧾 بيانات المالك وحقوق الملكية (Owner & Copyright)

| الحقل | القيمة |
|---|---|
| **المؤلف / Owner** | **Baran Avisat** |
| **البريد / Email** | [baranavisat@gmail.com](mailto:baranavisat@gmail.com) |
| **واتساب / WhatsApp** | +90 531 326 37 22 (00905313263722) |
| **الحساب البنكي / IBAN** | `TR10 0001 0090 1008 4013 0050 01` |
| **GitHub** | [github.com/aoodiakdiro0001-ops](https://github.com/aoodiakdiro0001-ops) |
| **المتجر / Store** | [baranavi.gumroad.com](https://baranavi.gumroad.com/) |
| **الترخيص / License** | MIT License (مع شرط الإسناد) © 2026 |

**© 2026 Baran Avisat — Pulse-ZeroBaran v1.0.0 — All Rights Reserved.**

> 📌 **تم حفظ هذا المشروع (الثالث والثلاثين) في سجلات قاعدة بيانات الابتكار البرمجي بنجاح تام لضمان عدم تكراره.**
> أي إعادة استخدام أو توزيع يجب أن يحافظ على اسم المؤلف **Baran Avisat** في README وLICENSE وواجهات النظام.

## 🛠️ الدعم الفني

- 📧 البريد: **baranavisat@gmail.com**
- 📱 واتساب: **+90 531 326 37 22**
- 🏦 للطلبات المدفوعة: IBAN `TR10 0001 0090 1008 4013 0050 01`

**الدعم:** إصلاحات المحتوى والتوضيحات مجاناً لمدة سنة كاملة من تاريخ الشراء.

---
**© 2026 Baran Avisat — جميع الحقوق محفوظة / All Rights Reserved.**
</div>
