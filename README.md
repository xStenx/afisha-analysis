# 📊 Анализ поведения пользователей билетного сервиса

Проект по анализу данных о заказах пользователей: изучение паттернов поведения, выявление ключевых факторов возврата и формирование рекомендаций по удержанию клиентов.

---

## 🛠 Установка

### 1. Клонируйте репозиторий

```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

### 2. Создайте виртуальное окружение

```bash
python -m venv venv
```

### 3. Активируйте окружение

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 4. Установите зависимости

```bash
pip install -r requirements.txt
```

### 5. Настройте переменные окружения

Создайте файл `.env` на основе `.env.example` и укажите параметры подключения к БД:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=events_db
DB_USER=postgres
DB_PASSWORD=your_password
```

---

## 🚀 Запуск

```bash
python main.py
```

---

## 📈 Результаты анализа

### Основные метрики

| Метрика | Значение |
|---|---|
| Всего заказов | 281 879 |
| Всего пользователей | 21 483 |
| Средняя выручка | 528.89 RUB |
| Доля возвратов | 61.28% |

### Ключевые выводы

- 🖥 **Устройство:** Desktop-пользователи возвращаются чаще (63.0% vs 60.1%)
- 🎭 **Жанр:** Выставки (63.5%), театр (62.8%), концерты (61.1%) — успешные точки входа
- 📍 **Регион:** В активных регионах (топ-10) доля возвратов выше на 4.4 п.п.
- 📅 **День недели:** Понедельник, среда и суббота — лучшие дни для первого заказа
- ⏱ **Время между заказами:** Единственный сильный предиктор количества заказов

### Рекомендации

1. 💪 Усилить продвижение концертов и театра
2. 📉 Оптимизировать маркетинговую активность в четверг и воскресенье
3. 🎯 Сфокусироваться на удержании пользователей из менее активных регионов
4. 🎁 Внедрить персонализированные предложения после первого заказа

---

## 📁 Структура проекта

```
.
├── data/                   # Исходные данные
├── notebooks/              # Jupyter-ноутбуки с анализом
├── src/                    # Исходный код проекта
│   ├── analysis.py         # Модуль анализа
│   └── utils.py            # Вспомогательные функции
├── main.py                 # Точка входа
├── requirements.txt        # Зависимости проекта
├── .env.example            # Шаблон переменных окружения
└── README.md               # Описание проекта
```

---

## 👤 Автор

**[Иванченко Александр Александрович]**  
Email: xKapellMeistex@yandex.ru 

---

## 📄 Лицензия

Этот проект распространяется под лицензией MIT.  
Подробности в файле [LICENSE](LICENSE).

```
MIT License

Copyright (c) 2026 [Ваше имя]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```