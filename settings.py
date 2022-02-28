from datetime import datetime, timedelta

now = datetime.now()
now_data = now.strftime("%d.%m.%Y")
next_data = datetime.strptime(now_data, "%d.%m.%Y") + timedelta(days=1)
next_data = next_data.strftime("%d.%m.%Y")

'''
SCENARIOS={
    /команда1:{
        "шаги":{
            "start":{
                "text" - вопрос, который задаем 
                "failure_text" - сообщение об ошибки входных данных
                "handler" - функция обработки прошлого ответа -> bool
                "old_step": None, - предыдущий шаг
                "next_step": "шаг0", - следующий шаг
                "keyboard": False, - нужна ли клавиатура выбора
                "branching" None/step{m}, - если есть разветвление по сценаруию, то на какой шаг идти 
            },
            "шаг0":{
                параметры...
                "next_step": "шаг1",
            }
            ...
            "шагN"{
                параметры..
                "next_step": "end",
            }
        }
    },
    /команда2:{
        "шаги": {
                --//--
        }
    }
}
    
'''


SCENARIOS = {
    '/lowprice': {
        "steps": {
            "start": {
                "text": f"Введите диапазон дат, которые вас интересуют:\nНапрмер {now_data}  {next_data}",
                "failure_text": "Формат: дата через точку [пробел] дата через точку\nБилеты отлета и прилета не могут быть в 1 день!\nВ прошлое билеты заказывать тоже нельзя :)",
                "handler": '',
                "next_step": "step-1",
                "keyboard": False,
                "branching": None,
            },
            "step-1": {
                "text": "Введите город, где хотите найти отели",
                "failure_text": "Такого города нет! Попробуйте другой город, где хотите найти отели",
                "handler": 'handler_data',
                "old_step": "start",
                "next_step": "step0",
                "keyboard": False,
                "branching": None,
            },
            'step0': {
                "text": "Нажмите на ваш вариант:",
                "failure_text": 'Выберите вариант!',
                "handler": "handler_country",
                "old_step": "step-1",
                "next_step": "step1",
                "keyboard": True,
                "branching": None,
            },
            'step1': {
                "text": "Будем искать в городе '{country}'.\nКоличество отелей, которые необходимо вывести в результате?",
                "failure_text": 'Должно быть целое число больше нуля, но меньше 25!',
                "handler": "handler_false",
                "old_step": "step0",
                "next_step": "step2",
                "keyboard": False,
                "branching": None,
            },
            'step2': {
                "text": "Нужно загружать фотографии для каждого отеля (“Да/Нет”)?",
                "failure_text": 'Да/Нет',
                "handler": "handler_quantity_hotels",
                "old_step": "step1",
                "next_step": "step3",
                "keyboard": False,
                "branching": None,
            },
            'step3': {
                "text": "{text}",
                "failure_text": '',
                "handler": "handler_photo",
                "old_step": "step2",
                "next_step": "end",
                "keyboard": False,
                "branching": 'step4',
            },
            'step4': {
                "text": "Количество фотографий?",
                "failure_text": 'Должно быть целое число больше нуля, но меньше XX!',
                "handler": "handler_photo",
                "old_step": "step2",
                "next_step": "step5",
                "keyboard": False,
                "branching": None,
            },
            'step5': {
                "text": "{text}",
                "failure_text": 'Должно быть целое число больше нуля, но меньше XX!',
                "handler": "handler_quantity_photos",
                "old_step": "step4",
                "next_step": "end",
                "keyboard": False,
                "branching": None,
            },

        }
    },
    '/bestdeal': {
        "steps": {
            "start": {
                "text": f"Введите диапазон дат, которые вас интересуют:\nНапрмер {now_data}  {next_data}",
                "failure_text": "Формат: дата через точку [пробел] дата через точку\nБилеты отлета и прилета не могут быть в 1 день!\nВ прошлое билеты заказывать тоже нельзя :)",
                "handler": '',
                "next_step": "step-1",
                "keyboard": False,
                "branching": None,
            },
            "step-1": {
                "text": "Введите город, где хотите найти отели",
                "failure_text": "",
                "handler": 'handler_data',
                "old_step": "start",
                "next_step": "step0",
                "keyboard": False,
                "branching": None,
            },
            'step0': {
                "text": "Нажмите на ваш вариант:",
                "failure_text": 'Выберите вариант!',
                "handler": "handler_country",
                "old_step": "step-1",
                "next_step": "step1",
                "keyboard": True,
                "branching": None,
            },
            'step1': {
                "text": "Введите диапазон цен:\nвида: min  max\nНапример 3000  5000\nОзначает от 3000руб до 50000руб за 1 ночь",
                "failure_text": 'Формат ввода: число1[пробел]число2',
                "handler": "handler_false",
                "old_step": "step0",
                "next_step": "step2",
                "keyboard": False,
                "branching": None,
            },
            'step2': {
                "text": "Введите диапазон расстояний, на котором находится отель от центра\nвида min - max\nНапример 2 - 10\nОзначает от 2км до 10км",
                "failure_text": 'Формат ввода: число1[пробел]число2',
                "handler": "handler_min_max_cost",
                "old_step": "step1",
                "next_step": "step3",
                "keyboard": False,
                "branching": None,
            },
            'step3': {
                "text": "Будем искать в городе '{country}'.\nКоличество отелей, которые необходимо вывести в результате?",
                "failure_text": 'Должно быть целое число больше нуля, но меньше 25!',
                "handler": "handler_min_max_d",
                "old_step": "step2",
                "next_step": "step4",
                "keyboard": False,
                "branching": None,
            },
            'step4': {
                "text": "Нужно загружать фотографии для каждого отеля (“Да/Нет”)?",
                "failure_text": 'Да/Нет',
                "handler": "handler_quantity_hotels",
                "old_step": "step3",
                "next_step": "step5",
                "keyboard": False,
                "branching": None,
            },
            'step5': {
                "text": "{text}",
                "failure_text": '',
                "handler": "handler_photo",
                "old_step": "step4",
                "next_step": "end",
                "keyboard": False,
                "branching": 'step6',
            },
            'step6': {
                "text": "Количество фотографий?",
                "failure_text": 'Должно быть целое число больше нуля, но меньше XX!',
                "handler": "handler_photo",
                "old_step": "step5",
                "next_step": "step7",
                "keyboard": False,
                "branching": None,
            },
            'step7': {
                "text": "{text}",
                "failure_text": 'Должно быть целое число больше нуля, но меньше XX!',
                "handler": "handler_quantity_photos",
                "old_step": "step6",
                "next_step": "end",
                "keyboard": False,
                "branching": None,
            },

        }
    }
}
