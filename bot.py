import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

# ============================================================
#  تنظیمات
# ============================================================
BOT_TOKEN = os.environ.get("BOT_TOKEN")  # از متغیر محیطی میخونه
SITE_URL = "https://melonacolloction.github.io/BenulaOfficial-/"

# ============================================================
#  دستور /start
# ============================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    first_name = user.first_name or "User"
    
    ref_code = context.args[0] if context.args else ''
    if ref_code.startswith('ref_'):
        ref_code = ref_code.replace('ref_', '')
    
    if ref_code:
        web_app_url = f"{SITE_URL}?ref={ref_code}"
    else:
        web_app_url = SITE_URL
    
    message = f"""
🎉 <b>Welcome to Benula Airdrop, {first_name}!</b>

💰 <b>What is Benula?</b>
Benula is a decentralized airdrop platform where you can earn free tokens by completing simple tasks.

📋 <b>How to get started?</b>
1️⃣ Click the button below to open the app
2️⃣ Join our channel and group
3️⃣ Complete tasks and earn rewards

🚀 <b>Start earning now!</b>
"""
    
    keyboard = [
        [InlineKeyboardButton("🚀 Open App", web_app={"url": web_app_url})],
        [
            InlineKeyboardButton("📢 Channel", url="https://t.me/Benula_Official"),
            InlineKeyboardButton("💬 Group", url="https://t.me/BenulaOfficial")
        ],
        [InlineKeyboardButton("▶️ YouTube", url="https://www.youtube.com/@BenulaOfficial")]
    ]
    
    await update.message.reply_text(
        message,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ============================================================
#  راه‌اندازی ربات
# ============================================================
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    
    print("🚀 Benula bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
