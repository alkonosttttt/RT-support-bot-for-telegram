import telebot
from telebot import types
import sqlite3
import threading
import speech_recognition as sr
import requests
import subprocess
import os


token = "1460700266:AAEKzHRwqR0WExJKOG8KUGD_86GvvXK9hI8"
bot = telebot.TeleBot(token)

# получаем список всех услуг
def get_Service():
    con = sqlite3.connect("db.sqlite3")
    cur = con.cursor()
    cur.execute("SELECT DISTINCT service FROM bot_questions")
    service = cur.fetchall()
    cur.close()
    con.close()
    return service

# /admin
@bot.message_handler(commands = ["admin"])
def admin(message):
    pass

# /start
@bot.message_handler(commands = ["start"])
def start(message):
    id = str(message.from_user.id)
    menu = types.ReplyKeyboardMarkup(True,False)
    menu.row("⁉️ Задать вопрос")
    bot.send_message(id,"Добро пожаловать!\nНаш бот готов ответить на все ваши вопросы.",reply_markup = menu)

# Обработка сообщений от пользователя
@bot.message_handler(content_types = ["text","voice"])
def body(message):
    if message.voice:
        id = str(message.from_user.id)
        file_info = bot.get_file(message.voice.file_id)
        file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(token, file_info.file_path))

        with open('1.ogg','wb') as f:
            f.write(file.content)
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
        bot.send_message(id,txt.lower())
        os.remove(src_filename)
        os.remove(dest_filename)

    if message.text:
        if message.text == "⁉️ Задать вопрос":
            menu = types.InlineKeyboardMarkup(row_width = 1)
            servs = get_Service()
            for serv in servs:
                b = types.InlineKeyboardButton(text = f"{serv[0]}", callback_data = f"service{serv[0]}")
                menu.add(b)
            bot.send_message(message.chat.id,"Выберите услугу , по которой у вас есть вопрос:",reply_markup = menu)



@bot.callback_query_handler(func=lambda c: True)
def inline(c):
    if c.data.startswith("service"):
        service = c.data.replace("service","")
        con = sqlite3.connect("db.sqlite3")
        cur = con.cursor()
        cur.execute("SELECT DISTINCT category_id FROM bot_questions WHERE service = ?",(service,))
        cats_id = cur.fetchall()
        cur.close()
        con.close()
        menu = types.InlineKeyboardMarkup(row_width = 1)
        i = 0
        for cat_id in cats_id:
            con = sqlite3.connect("db.sqlite3")
            cur = con.cursor()
            cur.execute("SELECT name FROM bot_categorys WHERE id = ?",(cat_id[0],))
            cat = cur.fetchone()
            cur.close()
            con.close()
            b = types.InlineKeyboardButton(text = f"{cat[0]}", callback_data = f"category{cat_id[0]}")
            menu.add(b)
            i+=1
        bot.send_message(c.message.chat.id,"Выберите категорию:",reply_markup = menu)

    elif c.data.startswith("category"):
        category = c.data.replace("category","")
        con = sqlite3.connect("db.sqlite3")
        cur = con.cursor()
        cur.execute("SELECT subcategory , id FROM bot_questions WHERE category_id = ?",(int(category),))
        cats = cur.fetchall()
        cur.close()
        con.close()
        menu = types.InlineKeyboardMarkup(row_width = 1)
        for cat in cats:
            if cat[0] != None:
                con = sqlite3.connect("db.sqlite3")
                cur = con.cursor()
                cur.execute("SELECT answere FROM bot_categorys WHERE id = ?",(category,))
                ans = cur.fetchone()
                cur.close()
                con.close()
                b = types.InlineKeyboardButton(text = f"{cat[0]}", callback_data = f"subcategory{cat[1]}")
                menu.add(b)
                bot.send_message(c.message.chat.id,f"{ans[0]}",reply_markup = menu)
            else:
                con = sqlite3.connect("db.sqlite3")
                cur = con.cursor()
                cur.execute("SELECT answere FROM bot_questions WHERE id = ?",(cat[1],))
                cat = cur.fetcall()
                cur.close()
                con.close()
                bot.send_message(c.message.chat.id,f"{cat[0]}")
    elif c.data.startswith("subcategory"):
        sub = c.data.replace("subcategory","")
        con = sqlite3.connect("db.sqlite3")
        cur = con.cursor()
        cur.execute("SELECT answere FROM bot_questions WHERE id = ?",(int(sub),))
        cats = cur.fetchone()
        cur.close()
        con.close()
        bot.send_message(c.message.chat.id,f"{cats[0]}")




bot.skip_pending = True
bot.polling(none_stop=True, interval=0)


# https://github.com/alkonosttttt
# https://github.com/nicstim
