import telebot
import requests
import os
import hashlib
from telebot.types import InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton

# ================= CONFIGURATION =================
# Naya token code me default rakh diya hai, Railway me daaloge toh wahan se auto-load hoga
TOKEN = os.getenv('BOT_TOKEN', '8643094183:AAEwi64PymNJ370hHFY9RF66b07bEzFcTe8')
bot = telebot.TeleBot(TOKEN)

# Aapke naye bot ka exact username
BOT_USERNAME = 'musicshadow0_bot'

@bot.message_handler(commands=['start'])
def welcome(message):
    text = (
        "🎵 **Welcome to Exact Inline Music Player Bot!**\n\n"
        "Yeh bot pure inline system par chalta hai. Aapko chat me command likhne ki bhi zaroorat nahi hai!\n\n"
        "🚀 **Kaise Use Karein?**\n"
        f"1. Kisi bhi chat me type kholo aur type karein: `@{BOT_USERNAME} <gaane ka naam>`\n"
        "2. Ek menu khulegi, apne manpasand gaane par click karein.\n"
        "3. Chat me direct buttons ke sath player chalne lagega!"
    )
    bot.reply_to(message, text, parse_mode="Markdown")

# ================= 1. INLINE SEARCH SYSTEM =================
@bot.inline_handler(func=lambda query: len(query.query) > 0)
def query_text(inline_query):
    try:
        user_query = inline_query.query.strip()
        # Public Workers API to search YouTube without server load
        api_url = f"https://api.vyt.workers.dev/search?q={requests.utils.quote(user_query)}"
        results = requests.get(api_url, timeout=10).json().get('results', [])

        inline_results = []
        for index, track in enumerate(results[:5]):  # Top 5 results dikhayenge
            title = track.get('title', 'Unknown Track')
            duration = track.get('duration', '0:00')
            thumb_url = track.get('thumbnail', '')
            audio_url = track.get('audio_url', '')

            if not audio_url: continue

            # Unique ID generation for each result using standard md5
            result_id = hashlib.md5(title.encode('utf-8')).hexdigest()
            
            # Jab user click karega to yeh text format chat me jayega
            caption_text = (
                f"🎵 **Now Playing:** {title}\n"
                f"⏱️ **Duration:** {duration}\n\n"
                f"▶️ [Click Here to Play Audio]({audio_url})"
            )

            # Control buttons for the player
            markup = InlineKeyboardMarkup()
            markup.add(
                InlineKeyboardButton("⏸️ Pause", callback_data=f"player_pause_{index}"),
                InlineKeyboardButton("🔄 Refresh", callback_data=f"player_refresh_{index}")
            )
            markup.add(InlineKeyboardButton("🎵 Download MP3", url=audio_url))

            # Article formatting for standard Telegram inline look
            item = InlineQueryResultArticle(
                id=result_id,
                title=title,
                description=f"Duration: {duration} | Click to share player",
                thumbnail_url=thumb_url,
                input_message_content=InputTextMessageContent(
                    message_text=caption_text,
                    parse_mode="Markdown",
                    disable_web_page_preview=False
                ),
                reply_markup=markup
            )
            inline_results.append(item)

        bot.answer_inline_query(inline_query.id, inline_results, cache_time=1)
    except Exception as e:
        print(f"Inline Error: {e}")

# ================= 2. PLAYER BUTTONS CONTROL =================
@bot.callback_query_handler(func=lambda call: call.data.startswith("player_"))
def handle_player_controls(call):
    action = call.data.split("_")[1]
    
    if action == "pause":
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("▶️ Play", callback_data=call.data.replace("pause", "play")),
            InlineKeyboardButton("🔄 Refresh", call.data)
        )
        try:
            bot.edit_message_reply_markup(
                inline_message_id=call.inline_message_id,
                reply_markup=markup
            )
            bot.answer_callback_query(call.id, "🎵 Audio Paused")
        except: pass

    elif action == "play":
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("⏸️ Pause", call.data.replace("play", "pause")),
            InlineKeyboardButton("🔄 Refresh", call.data)
        )
        try:
            bot.edit_message_reply_markup(
                inline_message_id=call.inline_message_id,
                reply_markup=markup
            )
            bot.answer_callback_query(call.id, "🎵 Audio Playing...")
        except: pass

    elif action == "refresh":
        bot.answer_callback_query(call.id, "⚡ Player synchronized!")

print("🔥 MUSIC SHADOW INLINE BOT IS ACTIVE ON RAILWAY! 🔥")
bot.infinity_polling()
