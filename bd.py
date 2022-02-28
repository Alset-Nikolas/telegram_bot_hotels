import datetime
from peewee import *

db = SqliteDatabase('bot_history.db')


class BaseTabel(Model):
    '''Базоый класс, для подключения к 1 бд'''

    class Meta:
        database = db  # This model uses the "people.db" database.


class History(BaseTabel):
    '''
        БД для истории запросов
    '''
    user_id = IntegerField()
    person_name = CharField()
    person_command = CharField()
    time = DateTimeField()
    hotels = CharField()


db.create_tables([History])


def add_to_history(user: int, answer_hotels: str) -> None:
    '''
        Добавить ответ, который получил user
    :param user: id user
    :param answer_hotels: Текст, который получил user
    :return: None
    '''
    History.create(
        user_id=user.id,
        person_name=f"{user.first_name} {user.last_name}",
        person_command=user.command if not user.reverse_sort else '/highprice',
        time=datetime.datetime.now(),
        hotels=answer_hotels,
    )


def search_history(person_id: int) -> str:
    '''
    Найти по id информацию, которую получил user
    :param person_id: id user
    :return:
    '''
    history_commands = History.select().where(History.user_id == person_id)
    if len(history_commands) == 0:
        return "Команд еще не было, введите /help, чтобы узнать команды"
    txt = ''
    for x in History.select().where(History.user_id == person_id).order_by(History.time)[::-1]:

        txt += f"{x.time} {x.person_name} -> {x.person_command}\n" \
               f"Результат поиска:\n" \
               f"{x.hotels}"
        if len(txt) > 1100:
            break
    return txt
