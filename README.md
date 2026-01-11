# Telegram кино-бот + WebApp монорепо

Полный MVP стек:
- API: FastAPI + SQLAlchemy + Alembic
- Bot: aiogram v3
- WebApp: React + Vite + TypeScript
- DB: PostgreSQL
- Redis: кеш/лимиты/локи
- Nginx: reverse proxy и SPA fallback

## Быстрый старт

```bash
cp .env.example .env
```

Заполните минимум:
- `BOT_TOKEN`
- `PUBLIC_BASE_URL` (например ngrok URL)
- `STORAGE_CHAT_ID`
- `API_SECRET_KEY`
- `ADMIN_PASS`
- `DATABASE_URL`

Запуск:

```bash
docker compose up --build
```

## URL'ы

- WebApp: `${PUBLIC_BASE_URL}/`
- API health: `${PUBLIC_BASE_URL}/api/health`
- Swagger: `${PUBLIC_BASE_URL}/api/docs` (если `ENABLE_DOCS=true`)
- Admin: `${PUBLIC_BASE_URL}/admin`

## Ngrok

```bash
ngrok http 8080
```

Установите:
- `PUBLIC_BASE_URL=https://xxxx.ngrok-free.app`

## STORAGE_CHAT_ID

1. Создайте чат или канал.
2. Добавьте бота админом.
3. Напишите любое сообщение.
4. Получите chat_id через `getUpdates` или сторонний бот.

## Проверка флоу

1. Откройте бота → `/start` → кнопка **Каталог**.
2. В WebApp должен быть каталог с тестовыми данными.
3. Откройте фильм/эпизод → запросите просмотр.
4. Non-premium: появится ad-gate и nonce.
5. После ad-gate → кнопка watch → бот отправит видео, если `telegram_file_id` готов.

## Troubleshooting

### Not Found на всех ссылках
Проверьте `infra/nginx/nginx.conf` — нужен SPA fallback `try_files $uri $uri/ /index.html;`.

### WebApp пустая
Проверьте:
- Seed данных в API (`apps/api/app/services/seed.py`)
- `API_PUBLIC_URL`, `WEBAPP_PUBLIC_URL`
- CORS и initData auth

### /api/docs недоступен
Убедитесь, что `ENABLE_DOCS=true`.

### /admin не открывается
Проверьте `ADMIN_USER` и `ADMIN_PASS`, а также proxy в nginx.

### В боте нет кнопок
Проверьте `/start` хэндлер в `apps/bot/bot.py`.

### Видео не отправляется
Проверьте:
- наличие `telegram_file_id` в `media_variants`
- `STORAGE_CHAT_ID`
- Local Bot API настройки

### Обход рекламы
Убедитесь, что `ad_pass` nonce одноразовый и имеет TTL. Логика в `apps/api/app/routers/ads.py` и `apps/api/app/routers/watch.py`.

### TTL по умолчанию
- `DELIVERY_TOKEN_TTL_SECONDS` и `VARIANT_COOLDOWN_SECONDS` по умолчанию 600 секунд (если не переопределены в env). 

## Команды

- API tests:
  ```bash
  docker compose exec api pytest -q
  ```
