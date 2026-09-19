import sys
import os

# Добавляем папку src в путь импорта
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from processing import DataProcessor


def main():
    """Главная функция приложения."""
    print("=" * 60)
    print("АНАЛИЗ ДАННЫХ ЯНДЕКС АФИШИ")
    print("=" * 60)

    # Создаем процессор данных
    processor = DataProcessor()

    # Шаг 1: Загрузка данных из БД
    print("\n[Шаг 1] Загрузка данных из базы данных...")
    df = processor.load_data_from_db()
    if df is None:
        print("Не удалось загрузить данные. Завершение работы.")
        return

    # Шаг 2: Загрузка курсов тенге
    print("\n[Шаг 2] Загрузка курсов тенге...")
    tenge_df = processor.load_tenge_data()
    if tenge_df is None:
        print("Не удалось загрузить курсы тенге. Завершение работы.")
        return

    # Шаг 3: Предобработка данных
    print("\n[Шаг 3] Предобработка данных...")
    processor.preprocess_data()

    # Шаг 4: Создание профиля пользователя
    print("\n[Шаг 4] Создание профиля пользователя...")
    processor.create_user_profile()

    # Шаг 5: Фильтрация аномальных пользователей
    print("\n[Шаг 5] Фильтрация аномальных пользователей...")
    processor.filter_user_outliers()

    # Шаг 6: Анализ возвратов по сегментам
    print("\n[Шаг 6] Анализ возвратов по сегментам...")
    processor.analyze_user_segments()

    # Шаг 7: Корреляционный анализ
    print("\n[Шаг 7] Корреляционный анализ...")
    processor.correlation_analysis()

    # Шаг 8: Итоговый отчёт
    print("\n[Шаг 8] Формирование итогового отчёта...")
    processor.print_summary()

    print("\n" + "=" * 60)
    print("АНАЛИЗ ЗАВЕРШЕН УСПЕШНО")
    print("=" * 60)


if __name__ == '__main__':
    main()