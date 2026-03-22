# 🍎 SmartEats AI: Продвинутый SaaS-нутрициолог в Telegram

![Python](https://img.shields.io/badge/python-3.11-blue?style=for-the-badge&logo=python)
![Aiogram](https://img.shields.io/badge/aiogram-3.x-orange?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/FastAPI-Admin-green?style=for-the-badge&logo=fastapi)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--Vision-black?style=for-the-badge&logo=openai)

> **Внимание:** Это репозиторий-портфолио (Code Showcase). Здесь представлены архитектурные фрагменты и примеры реализации логики. Полный исходный код проекта является коммерческой тайной.

---
<img width="657" height="509" alt="image" src="https://github.com/user-attachments/assets/2408bc3e-df39-48e2-92ad-4160c7ba843e" />


## 🌟 О проекте

**SmartEats AI** — это полноценный стартап «под ключ», который заменяет личного диетолога. Бот использует передовые модели компьютерного зрения для анализа питания и формирования полезных привычек на полном автомате.

### 🚀 Ключевые возможности:

*   📸 **AI Vision:** Распознавание сложных блюд по фотографии (читает бренды, определяет состав, оценивает вес).
*   🎙 **Voice-to-Data:** Логирование еды через голосовые сообщения (технология Whisper).
*   🧠 **Персональные планы:** Генерация меню на 3 дня вперед с учетом продуктов в холодильнике пользователя и его аллергий.
*   📊 **Интерактивный дневник:** Статистика КБЖУ с динамическим прогресс-баром и историей приемов пищи.
*   💎 **Биллинг и подписки:** Трехуровневая система тарифов (PRO, ULTRA, Годовой) с полной интеграцией платежных шлюзов.
*   🎁 **Реферальная петля:** Автоматическое начисление 10% бонусов за оплаты приглашенных друзей.

---

## 📸 Визуальный интерфейс

| Анализ по фото 🍳 | План питания 🗓 | Дневник питания 📗 | Личный кабинет 👤 |
| :--- | :--- | :--- | :--- |
| <img width="655" height="999" alt="image" src="https://github.com/user-attachments/assets/171e456f-5a9c-438b-9cec-bc9da7d8900d" />
| <img width="681" height="991" alt="image" src="https://github.com/user-attachments/assets/ea3964e8-0a78-4a23-8fd9-d0269bbc9698" />
 | <img width="475" height="527" alt="image" src="https://github.com/user-attachments/assets/122fd46d-8920-4100-9ac7-d87b94f25531" />
| <img width="676" height="636" alt="image" src="https://github.com/user-attachments/assets/cd06b8af-c875-4266-b4d6-c3362f9f52b0" />


---

## 🖥 Панель управления (Admin Dashboard)

В проект встроена полноценная веб-админка на **FastAPI**, позволяющая владельцу бизнеса управлять проектом из браузера:
*   **Управление пользователями:** Редактирование тарифов, балансов и лимитов.
*   **Аналитика:** Просмотр дневников питания и транзакций в реальном времени.
*   **Массовые рассылки:** Инструмент для маркетинга и возврата аудитории.
*   **Экспорт данных:** Выгрузка базы в Excel (с корректной кодировкой и разделением по столбцам).

---

## 🛠 Технический стек

*   **Core:** `Python 3.11` + `Aiogram 3.x` (Asynchronous bot engine)
*   **Database:** `PostgreSQL` (Persistence) + `SQLAlchemy 2.0` (ORM)
*   **Migrations:** `Alembic`
*   **Web Admin:** `FastAPI` + `SQLAdmin`
*   **Caching & FSM:** `Redis`
*   **AI Integration:** `OpenAI GPT-4o-mini / Vision`, `Whisper` (Speech-to-Text)
*   **Infrastructure:** `Docker` + `Docker Compose`
*   **Deployment:** `Amvera Cloud` (CI/CD ready)

---

## 🏗 Архитектура решения

Проект построен по принципу модульной архитектуры, что позволяет легко масштабировать его или перенести "мозги" (AI-сервисы и БД) на другую платформу (VK, Web, Mobile App):

1.  **Service Layer:** Изолированная логика работы с AI и платежами.
2.  **Database Layer:** Сложная схема связей (Users <-> Profiles <-> FoodLogs <-> Transactions).
3.  **UI Layer:** Асинхронные хендлеры с защитой от наслоения состояний (FSM).

---

## 📬 Контакты

Если вам нужен надежный разработчик для создания AI-стартапа или Telegram-сервиса «под ключ» — пишите:

*   **Telegram:** [@Danil_Berezin](https://t.me/Danil_Berezin)
*   **Email:** berezindanil2004@gmail.com
