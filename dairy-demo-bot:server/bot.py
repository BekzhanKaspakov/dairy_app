# from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
# import telegram
import uuid
import requests
import psycopg2
import speech_recognition as sr
from textblob import TextBlob
import subprocess
import os
from rake_nltk import Rake
import pandas as pd
import librosa
import glob
import keras
import numpy as np
from keras.models import model_from_json
import datetime
import socket
from _thread import start_new_thread
import threading
HOST = '172.20.10.2'  # Standard loopback interface address (localhost)
PORT = 65434        # Port to listen on (non-privileged ports are > 1023)

emotions = ['злой', 'спокойный', 'напуганный', 'счастливый', 'грустный',
            'злой', 'спокойный', 'напуганный', 'счастливый', 'грустный']


# def notify():
#     # bot = telegram.Bot(token='715725736:AAEYbFVMN85_aPKeKFDSzWulHjq1J_X8hSc')

#     try:
#         connection = psycopg2.connect(user="bekzhankaspakov",
#                                       password="7426",
#                                       host="127.0.0.1",
#                                       port="5432",
#                                       database="dairy")
#         cursor = connection.cursor()
#         postgres_select_query = """SELECT * FROM users"""
#         cursor.execute(postgres_select_query)
#         rows = cursor.fetchall()
#         connection.commit()

#         for row in rows:
#             bot.send_message(chat_id=int(
#                 row[0]), text='Hey! Please don\'t forget to record your entry today.')

#     except (Exception, psycopg2.Error) as error:
#         print("Error while connecting to PostgreSQL", error)

#     finally:
#         if(connection):
#             cursor.close()
#             connection.close()
#             print("PostgreSQL connection is closed")


def start(c, incoming_message):
    # chat_id = update.message.chat_id

    if incoming_message[1] == 'NoId':
        newUserId = uuid.uuid4()
        chat_id = str(newUserId)
        c.send(('USERID:' + chat_id).encode('utf-8'))
        data = c.recv(1024)
        if not data:
            print('Bye')
            return

        data = data.decode('utf-8')
        if data == 'OK':
            print('NEW USER RECEIVED HIS ID')
        try:
            connection = psycopg2.connect(user="bekzhankaspakov",
                                        password="7426",
                                        host="127.0.0.1",
                                        port="5432",
                                        database="dairy")
            cursor = connection.cursor()
            postgres_insert_query = """INSERT INTO users (chat_id) VALUES (%s) ON CONFLICT DO NOTHING"""
            record_to_insert = (str(chat_id),)
            cursor.execute(postgres_insert_query, record_to_insert)
            connection.commit()
            count = cursor.rowcount

        except (Exception, psycopg2.Error) as error:
            print("Error while connecting to PostgreSQL", error)

        finally:
            if(connection):
                cursor.close()
                connection.close()
                print("PostgreSQL connection is closed")
    else:
        chat_id = incoming_message[1] 

    # bot.send_message(
    #     chat_id=chat_id, text='Hi! I am here to support your mental health and well-being. Please record a short entry about your feelings.')
    c.send('Hi! I am here to support your mental health and well-being. Please record a short entry about your feelings.'.encode('utf-8'))

def extract_keywords(textentry):
    r = Rake(language="russian")
    r.extract_keywords_from_text(textentry)
    keywords = r.get_ranked_phrases()
    kwlist = ''
    for keyword in keywords:
        kwlist += keyword + ', '
    return kwlist


def recognize_emotion(fname):

    opt = keras.optimizers.rmsprop(lr=0.00001, decay=1e-6)

    json_file = open('model.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    loaded_model.load_weights("Emotion_Voice_Detection_Model.h5")

    X, sample_rate = librosa.load(
        fname, res_type='kaiser_fast', duration=2.5, sr=22050*2, offset=0.5)
    sample_rate = np.array(sample_rate)
    mfccs = np.mean(librosa.feature.mfcc(
        y=X, sr=sample_rate, n_mfcc=13), axis=0)
    featurelive = mfccs
    livedf2 = featurelive
    livedf2 = pd.DataFrame(data=livedf2)
    livedf2 = livedf2.stack().to_frame().T
    twodim = np.expand_dims(livedf2, axis=2)

    livepreds = loaded_model.predict(twodim, batch_size=32, verbose=1)
    livepreds1 = livepreds.argmax(axis=1)
    liveabc = livepreds1.astype(int).flatten()
    emotion = emotions[liveabc[0]]

    return emotion


def analyze(c, incoming_message):

    chat_id = incoming_message[1]
    currentDT = str(datetime.datetime.now())

    r = sr.Recognizer()
    src_filename = 'voice_' + chat_id + '.m4a'
    dest_filename = 'entry_' + chat_id + '.wav'
    with open(os.devnull, 'w') as devnull:
        process = subprocess.run(['ffmpeg', '-i', src_filename, dest_filename],stdout=devnull, stderr=subprocess.STDOUT)
    if process.returncode != 0:
        raise Exception("Something went wrong")
    audioentry = sr.AudioFile(dest_filename)
    with audioentry as source:
        audio = r.record(source)
    textentry = r.recognize_google(audio, language="ru_RU")
    print(textentry)

    keywords = extract_keywords(textentry)
    emotion = recognize_emotion(dest_filename)
    print(keywords)
    print(emotion)

    try:
        connection = psycopg2.connect(user="bekzhankaspakov",
                                      password="7426",
                                      host="127.0.0.1",
                                      port="5432",
                                      database="dairy")
        cursor = connection.cursor()
        postgres_insert_query = """INSERT INTO analysis (chat_id, datetimestamp, keywords, emotion) VALUES (%s, %s, %s, %s)"""
        record_to_insert = (chat_id, currentDT, keywords, emotion)
        cursor.execute(postgres_insert_query, record_to_insert)
        connection.commit()
        count = cursor.rowcount

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)

    finally:
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

    # bot.send_message(chat_id=chat_id, text=textentry)
    c.send(textentry.encode('utf-8'))
    # bot.send_message(chat_id=chat_id, text='Кажется ты сегодня ' + emotion)
    c.send(('Кажется ты сегодня ' + emotion).encode('utf-8'))
    os.remove(src_filename)
    os.remove(dest_filename)

def receive_audio(c, incoming_message):
    c.send('OKAUDIO'.encode('utf-8'))
    f = open('voice_' + incoming_message[1] + '.m4a', 'wb')
    total = 0
    while total < int(incoming_message[2]):
        l = c.recv(1024)
        f.write(l)
        total = total + len(l)
    print(total)
    # c.send('Done'.encode('utf-8'))
    old_file_position = f.tell()
    f.seek(0, os.SEEK_END)
    size = f.tell()
    f.seek(old_file_position, os.SEEK_SET)
    print('received:' + str(size))
    f.close()
    print("Done Receiving")
    # c.close()

    analyze(c, incoming_message)

def threaded(c):
    while True:
        # data received from client
        data = c.recv(1024)
        if not data:
            print('Bye')
            return

        string_data = data.decode('utf-8')
        incoming_message = string_data.split(':')
        # print(string_data[0:5])
        print(incoming_message[0])
        if incoming_message[0] == 'AUDIO':
            receive_audio(c, incoming_message)
        elif incoming_message[0] == 'START':
            start(c, incoming_message)
        else:
            c.send('Hi! I am here to support your mental health and well-being. Please record a short entry about your feelings.'.encode('utf-8'))

    return


def main():
        # TODO: Listen to incoming connections
        # TODO: Identify USER (i.e. how to store user identity in database)
        # TODO: Find out how to send notification messages to users
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    print("socket binded to port", PORT)

    # put the socket into listening mode
    s.listen(10)
    print("socket is listening")

    # a forever loop until client wants to exit
    while True:

        # establish connection with client
        c, addr = s.accept()

        # lock acquired by client
        # print_lock.acquire()
        print('Connection from :', addr[0], ':', addr[1])

        # Start a new thread and return its identifier
        start_new_thread(threaded, (c,))
    s.close()

    # updater = Updater('715725736:AAEYbFVMN85_aPKeKFDSzWulHjq1J_X8hSc')
    # dp = updater.dispatcher
    # dp.add_handler(CommandHandler('start', start))
    # dp.add_handler(CommandHandler('help', start))
    # dp.add_handler(CommandHandler('summary', get_summary))
    # dp.add_handler(CommandHandler('feedback', get_feedback))
    # dp.add_handler(MessageHandler(Filters.text, start))
    # dp.add_handler(MessageHandler(Filters.voice, analyze))
    # updater.start_polling()
    # updater.idle()
    # reverse a port on your computer
    # in our case it is 12345 but it
    # can be anything


if __name__ == '__main__':
    main()
