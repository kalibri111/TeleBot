from settings import POSTGRES_DSN, bot
from geolocation import get_location

from enum import Enum

import psycopg2


class STATE(Enum):
    START = 1,
    PLACE = 2,
    LOCATION = 3,
    CONFIRMATION = 4,


def execute(sql):
    conn = psycopg2.connect(POSTGRES_DSN)
    r = None
    with conn:
        with conn.cursor() as curs:
            curs.execute(sql)
            if curs.rowcount and 'select' in sql.lower():
                r = curs.fetchone()
    return r


def get_state(message):
    chat_id = message.chat.id
    request = execute('select state from chat where id = {};'.format(chat_id))
    if request is not None:
        request = request[0]
    return request


def update_state(message):
    cur_state = get_state(message)
    new_state = None
    if cur_state is None:
        execute(
            'insert into chat(id, state) values ({}, {});'.format(message.chat.id, 1)
        )
        new_state = 2
    elif cur_state < 4:
        new_state = cur_state + 1
    else:
        new_state = 1
    execute(
        'update chat set state = {} where id = {};'.format(
            new_state, message.chat.id
        )
    )


@bot.message_handler(
    func=lambda msg: get_state(msg) == STATE.START.value[0] or
                     get_state(msg) is None
)
def add_start_handler(message):
    bot.send_message(message.chat.id, 'Добавьте новое место')
    update_state(message)
    execute(
        'insert into place(chat_id, address, location) values ({}, null, null);'.
            format(message.chat.id)
    )


@bot.message_handler(func=lambda msg: get_state(msg) == STATE.PLACE.value[0])
def add_place_handler(message):
    execute(
        'update place set address = \'{}\' where chat_id = {};'.format(
            message.text, message.chat.id
        )
    )
    bot.send_message(message.chat.id, 'Добавьте геолокацию')
    update_state(message)


@bot.message_handler(func=lambda msg: get_state(msg) == STATE.LOCATION.value[0])
def add_location_handler(message):
    geo = get_location(message.text)
    execute(
        'update place set location = \'{}\' where chat_id = {}'.format(
            geo, message.chat.id
        )
    )
    update_state(message)
    bot.send_message(message.chat.id, 'Подтвердите сохранение')


@bot.message_handler(func=lambda msg: get_state(msg) == STATE.CONFIRMATION.value[0])
def add_confirmation_handler(message):
    if 'нет' in message.text:
        execute(
            'delete from place where chat_id = {}'.format(message.chat.id)
        )
        bot.send_message(message.chat.id, 'Отменено')
    else:
        bot.send_message('Успешно сохранено')
    update_state(message)
