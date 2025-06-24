#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Graffiti AI - Smart Telegram Bot for Virtual Try-On
بوت تليجرام ذكي لتجربة الملابس الافتراضية باستخدام الذكاء الاصطناعي

الملف الرئيسي - Main Bot File
"""

import logging
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# استيراد الوحدات المحلية
from config import TELEGRAM_TOKEN, logger
from basic_handlers import BasicHandlers
from virtual_tryon_handlers import VirtualTryOnHandlers
from image_handlers import ImageHandlers
from callback_handler import CallbackHandler
from session_manager import SessionManager

def setup_handlers(app: Application):
    """إعداد معالجات البوت"""
    
    # معالجات الأوامر الأساسية
    app.add_handler(CommandHandler("start", BasicHandlers.start_command))
    app.add_handler(CommandHandler("help", BasicHandlers.help_command))
    app.add_handler(CommandHandler("about", BasicHandlers.about_command))
    
    # معالج ضغطات الأزرار
    app.add_handler(CallbackQueryHandler(CallbackHandler.handle_callback))
    
    # معالج الصور
    app.add_handler(MessageHandler(filters.PHOTO, VirtualTryOnHandlers.handle_photo))
    
    # معالج النصوص
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, BasicHandlers.handle_text))


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """معالج الأخطاء العامة"""
    logger.error("Exception while handling an update:", exc_info=context.error)
    
    # تجاهل أخطاء الشبكة المؤقتة
    error_message = str(context.error)
    if "409" in error_message or "Conflict" in error_message:
        logger.warning("⚠️ تم اكتشاف تضارب في API - سيتم إعادة المحاولة تلقائياً")
        return
    elif "timeout" in error_message.lower() or "network" in error_message.lower():
        logger.warning("⚠️ مشكلة مؤقتة في الشبكة - سيتم إعادة المحاولة")
        return


def print_startup_messages():
    """طباعة رسائل بدء التشغيل"""
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


def main():
    """تشغيل البوت"""
    try:
        # إنشاء التطبيق مع إعدادات محسنة
        app = Application.builder()\
            .token(TELEGRAM_TOKEN)\
            .concurrent_updates(True)\
            .build()
        
        # إعداد المعالجات
        setup_handlers(app)
        
        # إضافة معالج الأخطاء
        app.add_error_handler(error_handler)
        
        # رسائل بدء التشغيل
        logger.info("🎨 Graffiti AI Bot Started Successfully!")
        print_startup_messages()
        
        # تشغيل البوت مع إعدادات محسنة
        app.run_polling(
            drop_pending_updates=True,
            allowed_updates=["message", "callback_query"],
            timeout=60,
            poll_interval=2.0
        )
        
    except Exception as e:
        logger.error(f"❌ خطأ في تشغيل البوت: {e}")
        print(f"❌ خطأ في تشغيل البوت: {e}")


if __name__ == '__main__':
    main()
