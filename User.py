import datetime
import time

from Image import Image
from Hotel import Hotel
import telebot
import log
from itertools import groupby
from settings import SCENARIOS
import handlers
from KeyBoard import KeyBoard
import api_work
from typing import List, Dict


class User:
    '''Основной класс, для прогонки сюжета'''

    def __init__(self, id_name: int, first_name: str, last_name: str, bot: telebot.TeleBot):
        '''

        :param id_name: id user
        :param first_name: имя
        :param last_name: фамилия
        :param bot: бот, в котором происходит общение
        '''
        self.id = id_name
        self.first_name = first_name
        self.last_name = last_name
        self.__command = None
        self.__step = 'start'
        self.context = {"country": None,
                        "quantity_hotels": None,
                        'photo_flag': None,
                        "quantity_photo": None,
                        'min_cost': None,
                        "max_cost": None,
                        'min_d': None,
                        'max_d': None,
                        "start_data": None,
                        "end_data": None,
                        "exit": False,
                        }
        self.end = False
        self.keyboard = None
        self.memory = dict()
        self.memory_id = dict()
        self.reverse_sort = False
        self.bot = bot

    @property
    def command(self) -> str:
        '''Вывод названии команды'''
        return self.__command

    @command.setter
    def command(self, command: str) -> None:
        '''
        Установка новой команды
        :param command: Название команды
        :return:
        '''
        self.__command = command

    def create_keyboard(self, step: Dict[str, str]) -> None:
        '''Если нужно пподготовим клавиатуру с выбором'''
        if step["keyboard"]:
            self.keyboard = KeyBoard(command=self.__command)
        else:
            self.keyboard = None

    def step_no_error(self, step: Dict[str, str], answer: Dict[str, str]) -> bool:
        '''Проверка входных данных'''
        if not hasattr(handlers, step["handler"]):
            return True
        handler = getattr(handlers, step["handler"])
        return handler(text=answer, context=self.context, keyboard=self.keyboard)

    def remember_buttons(self) -> None:
        '''
            Запомним значения с кнопок и их id
                   типо self.memory = {'country': {'Москва': '2395'}}
        '''
        if self.keyboard:
            for name_fact, val_fact in self.keyboard.objs.items():
                self.memory[name_fact] = val_fact

    def forget_unnecessary_information(self) -> None:
        '''Хотим сопоставить параметрам их id'''
        for name, val in self.context.items():
            if name in self.memory:
                for val, id_val in self.memory[name].items():
                    if val == self.context[name]:
                        self.memory_id[name] = id_val

    def next_step(self, answer: Dict[str, str]) -> str:
        '''Следующий шаг'''
        step_name = self.__step
        if self.__command == '/highprice':
            self.__command = '/lowprice'
            self.reverse_sort = True
        step = SCENARIOS[self.__command]['steps'][step_name]
        text = step['text']
        self.create_keyboard(step)
        if self.step_no_error(step, answer):
            if self.context['photo_flag'] and step['branching']:
                step_name = step['branching']
                step = SCENARIOS[self.__command]['steps'][step_name]
                text = step['text']
            self.__step = step["next_step"]
            if self.__step == 'end':
                self.forget_unnecessary_information()
                self.end = True
                answer = SearchAnswer(user=self, bot=self.bot)
                answer.search()
                answer.send_answer()
                return answer.send_text()
            self.remember_buttons()
            return text.format(**self.context)
        if api_work.ServerApiHotels().server_fell:
            self.end = True
            return "Ошибки на сервере. Попробуйте позже :("
        old_step_name = step["old_step"]
        old_step = SCENARIOS[self.__command]['steps'][old_step_name]
        return old_step['failure_text'].format(**self.context)

    def __str__(self):
        return f'id={self.id}, first_name={self.__first_name}, last_name={self.__last_name}, command={self.__command}'

class SearchAnswer:

    def __init__(self, user:User, bot: telebot.TeleBot):
        '''
        Формирование ответа
        :param user: User
        :param bot: бот
        '''
        self.user = user
        self.command = getattr(self, self.user.command[1:])
        self.context = self.user.context
        self.hotels = []
        self.start_text = ''
        self.next_page_search = None

        self.bot = bot

    def search(self) -> None:
        '''Основная функция для запска соответ. команды'''
        self.command()

    def calc_days(self) -> None:
        '''Подсчет кол-ва дней'''
        y1, m1, d1 = self.context["start_data"].split("-")
        y2, m2, d2 = self.context["end_data"].split("-")
        d1 = datetime.date(int(y1), int(m1), int(d1))
        d2 = datetime.date(int(y2), int(m2), int(d2))
        del_ = d2 - d1
        return int(str(del_).split()[0])

    @log.catch_error(text_er="Нет отеля или его параметров, которые ищут")
    def give_hotel(self, response: Dict[str, str]) -> List[Hotel]:
        '''Парсинг запроса (response), и создание обьетов Hotel'''
        big_obj = response['data']['body']['searchResults']
        self.next_page_search = big_obj["pagination"]["nextPageNumber"]
        Hotels = []
        for obj in big_obj['results']:
            id_ = obj['id']
            print(id_, obj['ratePlan']['price']['current'])
            name = obj['name']
            star_rating = obj['starRating']
            urls = obj['urls']

            try:
                address = obj['address']['streetAddress']
            except:
                address = "Найти не смогли"

            total_price = obj['ratePlan']['price']['current']
            info = obj['ratePlan']['price']["info"]
            distance = 0
            for landmark in obj['landmarks']:
                if landmark['label'] == 'Центр города':
                    distance = landmark['distance']
            photo = None
            price_one_day = float(total_price.split()[0].replace(",", "")) // self.calc_days()
            h = Hotel(name, id_, address, distance, price_one_day, total_price, photo, star_rating, urls, info)
            Hotels.append(h)
        return Hotels

    @log.repeat
    def sort_price(self) -> List[Hotel]:
        '''Запрос на сортировку'''
        if not self.user.reverse_sort:
            key = 'PRICE'
        else:
            key = 'PRICE_HIGHEST_FIRST'

        response = api_work.ServerApiHotels().api_sort_hotels(first_data=self.context["start_data"],
                                                              second_data=self.context["end_data"],
                                                              country_id=self.user.memory_id["country"],
                                                              quantity_hotels=self.context['quantity_hotels'], key=key)
        return self.give_hotel(response)

    @log.catch_error(text_er="Нет фотографий отеля")
    @log.repeat
    def search_photo(self, id_hotel: int) -> List[Image]:
        '''Находит фотографии по id отеля'''
        response = api_work.ServerApiHotels().api_search_photo(id_hotel)
        images = []
        id_ = response['hotelId']
        for obj in response['hotelImages']:
            if len(images) >= int(self.context['quantity_photo']):
                break
            base_url = obj['baseUrl']
            new_img = Image(id_=id_, url=base_url)
            images.append(new_img)
        return images

    def add_photo(self) -> None:
        '''Добавить фотографии к отелям'''
        if self.context['photo_flag']:
            for i, hotel in enumerate(self.hotels):
                self.hotels[i].images = self.search_photo(hotel.id)

    def lowprice(self) -> None:
        '''Команда /lowprice '''
        if not self.user.reverse_sort:
            self.start_text = 'Отели отсортированы (по возрастанию цены)\n'
        else:
            self.start_text = 'Отели отсортированы (по убыванию цены)\n'
        self.hotels = self.sort_price()
        self.hotels = self.kill_repeats(self.hotels)
        self.add_photo()

    def optimal_price(self) -> None:
        '''Запрос на оптимальную цену'''
        page_number = 1
        start_time = time.time()

        while len(self.hotels) < self.context["quantity_hotels"] and isinstance(page_number, int):
            response = api_work.ServerApiHotels().api_all_hotels(first_data=self.context["start_data"],
                                                                 second_data=self.context["end_data"],
                                                                 country_id=self.user.memory_id["country"],
                                                                 page_number=page_number,
                                                                 price_min=self.context["min_cost"],
                                                                 price_max=self.context["max_cost"])
            hotels = self.give_hotel(response)
            if hotels is not None:
                for hotel in hotels:
                    distance = hotel.distance.split()[0]
                    distance = float(distance.replace(",", '.'))

                    if float(self.context["min_d"]) <= distance <= float(self.context["max_d"]):
                        if not len(self.hotels) < self.context["quantity_hotels"]:
                            break
                        self.hotels.append(hotel)
            delat_time = time.time() - start_time
            if delat_time > 60:
                log.log_er.debug("Оень долго происходит поиск")
                break
            page_number = self.next_page_search

    def bestdeal(self):
        '''Команда /bestdeal'''
        self.start_text = 'Оптимальные отели:\nОтели отсортированы (по возрастанию расстояния от центра)\n'
        self.optimal_price()
        self.hotels = self.kill_repeats(self.hotels)
        self.add_photo()

    def kill_repeats(self, items_: List[Hotel]) -> List[Hotel]:
        '''Убрать повторы отелей'''
        itms_id = [itm.id for itm in items_]
        if len(set(itms_id)) != len(itms_id):
            itms_id = [el for el, _ in groupby(itms_id)]
            new_item = []
            for itm in items_:
                if itm.id in itms_id:
                    new_item.append(itm)
                    itms_id.pop(itms_id.index(itm.id))
            return new_item
        return items_

    def no_hotels(self, real_quantity_hotels: List[Hotel]) -> None:
        '''Если такого кол-ва отелей не смогли найти'''
        if self.context["quantity_hotels"] != real_quantity_hotels and real_quantity_hotels != 0:
            txt = f'По такому запросу нашли всего {real_quantity_hotels} вариант(ов): '
            log.log_info.info(f"person_id={self.user.id} message='{txt}'")
            self.bot.send_message(self.user.id, txt)

    def send_answer(self) -> None:
        '''Отправить ответ'''
        self.bot.send_message(self.user.id, self.start_text)
        self.no_hotels(real_quantity_hotels=len(self.hotels))
        if self.context["photo_flag"]:
            for i, hotel in enumerate(self.hotels):
                txt = f"Вариант № {i + 1}:\n"
                txt += str(hotel)
                flag_first_photo = True
                media = []
                for image in hotel.images:
                    if flag_first_photo:
                        media.append(telebot.types.InputMediaPhoto(image.url, caption=txt))
                        flag_first_photo = False
                    else:
                        media.append(telebot.types.InputMediaPhoto(image.url))
                log.log_info.info(f"person_id={self.user.id} message='{self.send_text()}'")
                self.bot.send_media_group(self.user.id, media=media)
        else:
            if len(self.hotels) == 0:
                txt = "По таким параметрам нет отелей"
                self.bot.send_message(self.user.id, txt)
                log.log_info.info(f"person_id={self.user.id} message='{txt}'")
            else:
                log_txt = ''
                for i, hotel in enumerate(self.hotels):
                    txt = f"Варивнт № {i + 1}:\n"
                    txt += str(hotel)
                    self.bot.send_message(self.user.id, txt)
                    log_txt += txt
                log.log_info.info(f"person_id={self.user.id} message='{log_txt}'")

    def send_text(self) -> str:
        '''Отпарвить текст'''
        txt = ''
        for i, hotel in enumerate(self.hotels):
            txt += f"Вариант № {i + 1}:\n"
            txt += str(hotel) + '\n\n'
        log.log_info.info(f"person_id={self.user.id} message='{txt}'")
        return txt
