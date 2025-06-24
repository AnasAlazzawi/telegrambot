#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
معالجات أوامر تليجرام الأساسية - Basic Telegram Command Handlers
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import MESSAGES
from session_manager import SessionManager

logger = logging.getLogger(__name__)


class BasicHandlers:
    """معالجات الأوامر الأساسية"""
    
    @staticmethod
    async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر البداية"""
        user = update.effective_user
        user_id = user.id
        
        # إعادة تعيين جلسة المستخدم
        SessionManager.clear_session(user_id)
        
        keyboard = [
            [InlineKeyboardButton("🎨 تجربة الملابس الافتراضية", callback_data="start_tryon")],
            [InlineKeyboardButton("🖼️ مولد الصور الذكي", callback_data="start_image_gen")],
            [InlineKeyboardButton("ℹ️ حول Graffiti AI", callback_data="about")],
            [InlineKeyboardButton("🆘 المساعدة", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = MESSAGES["welcome"].format(user=user.mention_html())
        
        try:
            if update.callback_query:
                await update.callback_query.edit_message_text(
                    welcome_text, parse_mode='HTML', reply_markup=reply_markup
                )
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
        keyboard = [
            [InlineKeyboardButton("🎨 تجربة الملابس", callback_data="start_tryon")],
            [InlineKeyboardButton("🖼️ مولد الصور", callback_data="start_image_gen")],
            [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                MESSAGES["help"], parse_mode='HTML', reply_markup=reply_markup
            )
        else:
            await update.message.reply_html(MESSAGES["help"], reply_markup=reply_markup)
    
    @staticmethod
    async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معلومات حول البوت"""
        keyboard = [
            [InlineKeyboardButton("🎨 تجربة الملابس", callback_data="start_tryon")],
            [InlineKeyboardButton("🖼️ مولد الصور", callback_data="start_image_gen")],
            [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                MESSAGES["about"], parse_mode='HTML', reply_markup=reply_markup
            )
        else:
            await update.message.reply_html(MESSAGES["about"], reply_markup=reply_markup)
    
    @staticmethod
    async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة الرسائل النصية"""
        user_id = update.effective_user.id
        
        # التحقق من وضع توليد الصور
        if SessionManager.is_in_mode(user_id, "image_generation"):
            if SessionManager.get_session_value(user_id, "step") == "waiting_prompt":
                # استيراد معالج توليد الصور
                from image_handlers import ImageHandlers
                prompt = update.message.text
                await ImageHandlers.handle_image_generation_text(update, context, prompt)
                return
        
        # الرد الافتراضي
        await update.message.reply_text(
            "🎨 مرحباً! أنا Graffiti AI\n\n"
            "استخدم /start لبدء تجربة الملابس الافتراضية أو توليد الصور ✨"
        )
