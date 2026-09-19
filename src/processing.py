import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns


class DataProcessor:
    """Класс для загрузки, обработки и анализа данных Яндекс Афиши."""

    def __init__(self):
        """Инициализация процессора данных."""
        load_dotenv()

        # Получаем параметры подключения из переменных окружения
        self.db_config = {
            'user': os.getenv('DB_USER', 'praktikum_student'),
            'password': os.getenv('DB_PASSWORD', 'Sdf4$2;d-d30pp'),
            'host': os.getenv('DB_HOST', 'rc1b-wcoijxj3yxfsf3fs.mdb.yandexcloud.net'),
            'port': int(os.getenv('DB_PORT', 6432)),
            'database': os.getenv('DB_NAME', 'data-analyst-afisha')
        }

        # Создаем строку подключения
        self.connection_string = 'postgresql://{}:{}@{}:{}/{}'.format(
            self.db_config['user'],
            self.db_config['password'],
            self.db_config['host'],
            self.db_config['port'],
            self.db_config['database']
        )

        self.df = None
        self.user_profile = None
        self.tenge_df = None

    def load_data_from_db(self):
        """Загрузка данных из базы данных PostgreSQL."""
        print("=" * 60)
        print("ЗАГРУЗКА ДАННЫХ ИЗ БАЗЫ ДАННЫХ")
        print("=" * 60)

        query = """
        SELECT
            p.user_id,
            p.device_type_canonical,
            p.order_id,
            p.created_dt_msk AS order_dt,
            p.created_ts_msk AS order_ts,
            p.currency_code,
            p.revenue,
            p.tickets_count,
            EXTRACT(DAY FROM p.created_dt_msk - LAG(p.created_dt_msk) OVER (
                PARTITION BY p.user_id 
                ORDER BY p.created_dt_msk
            ))::INTEGER AS days_since_prev,
            p.event_id,
            e.event_name_code AS event_name,
            e.event_type_main,
            p.service_name,
            r.region_name,
            c.city_name
        FROM afisha.purchases p
        JOIN afisha.events e ON p.event_id = e.event_id
        JOIN afisha.city c ON e.city_id = c.city_id
        JOIN afisha.regions r ON c.region_id = r.region_id
        WHERE p.device_type_canonical IN ('mobile', 'desktop')
          AND e.event_type_main NOT ILIKE '%фильм%'
        ORDER BY p.user_id
        """

        try:
            import psycopg2
            conn = psycopg2.connect(
                host=self.db_config['host'],
                database=self.db_config['database'],
                port=self.db_config['port'],
                user=self.db_config['user'],
                password=self.db_config['password']
            )
            self.df = pd.read_sql_query(query, conn)
            conn.close()
            print("Данные загружены успешно!")
            print(f"Размер датасета: {self.df.shape[0]} строк, {self.df.shape[1]} столбцов")
            return self.df
        except Exception as e:
            print(f"Ошибка при загрузке данных: {e}")
            return None

    def load_tenge_data(self, filepath='data/final_tickets_tenge_df.csv'):
        """Загрузка файла с курсами тенге."""
        print("\n" + "=" * 60)
        print("ЗАГРУЗКА ДАННЫХ О КУРСЕ ТЕНГЕ")
        print("=" * 60)

        try:
            self.tenge_df = pd.read_csv(filepath)
            self.tenge_df = self.tenge_df.rename(columns={
                'data': 'order_dt',
                'curs': 'exchange_rate'
            })
            self.tenge_df['order_dt'] = pd.to_datetime(self.tenge_df['order_dt']).dt.date

            print(f"✅ Курсы тенге загружены!")
            print(f"Период: {self.tenge_df['order_dt'].min()} - {self.tenge_df['order_dt'].max()}")
            print(f"Средний курс: {self.tenge_df['exchange_rate'].mean():.4f} RUB за 100 KZT")
            return self.tenge_df
        except Exception as e:
            print(f"❌ Ошибка при загрузке курсов тенге: {e}")
            return None

    def preprocess_data(self):
        """Предобработка данных: очистка, конвертация валют, фильтрация выбросов."""
        if self.df is None:
            print("Сначала загрузите данные!")
            return

        print("\n" + "=" * 60)
        print("ПРЕДОБРАБОТКА ДАННЫХ")
        print("=" * 60)

        # 1. Конвертация выручки из тенге в рубли
        print("\n1. Конвертация выручки из тенге в рубли...")

        # Создаем вспомогательный столбец с датой (только дата, без времени)
        self.df['order_date'] = pd.to_datetime(self.df['order_dt']).dt.date

        # Сливаем с курсами тенге
        self.df = self.df.merge(
            self.tenge_df[['order_dt', 'exchange_rate']],
            left_on='order_date',
            right_on='order_dt',
            how='left'
        )

        # Создаем revenue_rub
        self.df['revenue_rub'] = self.df.apply(
            lambda row: row['revenue'] if row['currency_code'] == 'rub'
            else row['revenue'] * row['exchange_rate'] / 100,
            axis=1
        )

        # Удаляем вспомогательные столбцы
        # После merge могут появиться order_dt_x и order_dt_y
        cols_to_drop = ['order_date', 'exchange_rate']

        # Проверяем какие колонки существуют
        if 'order_dt_x' in self.df.columns:
            cols_to_drop.append('order_dt_x')
        if 'order_dt_y' in self.df.columns:
            cols_to_drop.append('order_dt_y')
        if 'order_dt' in self.df.columns:
            cols_to_drop.append('order_dt')

        self.df = self.df.drop(columns=cols_to_drop)

        kzt_count = len(self.df[self.df['currency_code'] == 'kzt'])
        print(f"   Конвертировано заказов в тенге: {kzt_count}")

        # 2. Фильтрация отрицательной выручки
        print("\n2. Фильтрация отрицательной выручки...")
        negative_count = (self.df['revenue_rub'] <= 0).sum()
        self.df = self.df[self.df['revenue_rub'] > 0].copy()
        print(f"   Удалено записей с revenue_rub <= 0: {negative_count}")

        # 3. Фильтрация выбросов по выручке (99-й перцентиль)
        print("\n3. Фильтрация выбросов по выручке (99-й перцентиль)...")
        revenue_99 = self.df['revenue_rub'].quantile(0.99)
        size_before = len(self.df)
        self.df = self.df[self.df['revenue_rub'] <= revenue_99].copy()
        print(f"   99-й перцентиль: {revenue_99:.2f} RUB")
        print(
            f"   Удалено записей: {size_before - len(self.df)} ({(size_before - len(self.df)) / size_before * 100:.2f}%)")

        # 4. Оптимизация типов данных
        print("\n4. Оптимизация типов данных...")
        self.df['revenue_rub'] = self.df['revenue_rub'].astype('float32')
        self.df['revenue'] = self.df['revenue'].astype('float32')
        self.df['tickets_count'] = self.df['tickets_count'].astype('int16')
        self.df['event_id'] = self.df['event_id'].astype('int32')
        self.df['order_id'] = self.df['order_id'].astype('int32')
        print(f"   Размер DataFrame: {self.df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")

        print(f"\nПредобработка завершена!")
        print(f"Итоговый размер: {len(self.df):,} записей")

        return self.df

    def create_user_profile(self):
        """Создание профиля пользователя."""
        if self.df is None:
            print("❌ Сначала загрузите и обработайте данные!")
            return

        print("\n" + "=" * 60)
        print("СОЗДАНИЕ ПРОФИЛЯ ПОЛЬЗОВАТЕЛЯ")
        print("=" * 60)

        # Сортируем по времени
        df_sorted = self.df.sort_values('order_ts')

        # Создаем профиль
        self.user_profile = df_sorted.groupby('user_id').agg(
            first_order_date=('order_ts', 'min'),
            last_order_date=('order_ts', 'max'),
            first_device=('device_type_canonical', 'first'),
            first_region=('region_name', 'first'),
            first_event_genre=('event_type_main', 'first'),
            total_orders=('order_id', 'count'),
            avg_revenue_rub=('revenue_rub', 'mean'),
            avg_days_between=('days_since_prev', 'mean')
        ).reset_index()

        # Добавляем бинарный признак is_two
        self.user_profile['is_two'] = (self.user_profile['total_orders'] >= 2).astype(int)

        print(f"✅ Профиль создан для {len(self.user_profile):,} пользователей")

        return self.user_profile

    def filter_user_outliers(self):
        """Фильтрация аномальных пользователей по количеству заказов."""
        if self.user_profile is None:
            print("❌ Сначала создайте профиль пользователя!")
            return

        print("\n" + "=" * 60)
        print("ФИЛЬТРАЦИЯ АНОМАЛЬНЫХ ПОЛЬЗОВАТЕЛЕЙ")
        print("=" * 60)

        # 99-й перцентиль
        percentile_99 = self.user_profile['total_orders'].quantile(0.99)
        print(f"99-й перцентиль: {percentile_99:.0f} заказов")

        # Фильтруем
        size_before = len(self.user_profile)
        self.user_profile = self.user_profile[
            self.user_profile['total_orders'] <= percentile_99
            ].copy()

        print(f"Размер до фильтрации: {size_before:,}")
        print(f"Размер после фильтрации: {len(self.user_profile):,}")
        print(f"Отфильтровано: {size_before - len(self.user_profile):,} пользователей")

        return self.user_profile

    def analyze_user_segments(self):
        """Анализ возвратов по сегментам пользователей."""
        if self.user_profile is None:
            print(" Сначала создайте профиль пользователя!")
            return

        print("\n" + "=" * 60)
        print("АНАЛИЗ ВОЗВРАТОВ ПО СЕГМЕНТАМ")
        print("=" * 60)

        overall_rate = self.user_profile['is_two'].mean()
        print(f"Общая доля пользователей с 2+ заказами: {overall_rate * 100:.2f}%")

        # По типу устройства
        print("\nПо типу устройства:")
        device_stats = self.user_profile.groupby('first_device').agg(
            total=('user_id', 'count'),
            returning=('is_two', 'sum')
        )
        device_stats['rate'] = device_stats['returning'] / device_stats['total']
        print(device_stats)

        # По жанру
        print("\nПо жанру первого мероприятия:")
        genre_stats = self.user_profile.groupby('first_event_genre').agg(
            total=('user_id', 'count'),
            returning=('is_two', 'sum')
        )
        genre_stats['rate'] = genre_stats['returning'] / genre_stats['total']
        genre_stats = genre_stats.sort_values('total', ascending=False)
        print(genre_stats)

        return {
            'overall_rate': overall_rate,
            'device_stats': device_stats,
            'genre_stats': genre_stats
        }

    def correlation_analysis(self):
        """Корреляционный анализ признаков с количеством заказов."""
        if self.user_profile is None:
            print("❌ Сначала создайте профиль пользователя!")
            return

        print("\n" + "=" * 60)
        print("КОРРЕЛЯЦИОННЫЙ АНАЛИЗ")
        print("=" * 60)

        # Функция для расчета Cramér's V
        def cramers_v(confusion_matrix):
            chi2 = stats.chi2_contingency(confusion_matrix)[0]
            n = confusion_matrix.sum().sum()
            phi2 = chi2 / n
            r, k = confusion_matrix.shape
            phi2corr = max(0, phi2 - ((k - 1) * (r - 1)) / (n - 1))
            rcorr = r - ((r - 1) ** 2) / (n - 1)
            kcorr = k - ((k - 1) ** 2) / (n - 1)
            return np.sqrt(phi2corr / min((kcorr - 1), (rcorr - 1)))

        features = ['first_device', 'first_region', 'first_event_genre',
                    'avg_revenue_rub', 'avg_days_between']

        correlations = {}

        # Категориальные признаки
        for col in ['first_device', 'first_region', 'first_event_genre']:
            contingency_table = pd.crosstab(self.user_profile[col],
                                            self.user_profile['total_orders'])
            corr_value = cramers_v(contingency_table)
            correlations[col] = corr_value
            print(f"{col:25s}: Cramér's V = {corr_value:.4f}")

        # Числовые признаки
        for col in ['avg_revenue_rub', 'avg_days_between']:
            if self.user_profile[col].nunique() > 1:
                corr_value, _ = stats.spearmanr(self.user_profile[col],
                                                self.user_profile['total_orders'])
                correlations[col] = abs(corr_value)
                print(f"{col:25s}: Spearman  = {corr_value:.4f}")

        return correlations

    def print_summary(self):
        """Вывод итогового отчета."""
        print("\n" + "=" * 60)
        print("ИТОГОВЫЙ ОТЧЕТ")
        print("=" * 60)

        if self.df is not None:
            print(f"\n📊 Всего заказов: {len(self.df):,}")
            print(f" Всего пользователей: {len(self.user_profile):,}")
            print(f" Средняя выручка: {self.df['revenue_rub'].mean():.2f} RUB")
            print(f"📈 Доля возвратов: {self.user_profile['is_two'].mean() * 100:.2f}%")

        print("\n✅ Анализ завершен!")