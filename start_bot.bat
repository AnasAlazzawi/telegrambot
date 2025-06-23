@echo off
echo 🚀 بدء تشغيل Graffiti AI Bot...
echo.

REM التحقق من وجود Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ خطأ: Python غير مثبت
    echo 💡 يرجى تثبيت Python من https://python.org
    pause
    exit /b 1
)

REM التحقق من وجود ملف requirements.txt
if not exist requirements.txt (
    echo ❌ خطأ: ملف requirements.txt غير موجود
    pause
    exit /b 1
)

REM تثبيت المتطلبات
echo 📦 تثبيت المتطلبات...
pip install -r requirements.txt

REM التحقق من متغير البيئة
if "%TELEGRAM_BOT_TOKEN%"=="" (
    echo.
    echo ❌ خطأ: يجب تعيين متغير البيئة TELEGRAM_BOT_TOKEN
    echo.
    echo 💡 كيفية الحصول على التوكن:
    echo    1. تحدث مع @BotFather في تليجرام
    echo    2. أرسل /newbot
    echo    3. اتبع التعليمات لإنشاء بوت جديد
    echo    4. احصل على التوكن
    echo.
    echo 🔧 كيفية تعيين التوكن:
    echo    set TELEGRAM_BOT_TOKEN=your_token_here
    echo.
    pause
    exit /b 1
)

REM تشغيل البوت
echo.
echo ✅ بدء تشغيل البوت...
echo 📱 البوت جاهز لاستقبال الرسائل
echo 🛑 اضغط Ctrl+C لإيقاف البوت
echo.

python bot.py

echo.
echo 🛑 تم إيقاف البوت
pause
