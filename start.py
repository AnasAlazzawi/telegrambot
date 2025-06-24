#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكريپت تشغيل محسن لـ Railway
Enhanced startup script for Railway
"""

import os
import sys
import logging

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def check_files():
    """فحص وجود الملفات المطلوبة"""
    required_files = [
        'main.py',
        'config.py',
        'session_manager.py',
        'ai_services.py',
        'basic_handlers.py',
        'virtual_tryon_handlers.py',
        'image_handlers.py',
        'callback_handler.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        logger.error(f"❌ ملفات مفقودة: {missing_files}")
        return False
    
    logger.info("✅ جميع الملفات المطلوبة موجودة")
    return True

def add_current_directory_to_path():
    """إضافة المجلد الحالي للمسار"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    logger.info(f"📁 تم إضافة المجلد للمسار: {current_dir}")

def main():
    """تشغيل البوت مع فحوصات السلامة"""
    try:
        logger.info("🚀 بدء تشغيل Graffiti AI Bot على Railway...")
        
        # فحص الملفات
        if not check_files():
            logger.error("❌ فشل في فحص الملفات")
            sys.exit(1)
        
        # إضافة المجلد الحالي للمسار
        add_current_directory_to_path()
        
        # محاولة الاستيراد
        logger.info("📦 تحميل الوحدات...")
        
        try:
            import main
            logger.info("✅ تم تحميل الوحدات بنجاح")
        except ImportError as e:
            logger.error(f"❌ خطأ في الاستيراد: {e}")
            
            # محاولة أخيرة - استيراد مباشر
            logger.info("🔄 محاولة الاستيراد المباشر...")
            sys.path.append('.')
            import main
        
        # تشغيل البوت
        logger.info("🎨 تشغيل Graffiti AI Bot...")
        main.main()
        
    except Exception as e:
        logger.error(f"❌ خطأ في تشغيل البوت: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
