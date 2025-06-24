#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
معالج الأحداث والضغطات - Event and Callback Handler
"""

import logging
import sys
import os
from telegram import Update
from telegram.ext import ContextTypes

# إضافة المجلد الحالي للمسار
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from basic_handlers import BasicHandlers
    from virtual_tryon_handlers import VirtualTryOnHandlers
    from image_handlers import ImageHandlers
except ImportError:
    import basic_handlers
    import virtual_tryon_handlers
    import image_handlers
    BasicHandlers = basic_handlers.BasicHandlers
    VirtualTryOnHandlers = virtual_tryon_handlers.VirtualTryOnHandlers
    ImageHandlers = image_handlers.ImageHandlers

logger = logging.getLogger(__name__)


class CallbackHandler:
    """معالج ضغطات الأزرار والأحداث"""
    
    @staticmethod
    async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة ضغطات الأزرار"""
        try:
            query = update.callback_query
            user_id = query.from_user.id
            data = query.data
            
            await query.answer()
            
            # معالجة الأوامر الأساسية
            if data == "main_menu":
                await BasicHandlers.start_command(update, context)
                
            elif data == "help":
                await BasicHandlers.help_command(update, context)
                
            elif data == "about":
                await BasicHandlers.about_command(update, context)
            
            # معالجة تجربة الملابس
            elif data == "start_tryon":
                await VirtualTryOnHandlers.start_virtual_tryon(update, context)
                
            elif data.startswith("select_model_"):
                model_key = data.replace("select_model_", "")
                await VirtualTryOnHandlers.model_selected(update, context, model_key)
                
            elif data.startswith("garment_"):
                garment_type = data.replace("garment_", "")
                await VirtualTryOnHandlers.garment_type_selected(update, context, garment_type)
            
            # معالجة توليد الصور
            elif data == "start_image_gen":
                await ImageHandlers.start_image_generation(update, context)
        
        except Exception as e:
            logger.error(f"خطأ في معالجة الضغط: {e}")
            try:
                await update.callback_query.answer("❌ حدث خطأ، حاول مرة أخرى")
            except:
                pass
