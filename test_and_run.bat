@echo off
echo.
echo =====================================================
echo 🎨 Graffiti AI Bot - اختبار محلي
echo =====================================================
echo.

REM التحقق من Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ خطأ: Python غير مثبت
    echo 💡 قم بتثبيت Python من https://python.org
    echo.
    pause
    exit /b 1
)

echo ✅ Python مثبت بنجاح
echo.

REM التحقق من التوكن
if "%TELEGRAM_BOT_TOKEN%"=="" (
    echo ⚠️  تحذير: متغير TELEGRAM_BOT_TOKEN غير محدد
    echo.
    echo 📝 لاختبار البوت محلياً، قم بتعيين التوكن:
    echo    set TELEGRAM_BOT_TOKEN=your_token_here
    echo.
    echo 🤖 للحصول على التوكن:
    echo    1. ابحث عن @BotFather في تليجرام
    echo    2. أرسل /newbot
    echo    3. اتبع التعليمات
    echo    4. احصل على التوكن
    echo.
    echo 🧪 تشغيل اختبارات بدون توكن...
    echo.
) else (
    echo ✅ توكن التليجرام محدد
    echo.
)

REM تشغيل الاختبارات
echo 🧪 تشغيل اختبارات البوت...
python test_bot.py

if errorlevel 1 (
    echo.
    echo ❌ فشل في الاختبارات
    echo 🔧 تحقق من الأخطاء أعلاه
    echo.
    pause
    exit /b 1
)

echo.
echo =====================================================
echo ✅ جميع الاختبارات نجحت!
echo =====================================================
echo.

if not "%TELEGRAM_BOT_TOKEN%"=="" (
    echo 🚀 هل تريد تشغيل البوت الآن؟ (y/n)
    set /p choice="الاختيار: "
    
    if /i "%choice%"=="y" (
        echo.
        echo 🤖 بدء تشغيل البوت...
        echo 📱 البوت جاهز لاستقبال الرسائل
        echo 🛑 اضغط Ctrl+C لإيقاف البوت
        echo.
        
        python bot.py
    ) else (
        echo.
        echo 💡 لتشغيل البوت لاحقاً استخدم: python bot.py
        echo.
    )
) else (
    echo 💡 لتشغيل البوت، قم بتعيين التوكن أولاً ثم استخدم:
    echo    python bot.py
    echo.
)

pause
