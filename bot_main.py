#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Based on examples of the telegram-bot library
# Simple Bot to receive search urls of the Aviasales website.

"""
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, ParseMode)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)
from userInterpreter import UserInterpreter, ErrorIncorrectDate, ErrorCannotParseDate, ErrorNotYearAhead,ErrorDateSeq

import logging

TOKEN='661792378:AAH2ksyQmG2FE7V7tFweIlaS4va_Z3qLe0g'
REQUEST_KWARGS={
    'proxy_url': 'socks5://deimos.public.opennetwork.cc:1090',
    # Optional, if you need authentication:
    'urllib3_proxy_kwargs': {
        'username': '261350784',
        'password': 'fRMSr9ni',
    }
}

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
interpretator = UserInterpreter()

TYPING_NAME, TYPING_DEPARTURE, TYPING_ARRIVAL, TYPING_DATES, CHOOSE_CONFIRM, START_AGAIN = range(6)


def start(bot, update):
    update.message.reply_text(
        "Здравствуйте, я помогу вам с оформлением авиабилетов. Как я могу к вам обращаться?\n"
        "Отправьте /cancel, чтобы закончить разговор.\n")
    return TYPING_NAME

def cancel(bot, update):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('До свидания.\n'
                              'Отправьте /start, чтобы снова начать разговор.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

def input_name(bot, update, user_data):
    user = update.message.from_user
    name = update.message.text
    user_data['name'] = name
    logger.info("User %s has said that her name %s.", user.first_name, name)
    update.message.reply_text(name +", откуда вы полетите?")
    #update.message.reply_text( name+ ", пока!\n")
    return TYPING_DEPARTURE

def input_departure(bot, update, user_data):
    user = update.message.from_user
    departure_city = update.message.text
    iata = interpretator.get_city_code(departure_city)
    if iata is None:
         bot.send_message(chat_id=update.message.chat_id, text="Кажется, я не знаю этот город. Может быть вы выберете другой город поблизости?")
         logger.info("User %s  has sent an incorrect departure city %s.", user.first_name, departure_city)
         return TYPING_DEPARTURE
    user_data['departure_city'] = departure_city
    user_data['departure_iata'] = iata
    logger.info("User %s has sent a departure city %s.", user.first_name, departure_city)
    update.message.reply_text(user_data['name'] + ", куда вы полетите?")
    return TYPING_ARRIVAL

def input_arrival(bot, update, user_data):
    user = update.message.from_user
    arrival_city = update.message.text
    iata = interpretator.get_city_code(arrival_city)
    if iata is None:
        bot.send_message(chat_id=update.message.chat_id, text="Похоже, я не знаю этот город. Может быть вы выберете другой город поблизости?")
        logger.info("User %s  has sent an incorrect destination %s.", user.first_name, arrival_city)
        return TYPING_ARRIVAL
    user_data['arrival_city'] = arrival_city
    user_data['arrival_iata'] = iata
    logger.info("User %s has sent a destination city %s.", user.first_name, arrival_city)
    update.message.reply_text(user_data['name'] + ", в какие даты?")
    return TYPING_DATES

def input_dates(bot, update, user_data):
    user = update.message.from_user
    string_with_dates = update.message.text
    try:
        date1, date2 = interpretator.interpret_dates(string_with_dates)
    except (ErrorCannotParseDate, ErrorIncorrectDate) as e:
        bot.send_message(chat_id=update.message.chat_id, text="Не совсем вас понял.\n"
                                                              "Пожалуйста, укажите в какой период вы планируете поездку.\n"
                                                              "Например, _с 30 октября по 8 марта_.\n"
                                                              "Если вас интересуют билеты в один конец, отправьте только дату вылета.",
                         parse_mode=ParseMode.MARKDOWN)
        logger.info("User %s  has sent incorrect input: %s.", user.first_name, string_with_dates)
        return TYPING_DATES
    except ErrorNotYearAhead as e:
        logger.info(e)
        parsed_date = interpretator.convert_one_date_to_ru_str(e.get_date(), use_year = True)
        bot.send_message(chat_id=update.message.chat_id, text="Вы имели в виду {}?\n"
                                                              "К сожалению, могу советовать перелеты "
                                                              "только в течение года от текущей даты.".format(parsed_date))
        logger.info("User %s  has sent old or 'more than a year from now' dates: %s", user.first_name, string_with_dates)
        return TYPING_DATES
    except ErrorDateSeq as e:
        logger.info(e)
        bot.send_message(chat_id=update.message.chat_id, text="Путешествуете во времени? Боюсь, не могу вам ничего посоветовать.")
        logger.info("User %s  has sent old or 'more than a year from now' dates: %s", user.first_name, string_with_dates)
        return TYPING_DATES
    else:
        user_data['departure'] = date1
        user_data['return'] = date2

        logger.info("User %s has sent departure and return dates: from %s to %s.", user.first_name, str(date1),str(date2))

        show_confirm_form(update, user_data)

        return CHOOSE_CONFIRM

def show_confirm_form(update, user_data):

    reply_keyboard = [['Да', 'Нет']]
    answer = "Спасибо! Всё ли верно: вы собираетесь отправиться *из {}* *{}* *{}*"
    city_ro = interpretator.get_city_case(user_data['departure_city'], 'ro')
    city_vi = interpretator.get_city_case(user_data['arrival_city'], 'vi')
    str_date1 = interpretator.convert_one_date_to_ru_str(user_data['departure'])
    if user_data['return'] is None:
        update.message.reply_text(answer.format(city_ro, city_vi, str_date1),
                                  parse_mode=ParseMode.MARKDOWN,
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    else:
        str_date2 = interpretator.convert_one_date_to_ru_str(user_data['return'])
        answer = answer + " и вернуться *{}*?"
        update.message.reply_text(answer.format(city_ro, city_vi, str_date1, str_date2),
                                  parse_mode=ParseMode.MARKDOWN,
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))


def confirm(bot, update, user_data):
    user = update.message.from_user
    decision =  update.message.text
    logger.info("User %s  made a confirmation decision: %s", user.first_name, decision)
    if decision == 'Да':
        logger.info("User %s  confirmed the data.", user.first_name)
        url_result = interpretator.get_url(user_data['departure_iata'], user_data['arrival_iata'], user_data['departure'], user_data['return'])
        reply_keyboard = [['Да', 'Нет']]
        update.message.reply_text('Отлично. Предлагаю вам следующие варианты перелета: {}\n'
                                  'Хотите обсудить другую поездку?'.format(url_result),
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        return START_AGAIN
    else:
        logger.info("User %s doesn't  confirmed the data.", user.first_name)
        update.message.reply_text("Ладно, попробуем еще раз...\n"
                                  "Так откуда вы все-таки полетите?",
                                  reply_markup = ReplyKeyboardRemove())
        return TYPING_DEPARTURE

def another_query(bot, update, user_data):
    user = update.message.from_user
    decision = update.message.text
    logger.info("User %s  made a decision if she wants to continue: %s", user.first_name, decision)
    if decision == 'Да':
        logger.info("User %s  wants to enter another trip", user.first_name)
        update.message.reply_text("Хорошо! Начнем сначала...\n"
                                  "Откуда вы полетите на этот раз?",
                                  reply_markup=ReplyKeyboardRemove())
        return TYPING_DEPARTURE
    else:
        logger.info("User %s doesn't  want to enter another trip", user.first_name)
        # update.message.reply_text("До встречи, {}!", user_data['name'])
        # return TYPING_DEPARTURE
        update.message.reply_text("Окей, до свидания, {}.\n"
                                  "Отправьте /start, чтобы снова начать разговор.\n".format(user_data['name']),
                                  reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

def unknown(bot, update):
    logger.warning('Update "%s" is unknown', update.message.text)
    bot.send_message(chat_id=update.message.chat_id, text="Извините, не совсем вас понимаю. Не могли бы вы сформулировать по-другому?")




def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN, request_kwargs=REQUEST_KWARGS)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            TYPING_NAME: [RegexHandler('^([\sа-яА-ЯёЁA-Za-z0-9_-])*$', input_name,pass_user_data=True)],

            TYPING_DEPARTURE : [RegexHandler('^([\sа-яА-ЯёЁ0-9-])*$', input_departure,pass_user_data=True)],

            TYPING_ARRIVAL:  [RegexHandler('^([\sа-яА-ЯёЁ0-9-])*$', input_arrival,pass_user_data=True)],

            TYPING_DATES: [RegexHandler('^([\sа-яА-Я0-9_.-])*$', input_dates,pass_user_data=True)],

            CHOOSE_CONFIRM: [RegexHandler('^(Да|Нет)$', confirm, pass_user_data=True)],

            START_AGAIN: [RegexHandler('^(Да|Нет)$', another_query, pass_user_data=True)],
        },

        fallbacks=[CommandHandler('cancel', cancel),MessageHandler(Filters.text, unknown)]
    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()



