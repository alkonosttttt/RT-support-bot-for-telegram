import speech_recognition as sr
import telebot
from telebot import types
import subprocess
import os
import sqlite3

token = "1460700266:AAEKzHRwqR0WExJKOG8KUGD_86GvvXK9hI8"
bot = telebot.TeleBot(token)


def сheck_audio(user_id):
    src_filename = '1.ogg'
    dest_filename = 'output.wav'

    process = subprocess.run(['ffmpeg', '-i', src_filename, dest_filename])
    if process.returncode != 0:
        raise Exception("Что-то пошло не так")
    rec = sr.Recognizer()
    sample_audio = sr.AudioFile('output.wav')
    with sample_audio as audio_file:
        audio_content = rec.record(audio_file)
        txt = rec.recognize_google(audio_content, language = "ru-RU")
    bot.send_message(user_id,f"Ищем подходящие варианты.\nВаш запрос:\n{txt.lower()}")
    os.remove(src_filename)
    os.remove(dest_filename)
    word_list = txt.split(" ")
    con = sqlite3.connect("db.sqlite3")
    cur = con.cursor()
    cur.execute("SELECT * FROM bot_questions")
    questions = cur.fetchall()
    cur.close()
    con.close()
    count = 0
    for quest in questions:
        n = 0
        i = 0
        tags = quest[4].split(":")
        txt = txt.lower()
        txt = txt.replace("ё","е")
        for tag in tags:
            if txt in tag:
                n +=1
            for word in word_list:
                if word in tag:
                    i +=1
        if i > 4 or n > 0:
            count +=1
            try:
                bot.send_message(user_id,f"Возможно вам подойдет данное решение:\n{quest[3]}",parse_mode = 'html')
            except Exception as e:
                print(str(e))
    if count > 0:
        action = types.InlineKeyboardMarkup(row_width = 1)
        b = types.InlineKeyboardButton(text = "Связаться с оператором", callback_data = "manage")
        action.add(b)
        bot.send_message(user_id,"Не смогли найти ответ на свой вопрос?",reply_markup = action)

    else:
        action = types.InlineKeyboardMarkup(row_width = 1)
        b = types.InlineKeyboardButton(text = "Связаться с оператором", callback_data = "manage")
        action.add(b)
        bot.send_message(user_id,"Не удалось найти информацию в нашей базе знаний",reply_markup = action)



def check_msg(user_id,txt):
    bot.send_message(user_id,f"Ищем подходящие варианты.\nВаш запрос:\n{txt.lower()}")
    word_list = txt.split(" ")
    con = sqlite3.connect("db.sqlite3")
    cur = con.cursor()
    cur.execute("SELECT * FROM bot_questions")
    questions = cur.fetchall()
    cur.close()
    con.close()
    count = 0
    for quest in questions:
        n = 0
        i = 0
        tags = quest[4].split(":")
        for tag in tags:
            if txt.lower() in tag:
                n +=1
            for word in word_list:
                if word in tag:
                    i +=1
        if i > 4 or n > 0:
            count +=1
            try:
                bot.send_message(user_id,f"Возможно вам подойдет данное решение:\n{quest[3]}",parse_mode = 'html')
            except Exception as e:
                print(str(e))

    if count > 0:
        action = types.InlineKeyboardMarkup(row_width = 1)
        b = types.InlineKeyboardButton(text = "Связаться с оператором", callback_data = "manage")
        action.add(b)
        bot.send_message(user_id,"Не смогли найти ответ на свой вопрос?",reply_markup = action)

    else:
        action = types.InlineKeyboardMarkup(row_width = 1)
        b = types.InlineKeyboardButton(text = "Связаться с оператором", callback_data = "manage")
        action.add(b)
        bot.send_message(user_id,"Не удалось найти информацию в нашей базе знаний",reply_markup = action)
