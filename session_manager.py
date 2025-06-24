#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إدارة جلسات المستخدمين - User Session Management
"""

import logging

logger = logging.getLogger(__name__)

# قاموس لحفظ حالات المستخدمين
user_sessions = {}


class SessionManager:
    """مدير جلسات المستخدمين"""
    
    @staticmethod
    def create_session(user_id: int, mode: str = None):
        """إنشاء جلسة جديدة للمستخدم"""
        user_sessions[user_id] = {}
        if mode:
            user_sessions[user_id]["mode"] = mode
        logger.info(f"تم إنشاء جلسة جديدة للمستخدم {user_id}")
    
    @staticmethod
    def get_session(user_id: int) -> dict:
        """الحصول على جلسة المستخدم"""
        return user_sessions.get(user_id, {})
    
    @staticmethod
    def update_session(user_id: int, **kwargs):
        """تحديث جلسة المستخدم"""
        if user_id not in user_sessions:
            user_sessions[user_id] = {}
        
        for key, value in kwargs.items():
            user_sessions[user_id][key] = value
        
        logger.debug(f"تم تحديث جلسة المستخدم {user_id}: {kwargs}")
    
    @staticmethod
    def clear_session(user_id: int):
        """مسح جلسة المستخدم"""
        if user_id in user_sessions:
            del user_sessions[user_id]
            logger.info(f"تم مسح جلسة المستخدم {user_id}")
    
    @staticmethod
    def has_session(user_id: int) -> bool:
        """فحص وجود جلسة للمستخدم"""
        return user_id in user_sessions
    
    @staticmethod
    def get_session_value(user_id: int, key: str, default=None):
        """الحصول على قيمة معينة من جلسة المستخدم"""
        session = user_sessions.get(user_id, {})
        return session.get(key, default)
    
    @staticmethod
    def is_in_mode(user_id: int, mode: str) -> bool:
        """فحص إذا كان المستخدم في وضع معين"""
        session = user_sessions.get(user_id, {})
        return session.get("mode") == mode
    
    @staticmethod
    def get_all_sessions() -> dict:
        """الحصول على جميع الجلسات (للإحصائيات)"""
        return user_sessions.copy()
    
    @staticmethod
    def get_active_users_count() -> int:
        """عدد المستخدمين النشطين"""
        return len(user_sessions)


# دالات مساعدة للتوافق مع الكود الحالي
def get_user_session(user_id: int) -> dict:
    """دالة مساعدة للحصول على جلسة المستخدم"""
    return SessionManager.get_session(user_id)


def update_user_session(user_id: int, **kwargs):
    """دالة مساعدة لتحديث جلسة المستخدم"""
    SessionManager.update_session(user_id, **kwargs)


def clear_user_session(user_id: int):
    """دالة مساعدة لمسح جلسة المستخدم"""
    SessionManager.clear_session(user_id)
