@echo off
REM اسکریپت نصب خودکار برای ویندوز

echo 🚀 شروع نصب ربات توییتر...

REM چک کردن پایتون
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ پایتون نصب نیست!
    echo لطفاً از لینک زیر پایتون را دانلود و نصب کنید:
    echo https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ پایتون پیدا شد

REM ساخت محیط مجازی
echo 📦 ساخت محیط مجازی...
python -m venv .venv

REM فعال‌سازی محیط مجازی
echo 🔧 فعال‌سازی محیط مجازی...
call .venv\Scripts\activate.bat

REM نصب پکیج‌ها
echo 📥 نصب کتابخانه‌ها...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM چک کردن فایل .env
if not exist .env (
    echo ⚠️  فایل .env پیدا نشد!
    echo لطفاً فایل .env.example را به .env تغییر نام دهید و کلیدهای توییتر را در آن قرار دهید.
    pause
    exit /b 1
)

echo.
echo ✅ نصب با موفقیت انجام شد!
echo.
echo برای اجرای ربات:
echo   .venv\Scripts\activate.bat
echo   python bot.py --continuous
echo.
pause
