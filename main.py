from telebot import types, custom_filters
from telebot.handler_backends import State, StatesGroup #States
from telebot.storage import StateMemoryStorage
import requests
import json
import telebot
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


class States(StatesGroup):

    s_start = State()
    s_experience = State()
    s_schedule = State()
    s_data = State()
    s_salary = State()
    s_city = State()
    s_vacancy = State()
    s_contin = State()
    s_answer = State()
    s_show = State()

state_storage = StateMemoryStorage()
bot = telebot.TeleBot(os.getenv('TOKEN'), state_storage=state_storage)


params = {'text': 'Data Scientist',
              'area': '113',
              'type': 'open',
              'per_page': '100',
              'period': 7
              }

class Vacancy():
    def __init__(self, page):
        self.page = page
        keys = ['expirience', 'schedule', 'salary', 'city']

        for key in keys:
            self.key = None



    @bot.message_handler(commands=['start', 'help'])
    def get_experience(message):
        markup_experience = types.InlineKeyboardMarkup()
        zero = types.InlineKeyboardButton(text='Нет опыта', callback_data='noExperience')
        one = types.InlineKeyboardButton(text='От 1 года до 3 лет', callback_data='between1And3')
        three = types.InlineKeyboardButton(text='От 3 до 6 лет', callback_data='between3And6')
        six = types.InlineKeyboardButton(text='Более 6 лет', callback_data='moreThan6')
        markup_experience.add(zero, one)
        markup_experience.add(three, six)

        send_mess = f"<b>Привет, {message.from_user.first_name}</b>!\nПриступим к поиску вакансий!"
        bot.send_message(message.chat.id, send_mess, parse_mode='html')

        bot.send_message(message.chat.id, 'Выберите опыт работы', parse_mode='html', reply_markup=markup_experience)
        bot.set_state(message.chat.id, States.s_salary)


    @bot.callback_query_handler(func=lambda call: True, state=States.s_salary)
    def get_salary(call):
        params['experience.id'] = call.data
        bot.send_message(call.from_user.id, 'Введите желаемую зарплату')
        bot.set_state(call.from_user.id, States.s_schedule)

    @bot.message_handler(func=lambda m: True, state=States.s_schedule)
    def get_schedule(message):

        params['salary.from']  = message.text
        markup_schedule = types.InlineKeyboardMarkup()
        full = types.InlineKeyboardButton(text='Полный день', callback_data='fullDay')
        removable = types.InlineKeyboardButton(text='Сменный график', callback_data='shift')
        flexible = types.InlineKeyboardButton(text='Гибкий график', callback_data='flexible')
        remote = types.InlineKeyboardButton(text='Удаленная работа', callback_data='remote')
        markup_schedule.add(full, removable)
        markup_schedule.add(flexible, remote)
        bot.send_message(message.chat.id, 'Выберите график работы', reply_markup=markup_schedule)
        bot.set_state(message.chat.id, States.s_city)


    def getAreas(message):
        city = requests.get('https://api.hh.ru/areas', {'area': 113})
        data = city.content.decode()
        city.close()
        obj = json.loads(data)
        areas = []
        for k in obj:
            for i in range(len(k['areas'])):
                if len(k['areas'][i]['areas']) != 0:  # Если у зоны есть внутренние зоны
                    for j in range(len(k['areas'][i]['areas'])):
                        areas.append(k['areas'][i]['areas'][j]['name'])
                else:  # Если у зоны нет внутренних зон
                    areas.append(k['areas'][i]['name'])
        return areas

    @bot.callback_query_handler(func=lambda c: True, state=States.s_city)
    def get_city(call):
        params['schedule.id']  = call.data

        bot.send_message(call.from_user.id, 'Введите город')
        bot.set_state(call.from_user.id, States.s_vacancy)

    @bot.message_handler(func=lambda message: True, state=States.s_vacancy)
    def get_vacancies(message):
        city = message.text
        bot.send_message(message.chat.id, "Выбираю вакансии под вас...")
        list_of_jsons = []

        for page in range(10):
            params['page'] = page
            url = 'https://api.hh.ru/vacancies'
            response = requests.get(url, params)
            json = response.json()
            list_of_jsons.append(json)

        new_json = []

        for i in list_of_jsons:
            for item in i['items']:
                name = item['name']
                employer = item['employer']['name']
                area = item['area']['name']
                alternate_url = item['alternate_url']

                if item['salary'] != None:
                    if item['salary']['from'] != None and item['salary']['to'] != None:
                        salary_from = item['salary']['from']
                        salary_to = item['salary']['to']
                        salary = f"{salary_from} - {salary_to}"
                    elif item['salary']['from'] != None and item['salary']['to'] == None:
                        salary_from = item['salary']['from']
                        salary = f"от {salary_from}"
                    elif item['salary']['from'] == None and item['salary']['to'] != None:
                        salary_to = item['salary']['to']
                        salary = f"до {salary_to}"
                else:
                    salary = 'Зарплата не указана'

                vac = {
                    'name': name,
                    'salary': salary,
                    'employer': employer,
                    'area': area,
                    'alternate_url': alternate_url
                }

                if area == city:
                    new_json.append(vac)
                else:
                    pass


        vacancies = []
        for lists in new_json:
            for values in lists.values():
                vacancies.append(values)

        list = []
        for i in range(0, len(vacancies), 5):
            list.append(vacancies[i:i + 5])


        for item in list[:5]:
            for j in item:
                ssilka = item[4]
                vacan = item[:4]

                vacan2 = '\n'.join(map(str, vacan))

            markup_url = types.InlineKeyboardMarkup()
            url = types.InlineKeyboardButton(text='Подробнее', url=ssilka)
            markup_url.add(url)

            bot.send_message(message.chat.id, vacan2, reply_markup=markup_url)
            del list[:5]

        markup_search_again = types.InlineKeyboardMarkup()
        yes = types.InlineKeyboardButton(text='Да', callback_data='yes')
        no = types.InlineKeyboardButton(text='Нет', callback_data='no')
        markup_search_again.add(yes, no)
        bot.send_message(message.chat.id, 'Искать снова?', reply_markup=markup_search_again)

        bot.set_state(message.chat.id, States.s_answer)

        @bot.callback_query_handler(func=lambda c: True, state=States.s_answer)
        def answer(call):
            if call.data == 'yes':
                bot.delete_state(call.from_user.id)
                bot.send_message(call.from_user.id, 'Нажмите /start')
            else:
                bot.send_message(call.from_user.id, 'До новых встреч!')
                bot.delete_state(call.from_user.id)


bot.add_custom_filter(custom_filters.StateFilter(bot))

bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()

if __name__ == '__main__':
    bot.polling(non_stop=True)
