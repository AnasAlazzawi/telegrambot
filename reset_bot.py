#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكريبت لحل مشاكل Telegram API Conflicts
Script to resolve Telegram API conflicts
"""

import asyncio
import aiohttp
import logging
from config import TELEGRAM_TOKEN

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def reset_webhook():
    """إزالة أي webhook نشط"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/deleteWebhook"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get('ok'):
                        logger.info("✅ تم حذف Webhook بنجاح")
                    else:
                        logger.warning(f"⚠️ فشل في حذف Webhook: {result}")
                else:
                    logger.error(f"❌ خطأ HTTP: {response.status}")
    except Exception as e:
        logger.error(f"❌ خطأ في حذف Webhook: {e}")

async def get_updates_offset():
    """الحصول على آخر offset للتحديثات"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get('ok') and result.get('result'):
                        updates = result['result']
                        if updates:
                            last_update_id = updates[-1]['update_id']
                            logger.info(f"📊 آخر update_id: {last_update_id}")
                            return last_update_id + 1
                        else:
                            logger.info("📊 لا توجد تحديثات معلقة")
                            return None
                else:
                    logger.error(f"❌ خطأ HTTP: {response.status}")
                    return None
    except Exception as e:
        logger.error(f"❌ خطأ في الحصول على التحديثات: {e}")
        return None

async def clear_pending_updates():
    """مسح التحديثات المعلقة"""
    offset = await get_updates_offset()
    
    if offset:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
        params = {
            'offset': offset,
            'timeout': 1
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        logger.info("✅ تم مسح التحديثات المعلقة")
                    else:
                        logger.error(f"❌ خطأ في مسح التحديثات: {response.status}")
        except Exception as e:
            logger.error(f"❌ خطأ في مسح التحديثات: {e}")

async def main():
    """تنفيذ عمليات إعادة التعيين"""
    print("🔧 بدء إعادة تعيين Telegram API...")
    
    logger.info("1️⃣ حذف Webhook...")
    await reset_webhook()
    
    await asyncio.sleep(2)
    
    logger.info("2️⃣ مسح التحديثات المعلقة...")
    await clear_pending_updates()
    
    await asyncio.sleep(2)
    
    print("✅ تم إعادة تعيين Telegram API بنجاح!")
    print("🚀 يمكنك الآن تشغيل البوت باستخدام: python main.py")

if __name__ == "__main__":
    asyncio.run(main())
