#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار بسيط للتأكد من عمل المكتبات
"""

import os
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

# الحصول على التوكنات
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

print("🔍 اختبار التوكنات...")
print(f"✅ TELEGRAM_TOKEN: {TELEGRAM_TOKEN[:10]}..." if TELEGRAM_TOKEN else "❌ TELEGRAM_TOKEN غير موجود")
print(f"✅ GEMINI_API_KEY: {GEMINI_API_KEY[:10]}..." if GEMINI_API_KEY else "❌ GEMINI_API_KEY غير موجود")

# اختبار المكتبات
try:
    import telegram
    print("✅ مكتبة telegram متوفرة")
except ImportError as e:
    print(f"❌ خطأ في مكتبة telegram: {e}")

try:
    import google.generativeai as genai
    print("✅ مكتبة google.generativeai متوفرة")
    
    # اختبار إعداد Gemini
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        print("✅ تم إعداد Gemini بنجاح")
    else:
        print("⚠️ لا يمكن اختبار Gemini بدون API Key")
        
except ImportError as e:
    print(f"❌ خطأ في مكتبة google.generativeai: {e}")
except Exception as e:
    print(f"⚠️ خطأ في إعداد Gemini: {e}")

print("\n🚀 يمكنك الآن تشغيل البوت بالأمر: python bot.py")
