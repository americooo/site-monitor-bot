Архитектура проекта

Общий обзор

Бот написан на Python, использует Aiogram для интеграции с Telegram,
SQLAlchemy для работы с базой данных и aiohttp для асинхронных
HTTP-запросов.

Компоненты

-   bot.py: Запускает бота и задачи мониторинга/отчетов.
-   sites.py: Команды Telegram (добавление, удаление сайтов,
    статистика).
-   monitoring.py: Асинхронно проверяет сайты и отправляет уведомления.
-   reports.py: Формирует и отправляет еженедельные отчеты.
-   models.py: Определяет модели базы данных (Site, SiteHistory).
-   database.py: Настраивает SQLite и управление сессиями.

Паттерны проектирования

-   Repository Pattern: Работа с базой данных через SQLAlchemy.
-   Observer Pattern: Отправка уведомлений при изменении состояния
    мониторинга.
-   Модульный дизайн: Разделение кода на отдельные файлы для удобства
    поддержки.

Схема базы данных

-   sites:
    -   id: Integer (Primary Key)
    -   url: String (Уникальный)
    -   interval: Integer (По умолчанию: 60)
    -   notifications_enabled: Boolean (По умолчанию: True)
-   checks:
    -   id: Integer (Primary Key)
    -   site_id: Integer (Foreign Key на sites.id)
    -   status_code: Integer
    -   response_time: Integer
    -   checked_at: DateTime
    -   content_hash: String
