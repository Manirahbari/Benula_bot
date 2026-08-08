import telebot
from telebot import types

# ============================================================
#  CONFIG
# ============================================================
BOT_TOKEN = "8896407692:AAG8iRQDKAWx8DgCyR5ICO25tmyqUiNBPbw"
WEBAPP_URL = "https://melonacolloction.github.io/BenulaOfficial-/"

# ============================================================
#  INIT BOT
# ============================================================
bot = telebot.TeleBot(BOT_TOKEN)

# ============================================================
#  /START COMMAND - ONLY COMMAND
# ============================================================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    username = message.from_user.first_name or "User"
    
    # Check referral code from start=ref_XXXXXX
    ref_code = None
    text_parts = message.text.split()
    if len(text_parts) > 1:
        potential_ref = text_parts[1]
        if potential_ref.startswith('ref_'):
            ref_code = potential_ref[4:]
        elif len(potential_ref) == 6:
            ref_code = potential_ref
    
    # Build WebApp URL with referral code
    if ref_code:
        webapp_url = f"{WEBAPP_URL}?ref={ref_code}"
        welcome_text = f"""
🌟 Welcome {username}! 

You've joined **Benula Airdrop**! 🎉

✅ Referral code `{ref_code}` applied!
👇 Click the button below to open the app
        """
    else:
        webapp_url = WEBAPP_URL
        welcome_text = f"""
🌟 Welcome {username}! 

You've joined **Benula Airdrop**! 🎉

👇 Click the button below to open the app
        """
    
    # Create keyboard with WebApp button
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    
    # WebApp button - opens directly inside Telegram
    btn_open = types.InlineKeyboardButton(
        "🚀 Open App",
        web_app=types.WebAppInfo(url=webapp_url)
    )
    
    keyboard.add(btn_open)
    keyboard.add(
        types.InlineKeyboardButton("📢 Channel", url="https://t.me/Benula_Official"),
        types.InlineKeyboardButton("💬 Group", url="https://t.me/BenulaOfficial")
    )
    
    bot.send_message(
        message.chat.id,
        welcome_text,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

# ============================================================
#  RUN BOT
# ============================================================
if __name__ == '__main__':
    print("🤖 Benula Bot is running...")
    print(f"🔗 WebApp URL: {WEBAPP_URL}")
    print("✅ Waiting for /start commands...")
    bot.infinity_polling()
