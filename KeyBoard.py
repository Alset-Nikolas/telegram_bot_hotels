import telebot
from typing import Dict


class KeyBoard:
    '''Клавиатура'''

    def __init__(self, command: str):
        self.keyboard_obj = telebot.types.InlineKeyboardMarkup()
        self.command = command
        self.index_name = 0
        self.objs = dict()
        self.print = ''

    def add_btn(self, item: Dict[str, str]) -> None:
        '''
        Добавыить новую кнопку item
        '''
        self.print += str(item) + '\t'
        self.keyboard_obj.row(
            telebot.types.InlineKeyboardButton(item, callback_data=self.command + str(self.index_name)))
        self.index_name += 1

    def add_obj(self, name_objs: str, objs: Dict[str, int]) -> None:
        '''
        Запомнить обьект и его индекс на будущее
        :param name_objs: Названия обьектов, напрмер страна
        :param objs: Словари {'name_paramenr': id_parametr}
        '''
        for name_paramenr, id_parametr in objs.items():
            self.add_btn(item=name_paramenr)
        self.objs[name_objs] = objs

    def add_exit_btn(self) -> None:
        '''Добавляем кнопку выхода'''
        self.keyboard_obj.row(
            telebot.types.InlineKeyboardButton("Я передумал, завершить сценарий", callback_data="exit"))
        self.index_name += 1

    def __str__(self) -> str:
        return self.print

    def __len__(self):
        return self.index_name
