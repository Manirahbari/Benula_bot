import telebot
from telebot import types

# ============================================================
#  CONFIG
# ============================================================
BOT_TOKEN = "8896407692:AAG8iRQDKAWx8DgCyR5ICO25tmyqUiNBPbw"
SITE_URL = "https://melonacollocton.github.io/Benula"

# ============================================================
#  INIT BOT
# ============================================================
bot = telebot.TeleBot(BOT_TOKEN)

# ============================================================
#  /START COMMAND
# ============================================================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    username = message.from_user.first_name or "User"
    
    # بررسی کد معرف
    ref_code = None
    text_parts = message.text.split()
    if len(text_parts) > 1:
        potential_ref = text_parts[1]  # ref_ACN2kn
        if potential_ref.startswith('ref_'):
            ref_code = potential_ref[4:]  # ACN2kn
    
    # ساخت لینک
    if ref_code:
        link = f"{SITE_URL}?ref={ref_code}"
        welcome_text = f"""
🌟 Welcome {username}! 

Join **Benula Airdrop**! 🎉

✅ Referral code `{ref_code}` applied!
🔗 Click below to enter the app
        """
    else:
        link = SITE_URL
        welcome_text = f"""
🌟 Welcome {username}! 

Join **Benula Airdrop**! 🎉

🔗 Click below to enter the app
        """
    
    # دکمه‌ها
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(types.InlineKeyboardButton("🚀 Open App", url=link))
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
#  RUN
# ============================================================
if __name__ == '__main__':
    print("🤖 Benula Bot Running...")
    bot.infinity_polling()
