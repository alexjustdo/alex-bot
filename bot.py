import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import anthropic

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = "Si Alex, priateľská a schopná virtuálna asistentka. Hovoríš po slovensky — vždy, aj keď ti niekto píše po anglicky alebo inak. Si milá, efektívna a praktická. Pomáhaš s čímkoľvek — plánovaním, písaním emailov, brainstormingom, vysvetľovaním tém, zhrnutiami a ďalším. Odpovedáš stručne a prirodzene, ako dobrá asistentka. Nepoužívaš dlhé úvody."

conversation_histories = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conversation_histories[user_id] = []
    await update.message.reply_text(
        "👋 Ahoj! Som Alex, vaša virtuálna asistentka.\n\n"
        "Pomôžem vám s čímkoľvek — plánovaním, emailmi, nápadmi, otázkami a oveľa viac.\n\n"
        "Čím môžem začať? 😊"
    )

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conversation_histories[user_id] = []
    await update.message.reply_text("🔄 Konverzácia bola resetovaná. Začíname odznova!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💡 *Čo viem robiť:*\n\n"
        "• Písanie emailov a textov\n"
        "• Plánovanie úloh a dňa\n"
        "• Brainstorming a nápady\n"
        "• Vysvetľovanie tém\n"
        "• Zhrnutia textov\n"
        "• A čokoľvek iné!\n\n"
        "*Príkazy:*\n"
        "/start — Reštart\n"
        "/reset — Vymazať históriu\n"
        "/help — Táto správa",
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in conversation_histories:
        conversation_histories[user_id] = []

    conversation_histories[user_id].append({
        "role": "user",
        "content": update.message.text
    })

    if len(conversation_histories[user_id]) > 20:
        conversation_histories[user_id] = conversation_histories[user_id][-20:]

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        response = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=1000,
            system=SYSTEM_PROMPT,
            messages=conversation_histories[user_id]
        )
        reply = response.content[0].text
        conversation_histories[user_id].append({
            "role": "assistant",
            "content": reply
        })
        await update.message.reply_text(reply)
    except Exception as e:
        logger.error(f"Chyba: {e}")
        await update.message.reply_text("⚠️ Nastala chyba. Skúste to prosím znova.")

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("Alex bot beží...")
    app.run_polling()

if __name__ == "__main__":
    main()
