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

bot = Bot(token=TOKEN)
managers: [str] = ["n100o0"]

awaiting_manager: [str] = []
awaiting_client: [str] = []
chat_ids: {str: int} = {}


def log(msg: str, logtype="INFO") -> None:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {logtype}: {msg}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    username: str = update.effective_chat.username
    msg: str = update.message.text.lower()
    split: [str] = msg.split()

    log(
        f"Message from {username}: {update.message.text}",
        "MESSAGE",
    )

    if username in managers:
        if split[0] in awaiting_manager:
            if split[1] == "v":
                chat_id = chat_ids[split[0]]
                await context.bot.send_message(
                    chat_id, "Ваш заказ был одобрен. Подтвердите заказ: Да/Нет"
                )
                log(f"{split[0]}'s order has been approved")
                awaiting_manager.remove(split[0])
                awaiting_client.append(split[0])

            if split[1].isdigit():
                chat_id = chat_ids[split[0]]
                await context.bot.send_message(
                    chat_id,
                    f"Менеджер предлагает следующую цену для данного товара: {split[1]}. Подтвердите заказ: Да/Нет",
                )
                log(f"{split[0]}'s order has been changed")
                awaiting_manager.remove(split[0])
                awaiting_client.append(split[0])

    if username in awaiting_manager:
        return

    if username in awaiting_client:
        match split[0].lower():
            case "да":
                await update.message.reply_text("Ваш заказ в обработке.")
                awaiting_client.remove(username)
            case "нет":
                await update.message.reply_text("Заказ был отклонён.")
                awaiting_client.remove(username)
            case _:
                await update.message.reply_text('Ответьте "да" или "нет".')
                return

    if msg.startswith("заказ "):
        if len(split) < 2:
            await update.message.reply_text(
                'Цена не была предложена. Пример использования бота: "заказ 500".'
            )
            return

        if not split[1].isdigit():
            await update.message.reply_text("Предложенная цена недействительна.")
            return

        awaiting_manager.append(username)
        chat_ids[username] = update.effective_chat.id
        log(f"{username} has been added to orders ({split[1]})")
        await update.message.reply_text(
            "Ваш заказ принят, дождитесь одобрения заказа менеджером."
        )

        await send_to_manager(501711095, f"{username}: {split[1]}")


async def send_to_manager(chat_id, message: str):
    await bot.send_message(chat_id, text=message)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        f'Привет, {update.effective_chat.full_name}!\n\nЭто чат-бот, предназначенный для оптимизации бизнес-процесса.\nРассматриваемый бизнес процесс -- заказ клиентом определенного товара за цену, предлагаемую самим клиентом.\n\nИспользование: написать "заказ (стоимость товара)"'
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
