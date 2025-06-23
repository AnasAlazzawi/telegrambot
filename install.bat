@echo off
echo 📦 تثبيت متطلبات التطبيق...
echo.

REM تحديث pip
python -m pip install --upgrade pip

REM تثبيت المتطلبات
pip install -r requirements.txt

echo.
echo ✅ تم تثبيت جميع المتطلبات بنجاح!
echo.
echo يمكنك الآن تشغيل التطبيق بالنقر على start.bat
echo أو تشغيل الأمر: python web_app.py
echo.
pause
