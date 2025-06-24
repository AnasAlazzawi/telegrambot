#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
معالجات توليد الصور بالذكاء الاصطناعي - Image Generation Handlers
"""

import logging
import sys
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# إضافة المجلد الحالي للمسار
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from session_manager import SessionManager
    from ai_services import AIService, ImageGenerationService
except ImportError:
    import session_manager
    import ai_services
    SessionManager = session_manager.SessionManager
    AIService = ai_services.AIService
    ImageGenerationService = ai_services.ImageGenerationService

logger = logging.getLogger(__name__)


class ImageHandlers:
    """معالجات توليد الصور"""
    
    @staticmethod
    async def start_image_generation(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """بدء توليد الصور بالذكاء الاصطناعي"""
        user_id = update.callback_query.from_user.id
        
        SessionManager.create_session(user_id, mode="image_generation")
        SessionManager.update_session(user_id, step="waiting_prompt")
        
        keyboard = [
            [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        prompt_text = """
🖼️ <b>Graffiti G1-Image Generator</b>

🎨 <b>مولد الصور الذكي بالذكاء الاصطناعي</b>

✨ <b>الميزات الجديدة:</b>
• صور عالية الجودة (1024x1024)
• معالجة سريعة ومتطورة

📝 <b>كيفية الاستخدام:</b>
أرسل وصفاً تفصيلياً للصورة التي تريد إنشاءها بالعربية أو الإنجليزية

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
            "⏳ هذا قد يستغرق 30-60 ثانية\n",
            parse_mode='HTML'
        )
        
        # ترجمة النص إلى الإنجليزية باستخدام Gemini
        english_prompt = await AIService.translate_to_english(prompt)
        
        # توليد الصورة
        result, status = await ImageGenerationService.generate_image(english_prompt)
        
        await processing_msg.delete()
        
        if result:
            keyboard = [
                [InlineKeyboardButton("🖼️ إنشاء صورة أخرى", callback_data="start_image_gen")],
                [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            try:
                # إعداد caption مع معلومات الترجمة
                if english_prompt != prompt:
                    caption = f"🖼️ <b>Graffiti G1-Image Generator</b>\n\n" \
                             f"✨ {status}\n" \
                             f"📝 الوصف : {prompt}\n" \
                             f"🎨 تم إنشاء هذه الصورة بتقنية الذكاء الاصطناعي المتطورة!"
                else:
                    caption = f"🖼️ <b>Graffiti G1-Image Generator</b>\n\n" \
                             f"✨ {status}\n" \
                             f"📝 الوصف: {prompt}\n" \
                             f"🎨 تم إنشاء هذه الصورة بتقنية الذكاء الاصطناعي المتطورة!"
                
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=result,
                    caption=caption,
                    parse_mode='HTML',
                    reply_markup=reply_markup
                )
            except Exception as send_error:
                logger.error(f"❌ خطأ في إرسال الصورة عبر تليجرام: {send_error}")
                # محاولة إرسال رسالة نصية بدلاً من ذلك
                await update.message.reply_text(
                    f"❌ تم توليد الصورة بنجاح ولكن فشل في إرسالها عبر تليجرام\n\n"
                    f"📝 الوصف: {prompt}\n"
                    f"🔧 خطأ تقني: {str(send_error)}\n\n"
                    "💡 حاول مرة أخرى أو جرب وصفاً مختلفاً",
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
        SessionManager.clear_session(user_id)
