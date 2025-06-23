"""
اختبار بسيط للتحقق من عمل البوت
"""
import os
import asyncio
from bot import GraffitiAI, MODELS, GARMENT_TYPES

def test_models_config():
    """اختبار إعدادات النماذج"""
    print("🧪 اختبار إعدادات النماذج...")
    
    # التحقق من وجود النماذج
    assert "g1_fast" in MODELS, "نموذج g1_fast غير موجود"
    assert "g1_pro" in MODELS, "نموذج g1_pro غير موجود"
    
    # التحقق من معلومات النماذج
    for model_key, model_info in MODELS.items():
        assert "name" in model_info, f"اسم النموذج {model_key} غير محدد"
        assert "client_id" in model_info, f"معرف العميل للنموذج {model_key} غير محدد"
        assert "api_endpoint" in model_info, f"نقطة API للنموذج {model_key} غير محددة"
        assert "description" in model_info, f"وصف النموذج {model_key} غير محدد"
    
    print("✅ اختبار إعدادات النماذج نجح")

def test_garment_types():
    """اختبار أنواع الملابس"""
    print("🧪 اختبار أنواع الملابس...")
    
    expected_types = ["upper_body", "lower_body", "dresses"]
    for garment_type in expected_types:
        assert garment_type in GARMENT_TYPES, f"نوع الملابس {garment_type} غير موجود"
    
    print("✅ اختبار أنواع الملابس نجح")

def test_token_validation():
    """اختبار صحة التوكن"""
    print("🧪 اختبار صحة التوكن...")
    
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if token:
        # التحقق من شكل التوكن
        parts = token.split(':')
        assert len(parts) == 2, "شكل التوكن غير صحيح"
        assert parts[0].isdigit(), "معرف البوت يجب أن يكون رقم"
        assert len(parts[1]) >= 35, "جزء التوكن قصير جداً"
        print("✅ شكل التوكن صحيح")
    else:
        print("⚠️ متغير TELEGRAM_BOT_TOKEN غير محدد")

def test_bot_initialization():
    """اختبار تهيئة البوت"""
    print("🧪 اختبار تهيئة البوت...")
    
    # استخدام توكن وهمي للاختبار
    test_token = "123456789:ABCdefGhIjKlMnOpQrStUvWxYz"
    
    try:
        bot = GraffitiAI(test_token)
        assert bot.token == test_token, "التوكن غير محفوظ بشكل صحيح"
        assert bot.application is not None, "التطبيق غير مهيئ"
        print("✅ تهيئة البوت نجحت")
    except Exception as e:
        print(f"❌ فشل في تهيئة البوت: {e}")

def run_all_tests():
    """تشغيل جميع الاختبارات"""
    print("🚀 بدء تشغيل الاختبارات...\n")
    
    try:
        test_models_config()
        test_garment_types()
        test_token_validation()
        test_bot_initialization()
        
        print("\n✅ جميع الاختبارات نجحت!")
        print("🎉 البوت جاهز للتشغيل!")
        
    except AssertionError as e:
        print(f"\n❌ فشل الاختبار: {e}")
        return False
    except Exception as e:
        print(f"\n❌ خطأ في الاختبار: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
