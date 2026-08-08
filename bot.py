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

# لیست ادمین‌ها (آیدی عددی تلگرام)
ADMIN_IDS = [7713208330]  # آیدی ادمین شما

# فایل ذخیره آمار
STATS_FILE = "stats.json"

# ============================================================
#  INIT BOT
# ============================================================
bot = telebot.TeleBot(BOT_TOKEN)

# ============================================================
#  STATS MANAGEMENT
# ============================================================
def load_stats():
    """بارگذاری آمار از فایل"""
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"users": [], "total_tokens": 0, "total_users": 0}
    return {"users": [], "total_tokens": 0, "total_users": 0}

def save_stats(stats):
    """ذخیره آمار در فایل"""
    with open(STATS_FILE, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

def register_user(user_id, username, first_name, ref_code=None):
    """ثبت کاربر جدید و بروزرسانی آمار"""
    stats = load_stats()
    
    # بررسی اینکه کاربر قبلاً ثبت شده یا نه
    existing_user = next((u for u in stats['users'] if u['id'] == user_id), None)
    
    if existing_user:
        # کاربر قبلاً ثبت شده
        return False
    
    # ثبت کاربر جدید
    new_user = {
        'id': user_id,
        'username': username,
        'first_name': first_name,
        'ref_code': ref_code,
        'registered_at': datetime.now().isoformat(),
        'tokens': 0
    }
    
    stats['users'].append(new_user)
    stats['total_users'] = len(stats['users'])
    save_stats(stats)
    return True

def update_user_tokens(user_id, amount):
    """بروزرسانی توکن یک کاربر"""
    stats = load_stats()
    
    for user in stats['users']:
        if user['id'] == user_id:
            user['tokens'] = user.get('tokens', 0) + amount
            stats['total_tokens'] = sum(u.get('tokens', 0) for u in stats['users'])
            save_stats(stats)
            return True
    return False

def get_total_tokens():
    """دریافت کل توکن‌های جمع شده"""
    stats = load_stats()
    return stats.get('total_tokens', 0)

def get_total_users():
    """دریافت تعداد کل کاربران"""
    stats = load_stats()
    return stats.get('total_users', 0)

def get_user_stats():
    """دریافت آمار کامل کاربران"""
    stats = load_stats()
    return stats

# ============================================================
#  ADMIN COMMANDS
# ============================================================
@bot.message_handler(commands=['stats'])
def stats_command(message):
    """نمایش آمار کلی - فقط برای ادمین"""
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "⛔ شما دسترسی به این بخش را ندارید!")
        return
    
    stats = get_user_stats()
    total_users = stats.get('total_users', 0)
    total_tokens = stats.get('total_tokens', 0)
    
    # محاسبه میانگین توکن
    avg_tokens = total_tokens / total_users if total_users > 0 else 0
    
    # پیدا کردن کاربر با بیشترین توکن
    top_user = None
    top_tokens = 0
    for user in stats.get('users', []):
        if user.get('tokens', 0) > top_tokens:
            top_tokens = user.get('tokens', 0)
            top_user = user
    
    stats_text = f"""
📊 **آمار کلی Benula Airdrop**

👥 **تعداد کل کاربران:** {total_users}
🪙 **کل توکن‌های توزیع شده:** {total_tokens:,}
📈 **میانگین توکن هر کاربر:** {avg_tokens:,.0f}

🏆 **بیشترین توکن:**
"""
    
    if top_user:
        stats_text += f"""
👤 {top_user.get('first_name', 'Unknown')}
🆔 @{top_user.get('username', 'N/A')}
🪙 {top_tokens:,} توکن
"""
    else:
        stats_text += "\n❌ هنوز کاربری ثبت نام نکرده است!"
    
    # دکمه‌های مدیریت
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton("📋 لیست کاربران", callback_data="list_users"),
        types.InlineKeyboardButton("💎 برترین‌ها", callback_data="top_users"),
        types.InlineKeyboardButton("📊 بروزرسانی", callback_data="refresh_stats"),
        types.InlineKeyboardButton("📥 خروجی JSON", callback_data="export_json")
    )
    
    bot.reply_to(message, stats_text, reply_markup=keyboard, parse_mode='Markdown')

@bot.message_handler(commands=['users'])
def list_users_command(message):
    """نمایش لیست کاربران - فقط برای ادمین"""
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "⛔ شما دسترسی به این بخش را ندارید!")
        return
    
    stats = get_user_stats()
    users = stats.get('users', [])
    
    if not users:
        bot.reply_to(message, "📭 هنوز هیچ کاربری ثبت نام نکرده است!")
        return
    
    # نمایش ۱۰ کاربر اول
    text = "📋 **لیست کاربران (۱۰ نفر اول):**\n\n"
    for i, user in enumerate(users[:10], 1):
        text += f"{i}. {user.get('first_name', 'Unknown')} "
        if user.get('username'):
            text += f"(@{user['username']}) "
        text += f"- 🪙 {user.get('tokens', 0)} توکن\n"
    
    if len(users) > 10:
        text += f"\n... و {len(users) - 10} کاربر دیگر"
        text += f"\n\n📊 برای مشاهده کامل از دکمه استفاده کنید"
    
    bot.reply_to(message, text, parse_mode='Markdown')

@bot.message_handler(commands=['top'])
def top_users_command(message):
    """نمایش برترین کاربران - فقط برای ادمین"""
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "⛔ شما دسترسی به این بخش را ندارید!")
        return
    
    stats = get_user_stats()
    users = stats.get('users', [])
    
    if not users:
        bot.reply_to(message, "📭 هنوز هیچ کاربری ثبت نام نکرده است!")
        return
    
    # مرتب‌سازی بر اساس توکن
    sorted_users = sorted(users, key=lambda x: x.get('tokens', 0), reverse=True)
    
    text = "🏆 **برترین کاربران:**\n\n"
    medals = ["🥇", "🥈", "🥉"]
    
    for i, user in enumerate(sorted_users[:10], 1):
        medal = medals[i-1] if i <= 3 else f"{i}."
        text += f"{medal} {user.get('first_name', 'Unknown')} "
        if user.get('username'):
            text += f"(@{user['username']}) "
        text += f"- 🪙 {user.get('tokens', 0):,} توکن\n"
    
    bot.reply_to(message, text, parse_mode='Markdown')

@bot.message_handler(commands=['reset_stats'])
def reset_stats_command(message):
    """ریست کردن آمار - فقط برای ادمین"""
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "⛔ شما دسترسی به این بخش را ندارید!")
        return
    
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton("✅ بله، ریست کن", callback_data="confirm_reset"),
        types.InlineKeyboardButton("❌ لغو", callback_data="cancel_reset")
    )
    
    bot.reply_to(
        message, 
        "⚠️ **هشدار!**\n\nآیا مطمئن هستید که می‌خواهید تمام آمار را ریست کنید؟\nاین عمل قابل بازگشت نیست!",
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

# ============================================================
#  CALLBACK HANDLERS
# ============================================================
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.from_user.id not in ADMIN_IDS:
        bot.answer_callback_query(call.id, "⛔ شما دسترسی ندارید!")
        return
    
    if call.data == "list_users":
        # نمایش لیست کامل کاربران با صفحه‌بندی
        stats = get_user_stats()
        users = stats.get('users', [])
        
        if not users:
            bot.edit_message_text(
                "📭 هنوز هیچ کاربری ثبت نام نکرده است!",
                call.message.chat.id,
                call.message.message_id
            )
            return
        
        text = "📋 **لیست کامل کاربران:**\n\n"
        for i, user in enumerate(users, 1):
            text += f"{i}. {user.get('first_name', 'Unknown')} "
            if user.get('username'):
                text += f"(@{user['username']}) "
            text += f"- 🪙 {user.get('tokens', 0)} توکن\n"
            if i % 20 == 0:
                text += "---\n"
        
        if len(users) > 50:
            text += f"\n📊 مجموع: {len(users)} کاربر"
        
        bot.edit_message_text(
            text[:4000],
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown'
        )
        
    elif call.data == "top_users":
        stats = get_user_stats()
        users = stats.get('users', [])
        
        if not users:
            bot.edit_message_text(
                "📭 هنوز هیچ کاربری ثبت نام نکرده است!",
                call.message.chat.id,
                call.message.message_id
            )
            return
        
        sorted_users = sorted(users, key=lambda x: x.get('tokens', 0), reverse=True)
        text = "🏆 **۱۰ کاربر برتر:**\n\n"
        medals = ["🥇", "🥈", "🥉"]
        
        for i, user in enumerate(sorted_users[:10], 1):
            medal = medals[i-1] if i <= 3 else f"{i}."
            text += f"{medal} {user.get('first_name', 'Unknown')} "
            if user.get('username'):
                text += f"(@{user['username']}) "
            text += f"- 🪙 {user.get('tokens', 0):,} توکن\n"
        
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown'
        )
        
    elif call.data == "refresh_stats":
        stats = load_stats()
        total_users = stats.get('total_users', 0)
        total_tokens = stats.get('total_tokens', 0)
        
        bot.answer_callback_query(
            call.id,
            f"✅ بروزرسانی شد! {total_users} کاربر - {total_tokens:,} توکن"
        )
        
        stats_command(call.message)
        
    elif call.data == "export_json":
        stats = get_user_stats()
        json_text = json.dumps(stats, ensure_ascii=False, indent=2)
        
        if len(json_text) > 4000:
            summary = f"""
📊 **خلاصه آمار:**
- کاربران: {stats.get('total_users', 0)}
- کل توکن: {stats.get('total_tokens', 0):,}
- تعداد رکوردها: {len(stats.get('users', []))}

📁 برای دریافت فایل کامل JSON به پنل مدیریت مراجعه کنید.
            """
            bot.edit_message_text(
                summary,
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown'
            )
        else:
            bot.edit_message_text(
                f"```json\n{json_text}\n```",
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown'
            )
            
    elif call.data == "confirm_reset":
        empty_stats = {"users": [], "total_tokens": 0, "total_users": 0}
        save_stats(empty_stats)
        bot.edit_message_text(
            "✅ **آمار با موفقیت ریست شد!**\n\nهمه داده‌ها پاک شدند.",
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown'
        )
        
    elif call.data == "cancel_reset":
        bot.edit_message_text(
            "✅ عملیات لغو شد. آمار حفظ شد.",
            call.message.chat.id,
            call.message.message_id
        )

# ============================================================
#  /START COMMAND - WITH STATS TRACKING
# ============================================================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    username = message.from_user.first_name or "User"
    user_id = message.from_user.id
    
    # ثبت کاربر
    registered = register_user(
        user_id,
        message.from_user.username,
        message.from_user.first_name
    )
    
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
        if registered:
            welcome_text = f"""
🌟 Welcome {username}! 

You've joined **Benula Airdrop**! 🎉

✅ You've been registered successfully!
✅ Referral code `{ref_code}` applied!
🪙 Start earning tokens now!

👇 Click the button below to open the app
            """
        else:
            welcome_text = f"""
🌟 Welcome back {username}! 

You've already joined **Benula Airdrop**! 🎉

✅ Referral code `{ref_code}` applied!
🪙 Continue earning tokens!

👇 Click the button below to open the app
            """
    else:
        webapp_url = WEBAPP_URL
        if registered:
            welcome_text = f"""
🌟 Welcome {username}! 

You've joined **Benula Airdrop**! 🎉

✅ You've been registered successfully!
🪙 Start earning tokens now!

👇 Click the button below to open the app
            """
        else:
            welcome_text = f"""
🌟 Welcome back {username}! 

You've already joined **Benula Airdrop**! 🎉

🪙 Continue earning tokens!

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
    
    # اگر کاربر ادمین بود، دکمه آمار رو هم اضافه کن
    if user_id in ADMIN_IDS:
        keyboard.add(
            types.InlineKeyboardButton("📊 Admin Panel", callback_data="admin_panel")
        )
    
    bot.send_message(
        message.chat.id,
        welcome_text,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )
    
    # اگر کاربر جدید ثبت شده، به ادمین اطلاع بده
    if registered and user_id not in ADMIN_IDS:
        for admin_id in ADMIN_IDS:
            try:
                bot.send_message(
                    admin_id,
                    f"🆕 **کاربر جدید ثبت نام کرد!**\n\n"
                    f"👤 نام: {message.from_user.first_name}\n"
                    f"🆔 یوزرنیم: @{message.from_user.username or 'N/A'}\n"
                    f"📱 آیدی: `{user_id}`\n"
                    f"🔗 کد معرف: {ref_code or 'بدون کد'}\n"
                    f"📅 زمان: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                    parse_mode='Markdown'
                )
            except:
                pass

# ============================================================
#  ADMIN PANEL CALLBACK
# ============================================================
@bot.callback_query_handler(func=lambda call: call.data == "admin_panel")
def admin_panel(call):
    if call.from_user.id not in ADMIN_IDS:
        bot.answer_callback_query(call.id, "⛔ شما دسترسی ندارید!")
        return
    
    stats = get_user_stats()
    total_users = stats.get('total_users', 0)
    total_tokens = stats.get('total_tokens', 0)
    
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton("📊 آمار کلی", callback_data="refresh_stats"),
        types.InlineKeyboardButton("📋 لیست کاربران", callback_data="list_users"),
        types.InlineKeyboardButton("🏆 برترین‌ها", callback_data="top_users"),
        types.InlineKeyboardButton("📥 خروجی JSON", callback_data="export_json"),
        types.InlineKeyboardButton("⚠️ ریست آمار", callback_data="reset_stats"),
        types.InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_start")
    )
    
    bot.edit_message_text(
        f"🔐 **پنل مدیریت**\n\n"
        f"👥 کاربران: {total_users}\n"
        f"🪙 کل توکن: {total_tokens:,}\n"
        f"📈 میانگین: {total_tokens/total_users if total_users > 0 else 0:,.0f}\n\n"
        f"یک گزینه را انتخاب کنید:",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

@bot.callback_query_handler(func=lambda call: call.data == "back_to_start")
def back_to_start(call):
    if call.from_user.id not in ADMIN_IDS:
        bot.answer_callback_query(call.id, "⛔ شما دسترسی ندارید!")
        return
    
    # ارسال مجدد پیام شروع
    send_welcome(call.message)

# ============================================================
#  RUN BOT
# ============================================================
if __name__ == '__main__':
    print("🤖 Benula Bot is running...")
    print(f"🔗 WebApp URL: {WEBAPP_URL}")
    print(f"👥 Admin IDs: {ADMIN_IDS}")
    print("✅ Waiting for commands...")
    bot.infinity_polling()
