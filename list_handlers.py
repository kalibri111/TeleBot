from settings import bot
from postgres_stuff import execute

from collections import namedtuple


@bot.message_handler(commands=['list'])
def request_list_handler(message):
    last_10 = execute(
        'select * from place order by id desc limit 10;'
    )
    if type(last_10) is list and last_10 is not None:
        for place in last_10:
            bot.send_message(message.chat.id, place[2] + ' по адресу ' + place[3])
    elif last_10 is not None:
        bot.send_message(message.chat.id,  last_10[2] + ' по адресу ' + last_10[3])
    else:
        bot.send_message(message.chat.id, 'У вас нет сохраненных данных')
