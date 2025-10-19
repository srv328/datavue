#!/usr/bin/env python3
"""
Скрипт для загрузки Boston Housing Dataset в базу данных
"""

import sqlite3
import csv
import os
from database import DatabaseManager

def download_boston_dataset():
    """Скачиваем Boston Housing Dataset из интернета"""
    import urllib.request
    
    # URL для скачивания Boston Housing Dataset
    url = "https://raw.githubusercontent.com/selva86/datasets/master/BostonHousing.csv"
    
    print("Скачиваем Boston Housing Dataset...")
    urllib.request.urlretrieve(url, "boston_housing.csv")
    print("Датасет скачан в boston_housing.csv")

def load_boston_dataset_to_db():
    """Загружаем Boston Housing Dataset в базу данных"""
    
    # Проверяем, есть ли CSV файл
    if not os.path.exists("boston_housing.csv"):
        print("CSV файл не найден. Скачиваем датасет...")
        download_boston_dataset()
    
    # Инициализируем базу данных
    db = DatabaseManager()
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        # Проверяем, есть ли уже Boston Housing Dataset
        cursor.execute('''
            SELECT id FROM data_types WHERE name = 'Boston Housing Dataset'
        ''')
        existing = cursor.fetchone()
        
        if existing:
            data_type_id = existing[0]
            print("Boston Housing Dataset уже существует. Удаляем старые данные...")
            
            # Удаляем старые данные
            cursor.execute(f'DELETE FROM data_{data_type_id}')
        else:
            # Создаем новый тип данных
            print("Создаем новый тип данных...")
            # Получаем ID администратора
            cursor.execute('SELECT id FROM users WHERE role = "admin" LIMIT 1')
            admin_result = cursor.fetchone()
            if not admin_result:
                raise Exception("Администратор не найден в базе данных")
            admin_id = admin_result[0]
            
            cursor.execute('''
                INSERT INTO data_types (name, description, created_by, created_at)
                VALUES (?, ?, ?, ?)
            ''', (
                'Boston Housing Dataset',
                'Классический датасет для машинного обучения с информацией о недвижимости в Бостоне',
                admin_id,  # admin user
                db.get_current_timestamp()
            ))
            
            data_type_id = cursor.lastrowid
            
            # Создаем поля для датасета
            fields = [
                ('crim', 'decimal', True, 'Уровень преступности на душу населения'),
                ('zn', 'decimal', True, 'Доля жилых участков зонированных под участки более 25,000 кв.фт.'),
                ('indus', 'decimal', True, 'Доля не розничных коммерческих акров на город'),
                ('chas', 'integer', True, 'Ограничение реки Чарльз (1 если участок граничит с рекой, 0 иначе)'),
                ('nox', 'decimal', True, 'Концентрация оксидов азота (частей на 10 миллионов)'),
                ('rm', 'decimal', True, 'Среднее количество комнат на жилище'),
                ('age', 'decimal', True, 'Доля занятых единиц, построенных до 1940 года'),
                ('dis', 'decimal', True, 'Взвешенные расстояния до пяти центров занятости Бостона'),
                ('rad', 'integer', True, 'Индекс доступности к радиальным автомагистралям'),
                ('tax', 'decimal', True, 'Полная ставка налога на недвижимость на $10,000'),
                ('ptratio', 'decimal', True, 'Соотношение ученик-учитель по городам'),
                ('b', 'decimal', True, '1000(Bk - 0.63)^2 где Bk - доля чернокожих по городам'),
                ('lstat', 'decimal', True, 'Процент населения с низким статусом'),
                ('medv', 'decimal', True, 'Средняя стоимость домов, занимаемых владельцами, в $1000')
            ]
            
            for field_name, field_type, is_required, description in fields:
                cursor.execute('''
                    INSERT INTO data_fields (data_type_id, field_name, field_type, is_required, description, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (data_type_id, field_name, field_type, is_required, description, db.get_current_timestamp()))
            
            # Создаем таблицу данных
            db.create_data_table_with_cursor(cursor, data_type_id)
        
        # Читаем CSV файл и загружаем данные
        print("Загружаем данные из CSV...")
        with open('boston_housing.csv', 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            records_loaded = 0
            for row in csv_reader:
                # Преобразуем данные в нужные типы
                record_data = {
                    'crim': float(row['crim']),
                    'zn': float(row['zn']),
                    'indus': float(row['indus']),
                    'chas': int(row['chas']),
                    'nox': float(row['nox']),
                    'rm': float(row['rm']),
                    'age': float(row['age']),
                    'dis': float(row['dis']),
                    'rad': int(row['rad']),
                    'tax': float(row['tax']),
                    'ptratio': float(row['ptratio']),
                    'b': float(row['b']),
                    'lstat': float(row['lstat']),
                    'medv': float(row['medv'])
                }
                
                # Вставляем запись
                cursor.execute(f'''
                    INSERT INTO data_{data_type_id} 
                    (crim, zn, indus, chas, nox, rm, age, dis, rad, tax, ptratio, b, lstat, medv, created_by, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    record_data['crim'], record_data['zn'], record_data['indus'], record_data['chas'],
                    record_data['nox'], record_data['rm'], record_data['age'], record_data['dis'],
                    record_data['rad'], record_data['tax'], record_data['ptratio'], record_data['b'],
                    record_data['lstat'], record_data['medv'], admin_id, db.get_current_timestamp()
                ))
                
                records_loaded += 1
                if records_loaded % 100 == 0:
                    print(f"Загружено {records_loaded} записей...")
        
        conn.commit()
        print(f"Успешно загружено {records_loaded} записей Boston Housing Dataset!")
        print(f"Датасет содержит 14 полей")
        print(f"Данные о недвижимости в Бостоне готовы для анализа!")

if __name__ == "__main__":
    try:
        load_boston_dataset_to_db()
    except Exception as e:
        print(f"Ошибка при загрузке датасета: {e}")
        import traceback
        traceback.print_exc()
