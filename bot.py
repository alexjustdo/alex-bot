import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import anthropic
from tavily import TavilyClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
TAVILY_API_KEY = os.environ["TAVILY_API_KEY"]

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
tavily = TavilyClient(api_key=TAVILY_API_KEY)

SYSTEM_PROMPT = """Si Alex, priateľská a schopná virtuálna asistentka. Hovoríš po slovensky — vždy, aj keď ti niekto píše po anglicky alebo inak. Si milá, efektívna a praktická.

Ak potrebuješ aktuálne informácie zo sveta (správy, počasie, ceny, udalosti), použi funkciu web_search.
Odpovedáš stručne a prirodzene. Nepoužívaš dlhé úvody."""

tools = [
    {
        "name": "web_search",
        "description": "Vyhľadaj aktuálne informácie na internete. Použi keď potrebuješ správy, aktuálne udalosti, počasie, ceny alebo iné aktuálne informácie.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Vyhľadávací dotaz"
                }
            },
            "required": ["query"]
        }
    }
]

conversation_histories = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conversation_histories[user_id] = []
    await update.message.reply_text(
        "👋 Ahoj! Som Alex, vaša virtuálna asistentka.\n\n"
        "Teraz mám prístup na internet — môžem vyhľadávať správy, počasie, ceny a oveľa viac!\n\n"
        "Čím môžem začať? 😊"
    )

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conversation_histories[user_id] = []
    await update.message.reply_text("🔄 Konverzácia bola resetovaná. Začíname odznova!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💡 *Čo viem robiť:*\n\n"
        "• Vyhľadávanie správ a informácií 🌐\n"
        "• Písanie emailov a textov\n"
        "• Plánovanie úloh a dňa\n"
        "• Brainstorming a nápady\n"
        "• Vysvetľovanie tém\n"
        "• Zhrnutia textov\n\n"
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
        messages = conversation_histories[user_id].copy()
        
        while True:
            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=1000,
                system=SYSTEM_PROMPT,
                tools=tools,
                messages=messages
            )

            if response.stop_reason == "tool_use":
                tool_use = next(b for b in response.content if b.type == "tool_use")
                query = tool_use.input["query"]
                
                await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
                
                search_result = tavily.search(query=query, max_results=3)
                search_text = "\n".join([f"- {r['title']}: {r['content'][:200]}" for r in search_result['results']])

                messages.append({"role": "assistant", "content": response.content})
                messages.append({
                    "role": "user",
                    "content": [{"type": "tool_result", "tool_use_id": tool_use.id, "content": search_text}]
                })
            else:
                reply = next(b.text for b in response.content if hasattr(b, 'text'))
                break

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
