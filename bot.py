import telebot
import requests
import os
import hashlib
from telebot.types import InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton

# Config
TOKEN = os.getenv('BOT_TOKEN', '8643094183:AAEwi64PymNJ370hHFY9RF66b07bEzFcTe8')
bot = telebot.TeleBot(TOKEN)
BOT_USERNAME = 'musicshadow0_bot'

@bot.message_handler(commands=['start'])
def welcome(message):
    text = (
        "🎵 **Welcome to Music Shadow Player Bot!**\n\n"
        f"Kisi bhi chat me type karein: `@{BOT_USERNAME} <gaane ka naam>`\n"
        "Aur thoda rukiye, automatic list khul jayegi!"
    )
    bot.reply_to(message, text, parse_mode="Markdown")

# ================= INLINE SEARCH SYSTEM =================
@bot.inline_handler(func=lambda query: len(query.query) > 0)
def query_text(inline_query):
    try:
        user_query = inline_query.query.strip()
        
        # New Super Stable Alternative API
        api_url = f"https://scrapers.orionray.workers.dev/youtube/search?q={requests.utils.quote(user_query)}"
        response = requests.get(api_url, timeout=10).json()
        
        # Agar list standard format me na ho toh extract karein
        results = response.get('results', response if isinstance(response, list) else [])

        inline_results = []
        for index, track in enumerate(results[:5]):
            title = track.get('title', 'Unknown Track')
            duration = track.get('duration', '3:30')
            thumb_url = track.get('thumbnail', track.get('image', ''))
            
            # Streaming/Download link generation
            video_id = track.get('id', '')
            audio_url = track.get('audio_url', f"https://api.vevioz.com/download/mp3/{video_id}" if video_id else "")

            if not audio_url:
                continue

            result_id = hashlib.md5(title.encode('utf-8')).hexdigest()
            
            caption_text = (
                f"🎵 **Now Playing:** {title}\n"
                f"⏱️ **Duration:** {duration}\n\n"
                f"▶️ [Click Here to Play / Download Audio]({audio_url})"
            )

            markup = InlineKeyboardMarkup()
            markup.add(
                InlineKeyboardButton("⏸️ Pause", callback_data=f"player_pause_{index}"),
                InlineKeyboardButton("🔄 Refresh", callback_data=f"player_refresh_{index}")
            )
            markup.add(InlineKeyboardButton("🎵 Open Audio File", url=audio_url))

            item = InlineQueryResultArticle(
                id=result_id,
                title=title,
                description=f"Duration: {duration} | Tap to share",
                thumbnail_url=thumb_url if thumb_url else None,
                input_message_content=InputTextMessageContent(
                    message_text=caption_text,
                    parse_mode="Markdown",
                    disable_web_page_preview=False
                ),
                reply_markup=markup
            )
            inline_results.append(item)

        if inline_results:
            bot.answer_inline_query(inline_query.id, inline_results, cache_time=1)
        else:
            # Fallback agar kuch na mile
            print("No streamable results found.")
    except Exception as e:
        print(f"Inline Error Log: {e}")

# ================= PLAYER CONTROLS =================
@bot.callback_query_handler(func=lambda call: call.data.startswith("player_"))
def handle_player_controls(call):
    action = call.data.split("_")[1]
    if action in ["pause", "play"]:
        next_action = "play" if action == "pause" else "pause"
        btn_text = "▶️ Play" if action == "pause" else "⏸️ Pause"
        
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton(btn_text, callback_data=call.data.replace(action, next_action)),
            InlineKeyboardButton("🔄 Refresh", call.data)
        )
        try:
            bot.edit_message_reply_markup(inline_message_id=call.inline_message_id, reply_markup=markup)
            bot.answer_callback_query(call.id, f"🎵 Audio {action.capitalize()}ed")
        except: pass
    elif action == "refresh":
        bot.answer_callback_query(call.id, "⚡ Synced!")

print("🔥 NEW FAST API BOT IS ACTIVE ON RAILWAY! 🔥")
bot.infinity_polling()
