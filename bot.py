import telebot
from telebot import types
import json
import os
from datetime import datetime

# ============================================================
#  CONFIG
# ============================================================
BOT_TOKEN = "8896407692:AAG8iRQDKAWx8DgCyR5ICO25tmyqUiNBPbw"
WEBAPP_URL = "https://melonacolloction.github.io/BenulaOfficial-/"

# Admin ID
ADMIN_ID = 7713208330

# Stats file
STATS_FILE = "stats.json"

# ============================================================
#  INIT BOT
# ============================================================
bot = telebot.TeleBot(BOT_TOKEN)

# ============================================================
#  STATS MANAGEMENT
# ============================================================
def load_stats():
    """Load stats from file"""
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"users": []}
    return {"users": []}

def save_stats(stats):
    """Save stats to file"""
    with open(STATS_FILE, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

def register_user(user_id, username, first_name):
    """Register new user"""
    stats = load_stats()
    
    # Check if user already exists
    existing_user = next((u for u in stats['users'] if u['id'] == user_id), None)
    
    if existing_user:
        return False
    
    # Register new user
    new_user = {
        'id': user_id,
        'username': username,
        'first_name': first_name,
        'registered_at': datetime.now().isoformat()
    }
    
    stats['users'].append(new_user)
    save_stats(stats)
    return True

def get_total_users():
    """Get total number of registered users"""
    stats = load_stats()
    return len(stats.get('users', []))

# ============================================================
#  /ADMIN COMMAND - Only for admin
# ============================================================
@bot.message_handler(commands=['admin'])
def admin_stats(message):
    """Show total users - Admin only"""
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "⛔ You don't have access to this section!")
        return
    
    total_users = get_total_users()
    
    stats_text = f"""
📊 **Benula Airdrop Stats**

👥 **Total Registered Users:** {total_users}

📅 Last update: {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
    
    bot.reply_to(message, stats_text, parse_mode='Markdown')

# ============================================================
#  /START COMMAND
# ============================================================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    username = message.from_user.first_name or "User"
    user_id = message.from_user.id
    
    # Register user
    registered = register_user(
        user_id,
        message.from_user.username,
        message.from_user.first_name
    )
    
    # Check referral code
    ref_code = None
    text_parts = message.text.split()
    if len(text_parts) > 1:
        potential_ref = text_parts[1]
        if potential_ref.startswith('ref_'):
            ref_code = potential_ref[4:]
        elif len(potential_ref) == 6:
            ref_code = potential_ref
    
    # Build WebApp URL
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
    
    # Create keyboard
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    
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
    print("✅ Waiting for commands...")
    bot.infinity_polling()
