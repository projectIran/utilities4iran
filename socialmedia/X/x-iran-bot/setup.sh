#!/bin/bash
# اسکریپت نصب خودکار برای مک و لینوکس

echo "🚀 شروع نصب ربات توییتر..."

# چک کردن پایتون
if ! command -v python3 &> /dev/null; then
    echo "❌ پایتون نصب نیست!"
    echo "لطفاً از لینک زیر پایتون را دانلود و نصب کنید:"
    echo "https://www.python.org/downloads/"
    exit 1
fi

echo "✅ پایتون پیدا شد: $(python3 --version)"

# ساخت محیط مجازی
echo "📦 ساخت محیط مجازی..."
python3 -m venv .venv

# فعال‌سازی محیط مجازی
echo "🔧 فعال‌سازی محیط مجازی..."
source .venv/bin/activate

# نصب پکیج‌ها
echo "📥 نصب کتابخانه‌ها..."
pip install --upgrade pip
pip install -r requirements.txt

# چک کردن فایل .env
if [ ! -f .env ]; then
    echo "⚠️  فایل .env پیدا نشد!"
    echo "لطفاً فایل .env.example را به .env تغییر نام دهید و کلیدهای توییتر را در آن قرار دهید."
    exit 1
fi

echo ""
echo "✅ نصب با موفقیت انجام شد!"
echo ""
echo "برای اجرای ربات:"
echo "  source .venv/bin/activate"
echo "  python bot.py --continuous"
echo ""
