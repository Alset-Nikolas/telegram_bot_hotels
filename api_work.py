import json
from typing import Optional, Dict
import requests
from decouple import config
import log

TOKEN = config('TOKEN', default='')

if not TOKEN:
    raise 'Нужен TOKEN'


class ServerApiHotels:
    server_fell = False

    def __init__(self):
        self.headers = {
            'x-rapidapi-host': "hotels4.p.rapidapi.com",
            'x-rapidapi-key': TOKEN
        }

    def api_request(self, url: str, querystring: Dict[str, str], headers: dict) -> Optional[dict]:
        """
        Функция отправки запроса к API
        :param url: url запроса
        :param querystring: параметр запроса в формате словаря
        """
        try:
            response = requests.request("GET", url, headers=headers, params=querystring, timeout=20)
            if response.status_code == 200:
                result = json.loads(response.text)
            else:
                result = None
            if response.status_code == 429:
                ServerApiHotels.server_fell = True
                log.log_er.fatal("Нужно перегистрироваться на сайте апи!")
        except requests.Timeout as time_end:
            # logger.exception(time_end)
            result = None
        except requests.RequestException as er:
            # logger.exception(er)
            result = None

        return result

    def api_search_country(self, country: str) -> Optional[dict]:
        '''
        :param country: Город id которого пытаемся найти
        :return: параметр запроса в формате словаря
        '''
        url_search = "https://hotels4.p.rapidapi.com/locations/v2/search"
        querystring = {"query": country, "locale": "ru_RU"}

        return self.api_request(url=url_search, querystring=querystring, headers=self.headers)

    def api_search_photo(self, id_hotel: str) -> Optional[dict]:
        '''
        :param id_hotel: id отеля
        :return: Информация про отель в формате словаря
        '''
        url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"
        querystring = {"id": id_hotel}

        return self.api_request(url=url, querystring=querystring, headers=self.headers)

    def api_sort_hotels(self, first_data: str, second_data, country_id: str, quantity_hotels: int, key: str) -> \
    Optional[
        dict]:
        '''
        :param first_data: Дата заезда
        :param second_data: Дата уезда
        :param country_id: id Города
        :param quantity_hotels: Кол-во отелей
        :param key: Сортировать по убыванию или возрастанию
        :return: Информация про отлели
        '''
        url = "https://hotels4.p.rapidapi.com/properties/list"
        querystring = {"destinationId": country_id, "pageNumber": "1",
                       "pageSize": quantity_hotels, "checkIn": first_data,
                       "checkOut": second_data, "adults1": "1", "sortOrder": key, "locale": "ru_RU",
                       "currency": "RUB"}

        return self.api_request(url=url, querystring=querystring, headers=self.headers)

    def api_all_hotels(self, first_data: str, second_data: str, country_id: int, page_number: str, price_min: str,
                       price_max: str) -> Optional[dict]:
        '''
        :param first_data: Дата заезда
        :param second_data: Дата уезда
        :param country_id: id Города
        :param page_number: страница на сайте
        :param price_min: минимальная цена
        :param price_max: max цена
        :return: информация про отели
        '''
        url = "https://hotels4.p.rapidapi.com/properties/list"

        querystring = {"destinationId": country_id, "pageNumber": str(page_number), "pageSize": "25",
                       "checkIn": first_data,
                       "checkOut": second_data, "adults1": "1", "priceMin": str(int(price_min)),
                       "priceMax": str(int(price_max)),
                       "sortOrder": "DISTANCE_FROM_LANDMARK", "locale": "ru_RU", "currency": "RUB"}

        return self.api_request(url=url, querystring=querystring, headers=self.headers)
