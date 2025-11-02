#!/usr/bin/env python3
"""
Скрипт для сброса пароля администратора.
Использование: python reset_admin_password.py [username] [new_password]
Если параметры не указаны, использует: admin/admin
"""

import sys
import sqlite3
import hashlib
from database import DatabaseManager

def reset_admin_password(username=None, new_password=None):
    """Сброс пароля администратора"""
    
    if not username:
        username = "admin"
    
    if not new_password:
        new_password = "admin"
    
    db = DatabaseManager()
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, role FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        
        if not user:
            print(f"❌ Пользователь '{username}' не найден в базе данных.")
            
            create_new = input(f"\nСоздать нового администратора '{username}' с паролем '{new_password}'? (y/n): ")
            if create_new.lower() == 'y':
                password_hash = db.hash_password(new_password)
                current_time = db.get_current_timestamp()
                cursor.execute('''
                    INSERT INTO users (username, password_hash, role, full_name, created_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (username, password_hash, "admin", "Администратор системы", current_time))
                conn.commit()
                print(f"✅ Администратор '{username}' успешно создан!")
                print(f"📝 Логин: {username}")
                print(f"🔑 Пароль: {new_password}")
            else:
                print("Отмена операции.")
            return
        
        user_id, user_role = user
        
        if user_role != 'admin':
            print(f"⚠️  Внимание: Пользователь '{username}' не является администратором (роль: {user_role})")
            proceed = input("Все равно сбросить пароль? (y/n): ")
            if proceed.lower() != 'y':
                print("Отмена операции.")
                return
        
        password_hash = db.hash_password(new_password)
        cursor.execute('''
            UPDATE users
            SET password_hash = ?
            WHERE id = ?
        ''', (password_hash, user_id))
        
        conn.commit()
        
        print(f"✅ Пароль успешно сброшен для пользователя '{username}'!")
        print(f"📝 Логин: {username}")
        print(f"🔑 Новый пароль: {new_password}")
        print(f"\n💡 Теперь вы можете войти в систему с этими учетными данными.")

def list_admin_users():
    """Показать список всех администраторов"""
    db = DatabaseManager()
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, full_name, created_at FROM users WHERE role = 'admin'")
        admins = cursor.fetchall()
        
        if not admins:
            print("❌ В базе данных нет администраторов.")
            return
        
        print("\n📋 Список администраторов:")
        print("-" * 60)
        for admin in admins:
            admin_id, username, full_name, created_at = admin
            print(f"ID: {admin_id} | Логин: {username} | ФИО: {full_name or 'Не указано'}")

if __name__ == "__main__":
    print("=" * 60)
    print("🔐 Сброс пароля администратора")
    print("=" * 60)
    
    list_admin_users()
    print()
    
    if len(sys.argv) == 1:
        print(f"Использование значений по умолчанию: admin/admin")
        reset_admin_password()
    elif len(sys.argv) == 2:
        username = sys.argv[1]
        print(f"Сброс пароля для пользователя: {username}")
        print(f"Использование пароля по умолчанию: admin")
        reset_admin_password(username=username)
    elif len(sys.argv) == 3:
        username = sys.argv[1]
        new_password = sys.argv[2]
        print(f"Сброс пароля для пользователя: {username}")
        reset_admin_password(username=username, new_password=new_password)
    else:
        print("Использование:")
        print("  python reset_admin_password.py                    # admin/admin")
        print("  python reset_admin_password.py username           # username/admin")
        print("  python reset_admin_password.py username password # username/password")
        sys.exit(1)

