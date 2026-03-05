# Telegram Radar - رادار تلگرامی

بات مانیتورینگ که پست‌های ترند X (توییتر) درباره ایران/اسرائیل/آمریکا رو پیدا و به تلگرام ارسال می‌کنه.

**طراحی شده برای حداقل مصرف API** — فقط ~۷,۲۰۰ خوانش در ماه (پلن Basic اجازه ۱۰,۰۰۰ میده)

## موضوعات تحت نظر

- ایران و اسرائیل (حملات، درگیری نظامی)
- ایران و آمریکا (تحریم‌ها، هسته‌ای، جنگ)
- انقلاب ایران و اعتراضات
- رضا پهلوی، خامنه‌ای، سپاه

## نصب

```bash
cd telegram-radar
python -m venv .venv
source .venv/bin/activate   # مک/لینوکس
pip install -r requirements.txt
cp .env.example .env
```

## تنظیمات (.env)

### ۱. توکن X API
فقط `X_BEARER_TOKEN` لازمه (read-only، پست نمیذاره):
- برو به [developer.x.com](https://developer.x.com)
- Bearer Token رو کپی کن

### ۲. بات تلگرام
- توی تلگرام به `@BotFather` پیام بده
- `/newbot` بزن و مراحل رو طی کن
- توکن بات رو کپی کن → `TELEGRAM_BOT_TOKEN`

### ۳. Chat ID تلگرام
- بات رو به گروه یا کانال اضافه کن
- یا از `@userinfobot` برای گرفتن Chat ID استفاده کن
- Chat ID رو بذار → `TELEGRAM_CHAT_ID`

## اجرا

```bash
# اجرای مداوم (هر ۶۰ دقیقه چک می‌کنه)
python radar.py

# فقط یکبار اجرا
python radar.py --once

# تست بدون ارسال به تلگرام
python radar.py --dry-run

# تست یکبار بدون ارسال
python radar.py --once --dry-run
```

## هزینه API

| تنظیم | ریکوئست/روز | خوانش/ماه | وضعیت |
|--------|-------------|-----------|-------|
| هر ۶۰ دقیقه (پیشفرض) | ~۲۴ | ~۷,۲۰۰ | ✅ زیر سقف |
| هر ۱۲۰ دقیقه | ~۱۲ | ~۳,۶۰۰ | ✅ خیلی ارزان |
| هر ۳۰ دقیقه | ~۴۸ | ~۱۴,۴۰۰ | ⚠️ بالای سقف Basic |

> نکته: اگه بودجه API محدوده، `SEARCH_INTERVAL_MINUTES=120` بذار.

## اجرا روی سرور (۲۴/۷)

```bash
# با nohup
nohup python radar.py > /dev/null 2>&1 &

# یا با screen
screen -S radar
python radar.py
# Ctrl+A, D برای detach

# یا با systemd service
```

## فایل‌ها

| فایل | توضیح |
|------|-------|
| `radar.py` | اسکریپت اصلی |
| `.env` | تنظیمات (خصوصی) |
| `seen_tweets.json` | کش توییت‌های دیده شده (خودکار) |
| `stats.json` | آمار ارسال‌ها (خودکار) |
| `radar.log` | لاگ فعالیت‌ها |
