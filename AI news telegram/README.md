# AI News Telegram Bot

Простой Telegram бот, который по команде `/news` отправляет последние новости про AI.

## Установка

1. Перейди в папку проекта:

```bash
cd "AI news telegram"
```

2. Установи зависимости:

```bash
python3 -m pip install -r requirements.txt
```

## Telethon и чтение публичных каналов

Если хочешь собирать новости из публичных Telegram-каналов, добавь в окружение:

```bash
export TELEGRAM_API_ID="ваш_api_id"
export TELEGRAM_API_HASH="ваш_api_hash"
export SOURCE_CHANNELS="@channel1,@channel2"
```

- `TELEGRAM_API_ID` и `TELEGRAM_API_HASH` берутся на https://my.telegram.org
- `SOURCE_CHANNELS` — список публичных публичных каналов через запятую
- `SOURCE_CHANNELS` должен содержать реальные никнеймы каналов, например `@AI_news`
- при первом запуске `Telethon` может запросить код авторизации в консоли

### Пример списка каналов

```bash
export SOURCE_CHANNELS="@AI_news,@DeepLearning_AI,@MachineLearning_ru,@ai_updates"
```

### Как выбрать каналы

- ищи публичные каналы в Telegram по запросам «AI», «искусственный интеллект», «новости AI»
- добавляй только каналы с открытой публичной ссылкой и никнеймом
- бот не может автоматически собрать «все» открытые каналы — тебе нужно указать список

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
