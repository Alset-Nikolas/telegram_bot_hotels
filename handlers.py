import api_work
from datetime import datetime, timedelta
import re
import log
from typing import Dict
import KeyBoard


@log.repeat
def handler_country(text: dict, context: Dict[str, str], keyboard: KeyBoard = None) -> bool:
    '''
            API запрос на поиск городов
            :param text: Информация о новом сообщении от user
            :param context: Персональные данные user
            :param keyboard: Можно добавить кнопки
    '''
    response = api_work.ServerApiHotels().api_search_country(country=text.text)
    vars_country = {}

    if response is None:
        return False

    for obj in response['suggestions'][0]['entities']:
        if obj['type'] == "CITY":
            name = obj['name']
            vars_country[name] = obj['destinationId']
    keyboard.add_obj(name_objs="country", objs=vars_country)
    keyboard.add_exit_btn()
    if len(keyboard) == 0:
        return False
    return True


def handler_quantity_hotels(text: Dict[str, str], context: Dict[str, str], keyboard: KeyBoard = None) -> bool:
    '''
            Проверка кол-ва отелей
            :param text: Информация о новом сообщении от user
            :param context: Персональные данные user
            :param keyboard: Можно добавить кнопки
    '''
    number = text.text
    if number.isdigit() and 25 >= int(number) > 0:
        context['quantity_hotels'] = int(text.text)
        return True
    return False


def handler_photo(text: Dict[str, str], context: Dict[str, str], keyboard: KeyBoard = None) -> bool:
    '''
            Возмоно 2 значения да/нет
            :param text: Информация о новом сообщении от user
            :param context: Персональные данные user
            :param keyboard: Можно добавить кнопки
    '''
    number = text.text
    if number.lower() in {'да'}:
        context['photo_flag'] = True
        return True
    if number.lower() in {'нет'}:
        context['photo_flag'] = False
        return True
    return False


def handler_false(text: Dict[str, str], context: Dict[str, str], keyboard: KeyBoard = None) -> bool:
    '''Происходит взаимодействие только с кнопками'''

    if context['country'] is not None:
        return True
    return False


def handler_quantity_photos(text: Dict[str, str], context: Dict[str, str], keyboard: KeyBoard = None) -> bool:
    '''
    Проверка входных данных, кол-ва фото
    :param text:
    :param context:
    :param keyboard:
    :return:
    '''
    number = text.text
    if number.isdigit() and 25 >= int(number) > 0:
        context['quantity_photo'] = int(text.text)
        return True
    return False


def parser_cost(cost: str):
    '''
    Меняем формат цены
    :param cost: Цена
    :return:
    '''
    if cost.startswith("0"):
        cost.replace(",", '.')
    else:
        cost.replace(",", '')
    return float(cost)


def handler_min_max_cost(text: Dict[str, str], context: Dict[str, str], keyboard: KeyBoard = None) -> bool:
    '''
            Проверка входных данных, цены
            :param text:
            :param context:
            :param keyboard:
            :return:
    '''
    re_ = r'\d{1,}\s+\d{1,}'
    if re.search(re_, text.text):
        num_1, num_2 = text.text.split()
        num_1 = parser_cost(num_1)
        num_2 = parser_cost(num_2)
        context['min_cost'] = min(num_1, num_2)
        context['max_cost'] = max(num_1, num_2)
        return True
    return False


def handler_min_max_d(text: Dict[str, str], context: Dict[str, str], keyboard: KeyBoard = None) -> bool:
    '''
                Проверка входных данных, расстояния
                :param text:
                :param context:
                :param keyboard:
                :return:
    '''
    re_ = r'\d{1,}\s+\d{1,}'
    if re.search(re_, text.text):
        num_1, num_2 = text.text.split()
        num_1.replace(",", '.')
        num_2.replace(",", '.')
        num_1, num_2 = float(num_1), float(num_2)
        context['min_d'] = min(num_1, num_2)
        context['max_d'] = max(num_1, num_2)
        return True
    return False


def handler_data(text: Dict[str, str], context: Dict[str, str], keyboard: KeyBoard = None) -> bool:
    '''
                    Проверка входных данных, даты
                    :param text:
                    :param context:
                    :param keyboard:
                    :return:
    '''
    re_ = r'\d{1,2}.\d{1,2}.\d{4}'
    nums = text.text.split()
    if len(nums) == 2 and re.search(re_, nums[0]) and re.search(re_, nums[1]):
        start_data = datetime.strptime(nums[0], "%d.%m.%Y")
        start_data = start_data.strftime("%Y-%m-%d")
        end_data = datetime.strptime(nums[1], "%d.%m.%Y")
        end_data = end_data.strftime("%Y-%m-%d")
        now = datetime.now()
        now_data = now.strftime("%Y-%m-%d")
        if end_data > start_data and start_data >= now_data:
            context['start_data'] = start_data
            context['end_data'] = end_data
            return True
    return False
