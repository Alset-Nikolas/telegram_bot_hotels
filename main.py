import log
from BrainBot import BrainBot
from User import User
import telebot
import bd
from decouple import config
from typing import Dict

token_bot = config('token_bot', default='')

if not token_bot:
    raise 'Нужен TOKEN для бота'

bot = telebot.TeleBot(token_bot)
brain_bot = BrainBot()


@bot.chat_join_request_handler(func=lambda m: True)
def new_person(message: Dict[str, str]) -> None:
    bot.send_message(message.from_user.id,
                     f"Добрый день, Вас приветсвует бот {bot.first_name}.\nНапишите команду /help чтобы узнать, что я умею")


@bot.message_handler(commands=['start', 'help'])
def help_send(message: Dict[str, str]) -> None:
    log.log_info.info(f"person_id={message.from_user.id} message='{message.text}'")
    text = 'Я могу найти:\n' \
           'Топ самых дешёвых отелей в городе /lowprice.\n' \
           'Топ самых дорогих отелей в городе /highprice\n' \
           'Топ отелей, наиболее подходящих по цене и расположению от центра /bestdeal\n' \
           'Историю поиска отелей /history'
    bot.send_message(message.from_user.id, text)
    log.log_info.info(f"Ответ: person_id={message.from_user.id} message='{text}'")


def registration(message: Dict[str, str]) -> None:
    '''Регистрация нового человека'''
    person_id = message.from_user.id
    if person_id not in brain_bot.people:
        person = User(id_name=person_id, first_name=message.from_user.first_name, last_name=message.from_user.last_name,
                      bot=bot)
        person.command = message.text
        brain_bot.add_user(user=person, id_name=person_id)


@bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal', 'history'])
def commands_send(message: Dict[str, str]) -> None:
    '''Обработка команд'''
    person_id = message.from_user.id
    log.log_info.info(f"person_id={person_id} message='{message.text}'")
    if message.text == '/history':
        text = bd.search_history(person_id)
        log.log_info.info(f"Ответ: person_id={person_id} message='{text}' + кнопки")
        bot.send_message(message.from_user.id, text)
        return
    registration(message)
    person = brain_bot.people[person_id]
    text = person.next_step(message)
    if person.end:
        bd.add_to_history(user=person, answer_hotels=text)
        brain_bot.pop_user(id_name=person_id)
    else:
        if person.keyboard is None:
            log.log_info.info(f"Ответ: person_id={person_id} message='{text}'")
            bot.send_message(message.from_user.id, text)
        else:
            log.log_info.info(f"Ответ: person_id={person_id} message='{text}' + кнопки")
            bot.send_message(message.from_user.id, text, reply_markup=person.keyboard.keyboard_obj)


@bot.message_handler(content_types=['text'])
def get_text_messages(message: Dict[str, str]) -> None:
    '''Обработка сообщения от пользователя'''
    person_id = message.from_user.id
    if person_id not in brain_bot.people:
        log.log_info.info(f"person_id={person_id} message='{message.text}'")
        text = "Привет, чем я могу тебе помочь?\n" \
               "Если хочешь узнать список команд, напиши /help"
        bot.send_message(message.from_user.id, text)
        log.log_info.info(f"Ответ: person_id={person_id} message='{text}'")
    else:
        commands_send(message)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith('/lowprice') or call.data.startswith('/highprice') or call.data.startswith(
        '/bestdea'))
def choose_country(call: Dict[str, str]) -> None:
    '''Нажатая кнопка выбора'''
    country = call.message.json['reply_markup']['inline_keyboard'][0][0]['text']
    log.log_info.info(f"person_id={call.from_user.id}: Нажал на кнопку '{country}' ")
    if brain_bot.people[call.from_user.id].context['country'] is None:
        brain_bot.people[call.from_user.id].context['country'] = country
        bot.edit_message_text(chat_id=call.message.json["chat"]["id"], message_id=call.message.message_id,
                              text=f'Ваш выбор: {country}',
                              reply_markup=None)
        bot.send_message(call.message.chat.id, brain_bot.people[call.from_user.id].next_step(''))


@bot.callback_query_handler(func=lambda call: call.data.startswith('exit'))
def exit(call: Dict[str, str]) -> None:
    '''Кнопка выхода'''
    log.log_info.info(f"person_id={call.from_user.id}: Нажал на кнопку 'Выход' ")
    if brain_bot.people[call.from_user.id].context['country'] is None:
        bot.edit_message_text(chat_id=call.message.json["chat"]["id"], message_id=call.message.message_id,
                              text=f'Сценарий завершен! Введите новую команду:',
                              reply_markup=None)
        brain_bot.pop_user(id_name=call.from_user.id)


bot.infinity_polling()
