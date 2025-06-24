#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
خدمات الذكاء الاصطناعي - AI Services
"""

import os
import logging
import tempfile
import asyncio
import aiohttp
import re
from io import BytesIO
from PIL import Image
from gradio_client import Client
import google.generativeai as genai
from config import GEMINI_API_KEY, AI_MODELS

logger = logging.getLogger(__name__)

# حل مشكلة handle_file على Railway ومنصات النشر السحابية
try:
    from gradio_client import handle_file
    logger.info("✅ تم استيراد handle_file بنجاح")
except ImportError:
    def handle_file(file_path):
        logger.warning("⚠️ استخدام fallback لـ handle_file")
        return file_path
    logger.info("⚠️ استخدام fallback لـ handle_file")
except Exception as e:
    def handle_file(file_path):
        logger.error(f"❌ خطأ في handle_file: {e}")
        return file_path
    logger.error(f"❌ خطأ في استيراد handle_file: {e}")

# إعداد Gemini AI
genai.configure(api_key=GEMINI_API_KEY)

# إنشاء نموذج Gemini 2.0 Flash
try:
    gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')
    logger.info("✅ تم الاتصال بنموذج Gemini 2.0 Flash بنجاح")
except Exception as e:
    logger.error(f"❌ خطأ في إعداد Gemini: {e}")
    try:
        gemini_model = genai.GenerativeModel('gemini-pro')
        logger.info("✅ تم الاتصال بنموذج Gemini Pro البديل")
    except Exception as e2:
        logger.error(f"❌ فشل في إعداد جميع نماذج Gemini: {e2}")
        gemini_model = None


class AIService:
    """خدمة الذكاء الاصطناعي الرئيسية"""
    
    @staticmethod
    async def create_ai_client(model_key: str):
        """إنشاء عميل الذكاء الاصطناعي"""
        try:
            model_info = AI_MODELS[model_key]
            client = Client(model_info["client_id"])
            logger.info(f"✅ تم الاتصال بنموذج {model_info['name']}")
            return client
        except Exception as e:
            logger.error(f"❌ خطأ في إنشاء العميل {AI_MODELS.get(model_key, {}).get('name', model_key)}: {e}")
            
            # محاولة الاتصال بالنموذج البديل
            try:
                if model_key == "g1_fast":
                    alt_client = Client("PawanratRung/virtual-try-on")
                    logger.info("✅ تم الاتصال بالنموذج البديل G1 Pro")
                    return alt_client
                elif model_key == "g1_pro":
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
    async def translate_to_english(text: str) -> str:
        """ترجمة النص من العربية إلى الإنجليزية باستخدام Gemini 2.0 Flash"""
        try:
            if not gemini_model:
                logger.warning("⚠️ نموذج Gemini غير متاح، سيتم استخدام النص كما هو")
                return text
            
            # التحقق إذا كان النص يحتوي على أحرف عربية
            arabic_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]')
            if not arabic_pattern.search(text):
                return text
            
            translation_prompt = f"""
You are a professional translator. Translate the following Arabic text to English for AI image generation.
Make the translation natural, descriptive, and suitable for creating images.
Keep it concise but detailed enough for good image generation.

Arabic Text: {text}

Instructions:
- Translate accurately to English
- Make it descriptive and visual
- Use simple, clear language
- Focus on visual elements
- Return ONLY the English translation, nothing else

English Translation:"""
            
            response = await asyncio.to_thread(
                gemini_model.generate_content, 
                translation_prompt
            )
            
            if response and response.text:
                translated_text = response.text.strip()
                logger.info(f"✅ تم ترجمة النص: '{text}' -> '{translated_text}'")
                return translated_text
            else:
                logger.warning("⚠️ لم يتم الحصول على ترجمة، سيتم استخدام النص الأصلي")
                return text
                
        except Exception as e:
            logger.error(f"❌ خطأ في ترجمة النص: {e}")
            return text


class VirtualTryOnService:
    """خدمة تجربة الملابس الافتراضية"""
    
    @staticmethod
    async def process_virtual_tryon(person_img, garment_img, model_key, garment_type="upper_body"):
        """معالجة طلب تجربة الملابس الافتراضية"""
        try:
            # إنشاء عميل AI
            client = await AIService.create_ai_client(model_key)
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
                    logger.info("🔄 تشغيل G1 Fast...")
                    result = client.predict(
                        person_image=handle_file(person_path),
                        clothing_image=handle_file(garment_path),
                        api_name=model_info["api_endpoint"]
                    )
                    logger.info(f"📊 نتيجة G1 Fast: {type(result)} - {result}")
                else:  # g1_pro
                    logger.info("🔄 تشغيل G1 Pro...")
                    result = client.predict(
                        handle_file(person_path),
                        handle_file(garment_path),
                        garment_type,
                        api_name=model_info["api_endpoint"]
                    )
                    logger.info(f"📊 نتيجة G1 Pro: {type(result)} - {result}")
            except Exception as api_error:
                logger.error(f"❌ خطأ في API: {api_error}")                # محاولة مع النموذج البديل
                logger.warning("🔄 محاولة النموذج البديل...")
                try:
                    if model_key == "g1_fast":
                        # جرب النموذج البديل G1 Pro
                        logger.info("🔄 تجربة النموذج البديل G1 Pro...")
                        alt_client = Client("PawanratRung/virtual-try-on")
                        result = alt_client.predict(
                            handle_file(person_path),
                            handle_file(garment_path),
                            "upper_body",
                            api_name="/virtual_tryon"
                        )
                        logger.info(f"📊 نتيجة النموذج البديل: {type(result)} - {result}")
                    else:
                        # جرب النموذج البديل G1 Fast
                        logger.info("🔄 تجربة النموذج البديل G1 Fast...")
                        alt_client = Client("krsatyam7/Virtual_Clothing_Try-On-new")
                        result = alt_client.predict(
                            person_image=handle_file(person_path),
                            clothing_image=handle_file(garment_path),
                            api_name="/swap_clothing"
                        )
                        logger.info(f"📊 نتيجة النموذج البديل: {type(result)} - {result}")
                except Exception as fallback_error:
                    logger.error(f"❌ فشل في النموذج البديل: {fallback_error}")
                    
                    # تنظيف الملفات قبل الإرجاع
                    try:
                        os.unlink(person_path)
                        os.unlink(garment_path)
                    except:
                        pass
                    
                    return None, "❌ جميع النماذج غير متاحة حالياً، حاول لاحقاً"
              # تنظيف الملفات المؤقتة
            try:
                os.unlink(person_path)
                os.unlink(garment_path)
            except:
                pass
            
            # معالجة النتيجة بشكل شامل
            logger.info(f"🔍 فحص النتيجة: {type(result)}")
            
            if result is not None:
                logger.info(f"✅ تم الحصول على نتيجة من النوع: {type(result)}")
                
                # إذا كانت النتيجة string (مسار ملف)
                if isinstance(result, str):
                    logger.info(f"📁 مسار الملف: {result}")
                    if os.path.exists(result):
                        logger.info("✅ الملف موجود، سيتم إرجاعه")
                        return result, "✅ تم إنتاج النتيجة بنجاح!"
                    else:
                        logger.warning(f"⚠️ الملف غير موجود: {result}")
                
                # إذا كانت النتيجة قائمة
                elif isinstance(result, (list, tuple)):
                    logger.info(f"📋 قائمة بـ {len(result)} عنصر")
                    if len(result) > 0:
                        first_item = result[0]
                        logger.info(f"🔍 العنصر الأول: {type(first_item)} - {first_item}")
                        
                        if isinstance(first_item, str) and os.path.exists(first_item):
                            logger.info("✅ العنصر الأول هو مسار ملف صحيح")
                            return first_item, "✅ تم إنتاج النتيجة بنجاح!"
                        else:
                            # جرب العناصر الأخرى
                            for i, item in enumerate(result):
                                logger.info(f"🔍 العنصر {i}: {type(item)} - {item}")
                                if isinstance(item, str) and os.path.exists(item):
                                    logger.info(f"✅ العنصر {i} هو مسار ملف صحيح")
                                    return item, "✅ تم إنتاج النتيجة بنجاح!"
                
                # إذا كانت النتيجة كائن آخر، جرب إرجاعها مباشرة
                else:
                    logger.info("🔄 محاولة إرجاع النتيجة كما هي")
                    return result, "✅ تم إنتاج النتيجة بنجاح!"
                
                logger.warning("⚠️ لم يتم العثور على ملف صالح في النتيجة")
                return None, "❌ النتيجة لا تحتوي على ملف صالح"
            else:
                logger.error("❌ النتيجة فارغة (None)")
                return None, "❌ لم يتم إنتاج نتيجة"
                
        except Exception as e:
            logger.error(f"❌ خطأ في معالجة تجربة الملابس: {e}")
            return None, f"❌ خطأ: {str(e)}"


class ImageGenerationService:
    """خدمة توليد الصور بالذكاء الاصطناعي"""
    
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
                
                # التعامل مع أنواع مختلفة من النتائج
                if isinstance(result, str):
                    # إذا كان النتيجة URL
                    if result.startswith('http'):
                        try:
                            async with aiohttp.ClientSession() as session:
                                async with session.get(result) as response:
                                    if response.status == 200:
                                        image_data = await response.read()
                                        return BytesIO(image_data), "✅ تم توليد الصورة بنجاح!"
                                    else:
                                        return None, "❌ فشل في تحميل الصورة المولدة"
                        except Exception as download_error:
                            logger.error(f"❌ خطأ في تحميل الصورة من URL: {download_error}")
                            return None, "❌ فشل في تحميل الصورة المولدة"
                    
                    # إذا كان النتيجة مسار ملف محلي
                    elif os.path.exists(result):
                        try:
                            with open(result, 'rb') as f:
                                image_data = f.read()
                            return BytesIO(image_data), "✅ تم توليد الصورة بنجاح!"
                        except Exception as file_error:
                            logger.error(f"❌ خطأ في قراءة الملف: {file_error}")
                            return None, "❌ فشل في قراءة الصورة المولدة"
                
                # إذا كان النتيجة قائمة (multiple outputs)
                elif isinstance(result, (list, tuple)) and len(result) > 0:
                    first_result = result[0]
                    if isinstance(first_result, str):
                        if first_result.startswith('http'):
                            try:
                                async with aiohttp.ClientSession() as session:
                                    async with session.get(first_result) as response:
                                        if response.status == 200:
                                            image_data = await response.read()
                                            return BytesIO(image_data), "✅ تم توليد الصورة بنجاح!"
                            except Exception as download_error:
                                logger.error(f"❌ خطأ في تحميل الصورة من URL: {download_error}")
                        elif os.path.exists(first_result):
                            try:
                                with open(first_result, 'rb') as f:
                                    image_data = f.read()
                                return BytesIO(image_data), "✅ تم توليد الصورة بنجاح!"
                            except Exception as file_error:
                                logger.error(f"❌ خطأ في قراءة الملف: {file_error}")
                    else:
                        return first_result, "✅ تم توليد الصورة بنجاح!"
                
                # محاولة أخيرة - إذا كان النتيجة ملف مباشر
                else:
                    return result, "✅ تم توليد الصورة بنجاح!"
                    
                return None, "❌ تعذر معالجة الصورة المولدة"
            else:
                return None, "❌ لم يتم توليد الصورة"
                
        except Exception as e:
            logger.error(f"❌ خطأ في توليد الصورة: {e}")
            return None, f"❌ خطأ في توليد الصورة: {str(e)}"
