

from User import User


class BrainBot:
    '''Запоминаем всех людей, которые хотят поиграть с ботом'''

    def __init__(self) ->None:
        '''Атрибут для запоминания users'''
        self.people = dict()

    def add_user(self, user: User, id_name: int) -> None:
        '''Запомнить человека по id'''
        self.people[id_name] = user

    def pop_user(self, id_name: int) -> None:
        '''Забыть человека по id'''
        self.people.pop(id_name)
