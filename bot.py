import telebot
import os
import hashlib
from youtube_search import YoutubeSearch
from telebot.types import InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv('BOT_TOKEN', '8643094183:AAEwi64PymNJ370hHFY9RF66b07bEzFcTe8')
bot = telebot.TeleBot(TOKEN)
BOT_USERNAME = 'musicshadow0_bot'

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, f"🎵 **Music Shadow Bot Online!**\n\nType: `@{BOT_USERNAME} gaane ka naam`", parse_mode="Markdown")

@bot.inline_handler(func=lambda query: len(query.query) > 0)
def query_text(inline_query):
    try:
        user_query = inline_query.query.strip()
        
        # Direct Python Scraper (No External API Dependency)
        results = YoutubeSearch(user_query, max_results=5).to_dict()

        inline_results = []
        for index, track in enumerate(results):
            title = track.get('title', 'Unknown Track')
            duration = track.get('duration', '3:30')
            thumb_url = track.get('thumbnails', [''])[0]
            v_id = track.get('id', '')
            
            if not v_id: continue
            
            audio_url = f"https://api.vevioz.com/download/mp3/{v_id}"
            result_id = hashlib.md5(f"{v_id}".encode('utf-8')).hexdigest()
            
            caption_text = (
                f"🎵 **Now Playing:** {title}\n"
                f"⏱️ **Duration:** {duration}\n\n"
                f"▶️ [Click to Stream / Download]({audio_url})"
            )

            markup = InlineKeyboardMarkup()
            markup.add(
                InlineKeyboardButton("⏸️ Pause", callback_data=f"player_pause_{index}"),
                InlineKeyboardButton("🔄 Sync", callback_data=f"player_refresh_{index}")
            )
            markup.add(InlineKeyboardButton("🎵 Download MP3", url=audio_url))

            item = InlineQueryResultArticle(
                id=result_id,
                title=title,
                description=f"Duration: {duration} | Share Player",
                thumbnail_url=thumb_url if thumb_url else None,
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
        print(f"Error: {e}")
        try: bot.answer_inline_query(inline_query.id, [], cache_time=1)
        except: pass

@bot.callback_query_handler(func=lambda call: call.data.startswith("player_"))
def handle_player_controls(call):
    action = call.data.split("_")[1]
    if action in ["pause", "play"]:
        next_act = "play" if action == "pause" else "pause"
        txt = "▶️ Play" if action == "pause" else "⏸️ Pause"
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton(txt, callback_data=call.data.replace(action, next_act)),
            InlineKeyboardButton("🔄 Sync", call.data)
        )
        try: bot.edit_message_reply_markup(inline_message_id=call.inline_message_id, reply_markup=markup)
        except: pass

print("🔥 INDEPENDENT MUSIC BOT RUNNING! 🔥")
bot.infinity_polling()
