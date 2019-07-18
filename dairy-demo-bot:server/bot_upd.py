from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import telegram
import requests
import psycopg2
import datetime

def notify():
	bot = telegram.Bot(token='')	
	try:
	    connection = psycopg2.connect(user = "",
	                                  password = "",
	                                  host = "127.0.0.1",
	                                  port = "5432",
	                                  database = "dairy")
	    cursor = connection.cursor()
	    postgres_select_query = """SELECT * FROM users"""
	    cursor.execute(postgres_select_query)
	    rows = cursor.fetchall()
	    connection.commit()
	    for row in rows:
	    	bot.send_message(chat_id=int(row[0]), text='Не забудь сделать сегодня запись :)')
	except (Exception, psycopg2.Error) as error :
	    print ("Error while connecting to PostgreSQL", error)
	finally:
	        if(connection):
	            cursor.close()
	            connection.close()

def start(bot, update):
	chat_id = update.message.chat_id
	try:
	    connection = psycopg2.connect(user = "",
	                                  password = "",
	                                  host = "127.0.0.1",
	                                  port = "5432",
	                                  database = "dairy")
	    cursor = connection.cursor()
	    postgres_insert_query = """INSERT INTO users (chat_id) VALUES (%s) ON CONFLICT DO NOTHING"""
	    record_to_insert = (str(chat_id),)
	    cursor.execute(postgres_insert_query, record_to_insert)
	    connection.commit()
	    count = cursor.rowcount
	except (Exception, psycopg2.Error) as error :
	    print ("Error while connecting to PostgreSQL", error)
	finally:
	        if(connection):
	            cursor.close()
	            connection.close()
	bot.send_message(chat_id=chat_id, text='Привет!')

def save_emotion(bot, update):	
	currentDT = str(datetime.datetime.now())
	chat_id = update.callback_query.message.chat_id
	query = update.callback_query
	emotion = query.data
	query.edit_message_text(text='Запись сохранена')

	try:
	    connection = psycopg2.connect(user = "",
	                                  password = "",
	                                  host = "127.0.0.1",
	                                  port = "5432",
	                                  database = "dairy")
	    cursor = connection.cursor()
	    query = """SELECT * FROM emotions"""
	    cursor.execute(query)
	    connection.commit()
	    count = cursor.rowcount

	    query = """INSERT INTO emotions(entry_id, chat_id, datetimestamp, emotion) VALUES (%s, %s, %s, %s)"""
	    record_to_insert = (count+1, str(chat_id), currentDT, emotion)
	    cursor.execute(query, record_to_insert)
	    connection.commit()
	    count = cursor.rowcount

	except (Exception, psycopg2.Error) as error :
	    print ("Error while connecting to PostgreSQL", error)
	finally:
	        if(connection):
	            cursor.close()
	            connection.close()

def save_entry(bot, update):
	chat_id = update.message.chat_id

	try:
	    connection = psycopg2.connect(user = "",
	                                  password = "",
	                                  host = "127.0.0.1",
	                                  port = "5432",
	                                  database = "dairy")
	    cursor = connection.cursor()
	    query = """SELECT * FROM emotions"""
	    cursor.execute(query)
	    connection.commit()
	    count = cursor.rowcount
	except (Exception, psycopg2.Error) as error :
	    print ("Error while connecting to PostgreSQL", error)
	finally:
	        if(connection):
	            cursor.close()
	            connection.close()

	file = bot.getFile(update.message.voice.file_id)
	file.download('entries/' + str(count+1) + '.ogg')

	keyboard = [[InlineKeyboardButton("злость", callback_data='angry'),
                 InlineKeyboardButton("грусть", callback_data='sad')],
                [InlineKeyboardButton("радость", callback_data='happy')]]

	reply_markup = InlineKeyboardMarkup(keyboard)
	update.message.reply_text('Какая эмоция лучше всего описывает твое сегодняшнее состояние?', reply_markup=reply_markup)

def main():
	updater = Updater('')
	dp = updater.dispatcher
	dp.add_handler(CommandHandler('start', start))
	dp.add_handler(CommandHandler('help', start))
	dp.add_handler(MessageHandler(Filters.text, start))
	dp.add_handler(MessageHandler(Filters.voice, save_entry))
	dp.add_handler(CallbackQueryHandler(save_emotion))
	updater.start_polling()
	updater.idle()

if __name__ == '__main__':
    main()