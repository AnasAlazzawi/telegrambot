#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
معالجات تجربة الملابس الافتراضية - Virtual Try-On Handlers
"""

import logging
import sys
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# إضافة المجلد الحالي للمسار
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from config import AI_MODELS, GARMENT_TYPES
    from session_manager import SessionManager
    from ai_services import AIService, VirtualTryOnService
except ImportError:
    import config
    import session_manager
    import ai_services
    AI_MODELS = config.AI_MODELS
    GARMENT_TYPES = config.GARMENT_TYPES
    SessionManager = session_manager.SessionManager
    AIService = ai_services.AIService
    VirtualTryOnService = ai_services.VirtualTryOnService

logger = logging.getLogger(__name__)


class VirtualTryOnHandlers:
    """معالجات تجربة الملابس الافتراضية"""
    
    @staticmethod
    async def start_virtual_tryon(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """بدء تجربة الملابس الافتراضية"""
        user_id = update.callback_query.from_user.id
        
        SessionManager.create_session(user_id, mode="virtual_tryon")
        SessionManager.update_session(user_id, step="select_model")
        
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
        SessionManager.update_session(user_id, model=model_key, step="upload_person")
        
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
        garment_type_id = GARMENT_TYPES[garment_type]["id"]
        SessionManager.update_session(user_id, garment_type=garment_type_id, step="upload_person")
        
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
        
        if not SessionManager.is_in_mode(user_id, "virtual_tryon"):
            await update.message.reply_text("🎨 لبدء تجربة الملابس، استخدم الأمر /start")
            return
        
        session = SessionManager.get_session(user_id)
        photo = update.message.photo[-1]
        
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        if session.get("step") == "upload_person":
            # رفع صورة الشخص
            image = await AIService.download_telegram_image(photo.file_id, context.bot)
            if image:
                SessionManager.update_session(user_id, person_image=image, step="upload_garment")
                
                await update.message.reply_text(
                    "✅ تم حفظ صورة الشخص!\n\n"
                    "👕 الآن أرسل صورة الملابس التي تريد تجربتها\n\n"
                    "💡 <b>نصائح للملابس:</b>\n"                    "• خلفية بيضاء أو بسيطة\n"
                    "• ملابس واضحة ومفصلة\n"
                    "• تجنب الظلال القوية",
                    parse_mode='HTML'
                )
            else:
                await update.message.reply_text("❌ فشل في معالجة الصورة. حاول مرة أخرى.")
        
        elif session.get("step") == "upload_garment":
            # رفع صورة الملابس ومعالجة الطلب
            image = await AIService.download_telegram_image(photo.file_id, context.bot)
            if image:
                SessionManager.update_session(user_id, garment_image=image, step="processing")
                
                processing_msg = await update.message.reply_text(
                    "⚡ <b>Graffiti AI يعمل...</b>\n\n"
                    "🔄 جاري معالجة طلبك باستخدام الذكاء الاصطناعي\n"
                    "⏳ هذا قد يستغرق 30-60 ثانية\n"
                    "🤖 النموذج المستخدم: " + AI_MODELS[session["model"]]["name"],
                    parse_mode='HTML'
                )
                
                # معالجة تجربة الملابس
                logger.info(f"🎨 بدء معالجة تجربة الملابس للمستخدم {user_id}")
                result, status = await VirtualTryOnService.process_virtual_tryon(
                    session["person_image"],
                    session["garment_image"],
                    session["model"],
                    session.get("garment_type", "upper_body")
                )
                logger.info(f"📊 نتيجة المعالجة: {result is not None} - {status}")
                
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
                SessionManager.clear_session(user_id)
            else:
                await update.message.reply_text("❌ فشل في معالجة صورة الملابس. حاول مرة أخرى.")
