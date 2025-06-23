# 🚀 دليل النشر السريع - Graffiti AI Bot

## خطوات النشر على Railway

### 1. إعداد البوت في تليجرام
```
1. ابحث عن @BotFather في تليجرام
2. أرسل /newbot
3. اختر اسم البوت: Graffiti AI
4. اختر معرف البوت: graffiti_ai_bot (أو أي اسم متاح)
5. احفظ التوكن الذي سيرسله لك
```

### 2. رفع الكود إلى GitHub
```bash
# إنشاء مستودع جديد على GitHub
# ثم في مجلد المشروع:
git init
git add .
git commit -m "Initial commit - Graffiti AI Bot"
git branch -M main
git remote add origin https://github.com/yourusername/graffiti-ai-bot.git
git push -u origin main
```

### 3. النشر على Railway
```
1. اذهب إلى railway.app
2. سجل دخول أو أنشئ حساب
3. اضغط "New Project"
4. اختر "Deploy from GitHub repo"
5. اختر المستودع الذي أنشأته
6. Railway سيبدأ النشر تلقائياً
```

### 4. إعداد متغيرات البيئة
```
1. في لوحة تحكم Railway، اذهب إلى تبويب "Variables"
2. أضف متغير جديد:
   - Name: TELEGRAM_BOT_TOKEN
   - Value: [التوكن الذي حصلت عليه من BotFather]
3. احفظ التغييرات
```

### 5. التحقق من التشغيل
```
1. اذهب إلى تبويب "Logs"
2. يجب أن ترى: "🚀 بدء تشغيل Graffiti AI Bot..."
3. جرب إرسال /start للبوت في تليجرام
```

## 🛠️ استكشاف الأخطاء

### البوت لا يرد:
- تحقق من صحة التوكن في متغيرات البيئة
- تحقق من Logs في Railway
- تأكد من أن الخدمة تعمل (Deploy logs)

### رسائل خطأ:
- راجع Logs في Railway للتفاصيل
- تحقق من اتصال الإنترنت
- قد تحتاج إعادة تشغيل (Redeploy)

### مشاكل في معالجة الصور:
- تحقق من أن Gradio Client يعمل
- قد تكون الخدمة مشغولة، انتظر وحاول مرة أخرى

## 📊 مراقبة الأداء

- راقب Logs بانتظام
- تحقق من استخدام الذاكرة والمعالج
- اهتم بزمن الاستجابة للمستخدمين

## 🔄 التحديثات

لتحديث البوت:
```bash
# في مجلد المشروع:
git add .
git commit -m "Update bot features"
git push
```
Railway سيعيد النشر تلقائياً عند push جديد.

---

## 🎉 تم! البوت جاهز للاستخدام

بمجرد اكتمال النشر، ابحث عن البوت في تليجرام وجرب إرسال `/start`
