from aiogram import Bot, Dispatcher, executor, types
import requests
import json

from aiogram.types import ReplyKeyboardRemove

from Token_and_API import TOKEN, API
import logging
from Errors import Error_count_of_list, Too_late, Error_year, Error_month, Error_day, Error_hour, Error_minute, Error_seconds, City_not_found
from Checking import Checking
import asyncio
import datetime

bot = Bot(TOKEN)
dp = Dispatcher(bot)

user_states = {}
data_about_weather = {}
notification_about_weather = {}
city = {}

WAITING_FOR_START = 'waiting_for_start'
WAITING_FOR_ANSWER = 'waiting_for_answer'
WAITING_FOR_CITY = 'waiting_for_city'
WAITING_FOR_TIME = 'waiting_for_time'

# получение пользовательского логгера и установка уровня логирования
py_logger = logging.getLogger(__name__)
py_logger.setLevel(logging.INFO)

# настройка обработчика и форматировщика в соответствии с нашими нуждами
py_handler = logging.FileHandler("app.log", mode='a')
py_formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")

# добавление форматировщика к обработчику
py_handler.setFormatter(py_formatter)
# добавление обработчика к логгеру
py_logger.addHandler(py_handler)

# Начало логирования
py_logger.info('Start_logging: app.py')

async def send_notification(message: types.Message, chosen_time):
    city = notification_about_weather[message.chat.id]["name"]
    wait_time = chosen_time - datetime.datetime.now()
    await asyncio.sleep(delay=wait_time.total_seconds())
    res = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API}&units=metric')
    data = json.loads(res.text)
    with open('2152e6f0-d33d-4d73-ab25-925e351a77b6.png', 'rb') as f:
        await message.answer_photo(photo=f,caption=f'Здравствуйте!\nУведомляем Вас, что в данный момент в городе {city}:\nТемпература воздуха составляет: {data["main"]["temp"]}.\n'
                             f'Ощущается как {data["main"]["feels_like"]}\n'
                             f'Влажность воздуха составляет {data["main"]["humidity"]} %\n'
                             f'Атмосферное давление составляет {data["main"]["pressure"]} мм.рт.ст\n'
                             f'Скорость ветра составляет {data["wind"]["speed"]} км/ч\n'
                             f'Облачность составляет {data["clouds"]["all"]} баллов\n')


@dp.message_handler(lambda message: user_states.get(message.chat.id) is None or user_states.get(message.chat.id) == WAITING_FOR_START, commands=['start'])
async def start(message: types.Message):
    await message.answer('Здравствуйте!\nВас приветствует бот с информацией о погоде.\nЧтобы узнать дополнительную информацию, введите /info')

@dp.message_handler(lambda message: user_states.get(message.chat.id) is None or user_states.get(message.chat.id) == WAITING_FOR_START, commands=['info'])
async def info(message: types.Message):
    await message.answer('Чтобы узнать погоду, введите название интересующего вас города.\nПример: Moscow, Seattle, Paris.\nЕсли хотите, чтобы бот прислал уведомление о погоде в конкретном городе и в определённое время, то для этого введите команду /notification')

@dp.message_handler(lambda message: user_states.get(message.chat.id) is None or user_states.get(message.chat.id) == WAITING_FOR_START, commands=['notification'])
async def notification(message: types.Message):
    try:
        await message.answer('Введите интересующий Вас город')
        user_states[message.chat.id] = WAITING_FOR_CITY
    except Exception as e:
        await message.answer(f'Ошибка со стороны сервера: {e}\nПопробуйте ещё раз')
        py_logger.error(f'Ошибка со стороны сервера: {e}')

@dp.message_handler(lambda message: user_states.get(message.chat.id) == WAITING_FOR_CITY)
async def wait_city(message: types.Message):
    try:
        city[message.chat.id] = message.text.strip().lower()
        res = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city[message.chat.id]}&appid={API}&units=metric')
        data = json.loads(res.text)
        if data['cod'] == '404':
            raise City_not_found
        notification_about_weather[message.chat.id] = data
    except City_not_found:
        await message.reply('Ошибка! Данного города не существует\nПопробуйте ещё раз')
    except Exception as e:
        await message.answer(f'Ошибка со стороны сервера: {e}\nПопробуйте ещё раз')
        py_logger.error(f'Ошибка со стороны сервера: {e}')
    else:
        user_states[message.chat.id] = WAITING_FOR_TIME
        await message.answer('Введите дату и время уведомления в формате (через пробел!!!): год месяц день час минута секунда.\nНапример: 2024 5 12 10 0 0')

@dp.message_handler(lambda message: user_states.get(message.chat.id) == WAITING_FOR_TIME)
async def get_time(message: types.Message):
    try:
        time_notification = message.text.split()
        error = Checking.check_time(time_notification)
        if type(error) == Error_count_of_list:
            raise Error_count_of_list
        elif type(error) == ValueError:
            raise ValueError
        elif type(error) == Too_late:
            raise Too_late
        elif type(error) == Error_year:
            raise Error_year
        elif type(error) == Error_month:
            raise Error_month
        elif type(error) == Error_day:
            raise Error_day
        elif type(error) == Error_hour:
            raise Error_hour
        elif type(error) == Error_minute:
            raise Error_minute
        elif type(error) == Error_seconds:
            raise Error_seconds
    except Error_count_of_list:
        await message.answer('Ошибка! Неверное количество данных.\nВведите дату и время уведомления в формате (через пробел!!!): год месяц день час минута секунда.\nНапример: 2024 5 12 10 0 0')
    except ValueError:
        await message.answer('Ошибка! Введите корректные данные.\nВведите дату и время уведомления в формате (через пробел!!!): год месяц день час минута секунда.\nНапример: 2024 5 12 10 0 0')
    except Too_late:
        await message.answer('Ошибка! Введённая дата не должна быть меньше текущей')
    except Error_year:
        await message.answer('Ошибка! Введите корректный год')
    except Error_month:
        await message.answer('Ошибка! Введите корректный месяц')
    except Error_day:
        await message.answer('Ошибка! Введите корректный день')
    except Error_hour:
        await message.answer('Ошибка! Введите корректное количество часов')
    except Error_minute:
        await message.answer('Ошибка! Введите корректное количество минут')
    except Error_seconds:
        await message.answer('Ошибка! Введите корректное количество секунд')
    except Exception as e:
        await message.answer(f'Ошибка со стороны сервера: {e}\nПопробуйте ещё раз')
        py_logger.error(f'Ошибка со стороны сервера: {e}')
    else:
        time_notification = list(map(int, time_notification))
        chosen_time = datetime.datetime(time_notification[0], time_notification[1], time_notification[2], time_notification[3], time_notification[4], time_notification[5])
        time_to_notification = asyncio.create_task(send_notification(message, chosen_time))

        await message.answer('Уведомление создано успешно!')

        user_states[message.chat.id] = WAITING_FOR_START

@dp.message_handler(lambda message: user_states.get(message.chat.id) is None or user_states.get(message.chat.id) == WAITING_FOR_START, content_types=['text'])
async def get_weather(message: types.Message):
    try:
        city[message.chat.id] = message.text.strip().lower()
        res = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city[message.chat.id]}&appid={API}&units=metric')
        data = json.loads(res.text)
        data_about_weather[message.chat.id] = data
        if data_about_weather[message.chat.id]['cod'] == '404':
            raise City_not_found
    except City_not_found:
        await message.reply('Ошибка! Данного города не существует\nПопробуйте ещё раз')
    except Exception as e:
        await message.answer(f'Ошибка со стороны сервера: {e}\nПопробуйте ещё раз')
        py_logger.error(f'Ошибка со стороны сервера: {e}')
    else:
        markup = types.ReplyKeyboardMarkup()
        markup.add(types.KeyboardButton('Температура воздуха'))
        markup.add(types.KeyboardButton('Влажность воздуха'))
        markup.add(types.KeyboardButton('Атмосферное давление'))
        markup.add(types.KeyboardButton('Ветер'))
        markup.add(types.KeyboardButton('Облачность'))
        markup.add(types.KeyboardButton('⬅️Назад'))
        await message.reply('Что Вас интересует?', reply_markup=markup)
        user_states[message.chat.id] = WAITING_FOR_ANSWER

@dp.message_handler(lambda message: user_states.get(message.chat.id) == WAITING_FOR_ANSWER)
async def information_about_weather(message: types.Message):
    try:
        if message.text == 'Температура воздуха':
            await message.answer(f'Температура воздуха в данный момент: {data_about_weather[message.chat.id]["main"]["temp"]}.\nОщущается как {data_about_weather[message.chat.id]["main"]["feels_like"]}')
        elif message.text == 'Влажность воздуха':
            await message.answer(f'Влажность воздуха составляет {data_about_weather[message.chat.id]["main"]["humidity"]} %')
        elif message.text == 'Атмосферное давление':
            await message.answer(f'Атмосферное давление составляет {data_about_weather[message.chat.id]["main"]["pressure"]} мм.рт.ст')
        elif message.text == 'Ветер':
            await message.answer(f'Скорость ветра составляет {data_about_weather[message.chat.id]["wind"]["speed"]} км/ч')
        elif message.text == 'Облачность':
            await message.answer(f'Облачность составляет {data_about_weather[message.chat.id]["clouds"]["all"]} баллов')
        elif message.text == '⬅️Назад':
            user_states[message.chat.id] = WAITING_FOR_START
            await message.answer('Чтобы узнать погоду, введите название интересующего вас города.\nПример: Moscow, Seattle, Paris', reply_markup=ReplyKeyboardRemove())
        else:
            await message.answer('Ошибка, введите корректную характеристику погоды.')
    except Exception as e:
        await message.answer(f'Ошибка со стороны сервера: {e}\nПопробуйте ещё раз')
        py_logger.error(f'Ошибка со стороны сервера: {e}')

if __name__ == "__main__":
    executor.start_polling(dp)
