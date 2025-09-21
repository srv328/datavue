"""Модуль для сервера Flask."""
from flask import Flask, jsonify
from flask_cors import CORS
from sklearn.datasets import fetch_california_housing
import pandas as pd

app = Flask(__name__)
CORS(app)


@app.route('/api/data', methods=['GET'])
def get_data():
    """Функция для получения данных из датасета California Housing."""
    housing = fetch_california_housing()

    df = pd.DataFrame(housing.data, columns=housing.feature_names)
    df['PRICE'] = housing.target

    data = []
    for i, row in df.iterrows():
        if i >= 1000:
            break
        item = row.to_dict()
        data.append(item)

    return jsonify(data)


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Функция для получения статистики по датасету."""
    housing = fetch_california_housing()

    df = pd.DataFrame(housing.data, columns=housing.feature_names)
    df['PRICE'] = housing.target

    stats = {
        'count': len(df),
        'mean': df.mean().to_dict(),
        'median': df.median().to_dict(),
        'min': df.min().to_dict(),
        'max': df.max().to_dict(),
        'corr': df.corr()['PRICE'].to_dict(),
        'corr_matrix': df.corr().to_dict()
    }

    return jsonify(stats)


@app.route('/api/features', methods=['GET'])
def get_features():
    """Функция для получения названий признаков и их описания."""
    features = [
        {'name': 'MedInc',
         'description': 'Средний доход в группе блоков '
                        '(в десятках тысяч долларов в год)'},
        {'name': 'HouseAge',
         'description': 'Средний возраст домов в группе блоков '
                        '(в годах, целое число)'},
        {'name': 'AveRooms',
         'description': 'Среднее количество комнат на домохозяйство '
                        '(включая спальни)'},
        {'name': 'AveBedrms',
         'description': 'Среднее количество спален на домохозяйство'},
        {'name': 'Population',
         'description': 'Население группы блоков (количество человек)'},
        {'name': 'AveOccup',
         'description': 'Среднее количество членов домохозяйства '
                        '(человек на дом)'},
        {'name': 'Latitude',
         'description': 'Широта группы блоков (географические координаты)'},
        {'name': 'Longitude',
         'description': 'Долгота группы блоков (географические координаты)'},
        {'name': 'PRICE',
         'description': 'Средняя стоимость дома '
                        '(в сотнях тысяч долларов за весь дом)'}
    ]

    return jsonify(features)


if __name__ == '__main__':
    app.run(debug=True)
