#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إعدادات البوت والمتغيرات الثابتة
Bot Configuration and Constants
"""

import os
import logging
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# توكن التليجرام ومفاتيح API
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# التحقق من المتغيرات المطلوبة
if not TELEGRAM_TOKEN:
    raise ValueError("❌ TELEGRAM_TOKEN مطلوب في ملف .env")

if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY مطلوب في ملف .env")

# نماذج الذكاء الاصطناعي المتاحة
AI_MODELS = {
    "g1_fast": {
        "name": "Graffiti G1 Fast",
        "client_id": "krsatyam7/Virtual_Clothing_Try-On-new",
        "api_endpoint": "/swap_clothing",
        "description": "نموذج سريع ومحسن للاستخدام اليومي"
    },
    "g1_pro": {
        "name": "Graffiti G1 Pro", 
        "client_id": "PawanratRung/virtual-try-on",
        "api_endpoint": "/virtual_tryon",
        "description": "نموذج متقدم مع خيارات متنوعة للملابس"
    },
    "g1_image": {
        "name": "Graffiti G1-Image Generator",
        "client_id": "black-forest-labs/FLUX.1-dev",
        "api_endpoint": "/infer",
        "description": "مولد صور ذكي بالذكاء الاصطناعي"
    }
}

# أنواع الملابس للنموذج المتقدم
GARMENT_TYPES = {
    "upper": {"id": "upper_body", "name": "ملابس علوية"},
    "lower": {"id": "lower_body", "name": "ملابس سفلية"}, 
    "dress": {"id": "dresses", "name": "فساتين"}
}

# رسائل البوت
MESSAGES = {
    "welcome": """🎨 <b>مرحباً {user}!</b>

أنا <b>Graffiti AI</b> - بوت ذكي متطور لتجربة الملابس الافتراضية وتوليد الصور 🤖

✨ <b>الميزات المتاحة:</b>
🔥 تجربة ملابس واقعية باستخدام AI
🖼️ توليد صور إبداعية بالذكاء الاصطناعي
🚀 نماذج متطورة متعددة للاختيار
🎯 دعم أنواع ملابس متنوعة
⚡ معالجة سريعة وعالية الجودة

👇 <b>اختر ما تريد فعله:</b>""",

    "help": """🆘 <b>مساعدة Graffiti AI</b>

<b>🎯 كيفية استخدام تجربة الملابس:</b>
1️⃣ اضغط "تجربة الملابس الافتراضية"
2️⃣ اختر النموذج المناسب
3️⃣ ارفع صورة الشخص
4️⃣ ارفع صورة الملابس
5️⃣ احصل على النتيجة!

<b>🖼️ كيفية استخدام مولد الصور:</b>
1️⃣ اضغط "مولد الصور الذكي"
2️⃣ اكتب وصف الصورة المطلوبة
3️⃣ انتظر النتيجة (30-60 ثانية)

<b>🤖 النماذج المتاحة:</b>
🔥 <b>Graffiti G1 Fast:</b> سريع ومحسن
🚀 <b>Graffiti G1 Pro:</b> متقدم مع خيارات أكثر
🖼️ <b>Graffiti G1-Image Generator:</b> توليد صور بـ FLUX.1-dev

<b>💡 نصائح للنتائج الأفضل:</b>
• استخدم صور واضحة وعالية الجودة
• تأكد من إضاءة جيدة في الصور
• اختر خلفيات بسيطة للملابس
• استخدم أوصافاً مفصلة للصور

<b>📞 الأوامر المتاحة:</b>
/start - القائمة الرئيسية
/help - هذه المساعدة
/about - حول البوت""",

    "about": """🎨 <b>Graffiti AI</b>

<b>🤖 حول البوت:</b>
Graffiti AI هو بوت ذكي متطور يستخدم أحدث تقنيات الذكاء الاصطناعي لتجربة الملابس الافتراضية وتوليد الصور الإبداعية

<b>⚡ التقنيات المستخدمة:</b>
• نماذج AI متطورة للرؤية الحاسوبية
• تقنية FLUX.1-dev لتوليد الصور
• معالجة الصور بالذكاء الاصطناعي
• خوارزميات التعلم العميق المتطورة
• واجهة تليجرام تفاعلية وسهلة

<b>🔥 النماذج المتاحة:</b>
• <b>Graffiti G1 Fast:</b> نموذج محسن للسرعة
• <b>Graffiti G1 Pro:</b> نموذج متقدم للدقة
• <b>Graffiti G1-Image Generator:</b> مولد صور إبداعي

<b>✨ الميزات الجديدة:</b>
🖼️ توليد صور إبداعية من الوصف النصي
🎨 تجربة ملابس افتراضية واقعية
🚀 معالجة سريعة وعالية الجودة
🌍 دعم كامل للغة العربية

<b>✨ الإصدار:</b> 2.2
<b>🔧 المطور:</b> Graffiti AI Team"""
}
