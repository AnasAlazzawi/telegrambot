#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Graffiti AI - Smart Telegram Bot for Virtual Try-On
بوت تليجرام ذكي لتجربة الملابس الافتراضية باستخدام الذكاء الاصطناعي
"""

import os
import logging
import asyncio
import tempfile
import aiohttp
from io import BytesIO
from PIL import Image
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from dotenv import load_dotenv
from gradio_client import Client

# تحميل متغيرات البيئة
load_dotenv()

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# حل مشكلة handle_file على Railway ومنصات النشر السحابية
try:
    from gradio_client import handle_file
    logger.info("✅ تم استيراد handle_file بنجاح")
except ImportError:
    # Fallback للإصدارات الأقدم أو عندما handle_file غير متوفر
    def handle_file(file_path):
        """Fallback function when handle_file is not available"""
        logger.warning("⚠️ استخدام fallback لـ handle_file")
        return file_path
    logger.info("⚠️ استخدام fallback لـ handle_file")
except Exception as e:
    # حل إضافي للأخطاء غير المتوقعة
    def handle_file(file_path):
        """Emergency fallback function"""
        logger.error(f"❌ خطأ في handle_file: {e}")
        return file_path
    logger.error(f"❌ خطأ في استيراد handle_file: {e}")

# الحصول على توكن التليجرام
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

if not TELEGRAM_TOKEN:
    raise ValueError("❌ TELEGRAM_TOKEN مطلوب في ملف .env")

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

# حالات المستخدمين
user_sessions = {}

class GraffitiAI:
    """فئة رئيسية لبوت Graffiti AI"""
    
    @staticmethod
    async def create_ai_client(model_key: str):
        """إنشاء عميل الذكاء الاصطناعي"""
        try:
            model_info = AI_MODELS[model_key]
            # إنشاء العميل بدون timeout (غير مدعوم في هذا الإصدار)
            client = Client(model_info["client_id"])
            logger.info(f"✅ تم الاتصال بنموذج {model_info['name']}")
            return client
        except Exception as e:
            logger.error(f"❌ خطأ في إنشاء العميل {AI_MODELS.get(model_key, {}).get('name', model_key)}: {e}")
            # محاولة الاتصال بالنموذج البديل
            try:
                if model_key == "g1_fast":
                    # جرب النموذج البديل
                    alt_client = Client("PawanratRung/virtual-try-on")
                    logger.info("✅ تم الاتصال بالنموذج البديل G1 Pro")
                    return alt_client
                elif model_key == "g1_pro":
                    # جرب النموذج البديل
                    alt_client = Client("krsatyam7/Virtual_Clothing_Try-On-new")
                    logger.info("✅ تم الاتصال بالنموذج البديل G1 Fast")
                    return alt_client
            except Exception as e2:
                logger.error(f"❌ فشل في الاتصال بالنموذج البديل: {e2}")
            return None
    
    @staticmethod
    async def download_telegram_image(file_id: str, bot):
        """تحميل وتحويل صورة من تليجرام إلى PIL Image"""
        try:
            file = await bot.get_file(file_id)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(file.file_path) as response:
                    if response.status == 200:
                        image_data = await response.read()
                        return Image.open(BytesIO(image_data))
            return None
        except Exception as e:
            logger.error(f"❌ خطأ في تحميل الصورة: {e}")
            return None
    
    @staticmethod
    async def process_virtual_tryon(person_img, garment_img, model_key, garment_type="upper_body"):
        """معالجة طلب تجربة الملابس الافتراضية"""
        try:
            # إنشاء عميل AI
            client = await GraffitiAI.create_ai_client(model_key)
            if not client:
                return None, "❌ فشل في الاتصال بخدمة الذكاء الاصطناعي"
            
            # حفظ الصور مؤقتاً
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as person_file:
                person_img.save(person_file.name, format='PNG')
                person_path = person_file.name
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as garment_file:
                garment_img.save(garment_file.name, format='PNG')
                garment_path = garment_file.name
              # تشغيل النموذج المناسب مع إعادة المحاولة
            model_info = AI_MODELS[model_key]
            result = None
            
            try:
                if model_key == "g1_fast":
                    # النموذج الأول: krsatyam7/Virtual_Clothing_Try-On-new
                    result = client.predict(
                        person_image=handle_file(person_path),
                        clothing_image=handle_file(garment_path),
                        api_name=model_info["api_endpoint"]
                    )
                else:  # g1_pro
                    # النموذج الثاني: PawanratRung/virtual-try-on
                    result = client.predict(
                        handle_file(person_path),
                        handle_file(garment_path),
                        garment_type,
                        api_name=model_info["api_endpoint"]
                    )
            except Exception as api_error:
                logger.error(f"❌ خطأ في API: {api_error}")
                # محاولة مع النموذج البديل
                try:
                    if model_key == "g1_fast":
                        # جرب النموذج البديل G1 Pro
                        alt_client = Client("PawanratRung/virtual-try-on")
                        result = alt_client.predict(
                            handle_file(person_path),
                            handle_file(garment_path),
                            "upper_body",
                            api_name="/virtual_tryon"
                        )
                    else:
                        # جرب النموذج البديل G1 Fast
                        alt_client = Client("krsatyam7/Virtual_Clothing_Try-On-new")
                        result = alt_client.predict(
                            person_image=handle_file(person_path),
                            clothing_image=handle_file(garment_path),
                            api_name="/swap_clothing"
                        )
                except Exception as fallback_error:
                    logger.error(f"❌ فشل في النموذج البديل: {fallback_error}")
                    return None, "❌ جميع النماذج غير متاحة حالياً، حاول لاحقاً"
            
            # تنظيف الملفات المؤقتة
            try:
                os.unlink(person_path)
                os.unlink(garment_path)
            except:
                pass
            
            if result:
                return result, "✅ تم إنتاج النتيجة بنجاح!"
            else:
                return None, "❌ لم يتم إنتاج نتيجة"                
        except Exception as e:
            logger.error(f"❌ خطأ في معالجة تجربة الملابس: {e}")
            return None, f"❌ خطأ: {str(e)}"
    
    @staticmethod
    async def generate_image(prompt: str, width: int = 1024, height: int = 1024):
        """توليد صورة باستخدام الذكاء الاصطناعي"""
        try:
            # إنشاء عميل توليد الصور
            client = Client("black-forest-labs/FLUX.1-dev")
            logger.info("✅ تم الاتصال بمولد الصور Graffiti G1-Image Generator")
            
            # توليد الصورة
            result = client.predict(
                prompt=prompt,
                seed=0,
                randomize_seed=True,
                width=width,
                height=height,
                guidance_scale=3.5,
                num_inference_steps=28,
                api_name="/infer"
            )
            
            if result:
                logger.info("✅ تم توليد الصورة بنجاح")
                # إذا كان النتيجة URL، نحتاج إلى تحميل الصورة
                if isinstance(result, str) and result.startswith('http'):
                    async with aiohttp.ClientSession() as session:
                        async with session.get(result) as response:
                            if response.status == 200:
                                image_data = await response.read()
                                return BytesIO(image_data), "✅ تم توليد الصورة بنجاح!"
                            else:
                                return None, "❌ فشل في تحميل الصورة المولدة"
                else:
                    # إذا كان النتيجة ملف مباشر
                    return result, "✅ تم توليد الصورة بنجاح!"
            else:
                return None, "❌ لم يتم توليد الصورة"
                
        except Exception as e:
            logger.error(f"❌ خطأ في توليد الصورة: {e}")
            return None, f"❌ خطأ في توليد الصورة: {str(e)}"

class TelegramHandlers:
    """معالجات رسائل تليجرام"""
    
    @staticmethod
    async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر البداية"""
        user = update.effective_user
        user_id = user.id
        
        # إعادة تعيين جلسة المستخدم
        user_sessions[user_id] = {}        
        keyboard = [
            [InlineKeyboardButton("🎨 تجربة الملابس الافتراضية", callback_data="start_tryon")],
            [InlineKeyboardButton("🖼️ مولد الصور الذكي", callback_data="start_image_gen")],
            [InlineKeyboardButton("ℹ️ حول Graffiti AI", callback_data="about")],
            [InlineKeyboardButton("🆘 المساعدة", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = f"""🎨 <b>مرحباً {user.mention_html()}!</b>

أنا <b>Graffiti AI</b> - بوت ذكي متطور لتجربة الملابس الافتراضية وتوليد الصور 🤖

✨ <b>الميزات المتاحة:</b>
🔥 تجربة ملابس واقعية باستخدام AI
🖼️ توليد صور إبداعية بالذكاء الاصطناعي
🚀 نماذج متطورة متعددة للاختيار
🎯 دعم أنواع ملابس متنوعة
⚡ معالجة سريعة وعالية الجودة

👇 <b>اختر ما تريد فعله:</b>"""
        
        try:
            if update.callback_query:
                await update.callback_query.edit_message_text(welcome_text, parse_mode='HTML', reply_markup=reply_markup)
            else:
                await update.message.reply_html(welcome_text, reply_markup=reply_markup)
        except Exception as e:
            logger.error(f"خطأ في إرسال رسالة البداية: {e}")
            # إرسال رسالة جديدة بدلاً من تحرير الموجودة
            if update.callback_query:
                await update.callback_query.message.reply_html(welcome_text, reply_markup=reply_markup)
            else:
                await update.message.reply_html(welcome_text, reply_markup=reply_markup)
    
    @staticmethod
    async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر المساعدة"""
        help_text = """
🆘 <b>مساعدة Graffiti AI</b>

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
/about - حول البوت
        """
        
        keyboard = [
            [InlineKeyboardButton("🎨 تجربة الملابس", callback_data="start_tryon")],
            [InlineKeyboardButton("🖼️ مولد الصور", callback_data="start_image_gen")],
            [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                help_text, parse_mode='HTML', reply_markup=reply_markup
            )
        else:
            await update.message.reply_html(help_text, reply_markup=reply_markup)
    
    @staticmethod
    async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معلومات حول البوت"""
        about_text = """
🎨 <b>Graffiti AI</b>

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
• <b>Graffiti G1-Image Generator:</b> مولد صور بـ FLUX.1-dev

<b>✨ الميزات الجديدة:</b>
🖼️ توليد صور إبداعية من الوصف النصي
🎨 تجربة ملابس افتراضية واقعية
🚀 معالجة سريعة وعالية الجودة

<b>✨ الإصدار:</b> 2.1
<b>🔧 المطور:</b> Graffiti AI Team
        """
        
        keyboard = [
            [InlineKeyboardButton("🎨 تجربة الملابس", callback_data="start_tryon")],
            [InlineKeyboardButton("🖼️ مولد الصور", callback_data="start_image_gen")],
            [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                about_text, parse_mode='HTML', reply_markup=reply_markup
            )
        else:
            await update.message.reply_html(about_text, reply_markup=reply_markup)
    
    @staticmethod
    async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة ضغطات الأزرار"""
        try:
            query = update.callback_query
            user_id = query.from_user.id
            data = query.data
            
            await query.answer()
            
            if data == "main_menu":
                await TelegramHandlers.start_command(update, context)
                
            elif data == "help":
                await TelegramHandlers.help_command(update, context)
                
            elif data == "about":
                await TelegramHandlers.about_command(update, context)
                
            elif data == "start_tryon":
                await TelegramHandlers.start_virtual_tryon(update, context)
                
            elif data == "start_image_gen":
                await TelegramHandlers.start_image_generation(update, context)
                
            elif data.startswith("select_model_"):
                model_key = data.replace("select_model_", "")
                await TelegramHandlers.model_selected(update, context, model_key)
                
            elif data.startswith("garment_"):
                garment_type = data.replace("garment_", "")
                await TelegramHandlers.garment_type_selected(update, context, garment_type)
        
        except Exception as e:
            logger.error(f"خطأ في معالجة الضغط: {e}")
            try:
                await update.callback_query.answer("❌ حدث خطأ، حاول مرة أخرى")
            except:
                pass
    
    @staticmethod
    async def start_virtual_tryon(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """بدء تجربة الملابس الافتراضية"""
        user_id = update.callback_query.from_user.id
        
        user_sessions[user_id] = {
            "mode": "virtual_tryon",
            "step": "select_model"
        }
        
        keyboard = [
            [InlineKeyboardButton("🔥 Graffiti G1 Fast", callback_data="select_model_g1_fast")],
            [InlineKeyboardButton("🚀 Graffiti G1 Pro", callback_data="select_model_g1_pro")],
            [InlineKeyboardButton("🔙 العودة", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        model_text = """
🎨 <b>اختر نموذج Graffiti AI</b>

<b>🔥 Graffiti G1 Fast:</b>
• معالجة سريعة ومحسنة
• مناسب للاستخدام اليومي
• نتائج عالية الجودة

<b>🚀 Graffiti G1 Pro:</b>
• نموذج متقدم ومتطور
• دعم أنواع ملابس متعددة
• دقة عالية جداً
• خيارات تخصيص أكثر

👇 <b>اختر النموذج المناسب:</b>
        """
        
        await update.callback_query.edit_message_text(
            model_text, parse_mode='HTML', reply_markup=reply_markup
        )
    
    @staticmethod
    async def model_selected(update: Update, context: ContextTypes.DEFAULT_TYPE, model_key: str):
        """تم اختيار النموذج"""
        user_id = update.callback_query.from_user.id
        user_sessions[user_id]["model"] = model_key
        user_sessions[user_id]["step"] = "upload_person"
        
        model_name = AI_MODELS[model_key]["name"]
        
        if model_key == "g1_pro":
            # للنموذج المتقدم، اختر نوع الملابس أولاً
            keyboard = [
                [InlineKeyboardButton("👕 ملابس علوية", callback_data="garment_upper")],
                [InlineKeyboardButton("👖 ملابس سفلية", callback_data="garment_lower")],
                [InlineKeyboardButton("👗 فساتين", callback_data="garment_dress")],
                [InlineKeyboardButton("🔙 تغيير النموذج", callback_data="start_tryon")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.callback_query.edit_message_text(
                f"✅ تم اختيار: <b>{model_name}</b>\n\n"
                "👔 اختر نوع الملابس التي ستجربها:",
                parse_mode='HTML',
                reply_markup=reply_markup
            )
        else:
            # للنموذج السريع، انتقل مباشرة لرفع صورة الشخص
            keyboard = [
                [InlineKeyboardButton("🔙 تغيير النموذج", callback_data="start_tryon")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.callback_query.edit_message_text(
                f"✅ تم اختيار: <b>{model_name}</b>\n\n"
                "📸 أرسل صورة الشخص الذي تريد تجربة الملابس عليه\n\n"
                "💡 <b>نصائح:</b>\n"
                "• صورة واضحة وعالية الجودة\n"
                "• إضاءة جيدة\n"
                "• خلفية بسيطة",
                parse_mode='HTML',
                reply_markup=reply_markup
            )
    
    @staticmethod
    async def garment_type_selected(update: Update, context: ContextTypes.DEFAULT_TYPE, garment_type: str):
        """تم اختيار نوع الملابس"""
        user_id = update.callback_query.from_user.id
        user_sessions[user_id]["garment_type"] = GARMENT_TYPES[garment_type]["id"]
        user_sessions[user_id]["step"] = "upload_person"
        
        type_name = GARMENT_TYPES[garment_type]["name"]
        keyboard = [
            [InlineKeyboardButton("🔙 تغيير النوع", callback_data="select_model_g1_pro")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            f"✅ تم اختيار: <b>{type_name}</b>\n\n"
            "📸 أرسل صورة الشخص الذي تريد تجربة الملابس عليه\n\n"
            "💡 <b>نصائح:</b>\n"
            "• صورة واضحة وعالية الجودة\n"
            "• إضاءة جيدة\n"
            "• خلفية بسيطة",
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    
    @staticmethod
    async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة الصور المرسلة"""
        user_id = update.effective_user.id
        
        if user_id not in user_sessions or user_sessions[user_id].get("mode") != "virtual_tryon":
            await update.message.reply_text("🎨 لبدء تجربة الملابس، استخدم الأمر /start")
            return
        
        session = user_sessions[user_id]
        photo = update.message.photo[-1]
        
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        if session.get("step") == "upload_person":
            # رفع صورة الشخص
            image = await GraffitiAI.download_telegram_image(photo.file_id, context.bot)
            if image:
                session["person_image"] = image
                session["step"] = "upload_garment"
                
                await update.message.reply_text(
                    "✅ تم حفظ صورة الشخص!\n\n"
                    "👕 الآن أرسل صورة الملابس التي تريد تجربتها\n\n"
                    "💡 <b>نصائح للملابس:</b>\n"
                    "• خلفية بيضاء أو بسيطة\n"
                    "• ملابس واضحة ومفصلة\n"
                    "• تجنب الظلال القوية",
                    parse_mode='HTML'
                )
            else:
                await update.message.reply_text("❌ فشل في معالجة الصورة. حاول مرة أخرى.")
        
        elif session.get("step") == "upload_garment":
            # رفع صورة الملابس ومعالجة الطلب
            image = await GraffitiAI.download_telegram_image(photo.file_id, context.bot)
            if image:
                session["garment_image"] = image
                session["step"] = "processing"
                
                processing_msg = await update.message.reply_text(
                    "⚡ <b>Graffiti AI يعمل...</b>\n\n"
                    "🔄 جاري معالجة طلبك\n"
                    "⏳ هذا قد يستغرق بضع ثوانٍ",
                    parse_mode='HTML'
                )
                
                # معالجة تجربة الملابس
                result, status = await GraffitiAI.process_virtual_tryon(
                    session["person_image"],
                    session["garment_image"],
                    session["model"],
                    session.get("garment_type", "upper_body")
                )
                
                await processing_msg.delete()
                
                if result:
                    keyboard = [
                        [InlineKeyboardButton("🔄 تجربة أخرى", callback_data="start_tryon")],
                        [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    model_name = AI_MODELS[session["model"]]["name"]
                    
                    await context.bot.send_photo(
                        chat_id=update.effective_chat.id,
                        photo=result,
                        caption=f"🎨 <b>Graffiti AI - النتيجة</b>\n\n"
                               f"✨ {status}\n"
                               f"🤖 النموذج: {model_name}\n\n"
                               f"🔥 تم إنتاج هذه النتيجة بتقنية الذكاء الاصطناعي المتطورة!",
                        parse_mode='HTML',
                        reply_markup=reply_markup
                    )
                else:
                    keyboard = [
                        [InlineKeyboardButton("🔄 حاول مرة أخرى", callback_data="start_tryon")],
                        [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await update.message.reply_text(
                        f"❌ {status}\n\n"
                        "💡 نصائح لنتائج أفضل:\n"
                        "• استخدم صور أوضح\n"
                        "• تأكد من الإضاءة الجيدة\n"
                        "• جرب نموذج مختلف",
                        reply_markup=reply_markup
                    )
                
                # إعادة تعيين الجلسة
                user_sessions[user_id] = {}
            else:                await update.message.reply_text("❌ فشل في معالجة صورة الملابس. حاول مرة أخرى.")
    
    @staticmethod
    async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة الرسائل النصية"""
        user_id = update.effective_user.id
        
        # التحقق من وضع توليد الصور
        if user_id in user_sessions and user_sessions[user_id].get("mode") == "image_generation":
            if user_sessions[user_id].get("step") == "waiting_prompt":
                prompt = update.message.text
                await TelegramHandlers.handle_image_generation_text(update, context, prompt)
                return
        
        # الرد الافتراضي
        await update.message.reply_text(
            "🎨 مرحباً! أنا Graffiti AI\n\n"
            "استخدم /start لبدء تجربة الملابس الافتراضية أو توليد الصور ✨"
        )
    
    @staticmethod
    async def start_image_generation(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """بدء توليد الصور بالذكاء الاصطناعي"""
        user_id = update.callback_query.from_user.id
        
        user_sessions[user_id] = {
            "mode": "image_generation",
            "step": "waiting_prompt"
        }
        
        keyboard = [
            [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        prompt_text = """
🖼️ <b>Graffiti G1-Image Generator</b>

🎨 <b>مولد الصور الذكي بالذكاء الاصطناعي</b>

✨ <b>الميزات:</b>
• تقنية FLUX.1-dev المتطورة
• صور عالية الجودة (1024x1024)
• دعم الوصف باللغة العربية والإنجليزية
• معالجة سريعة ومتطورة

📝 <b>كيفية الاستخدام:</b>
أرسل وصفاً تفصيلياً للصورة التي تريد إنشاءها

💡 <b>أمثلة على الأوصاف:</b>
• "قطة جميلة في الحديقة"
• "منظر طبيعي خلاب عند الغروب"
• "سيارة رياضية حمراء في المدينة"
• "A majestic lion in the savanna"

✍️ <b>اكتب وصف الصورة التي تريد إنشاءها:</b>
        """
        
        await update.callback_query.edit_message_text(
            prompt_text, parse_mode='HTML', reply_markup=reply_markup
        )
    
    @staticmethod
    async def handle_image_generation_text(update: Update, context: ContextTypes.DEFAULT_TYPE, prompt: str):
        """معالجة طلب توليد الصورة"""
        user_id = update.effective_user.id
        
        # إرسال رسالة المعالجة
        processing_msg = await update.message.reply_text(
            "🖼️ <b>Graffiti G1-Image Generator يعمل...</b>\n\n"
            "🎨 جاري إنشاء صورتك الفنية\n"
            "⏳ هذا قد يستغرق 30-60 ثانية\n"
            "✨ نستخدم تقنية FLUX.1-dev المتطورة",
            parse_mode='HTML'
        )
        
        # توليد الصورة
        result, status = await GraffitiAI.generate_image(prompt)
        
        await processing_msg.delete()
        
        if result:
            keyboard = [
                [InlineKeyboardButton("🖼️ إنشاء صورة أخرى", callback_data="start_image_gen")],
                [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=result,
                caption=f"🖼️ <b>Graffiti G1-Image Generator</b>\n\n"
                       f"✨ {status}\n"
                       f"📝 الوصف: {prompt}\n"
                       f"🤖 النموذج: FLUX.1-dev\n\n"
                       f"🎨 تم إنشاء هذه الصورة بتقنية الذكاء الاصطناعي المتطورة!",
                parse_mode='HTML',
                reply_markup=reply_markup
            )
        else:
            keyboard = [
                [InlineKeyboardButton("🔄 حاول مرة أخرى", callback_data="start_image_gen")],
                [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"❌ {status}\n\n"
                "💡 نصائح لنتائج أفضل:\n"
                "• استخدم وصفاً أكثر تفصيلاً\n"
                "• تجنب الكلمات المعقدة\n"
                "• جرب وصفاً مختلفاً",
                reply_markup=reply_markup
            )
        
        # إعادة تعيين الجلسة
        user_sessions[user_id] = {}

def main():
    """تشغيل البوت"""
    try:
        # إنشاء التطبيق
        app = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # إضافة المعالجات
        app.add_handler(CommandHandler("start", TelegramHandlers.start_command))
        app.add_handler(CommandHandler("help", TelegramHandlers.help_command))
        app.add_handler(CommandHandler("about", TelegramHandlers.about_command))
        
        app.add_handler(CallbackQueryHandler(TelegramHandlers.handle_callback))
        app.add_handler(MessageHandler(filters.PHOTO, TelegramHandlers.handle_photo))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, TelegramHandlers.handle_text))
        
        # إضافة معالج الأخطاء
        async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
            logger.error("Exception while handling an update:", exc_info=context.error)
        
        app.add_error_handler(error_handler)
        
        # رسائل بدء التشغيل
        logger.info("🎨 Graffiti AI Bot Started Successfully!")
        print("=" * 50)
        print("🎨 GRAFFITI AI BOT")
        print("=" * 50)
        print("✅ البوت يعمل الآن!")
        print("🔥 Graffiti G1 Fast - نموذج سريع")
        print("🚀 Graffiti G1 Pro - نموذج متقدم")
        print("🖼️ Graffiti G1-Image Generator - مولد صور ذكي")
        print("⚡ تجربة ملابس افتراضية بالذكاء الاصطناعي")
        print("🎨 توليد صور إبداعية بتقنية FLUX.1-dev")
        print("🛑 اضغط Ctrl+C للإيقاف")
        print("=" * 50)
        
        # تشغيل البوت
        app.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        logger.error(f"❌ خطأ في تشغيل البوت: {e}")
        print(f"❌ خطأ في تشغيل البوت: {e}")

if __name__ == '__main__':
    main()
