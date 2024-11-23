#импортируем модули
import telebot
import sqlite3
from dotenv import load_dotenv
import os
#задаю глобальные переменные
load_dotenv()
bot = telebot.TeleBot(os.getenv('TOKEN'))
name = None
students_counter = 0

#обработка стартового сообщения,начало программы
@bot.message_handler(commands=['start'])
def start(message):
    markup=telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1=telebot.types.KeyboardButton("Абитуриент")
    item2=telebot.types.KeyboardButton('Студент')
    markup.add(item1,item2)
    bot.send_message(message.chat.id,'Здравствуй, настоящий или будущий студент ИКТИБа, прежде чем раскрыть все тайны и загадки нашего института, пожалуйста, укажи, кем ты являешься:',reply_markup=markup)

#ветвление на два клиента (абитуриент <=> студент)
@bot.message_handler(content_types='text')
def message_reply(message):
    #если выбран абитуриент
    if message.text=="Абитуриент":
        bot.send_message(message.chat.id, 'Добро пожаловать!Как дела?',reply_markup=telebot.types.ReplyKeyboardRemove())
        def user_list(message):
            #список всех студентов из БД
            markup = telebot.types.InlineKeyboardMarkup()
            markup.add(telebot.types.InlineKeyboardButton('Список студентов по разным вопросам', callback_data='users'))
            bot.send_message(message.chat.id, 'Введите номер студента,к которому хотите обратиться', reply_markup=markup)
            bot.register_next_step_handler(message, notification)
        bot.register_next_step_handler(message,user_list)
        def notification(message):
            #уведомление студета о нахождении абитуриента
            student_number= message.text.strip()
            info = ''
            conn = sqlite3.connect('base.sql')
            cur = conn.cursor()
            cur.execute("SELECT * FROM users")
            users = cur.fetchall()
            for el in users:
                info += f'number{el[5]} id:{el[4]}\n'
            favid = ''
            #обработка БД как строки и поиск ID
            for i in range(info.find("number" + str(student_number)) + 11, len(info)):
                if info[i].isdigit():
                    favid += info[i]
                else:
                    break
            bot.send_message(message.chat.id,'Уведомление отправлену выбранному студенту \n Он свяжется с вами в близжайшее время')
            bot.send_message(chat_id=int(favid),text = f'Вам нашёлся абитуриент - {message.from_user.first_name} : @{message.from_user.username} \n Cвяжитесь с ним по нику')
    #если выбран студент
    if message.text == "Студент":
        #регстрация в БД
        studentid = message.from_user.id
        bot.send_message(message.chat.id, 'Введите свое имя', reply_markup=telebot.types.ReplyKeyboardRemove())
        conn = sqlite3.connect('base.sql')
        cur = conn.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS users (id int auto_increment primary key,name varchar(50),contact varchar(50),question varchar(50),studentid varchar(50),number varchar(50) ) ')
        cur.execute("SELECT * FROM users")
        users = cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()
        def user_name(message):
            global name
            name = message.text.strip()
            bot.send_message(message.chat.id, 'Введите названия тем,в которых можете помочь')
            bot.register_next_step_handler(message, user_que)
        bot.register_next_step_handler(message, user_name)

        def user_que(message):
            global question
            question = message.text.strip()
            bot.send_message(message.chat.id, 'Введите данные для связи с вами ')
            bot.register_next_step_handler(message, user_contact)

        def user_contact(message):
            global students_counter
            contact= message.text.strip()
            conn = sqlite3.connect('base.sql')
            cur = conn.cursor()
            #Добавление всех значений в БД
            students_counter +=1
            cur.execute("INSERT INTO users (name,contact,question,studentid,number) VALUES('%s','%s','%s','%s','%s')" % (name, contact,question,studentid,students_counter))
            conn.commit()
            cur.close()
            conn.close()
            bot.send_message(message.chat.id, 'Регистрация успешно закончена \n \n Спасибо за участие в проекте \n Мы уведомим вас, когда абитуриент заинтересуется темой, в которой вы разбираетесь ')
#возврат БД при запросе
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    conn = sqlite3.connect('base.sql')
    cur = conn.cursor()
    cur.execute("SELECT * FROM users")
    users = cur.fetchall()
    #запись БД как строки
    info = ''
    for el in users:
        info += f'№:{el[5]}, {el[1]}, Контакт: {el[2]} , может помочь с: {el[3]} \n'
    cur.close()
    conn.close()
    bot.send_message(call.message.chat.id, info)

#бесконечный цикл для бота
bot.infinity_polling()
