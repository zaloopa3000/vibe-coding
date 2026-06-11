# AI News Telegram Bot

Простой Telegram бот, который по команде `/news` отправляет последние новости про AI.

## Установка

1. Перейди в папку проекта:

```bash
cd "AI news telegram"
```

2. Установи зависимости:

```bash
python -m pip install -r requirements.txt
```

## Запуск

1. Создай бота через BotFather и получи `TELEGRAM_TOKEN`.
2. Запусти бот:

```bash
export TELEGRAM_TOKEN="ваш_токен"
python bot.py
```

3. Напиши боту `/news`.

## Twitter API (опционально)

Если хочешь использовать реальные твиты, установи `TWITTER_BEARER_TOKEN`:

```bash
export TWITTER_BEARER_TOKEN="ваш_bearer_token"
```

Если токен Twitter не задан, бот будет возвращать примерные новости про AI.
