from dotenv import load_dotenv
from threading import Timer
from telebot import types
import datetime
import requests
import sqlite3
import telebot
import time
import os

load_dotenv()
TOKEN = os.getenv('TOKEN')
bot = telebot.TeleBot(TOKEN)
day = False
week = False
month = False


def check_url(url):
    try:
        requests.get(url)
        return True, "Work"
    except:
        return False, "Doesn't work"


def user_create(id_user):
    with sqlite3.connect("db.db") as db:
        cursor = db.cursor()
        cursor.execute(f"""SELECT * FROM Users WHERE id_user = (?) """,
                       [id_user])
        data = cursor.fetchall()

        if len(data) == 0:
            cursor.execute("""SELECT * FROM Users""")
            id = len(cursor.fetchall())
            cursor.execute(f"INSERT INTO Users VALUES(?, ?, ?)",
                           [id, id_user, 0])


def db_create():
    with sqlite3.connect("db.db") as db:
        cursor = db.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS "Urls" (
                            "id"	INTEGER,
                            "id_user"	INTEGER,
                            "url"	TEXT,
                            PRIMARY KEY("id")
                        )""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS "Users" (
                        "id"	INTEGER,
                        "id_user"	INTEGER,
                        "id_time_check"	INTEGER,
                        PRIMARY KEY("id")
                    )""")


@bot.message_handler(commands=["start"])
def start(message):
    db_create()
    user_create(message.chat.id)
    Markup = types.InlineKeyboardMarkup()
    Markup.add(types.InlineKeyboardButton("Add url", callback_data="add"),
               types.InlineKeyboardButton("Setting", callback_data="setting_0"))
    bot.send_message(message.chat.id,
                     f"Hi {message.from_user.first_name} this bot will ping sites which you will indicate",
                     reply_markup=Markup)


def add_url(message):
    have_url = True
    url = message.text

    with sqlite3.connect("db.db") as db:
        cursor = db.cursor()
        cursor.execute(f"""SELECT * FROM Urls WHERE id_user = (?) AND url = (?)""", [message.chat.id, url])
        data = cursor.fetchall()

        if len(data) == 0:
            have_url = False

    if url != "exit" and have_url == False:
        try:
            requests.get(url)
            with sqlite3.connect("db.db") as db:
                cursor = db.cursor()
                cursor.execute(f"""SELECT * FROM Urls WHERE id_user = (?) AND url = (?)""",
                               [message.chat.id, url])
                data = cursor.fetchall()
                print(data)
                if len(data) == 0:
                    cursor.execute("""SELECT * FROM Urls""")
                    id = len(cursor.fetchall())

                    cursor.execute(f"INSERT INTO Urls VALUES(?, ?, ?)",
                                   [id, message.chat.id, url])
                    print("aa")

                bot.send_message(message.chat.id, f"The data is recorded\nStatus:{check_url(url)[1]}")
            start(message)

        except:
            bot.send_message(message.chat.id, "It's not a url")
            mes = bot.send_message(message.chat.id, "Send url(write exit for exit)")
            bot.register_next_step_handler(mes, add_url)
    elif have_url == True:
        bot.send_message(message.chat.id, "Such a url is already")
        mes = bot.send_message(message.chat.id, "Send url(write exit for exit)")
        bot.register_next_step_handler(mes, add_url)

    else:
        bot.send_message(message.chat.id, "Out")
        start(message)


def delete_url(message):
    url = message.text

    with sqlite3.connect("db.db") as db:
        cursor = db.cursor()
        cursor.execute(f"""SELECT * FROM Urls WHERE id_user = (?) AND url = (?)""", [message.chat.id, url])
        data = cursor.fetchall()
        if len(data) != 0 and url != "exit":
            cursor.execute("""DELETE FROM Urls WHERE id_user = (?) AND url = (?)""", [message.chat.id, url])
            bot.send_message(message.chat.id, "Removed")
            start(message)
        elif url != "exit":
            bot.send_message(message.chat.id, "There is no such url")
            mes = bot.send_message(message.chat.id, "Send the url that you want to delete(write exit for exit)")
            bot.register_next_step_handler(mes, delete_url)
        else:
            bot.send_message(message.chat.id, "Out")
            start(message)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    data_list = call.data.split("_")

    if data_list[0] == "add":

        mes = bot.send_message(call.message.chat.id, "Send url(write exit for exit)")
        bot.register_next_step_handler(mes, add_url)
    elif data_list[0] == "setting":
        if data_list[1] == "0":
            Markup = types.InlineKeyboardMarkup()
            Markup.add(types.InlineKeyboardButton("Add send time", callback_data="setting_add"),
                       types.InlineKeyboardButton("Delete url", callback_data="setting_delete"))
            Markup.add(types.InlineKeyboardButton("Return", callback_data="return"))
            bot.send_message(call.message.chat.id, "Select Settings", reply_markup=Markup)
        elif data_list[1] == "add":
            Markup = types.InlineKeyboardMarkup()
            Markup.add(types.InlineKeyboardButton("Every day", callback_data="setting_day"),
                       types.InlineKeyboardButton("Every week", callback_data="setting_week"),
                       types.InlineKeyboardButton("Every month", callback_data="setting_month"))
            Markup.add(types.InlineKeyboardButton("Never", callback_data="setting_never"))
            bot.send_message(call.message.chat.id, "Choose the time when the bot sends a message that it works",
                             reply_markup=Markup)
        elif data_list[1] == "day":
            with sqlite3.connect("db.db") as db:
                cursor = db.cursor()
                cursor.execute("""UPDATE Users SET id_time_check = 1 WHERE id_user = (?)""", [call.message.chat.id])
                bot.send_message(call.message.chat.id, "Selected")
                start(call.message)
        elif data_list[1] == "week":
            with sqlite3.connect("db.db") as db:
                cursor = db.cursor()
                cursor.execute("""UPDATE Users SET id_time_check = 2 WHERE id_user = (?)""", [call.message.chat.id])
                bot.send_message(call.message.chat.id, "Selected")
                start(call.message)
        elif data_list[1] == "month":
            with sqlite3.connect("db.db") as db:
                cursor = db.cursor()
                cursor.execute("""UPDATE Users SET id_time_check = 3 WHERE id_user = (?)""", [call.message.chat.id])
                bot.send_message(call.message.chat.id, "Selected")
                start(call.message)
        elif data_list[1] == "never":
            with sqlite3.connect("db.db") as db:
                cursor = db.cursor()
                cursor.execute("""UPDATE Users SET id_time_check = 0 WHERE id_user = (?)""", [call.message.chat.id])
                bot.send_message(call.message.chat.id, "Selected")
                start(call.message)
        elif data_list[1] == "delete":
            with sqlite3.connect("db.db") as db:
                cursor = db.cursor()
                cursor.execute(f"""SELECT url FROM Urls WHERE id_user = (?)""", [call.message.chat.id])
                data = cursor.fetchall()
                text = ""
                for i in range(len(data)):
                    text += f"{i + 1}. {data[i][0]}\n"
                if text == "":
                    text = "You don't follow the urls"
                    bot.send_message(call.message.chat.id, text)
                    start(call.message)
                else:
                    bot.send_message(call.message.chat.id, text)
                    mes = bot.send_message(call.message.chat.id,
                                           "Send the url that you want to delete(write exit for exit) ")
                    bot.register_next_step_handler(mes, delete_url)
    elif data_list[0] == "return":
        start(call.message)


def loop():
    global day, week, month
    while True:
        with sqlite3.connect("db.db") as db:
            cursor = db.cursor()
            cursor.execute("""SELECT id FROM Urls""")
            ids = cursor.fetchall()
            for i in ids:
                id = i[0]
                cursor.execute("""SELECT url FROM Urls WHERE id = (?)""", [id])
                url = cursor.fetchall()[0][0]
                if not check_url(url)[0]:
                    cursor.execute("""SELECT id_user FROM Urls WHERE id = (?)""", [id])
                    id_user = cursor.fetchall()[0][0]
                    bot.send_message(id_user, f"Url {url} isn't working")
                    cursor.execute("""DELETE FROM Urls WHERE id = (?)""", [id])

            if datetime.datetime.today().hour == 12 and not day:
                cursor.execute(f"""SELECT id_user FROM Users WHERE id_time_check = 1""")
                data = cursor.fetchall()
                for i in data:
                    bot.send_message(i[0], "I work")

                day = True
            if datetime.datetime.today().hour == 12 and datetime.datetime.weekday(
                    datetime.datetime.now()) == 0 and not week:
                cursor.execute(f"""SELECT id_user FROM Users WHERE id_time_check = 2""")
                data = cursor.fetchall()
                for i in data:
                    bot.send_message(i[0], "I work")
                week = True
            if datetime.datetime.today().hour == 12 and int(datetime.datetime.today().day) == 1 and not month:
                cursor.execute(f"""SELECT id_user FROM Users WHERE id_time_check = 3""")
                data = cursor.fetchall()
                for i in data:
                    bot.send_message(i[0], "I work")
                month = True
            if datetime.datetime.today().hour == 13:
                day = False
                week = False
                month = False
            time.sleep(1)


if __name__ == '__main__':
    t = Timer(0, loop)
    t.start()
    bot.infinity_polling()
