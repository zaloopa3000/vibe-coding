import os
import logging
from typing import List

import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

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
            "Напиши /news, чтобы получить последние заголовки."
        ),
    )


async def news_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tweets = fetch_ai_tweets()
    if not tweets:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Не удалось найти новости про AI. Попробуй позже.",
        )
        return

    text = "\n\n".join(f"{idx + 1}. {item}" for idx, item in enumerate(tweets))
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def fetch_ai_tweets() -> List[str]:
    bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
    if not bearer_token:
        logger.info("TWITTER_BEARER_TOKEN not found, using sample AI news.")
        return SAMPLE_AI_NEWS

    url = "https://api.twitter.com/2/tweets/search/recent"
    params = {
        "query": "AI OR \"artificial intelligence\" -is:retweet lang:en",
        "max_results": 5,
        "tweet.fields": "text",
    }
    headers = {"Authorization": f"Bearer {bearer_token}"}

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        tweets = [item["text"] for item in data.get("data", [])][:5]
        if not tweets:
            logger.warning("Twitter API returned no tweets, using sample data.")
            return SAMPLE_AI_NEWS
        return tweets
    except Exception as exc:
        logger.exception("Не удалось получить данные из Twitter API: %s", exc)
        return SAMPLE_AI_NEWS


def main() -> None:
    token = get_env_var("TELEGRAM_TOKEN")

    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("news", news_command))

    logger.info("Starting Telegram bot...")
    app.run_polling()


if __name__ == "__main__":
    main()
