import asyncio
import logging
import os
import re
from typing import List, Optional, Set

from telegram import Update, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from telethon import TelegramClient
from telethon.errors import ChannelPrivateError, UsernameNotOccupiedError
from telethon.errors.rpcerrorlist import SessionPasswordNeededError

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

SAMPLE_AI_NEWS = [
    "OpenAI анонсировала новую модель для генерации текста.",
    "Microsoft инвестирует в проекты по искусственному интеллекту.",
    "Исследователи выпустили открытую библиотеку для обучения нейросетей.",
    "Стартап создал AI-помощника для анализа технических статей.",
    "Эксперты обсуждают этику использования генеративного ИИ.",
]


def get_env_var(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Environment variable {name} is required.")
    return value


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            "Привет! Я бот, который помогает найти новости про AI.\n"
            "Напиши /news, чтобы получить последние заголовки.\n"
            "Напиши /stop, чтобы остановить бота."
        ),
    )


NEWS_KEYWORDS = re.compile(
    r"(?i)\b(искусственный интеллект|AI|нейросеть|нейросети|машинное обучение|ML|GPT|чатGPT|ChatGPT|новость|новости|анонс)\b"
)

telethon_client: Optional[TelegramClient] = None


async def init_telethon_client() -> Optional[TelegramClient]:
    global telethon_client
    if telethon_client is not None:
        return telethon_client

    api_id = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")
    if not api_id or not api_hash:
        logger.warning("TELEGRAM_API_ID или TELEGRAM_API_HASH не заданы.")
        return None
    if api_id.strip().lower() in {"your_api_id", "ваш_api_id"}:
        logger.warning("TELEGRAM_API_ID содержит placeholder. Установи реальный api_id.")
        return None
    if api_hash.strip().lower() in {"your_api_hash", "ваш_api_hash"}:
        logger.warning("TELEGRAM_API_HASH содержит placeholder. Установи реальный api_hash.")
        return None
    if not api_id.isdigit():
        logger.warning("TELEGRAM_API_ID должен быть числом. Текущее значение: %s", api_id)
        return None

    session_name = os.getenv("TELETHON_SESSION", "telethon_session")
    try:
        client = TelegramClient(session_name, int(api_id), api_hash)
        await client.start()
        telethon_client = client
        return telethon_client
    except SessionPasswordNeededError:
        logger.error("Telethon требует пароль двухфакторной аутентификации.")
        return None
    except Exception as exc:
        logger.exception("Не удалось инициализировать Telethon: %s", exc)
        return None


async def fetch_ai_tweets() -> List[str]:
    channel_list = [item.strip() for item in os.getenv("SOURCE_CHANNELS", "").split(",") if item.strip()]
    client = await init_telethon_client()
    if client is None or not channel_list:
        logger.info("Telethon не настроен или каналы не указаны, возвращаю примеры.")
        return SAMPLE_AI_NEWS

    headlines: List[str] = []
    seen: Set[str] = set()

    for channel in channel_list:
        try:
            entity = await client.get_entity(channel)
            messages = await client.get_messages(entity, limit=30)
        except (ChannelPrivateError, UsernameNotOccupiedError) as exc:
            logger.warning("Не удалось получить канал %s: %s", channel, exc)
            continue
        except Exception as exc:
            logger.exception("Ошибка при чтении канала %s: %s", channel, exc)
            continue

        for message in messages:
            text = (message.message or "").strip()
            if not text:
                continue

            if NEWS_KEYWORDS.search(text):
                headline = text.split("\n", 1)[0].strip()
                if len(headline) > 320:
                    headline = headline[:320].rstrip() + "…"

                if headline and headline not in seen:
                    seen.add(headline)
                    headlines.append(headline)
                    if len(headlines) >= 10:
                        break
        if len(headlines) >= 10:
            break

    if not headlines:
        logger.info("Не найдено новостей в каналах, возвращаю примеры.")
        return SAMPLE_AI_NEWS

    return headlines


async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="✅ Бот успешно остановлен!"
    )
    await context.application.stop()


async def news_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tweets = await fetch_ai_tweets()
    if not tweets:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Не удалось найти новости про AI. Попробуй позже.",
        )
        return

    text = "\n\n".join(f"{idx + 1}. {item}" for idx, item in enumerate(tweets))
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


async def set_bot_commands(app) -> None:
    """Установить саджесты команд для отображения при вводе /"""
    commands = [
        BotCommand("start", "Запустить бота"),
        BotCommand("news", "Получить новости про AI"),
        BotCommand("stop", "Остановить бота"),
    ]
    await app.bot.set_my_commands(commands)


def main() -> None:
    token = get_env_var("TELEGRAM_TOKEN")

    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("news", news_command))
    app.add_handler(CommandHandler("stop", stop_command))

    async def post_init_setup(app):
        await set_bot_commands(app)
    
    app.post_init = post_init_setup

    logger.info("Starting Telegram bot...")
    app.run_polling()


if __name__ == "__main__":
    main()
