from typing import List


class Hotel:
    def __init__(self, name: str, id_: int, address: str, distance: str, price: str, total_price: str,
                 photo: List[str] = None, star_rating: str = None, urls: List[str] = None,
                 info: str = None) -> None:
        '''

        :param name: Название отеля
        :param id_: id Отеля
        :param address: Адрес отеля
        :param distance: Расстояние от центра
        :param price: Цена за ночь
        :param total_price: Цена за период
        :param photo: Фотографии отеля
        :param star_rating: Звезды отеля
        :param urls: Ссылка
        :param info: Общая информация
        '''
        self.name = name
        self.id = id_
        self.address = address
        self.distance = distance
        self.price = price
        self.total_price = total_price
        self.photo = photo
        self.star_rating = star_rating
        self.urls = urls
        self.info = info

        self.image = []

    def __str__(self) -> str:
        '''Вывод информации по отелю'''
        return f'Отель: {self.name},\n' \
               f'адрес: {self.address}\n' \
               f'Расстояние от центра: {self.distance}\n' \
               f'Цена за ночь: {self.price} RUB, на данный период={self.total_price} \n' \
               f'Звезд: {self.star_rating}\n' \
               f'https://ru.hotels.com/ho{self.id}'
