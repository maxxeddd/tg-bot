from dotenv import load_dotenv
import os
import datetime

from telegram import Update, Bot
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

pending_orders: [str] = []


def log(msg: str, logtype="INFO") -> None:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {logtype}: {msg}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    username: str = update.effective_chat.username
    msg: str = update.message.text.lower()

    log(
        f"Message from {username}: {update.message.text}",
        "MESSAGE",
    )

    if username in managers:
        pass

    split: [str] = msg.split()

    if msg.startswith("заказ "):
        if len(split) < 2:
            await update.message.reply_text(
                'Цена не была предложена. Пример использования бота: "заказ 500".'
            )
            return

        if not split[1].isdigit():
            await update.message.reply_text("Предложенная цена недействительна.")
            return

        pending_orders.append(username)
        log(f"{username} has been added to pending requests")
        await update.message.reply_text("Ваш заказ принят, дождитесь ответа менеджера.")

        await send_to_manager(501711095, f"{username}: {split[1]}")


async def send_to_manager(chat_id, message: str):
    bot = Bot(token=TOKEN)
    await bot.send_message(chat_id, text=message)


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
