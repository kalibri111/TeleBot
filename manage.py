from add_handlers import add_confirmation_handler, add_location_handler,\
    add_place_handler, add_start_handler
from list_handlers import request_list_handler
from reser_handlers import reset_handler
from settings import bot


if __name__ == '__main__':
    bot.polling()
