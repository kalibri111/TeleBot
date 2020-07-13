from .manage import bot
from .settings import POSTGRES_DSN

from enum import Enum

import psycopg2


class STATE(Enum):
    START = 1,
    PLACE = 2,
    LOCATION = 3,
    CONFIRMATION = 4


def execute(sql):
    conn = psycopg2.connect(POSTGRES_DSN)
    with conn:
        with conn.cursor() as curs:
            return curs.execute(sql)


def get_state(message):
    chat_id = message.chat.id
    return execute('select state from "user" where id = {};'.format(chat_id))


def update_state(message):
    cur_state = get_state(message)
    new_state = None
    if cur_state < 4:
        new_state = cur_state + 1
    else:
        new_state = 1
    execute(
        'update "user" set state = {} where id = {};'.format(
            new_state, message.chat.id
        )
    )


@bot.message_handler(commands=['start'], func=lambda msg: get_state(msg) == STATE.START.value[0])
def add_start_handler(message):
    bot.send_message(message.chat.id, 'Добавьте новое место')
    execute(
        'insert into "user"(id) values ({});'.format(message.chat.id)
    )
    update_state(message)


@bot.message_handler(commands=['start'], func=lambda msg: get_state(msg) == STATE.PLACE.value[0])
def add_place_handler(message):
    execute(
        'update place set address = {} where user_id = {};'.format(
            message.text, message.chat.id
        )
    )
    bot.send_message(message.chat.id, 'Добавьте геолокацию')
    update_state(message)


@bot.message_handler(commands=['start'], func=lambda msg: get_state(msg) == STATE.LOCATION.value[0])
def add_location_handler(message):
    geo = get_location(message.text)
    execute(
        'update place set location = {} where user_id = {}'.format(
            geo, message.chat.id
        )
    )
    bot.send_message(message.chat.id, 'Подтвердите сохранение')


@bot.message_handler(commands=['start'], func=lambda msg: get_state(msg) == 'confirmation')
def add_confirmation_handler(message):
    if 'нет' in message.text:
        execute(
            'delete from place where user_id = {}'.format(message.chat.id)
        )
        bot.send_message(message.chat.id, 'Отменено')
