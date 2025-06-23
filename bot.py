#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
بوت تليجرام ذكي لتجربة الملابس الافتراضية باستخدام AI
Smart Telegram Bot for Virtual Try-On using AI
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

# الحصول على التوكنات من متغيرات البيئة
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

# التحقق من وجود التوكنات
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN غير موجود في ملف .env")

# حالات المستخدمين للتفاعل مع الملابس
user_states = {}

# خيارات النماذج المتاحة
MODELS = {
    "model1": {
        "name": "النموذج الأول - Kolors",
        "client": "krsatyam7/Virtual_Clothing_Try-On-new",
        "api": "/swap_clothing"
    },
    "model2": {
        "name": "النموذج الثاني - PawanratRung", 
        "client": "PawanratRung/virtual-try-on",
        "api": "/virtual_tryon"
    }
}

# أنواع الملابس للنموذج الثاني
GARMENT_TYPES = {
    "upper": "upper_body",
    "lower": "lower_body", 
    "dress": "dresses"
}

# دوال تجربة الملابس الافتراضية
async def initialize_virtual_tryon_client(model_choice):
    """تهيئة عميل تجربة الملابس"""
    try:
        client_id = MODELS[model_choice]["client"]
        client = Client(client_id)
        return client
    except Exception as e:
        logger.error(f"خطأ في تهيئة عميل تجربة الملابس: {e}")
        return None

async def download_image_from_telegram(file_path, bot):
    """تحميل صورة من تليجرام وتحويلها إلى PIL Image"""
    try:
        file = await bot.get_file(file_path)
        
        # تحميل البيانات
        async with aiohttp.ClientSession() as session:
            async with session.get(file.file_path) as response:
                if response.status == 200:
                    image_data = await response.read()
                    image = Image.open(BytesIO(image_data))
                    return image
                else:
                    return None
    except Exception as e:
        logger.error(f"خطأ في تحميل الصورة: {e}")
        return None

async def process_virtual_tryon(person_image, garment_image, model_choice, garment_type="upper_body"):
    """معالجة طلب تجربة الملابس الافتراضية"""
    try:
        # تهيئة العميل
        client = await initialize_virtual_tryon_client(model_choice)
        if client is None:
            return None, "❌ خطأ في الاتصال بخدمة تجربة الملابس"
        
        # حفظ الصور مؤقتاً
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as person_temp:
            person_image.save(person_temp.name, format='PNG')
            person_temp_path = person_temp.name
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as garment_temp:
            garment_image.save(garment_temp.name, format='PNG')
            garment_temp_path = garment_temp.name
        
        # تشغيل النموذج المناسب مع معالجة أفضل للملفات
        try:
            if model_choice == "model1":
                # استخدام handle_file إذا كان متوفراً، وإلا استخدام المسار مباشرة
                try:
                    result = client.predict(
                        person_image=handle_file(person_temp_path),
                        clothing_image=handle_file(garment_temp_path),
                        api_name="/swap_clothing"
                    )
                except:
                    # Fallback: استخدام المسار مباشرة
                    result = client.predict(
                        person_image=person_temp_path,
                        clothing_image=garment_temp_path,
                        api_name="/swap_clothing"
                    )
            else:  # model2
                try:
                    result = client.predict(
                        person_path=handle_file(person_temp_path),
                        garment_path=handle_file(garment_temp_path),
                        garment_type=garment_type,
                        api_name="/virtual_tryon"
                    )
                except:
                    # Fallback: استخدام المسار مباشرة
                    result = client.predict(
                        person_path=person_temp_path,
                        garment_path=garment_temp_path,
                        garment_type=garment_type,
                        api_name="/virtual_tryon"
                    )
                    
        except Exception as api_error:
            logger.error(f"خطأ في استدعاء API: {api_error}")
            return None, f"❌ خطأ في معالجة الصور: {str(api_error)}"
        
        # تنظيف الملفات المؤقتة
        try:
            os.unlink(person_temp_path)
            os.unlink(garment_temp_path)
        except:
            pass
        
        return result, "✅ تم إنشاء النتيجة بنجاح!"
        
    except Exception as e:
        logger.error(f"خطأ في معالجة تجربة الملابس: {e}")
        return None, f"❌ خطأ: {str(e)}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """إرسال رسالة عند الأمر /start."""
    user = update.effective_user
    user_id = user.id
    
    # إعادة تعيين حالة المستخدم
    user_states[user_id] = {}
    
    # إنشاء لوحة المفاتيح
    keyboard = [
        [InlineKeyboardButton("👕 تجربة الملابس الافتراضية", callback_data="virtual_tryon")],
        [InlineKeyboardButton("ℹ️ المساعدة", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_html(
        f"🎉 <b>مرحباً {user.mention_html()}!</b> 🤖\n\n"
        f"أنا بوت ذكي لتجربة الملابس الافتراضية باستخدام الذكاء الاصطناعي\n\n"
        f"👕 <b>تجربة الملابس الافتراضية</b>\n"
        f"   • جرب الملابس على أي شخص باستخدام AI\n"
        f"   • نموذجان متطوران للاختيار\n"
        f"   • نتائج واقعية ومذهلة\n"
        f"   • أنواع ملابس متنوعة (علوية، سفلية، فساتين)\n\n"
        f"👇 <b>اضغط على الزر أدناه لبدء تجربة الملابس:</b>",
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """إرسال رسالة المساعدة عند الأمر /help."""
    keyboard = [
        [InlineKeyboardButton("👕 تجربة الملابس", callback_data="virtual_tryon")],
        [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    help_text = """
🤖 *مساعدة بوت تجربة الملابس الافتراضية*

*🎯 الخدمات المتاحة:*

*👕 تجربة الملابس الافتراضية:*
• ارفع صورة شخص + صورة ملابس
• اختر النموذج المناسب (Kolors أو PawanratRung)
• احصل على نتيجة واقعية مذهلة

* الأوامر:*
/start - القائمة الرئيسية
/help - هذه المساعدة
/tryon - بدء تجربة الملابس مباشرة

*💡 نصائح للحصول على أفضل النتائج:*
• استخدم صور واضحة وعالية الجودة
• تأكد من ظهور الشخص كاملاً في الصورة
• اختر ملابس بخلفية بسيطة
• تجنب الصور الضبابية أو المظلمة

*🔧 النماذج المتاحة:*
• النموذج الأول (Kolors): سريع وسهل الاستخدام
• النموذج الثاني (PawanratRung): يدعم أنواع ملابس متنوعة
    """
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            help_text, 
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            help_text, 
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة الضغط على الأزرار"""
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    
    await query.answer()
    
    if data == "virtual_tryon":
        # بدء تجربة الملابس
        user_states[user_id] = {
            "mode": "virtual_tryon",
            "step": "choose_model",
            "person_image": None,
            "garment_image": None,
            "model": None,
            "garment_type": "upper_body"
        }
        
        keyboard = [
            [InlineKeyboardButton("🎨 " + MODELS["model1"]["name"], callback_data="select_model1")],
            [InlineKeyboardButton("🚀 " + MODELS["model2"]["name"], callback_data="select_model2")],
            [InlineKeyboardButton("🔙 العودة", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "👕 *تجربة الملابس الافتراضية*\n\n"
            "اختر النموذج الذي تريد استخدامه:\n\n"
            "🎨 *النموذج الأول (Kolors):*\n"
            "• أسرع في المعالجة\n"
            "• سهل الاستخدام\n"
            "• مناسب للاستخدام السريع\n\n"
            "🚀 *النموذج الثاني (PawanratRung):*\n"
            "• يدعم أنواع ملابس متنوعة\n"
            "• نتائج أكثر تفصيلاً\n"
            "• خيارات متقدمة أكثر",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    elif data.startswith("select_model"):
        model_num = data.replace("select_model", "")
        user_states[user_id]["model"] = f"model{model_num}"
        user_states[user_id]["step"] = "upload_person"
        
        selected_model = MODELS[f"model{model_num}"]["name"]
        
        # إذا كان النموذج الثاني، اطلب نوع الملابس
        if model_num == "2":
            keyboard = [
                [InlineKeyboardButton("👔 ملابس علوية (قمصان، بلوزات)", callback_data="garment_upper")],
                [InlineKeyboardButton("👖 ملابس سفلية (بناطيل)", callback_data="garment_lower")],
                [InlineKeyboardButton("👗 فساتين", callback_data="garment_dress")],
                [InlineKeyboardButton("🔙 تغيير النموذج", callback_data="virtual_tryon")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            user_states[user_id]["step"] = "choose_garment_type"
            
            await query.edit_message_text(
                f"✅ تم اختيار: *{selected_model}*\n\n"
                "👔 اختر نوع الملابس التي ستجربها:",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        else:
            keyboard = [
                [InlineKeyboardButton("🔙 تغيير النموذج", callback_data="virtual_tryon")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                f"✅ تم اختيار: *{selected_model}*\n\n"
                "📸 الآن أرسل صورة الشخص الذي تريد تجربة الملابس عليه\n\n"
                "💡 *نصائح للحصول على أفضل النتائج:*\n"
                "• استخدم صورة واضحة وعالية الجودة\n"
                "• تأكد من ظهور الشخص كاملاً\n"
                "• تجنب الخلفيات المعقدة",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
    
    elif data.startswith("garment_"):
        garment_type = data.replace("garment_", "")
        user_states[user_id]["garment_type"] = GARMENT_TYPES[garment_type]
        user_states[user_id]["step"] = "upload_person"
        
        type_names = {
            "upper": "ملابس علوية (قمصان، بلوزات)",
            "lower": "ملابس سفلية (بناطيل)",
            "dress": "فساتين"
        }
        
        keyboard = [
            [InlineKeyboardButton("🔙 تغيير النوع", callback_data="select_model2")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"✅ تم اختيار: *{type_names[garment_type]}*\n\n"
            "📸 الآن أرسل صورة الشخص الذي تريد تجربة الملابس عليه\n\n"
            "💡 *نصائح للحصول على أفضل النتائج:*\n"
            "• استخدم صورة واضحة وعالية الجودة\n"
            "• تأكد من ظهور الشخص كاملاً\n"
            "• تجنب الخلفيات المعقدة",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    elif data == "help":
        await help_command(update, context)
    
    elif data == "main_menu":
        # إعادة تعيين حالة المستخدم
        user_states[user_id] = {}
        
        # إنشاء لوحة المفاتيح
        keyboard = [
            [InlineKeyboardButton("� تجربة الملابس الافتراضية", callback_data="virtual_tryon")],
            [InlineKeyboardButton("ℹ️ المساعدة", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"🎉 <b>مرحباً بك مرة أخرى!</b> 🤖\n\n"
            f"أنا بوت ذكي لتجربة الملابس الافتراضية باستخدام الذكاء الاصطناعي\n\n"
            f"👕 <b>تجربة الملابس الافتراضية</b>\n"
            f"   • جرب الملابس على أي شخص باستخدام AI\n"
            f"   • نموذجان متطوران للاختيار\n"
            f"   • نتائج واقعية ومذهلة\n"
            f"   • أنواع ملابس متنوعة (علوية، سفلية، فساتين)\n\n"
            f"👇 <b>اضغط على الزر أدناه لبدء تجربة الملابس:</b>",
            parse_mode='HTML',
            reply_markup=reply_markup
        )

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """عرض القائمة الرئيسية مع الأزرار"""
    user = update.effective_user
    user_id = user.id
    
    # إعادة تعيين حالة المستخدم
    user_states[user_id] = {}
    
    # إنشاء لوحة المفاتيح
    keyboard = [
        [InlineKeyboardButton("👕 تجربة الملابس الافتراضية", callback_data="virtual_tryon")],
        [InlineKeyboardButton("ℹ️ المساعدة", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_html(
        f"🎉 <b>مرحباً {user.mention_html()}!</b> 🤖\n\n"
        f"أنا بوت ذكي لتجربة الملابس الافتراضية باستخدام الذكاء الاصطناعي\n\n"
        f"👕 <b>تجربة الملابس الافتراضية</b>\n"
        f"   • جرب الملابس على أي شخص باستخدام AI\n"
        f"   • نموذجان متطوران للاختيار\n"
        f"   • نتائج واقعية ومذهلة\n"
        f"   • أنواع ملابس متنوعة (علوية، سفلية، فساتين)\n\n"
        f"👇 <b>اضغط على الزر أدناه لبدء تجربة الملابس:</b>",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """التعامل مع الرسائل النصية والصور."""
    try:
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name
        
        # التحقق من حالة المستخدم
        if user_id not in user_states:
            user_states[user_id] = {}
        
        user_state = user_states[user_id]
        
        # معالجة الصور لتجربة الملابس
        if update.message.photo and user_state.get("mode") == "virtual_tryon":
            await handle_photo_for_tryon(update, context)
            return
        
        # معالجة الرسائل النصية
        if update.message.text:
            # إذا لم يكن لديه وضع محدد، عرض القائمة الرئيسية
            if not user_state.get("mode"):
                await show_main_menu(update, context)
                return
            
            # رسالة تذكير للمستخدم بالعملية الجارية
            if user_state.get("mode") == "virtual_tryon":
                step = user_state.get("step", "")
                if step == "upload_person":
                    await update.message.reply_text(
                        "📸 أنتظر منك إرسال صورة الشخص، وليس رسالة نصية.\n\n"
                        "💡 ارفع الصورة كصورة (Photo) وليس كملف."
                    )
                elif step == "upload_garment":
                    await update.message.reply_text(
                        "👕 أنتظر منك إرسال صورة الملابس، وليس رسالة نصية.\n\n"
                        "💡 ارفع الصورة كصورة (Photo) وليس كملف."
                    )
                else:
                    # إذا لم يكن في خطوة تحميل، أعرض القائمة الرئيسية
                    await show_main_menu(update, context)
        
    except Exception as e:
        logger.error(f"خطأ في معالجة الرسالة: {e}")
        await update.message.reply_text(
            "عذراً، حدث خطأ أثناء معالجة رسالتك. يرجى المحاولة مرة أخرى. 🙏"
        )

async def handle_photo_for_tryon(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة الصور لتجربة الملابس الافتراضية"""
    user_id = update.effective_user.id
    user_state = user_states[user_id]
    
    try:
        # الحصول على أكبر حجم للصورة
        photo = update.message.photo[-1]
        
        # إرسال إشعار "يكتب..."
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        if user_state.get("step") == "upload_person":
            # تحميل صورة الشخص
            image = await download_image_from_telegram(photo.file_id, context.bot)
            if image:
                user_state["person_image"] = image
                user_state["step"] = "upload_garment"
                
                keyboard = [
                    [InlineKeyboardButton("🔙 تغيير صورة الشخص", callback_data="virtual_tryon")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    "✅ تم حفظ صورة الشخص بنجاح!\n\n"
                    "👕 الآن أرسل صورة الملابس التي تريد تجربتها\n\n"
                    "💡 *نصائح للملابس:*\n"
                    "• اختر ملابس بخلفية بيضاء أو بسيطة\n"
                    "• تأكد من وضوح الملابس في الصورة\n"
                    "• تجنب الصور الضبابية",
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
            else:
                await update.message.reply_text(
                    "❌ فشل في تحميل الصورة. حاول مرة أخرى."
                )
        
        elif user_state.get("step") == "upload_garment":
            # تحميل صورة الملابس
            image = await download_image_from_telegram(photo.file_id, context.bot)
            if image:
                user_state["garment_image"] = image
                user_state["step"] = "processing"
                
                await update.message.reply_text(
                    "✅ تم حفظ صورة الملابس!\n\n"
                    "🔄 جاري معالجة طلبك... هذا قد يستغرق بضع ثوانٍ\n\n"
                    "⏰ يرجى الانتظار..."
                )
                
                # معالجة تجربة الملابس
                result_image, status_message = await process_virtual_tryon(
                    user_state["person_image"],
                    user_state["garment_image"], 
                    user_state["model"],
                    user_state.get("garment_type", "upper_body")
                )
                
                if result_image:
                    # إرسال النتيجة
                    keyboard = [
                        [InlineKeyboardButton("🔄 تجربة أخرى", callback_data="virtual_tryon")],
                        [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    # إرسال الصورة النتيجة
                    await context.bot.send_photo(
                        chat_id=update.effective_chat.id,
                        photo=result_image,
                        caption=f"🎉 {status_message}\n\n"
                               f"تم استخدام: {MODELS[user_state['model']]['name']}\n"
                               f"يمكنك تجربة ملابس أخرى أو العودة للقائمة الرئيسية.",
                        reply_markup=reply_markup
                    )
                else:
                    keyboard = [
                        [InlineKeyboardButton("🔄 حاول مرة أخرى", callback_data="virtual_tryon")],
                        [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await update.message.reply_text(
                        f"❌ {status_message}\n\n"
                        "يمكنك المحاولة مرة أخرى أو اختيار نموذج مختلف.",
                        reply_markup=reply_markup
                    )
                
                # إعادة تعيين حالة المستخدم
                user_states[user_id] = {}
            else:
                await update.message.reply_text(
                    "❌ فشل في تحميل صورة الملابس. حاول مرة أخرى."
                )
    
    except Exception as e:
        logger.error(f"خطأ في معالجة الصورة: {e}")
        await update.message.reply_text(
            "❌ حدث خطأ أثناء معالجة الصورة. يرجى المحاولة مرة أخرى."
        )

async def handle_chat_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالجة رسائل المحادثة العادية - تم إلغاؤها"""
    # تم إزالة وضع المحادثة، عرض القائمة الرئيسية
    await show_main_menu(update, context)

async def tryon_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """أمر مباشر لبدء تجربة الملابس"""
    user_id = update.effective_user.id
    
    # إعادة تعيين حالة المستخدم
    user_states[user_id] = {
        "mode": "virtual_tryon",
        "step": "choose_model",
        "person_image": None,
        "garment_image": None,
        "model": None,
        "garment_type": "upper_body"
    }
    
    keyboard = [
        [InlineKeyboardButton("🎨 " + MODELS["model1"]["name"], callback_data="select_model1")],
        [InlineKeyboardButton("🚀 " + MODELS["model2"]["name"], callback_data="select_model2")],
        [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "👕 *تجربة الملابس الافتراضية*\n\n"
        "اختر النموذج الذي تريد استخدامه:\n\n"
        "🎨 *النموذج الأول (Kolors):*\n"
        "• أسرع في المعالجة\n"
        "• سهل الاستخدام\n"
        "• مناسب للاستخدام السريع\n\n"
        "🚀 *النموذج الثاني (PawanratRung):*\n"
        "• يدعم أنواع ملابس متنوعة\n"
        "• نتائج أكثر تفصيلاً\n"
        "• خيارات متقدمة أكثر",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """تسجيل الأخطاء."""
    logger.error("Exception while handling an update:", exc_info=context.error)

def main() -> None:
    """تشغيل البوت."""
    try:
        # إنشاء التطبيق
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # إضافة معالجات الأوامر
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("tryon", tryon_command))
        
        # إضافة معالج الأزرار
        application.add_handler(CallbackQueryHandler(button_callback))
        
        # إضافة معالج الرسائل (نص وصور)
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        application.add_handler(MessageHandler(filters.PHOTO, handle_message))
        
        # إضافة معالج الأخطاء
        application.add_error_handler(error_handler)
        
        logger.info("🤖 بدء تشغيل بوت تجربة الملابس الافتراضية...")
        print("🤖 بوت تجربة الملابس الافتراضية يعمل الآن! اضغط Ctrl+C للإيقاف")
        print("✨ الميزات المتاحة:")
        print("   👕 تجربة الملابس الافتراضية")
        print("   🎨 نموذجان متطوران (Kolors و PawanratRung)")
        print("   � أنواع ملابس متنوعة")
        
        # تشغيل البوت
        application.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        logger.error(f"خطأ في تشغيل البوت: {e}")
        print(f"❌ خطأ في تشغيل البوت: {e}")

if __name__ == '__main__':
    main()
