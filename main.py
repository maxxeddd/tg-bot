from dotenv import load_dotenv
import os
import datetime

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

load_dotenv()
TOKEN: str = os.environ.get("TOKEN")

managers: [str] = ["n100o0"]


def log(msg: str, logtype="INFO") -> None:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {logtype}: {msg}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log(
        f"Message from {update.effective_chat.username}: {update.message.text}",
        "MESSAGE",
    )

    # if update.effective_chat.username in managers:
    # pass

    msg: str = update.message.text.lower()
    split: [str] = msg.split()

    if msg.startswith("заказ"):
        if len(split) < 2:
            await update.message.reply_text(
                'Цена не была предложена. Пример использования бота: "заказ 500".'
            )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        f'Привет, {update.effective_chat.full_name}!\n\n Это чат-бот, предназначенный для оптимизации бизнес-процесса.\nРассматриваемый бизнес процесс -- заказ клиентом определенного товара за цену, предлагаемую самим клиентом.\n\nИспользование: написать "заказ (стоимость товара)"'
    )


async def on_start(application):
    log("Bot has been started")


def main():
    app: ApplicationBuilder = (
        ApplicationBuilder().token(TOKEN).post_init(on_start).build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    log("Starting the bot")
    app.run_polling()


if __name__ == "__main__":
    main()
