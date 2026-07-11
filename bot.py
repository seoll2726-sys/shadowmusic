import telebot
import requests
import os

TOKEN = os.getenv('BOT_TOKEN', '8643094183:AAEwi64PymNJ370hHFY9RF66b07bEzFcTe8')
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "🎵 **Music Bot is Live!**\n\nKisi bhi chat me ja kar type karo:\n`@musicshadow0_bot <gaane ka naam>`", parse_mode="Markdown")

@bot.inline_handler(func=lambda query: len(query.query) > 0)
def search_music(inline_query):
    try:
        query = inline_query.query.strip()
        # iTunes API - Duniya ki sabse stable API, IP block nahi karegi aur fast chalegi
        url = f"https://itunes.apple.com/search?term={requests.utils.quote(query)}&entity=song&limit=5"
        response = requests.get(url, timeout=10).json()
        
        results = []
        for index, track in enumerate(response.get('results', [])):
            audio_url = track.get('previewUrl')
            if not audio_url:
                continue
                
            # Telegram ka asli Audio Player generate karna
            item = telebot.types.InlineQueryResultAudio(
                id=str(index),
                audio_url=audio_url,
                title=track.get('trackName', 'Unknown Song'),
                performer=track.get('artistName', 'Unknown Artist')
            )
            results.append(item)
            
        if results:
            bot.answer_inline_query(inline_query.id, results, cache_time=1)
        else:
            bot.answer_inline_query(inline_query.id, [], cache_time=1)
            
    except Exception as e:
        print(f"Error: {e}")
        try:
            bot.answer_inline_query(inline_query.id, [], cache_time=1)
        except: pass

print("✅ BOT SUCCESSFULLY RUNNING!")
bot.infinity_polling()
