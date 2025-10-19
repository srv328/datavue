"""Модуль для работы с базой данных SQLite."""

import sqlite3
import hashlib
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional


class DatabaseManager:
    def __init__(self, db_path: str = "datavue.db"):
        """Инициализация менеджера базы данных."""
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self, timeout=30.0):
        """Получение соединения с базой данных с оптимальными настройками."""
        conn = sqlite3.connect(
            self.db_path, 
            timeout=timeout,
            check_same_thread=False
        )
        # Настройки для избежания блокировок
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA temp_store=MEMORY")
        conn.execute("PRAGMA busy_timeout=30000")  # 30 секунд таймаут
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA cache_size=10000")
        return conn
    
    def get_current_timestamp(self) -> str:
        """Получение текущего времени в формате для SQLite с правильным часовым поясом."""
        # Получаем текущее время в UTC
        now_utc = datetime.now(timezone.utc)
        # Конвертируем в локальное время (часовой пояс системы)
        now_local = now_utc.astimezone()
        # Возвращаем в формате, который понимает SQLite
        return now_local.strftime('%Y-%m-%d %H:%M:%S')
    
    def format_datetime(self, dt_string: str) -> str:
        """Форматирование даты и времени для отображения пользователю."""
        if not dt_string:
            return ""
        
        try:
            # Парсим время из базы данных
            dt = datetime.strptime(dt_string, '%Y-%m-%d %H:%M:%S')
            # Возвращаем в ISO формате для корректного парсинга в JavaScript
            return dt.isoformat()
        except (ValueError, TypeError):
            return dt_string

    def init_database(self):
        """Инициализация базы данных и создание таблиц."""
        # Принудительно закрываем все соединения
        try:
            sqlite3.connect(self.db_path).close()
        except:
            pass
            
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Таблица пользователей
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    full_name TEXT,
                    role TEXT NOT NULL CHECK (role IN ('admin', 'user')),
                    created_at TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            ''')
            
            # Проверяем, есть ли поле full_name в таблице users
            cursor.execute("PRAGMA table_info(users)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'full_name' not in columns:
                # Добавляем поле full_name если его нет
                cursor.execute('ALTER TABLE users ADD COLUMN full_name TEXT')
                print("Добавлено поле full_name в таблицу users")
                
                # Обновляем существующего администратора
                cursor.execute('''
                    UPDATE users 
                    SET full_name = 'Администратор системы' 
                    WHERE username = 'admin' AND full_name IS NULL
                ''')
                print("Обновлен ФИО для администратора")
            
            # Таблица справочников (типы данных)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS data_types (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    created_by INTEGER,
                    created_at TIMESTAMP,
                    FOREIGN KEY (created_by) REFERENCES users (id)
                )
            ''')
            
            # Сначала проверяем, существует ли таблица data_fields
            cursor.execute('''
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='data_fields'
            ''')
            table_exists = cursor.fetchone()
            
            if table_exists:
                # Если таблица существует, пересоздаем её с новым constraint
                # Сначала создаем новую таблицу с новым constraint
                cursor.execute('''
                    CREATE TABLE data_fields_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        data_type_id INTEGER NOT NULL,
                        field_name TEXT NOT NULL,
                        field_type TEXT NOT NULL CHECK (field_type IN ('text', 'integer', 'decimal', 'date', 'boolean')),
                        is_required BOOLEAN DEFAULT 0,
                        description TEXT,
                        validation_rules TEXT,
                        created_at TIMESTAMP,
                        FOREIGN KEY (data_type_id) REFERENCES data_types (id),
                        UNIQUE(data_type_id, field_name)
                    )
                ''')
                
                # Копируем данные, обновляя 'number' на 'decimal'
                cursor.execute('''
                    INSERT INTO data_fields_new 
                    SELECT 
                        id,
                        data_type_id,
                        field_name,
                        CASE 
                            WHEN field_type = 'number' THEN 'decimal'
                            ELSE field_type
                        END as field_type,
                        is_required,
                        description,
                        validation_rules,
                        created_at
                    FROM data_fields
                ''')
                
                cursor.execute('DROP TABLE data_fields')
                cursor.execute('ALTER TABLE data_fields_new RENAME TO data_fields')
            else:
                # Если таблица не существует, создаем с новым constraint
                cursor.execute('''
                    CREATE TABLE data_fields (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        data_type_id INTEGER NOT NULL,
                        field_name TEXT NOT NULL,
                        field_type TEXT NOT NULL CHECK (field_type IN ('text', 'integer', 'decimal', 'date', 'boolean')),
                        is_required BOOLEAN DEFAULT 0,
                        description TEXT,
                        validation_rules TEXT,
                        created_at TIMESTAMP,
                        FOREIGN KEY (data_type_id) REFERENCES data_types (id),
                        UNIQUE(data_type_id, field_name)
                    )
                ''')
            
            # Таблица разрешений пользователей на справочники
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_permissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    data_type_id INTEGER NOT NULL,
                    permission_type TEXT NOT NULL CHECK (
                        permission_type IN ('read', 'write', 'admin')
                    ),
                    granted_by INTEGER,
                    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (data_type_id) REFERENCES data_types (id),
                    FOREIGN KEY (granted_by) REFERENCES users (id),
                    UNIQUE(user_id, data_type_id)
                )
            ''')
            
            # Таблица данных (динамическая, создается для каждого справочника)
            # Структура: data_{data_type_id} с полями из data_fields
            
            # Создаем администратора по умолчанию
            self.create_default_admin()
            
            # Создаем недостающие таблицы данных
            self.create_missing_data_tables()
            
            conn.commit()
            
            # Инициализируем демонстрационные данные
            self.init_demo_data()
    
    def create_default_admin(self):
        """Создание администратора по умолчанию."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Проверяем, есть ли уже администратор
            cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
            if cursor.fetchone()[0] == 0:
                # Создаем хеш пароля для admin/admin
                password_hash = hashlib.sha256("admin".encode()).hexdigest()
                current_time = self.get_current_timestamp()
                cursor.execute('''
                    INSERT INTO users (username, password_hash, role, full_name, created_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', ("admin", password_hash, "admin", "Администратор системы", current_time))
                print("Создан администратор по умолчанию: admin/admin")
    
    def hash_password(self, password: str) -> str:
        """Хеширование пароля"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Аутентификация пользователя"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            password_hash = self.hash_password(password)
            
            cursor.execute('''
                SELECT id, username, role, is_active
                FROM users
                WHERE username = ? AND password_hash = ? AND is_active = 1
            ''', (username, password_hash))
            
            result = cursor.fetchone()
            if result:
                return {
                    'id': result[0],
                    'username': result[1],
                    'role': result[2],
                    'is_active': result[3]
                }
            return None
    
    def create_data_type(self, name: str, description: str, created_by: int) -> int:
        """Создание нового типа данных (справочника)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            current_time = self.get_current_timestamp()
            cursor.execute('''
                INSERT INTO data_types (name, description, created_by, created_at)
                VALUES (?, ?, ?, ?)
            ''', (name, description, created_by, current_time))
            
            data_type_id = cursor.lastrowid
            
            # Создаем базовую таблицу для данных этого типа (без полей)
            self.create_basic_data_table_with_cursor(cursor, data_type_id)
            
            conn.commit()
            return data_type_id
    
    def create_missing_data_tables(self):
        """Создание недостающих таблиц данных для существующих типов данных"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Получаем все существующие типы данных
            cursor.execute('SELECT id FROM data_types')
            data_type_ids = [row[0] for row in cursor.fetchall()]
            
            for data_type_id in data_type_ids:
                table_name = f"data_{data_type_id}"
                
                # Проверяем, существует ли таблица
                cursor.execute(f'''
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name=?
                ''', (table_name,))
                
                if not cursor.fetchone():
                    # Создаем недостающую таблицу
                    self.create_data_table_with_cursor(cursor, data_type_id)
                    print(f"Создана таблица {table_name}")
            
            conn.commit()
    
    def create_basic_data_table(self, data_type_id: int):
        """Создание базовой таблицы для хранения данных конкретного типа (без полей)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            self.create_basic_data_table_with_cursor(cursor, data_type_id)
    
    def create_basic_data_table_with_cursor(self, cursor, data_type_id: int):
        """Создание базовой таблицы для хранения данных конкретного типа (без полей) с использованием существующего курсора"""
        table_name = f"data_{data_type_id}"
        
        create_sql = f'''
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_by INTEGER,
                created_at TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users (id)
            )
        '''
        
        cursor.execute(create_sql)
    
    def create_data_table(self, data_type_id: int):
        """Создание таблицы для хранения данных конкретного типа"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            self.create_data_table_with_cursor(cursor, data_type_id)
    
    def create_data_table_with_cursor(self, cursor, data_type_id: int):
        """Создание таблицы для хранения данных конкретного типа с использованием существующего курсора"""
        # Получаем поля для этого типа данных
        cursor.execute('''
            SELECT field_name, field_type
            FROM data_fields
            WHERE data_type_id = ?
            ORDER BY id
        ''', (data_type_id,))
        
        fields = cursor.fetchall()
        table_name = f"data_{data_type_id}"
        
        if fields:
            # Создаем таблицу с полями
            field_definitions = []
            for field_name, field_type in fields:
                sql_type = self.get_sql_type(field_type)
                field_definitions.append(f"{field_name} {sql_type}")
            
            create_sql = f'''
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_by INTEGER,
                    created_at TIMESTAMP,
                    {', '.join(field_definitions)},
                    FOREIGN KEY (created_by) REFERENCES users (id)
                )
            '''
        else:
            # Создаем базовую таблицу без полей
            create_sql = f'''
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_by INTEGER,
                    created_at TIMESTAMP,
                    FOREIGN KEY (created_by) REFERENCES users (id)
                )
            '''
        
        cursor.execute(create_sql)
    
    def get_sql_type(self, field_type: str) -> str:
        """Преобразование типа поля в SQL тип"""
        type_mapping = {
            'text': 'TEXT',
            'integer': 'INTEGER',
            'decimal': 'REAL',
            'date': 'TIMESTAMP',
            'boolean': 'BOOLEAN'
        }
        return type_mapping.get(field_type, 'TEXT')
    
    def add_field_to_data_type(self, data_type_id: int, field_name: str, 
                              field_type: str, is_required: bool = False, 
                              description: str = "", validation_rules: str = ""):
        """Добавление поля к типу данных"""
        import time
        
        # Пытаемся подключиться с таймаутом
        max_retries = 5
        for attempt in range(max_retries):
            try:
                with self.get_connection(timeout=30.0) as conn:
                    cursor = conn.cursor()
                    
                    # Проверяем, существует ли уже поле с таким именем
                    cursor.execute('''
                        SELECT id FROM data_fields 
                        WHERE data_type_id = ? AND field_name = ?
                    ''', (data_type_id, field_name))
                    
                    if cursor.fetchone():
                        raise ValueError(f"Поле '{field_name}' уже существует для данного типа данных")
                    
                    current_time = self.get_current_timestamp()
                    cursor.execute('''
                        INSERT INTO data_fields (data_type_id, field_name, field_type, 
                                               is_required, description, validation_rules, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (data_type_id, field_name, field_type, is_required, description, validation_rules, current_time))
                    
                    # Пересоздаем таблицу данных с новым полем
                    self.recreate_data_table_with_cursor(cursor, data_type_id)
                    conn.commit()
                    break  # Успешно выполнили операцию
                    
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e) and attempt < max_retries - 1:
                    print(f"База данных заблокирована, попытка {attempt + 1}/{max_retries}")
                    time.sleep(0.5)  # Ждем 500мс перед следующей попыткой
                    continue
                else:
                    raise e
    
    def delete_field_from_data_type(self, data_type_id: int, field_id: int):
        """Удаление поля из типа данных"""
        import time
        
        # Пытаемся подключиться с таймаутом
        max_retries = 5
        for attempt in range(max_retries):
            try:
                with self.get_connection(timeout=30.0) as conn:
                    cursor = conn.cursor()
                    
                    # Проверяем, существует ли поле
                    cursor.execute('''
                        SELECT field_name FROM data_fields 
                        WHERE id = ? AND data_type_id = ?
                    ''', (field_id, data_type_id))
                    
                    field = cursor.fetchone()
                    if not field:
                        raise ValueError("Поле не найдено")
                    
                    # Удаляем поле
                    cursor.execute('''
                        DELETE FROM data_fields 
                        WHERE id = ? AND data_type_id = ?
                    ''', (field_id, data_type_id))
                    
                    # Пересоздаем таблицу данных без удаленного поля
                    self.recreate_data_table_with_cursor(cursor, data_type_id)
                    conn.commit()
                    break  # Успешно выполнили операцию
                    
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e) and attempt < max_retries - 1:
                    print(f"База данных заблокирована, попытка {attempt + 1}/{max_retries}")
                    time.sleep(0.5)  # Ждем 500мс перед следующей попыткой
                    continue
                else:
                    raise e
    
    def delete_data_type(self, data_type_id: int):
        """Удаление типа данных и всех связанных данных"""
        import time
        
        # Пытаемся подключиться с таймаутом
        max_retries = 5
        for attempt in range(max_retries):
            try:
                with self.get_connection(timeout=30.0) as conn:
                    cursor = conn.cursor()
                    
                    # Проверяем, существует ли тип данных
                    cursor.execute('''
                        SELECT name FROM data_types WHERE id = ?
                    ''', (data_type_id,))
                    
                    if not cursor.fetchone():
                        raise ValueError("Тип данных не найден")
                    
                    # Удаляем все записи данных
                    table_name = f"data_{data_type_id}"
                    cursor.execute(f'DROP TABLE IF EXISTS {table_name}')
                    
                    # Удаляем все поля типа данных
                    cursor.execute('''
                        DELETE FROM data_fields WHERE data_type_id = ?
                    ''', (data_type_id,))
                    
                    # Удаляем все права доступа к типу данных
                    cursor.execute('''
                        DELETE FROM user_permissions WHERE data_type_id = ?
                    ''', (data_type_id,))
                    
                    # Удаляем сам тип данных
                    cursor.execute('''
                        DELETE FROM data_types WHERE id = ?
                    ''', (data_type_id,))
                    
                    conn.commit()
                    break  # Успешно выполнили операцию
                    
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e) and attempt < max_retries - 1:
                    print(f"База данных заблокирована, попытка {attempt + 1}/{max_retries}")
                    time.sleep(0.5)  # Ждем 500мс перед следующей попыткой
                    continue
                else:
                    raise e
    
    def recreate_data_table(self, data_type_id: int):
        """Пересоздание таблицы данных с учетом новых полей"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            self.recreate_data_table_with_cursor(cursor, data_type_id)
    
    def recreate_data_table_with_cursor(self, cursor, data_type_id: int):
        """Пересоздание таблицы данных с учетом новых полей с использованием существующего курсора"""
        table_name = f"data_{data_type_id}"
        
        # Получаем текущие поля
        cursor.execute('''
            SELECT field_name, field_type
            FROM data_fields
            WHERE data_type_id = ?
            ORDER BY id
        ''', (data_type_id,))
        
        fields = cursor.fetchall()
        
        # Удаляем старую таблицу
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        
        if fields:
            # Создаем новую таблицу с полями
            field_definitions = []
            for field_name, field_type in fields:
                sql_type = self.get_sql_type(field_type)
                field_definitions.append(f"{field_name} {sql_type}")
            
            create_sql = f'''
                CREATE TABLE {table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_by INTEGER,
                    created_at TIMESTAMP,
                    {', '.join(field_definitions)},
                    FOREIGN KEY (created_by) REFERENCES users (id)
                )
            '''
        else:
            # Создаем базовую таблицу без полей
            create_sql = f'''
                CREATE TABLE {table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_by INTEGER,
                    created_at TIMESTAMP,
                    FOREIGN KEY (created_by) REFERENCES users (id)
                )
            '''
        
        cursor.execute(create_sql)
    
    def get_user_permissions(self, user_id: int) -> List[Dict[str, Any]]:
        """Получение прав доступа пользователя"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT data_type_id, permission_type, granted_at
                FROM user_permissions
                WHERE user_id = ?
                ORDER BY granted_at DESC
            ''', (user_id,))
            
            results = cursor.fetchall()
            return [{
                'data_type_id': row[0],
                'permission_type': row[1],
                'granted_at': row[2]
            } for row in results]
    
    def grant_permission(self, user_id: int, data_type_id: int, permission_type: str, granted_by: int):
        """Выдача разрешения пользователю на работу с типом данных"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            current_time = self.get_current_timestamp()
            cursor.execute('''
                INSERT OR REPLACE INTO user_permissions 
                (user_id, data_type_id, permission_type, granted_by, granted_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, data_type_id, permission_type, granted_by, current_time))
            conn.commit()
    
    def revoke_permission(self, user_id: int, data_type_id: int):
        """Отзыв разрешения пользователя"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM user_permissions
                WHERE user_id = ? AND data_type_id = ?
            ''', (user_id, data_type_id))
            conn.commit()
    
    def get_data_types(self, user_id: int) -> List[Dict[str, Any]]:
        """Получение доступных типов данных для пользователя"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Все пользователи видят все типы данных
            cursor.execute('''
                SELECT dt.id, dt.name, dt.description, dt.created_at,
                       u.username as created_by_username
                FROM data_types dt
                JOIN users u ON dt.created_by = u.id
                ORDER BY dt.created_at DESC
            ''')
            
            results = cursor.fetchall()
            
            # Получаем права пользователя на редактирование
            cursor.execute('''
                SELECT data_type_id FROM user_permissions
                WHERE user_id = ? AND permission_type = 'write'
            ''', (user_id,))
            
            write_permissions = {row[0] for row in cursor.fetchall()}
            
            return [{
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'created_at': self.format_datetime(row[3]),
                'created_by_username': row[4],
                'can_edit': row[0] in write_permissions or self.is_admin(user_id)
            } for row in results]
    
    def is_admin(self, user_id: int) -> bool:
        """Проверка, является ли пользователь администратором"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT role FROM users WHERE id = ?", (user_id,))
            result = cursor.fetchone()
            return result and result[0] == 'admin'
    
    def has_permission(self, user_id: int, data_type_id: int, permission_type: str) -> bool:
        """Проверка прав доступа пользователя к типу данных"""
        # Администраторы имеют все права
        if self.is_admin(user_id):
            return True
        
        # Все пользователи могут просматривать данные
        if permission_type == 'read':
            return True
        
        # Для редактирования проверяем права
        if permission_type == 'write':
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT permission_type FROM user_permissions
                    WHERE user_id = ? AND data_type_id = ?
                ''', (user_id, data_type_id))
                
                result = cursor.fetchone()
                return result is not None and result[0] == 'write'
        
        return False
    
    def get_data_type(self, data_type_id: int) -> Dict[str, Any]:
        """Получение информации о типе данных"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, description, created_by, created_at
                FROM data_types
                WHERE id = ?
            ''', (data_type_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return {
                'id': row[0],
                'name': row[1],
                'description': row[2] or '',
                'created_by': row[3],
                'created_at': self.format_datetime(row[4])
            }
    
    def get_data_fields(self, data_type_id: int) -> List[Dict[str, Any]]:
        """Получение полей для типа данных"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, field_name, field_type, is_required, description, validation_rules
                FROM data_fields
                WHERE data_type_id = ?
                ORDER BY id
            ''', (data_type_id,))
            
            results = cursor.fetchall()
            return [{
                'id': row[0],
                'field_name': row[1],
                'field_type': row[2],
                'is_required': row[3],
                'description': row[4],
                'validation_rules': row[5]
            } for row in results]
    
    def has_data_fields(self, data_type_id: int) -> bool:
        """Проверка наличия полей у типа данных"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) FROM data_fields
                WHERE data_type_id = ?
            ''', (data_type_id,))
            
            result = cursor.fetchone()
            return result[0] > 0
    
    def insert_data_record(self, data_type_id: int, data: Dict[str, Any], created_by: int) -> int:
        """Вставка записи данных"""
        # Проверяем, есть ли поля у типа данных
        if not self.has_data_fields(data_type_id):
            raise ValueError("Нельзя добавлять записи в тип данных без полей. Сначала добавьте поля к типу данных.")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            table_name = f"data_{data_type_id}"
            
            # Подготавливаем данные для вставки
            fields = list(data.keys())
            values = list(data.values())
            
            # Добавляем обязательные поля если их нет
            if 'created_by' not in fields:
                fields.append('created_by')
                values.append(created_by)
            if 'created_at' not in fields:
                fields.append('created_at')
                values.append(self.get_current_timestamp())
            
            # Создаем placeholders для всех полей
            placeholders = ', '.join(['?' for _ in fields])
            fields_str = ', '.join(fields)
            
            cursor.execute(f'''
                INSERT INTO {table_name} ({fields_str})
                VALUES ({placeholders})
            ''', values)
            
            record_id = cursor.lastrowid
            conn.commit()
            return record_id
    
    def get_data_records(self, data_type_id: int, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Получение записей данных с информацией о пользователе"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            table_name = f"data_{data_type_id}"
            
            # Проверяем, существует ли таблица
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            table_exists = cursor.fetchone()
            
            if not table_exists:
                return []
            
            # Получаем записи с информацией о пользователе
            if limit > 0:
                cursor.execute(f'''
                    SELECT d.*, u.username as created_by_username, u.full_name as created_by_full_name
                    FROM {table_name} d
                    LEFT JOIN users u ON d.created_by = u.id
                    ORDER BY d.created_at DESC
                    LIMIT ? OFFSET ?
                ''', (limit, offset))
            else:
                # Если limit=0, получаем все записи
                cursor.execute(f'''
                    SELECT d.*, u.username as created_by_username, u.full_name as created_by_full_name
                    FROM {table_name} d
                    LEFT JOIN users u ON d.created_by = u.id
                    ORDER BY d.created_at DESC
                ''')
            
            # Получаем названия колонок
            column_names = [description[0] for description in cursor.description]
            
            results = cursor.fetchall()
            records = []
            for row in results:
                record = dict(zip(column_names, row))
                # Форматируем время создания если оно есть
                if 'created_at' in record:
                    record['created_at'] = self.format_datetime(record['created_at'])
                records.append(record)
            return records
    
    def get_data_statistics(self, data_type_id: int) -> Dict[str, Any]:
        """Получение статистики по данным."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            table_name = f"data_{data_type_id}"
            
            # Получаем поля типа integer и decimal для статистики
            cursor.execute('''
                SELECT field_name FROM data_fields
                WHERE data_type_id = ? AND field_type IN ('integer', 'decimal')
            ''', (data_type_id,))
            
            number_fields = [row[0] for row in cursor.fetchall()]
            
            stats = {}
            
            for field in number_fields:
                cursor.execute(f'''
                    SELECT 
                        COUNT(*) as count,
                        AVG({field}) as mean,
                        MIN({field}) as min,
                        MAX({field}) as max
                    FROM {table_name}
                    WHERE {field} IS NOT NULL
                ''')
                
                result = cursor.fetchone()
                if result and result[0] > 0:
                    stats[field] = {
                        'count': result[0],
                        'mean': result[1],
                        'min': result[2],
                        'max': result[3]
                    }
            
            return stats
    
    def generate_users(self, count: int, role: str = 'user') -> List[Dict[str, Any]]:
        """Автоматическая генерация пользователей."""
        import random
        import string
        
        generated_users = []
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            for i in range(count):
                # Генерируем случайное имя пользователя из английских букв, цифр и подчеркиваний
                username_length = random.randint(6, 12)
                username_chars = string.ascii_lowercase + string.digits + '_'
                username = ''.join(random.choices(username_chars, k=username_length))
                
                # Убеждаемся, что имя начинается с буквы
                if username[0].isdigit() or username[0] == '_':
                    username = random.choice(string.ascii_lowercase) + username[1:]
                
                # Проверяем уникальность
                counter = 1
                original_username = username
                while True:
                    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
                    if not cursor.fetchone():
                        break
                    username = f"{original_username}{counter}"
                    counter += 1
                
                # Генерируем пароль
                password = ''.join(random.choices(
                    string.ascii_letters + string.digits, k=8
                ))
                
                # ФИО не генерируем - оставляем пустым для ручного заполнения
                full_name = None
                
                # Создаем пользователя с правильным временем
                password_hash = self.hash_password(password)
                current_time = self.get_current_timestamp()
                cursor.execute('''
                    INSERT INTO users (username, password_hash, role, full_name, created_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (username, password_hash, role, full_name, current_time))
                
                user_id = cursor.lastrowid
                generated_users.append({
                    'id': user_id,
                    'username': username,
                    'password': password,
                    'role': role,
                    'full_name': full_name
                })
            
            conn.commit()
        
        return generated_users
    
    def init_demo_data(self):
        """Проверка наличия демонстрационных данных"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Проверяем, есть ли уже демо-данные
            cursor.execute('''
                SELECT COUNT(*) FROM data_types WHERE name = 'Boston Housing Dataset'
            ''')
            if cursor.fetchone()[0] > 0:
                print("Boston Housing Dataset уже загружен")
                return  # Демо-данные уже существуют
            
            print("Boston Housing Dataset не найден. Запустите load_boston_dataset.py для загрузки полного датасета.")
