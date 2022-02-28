import logging
from typing import Any

log_er = logging.getLogger('error')
log_info = logging.getLogger('info')


def configure_logging():
    log_info.setLevel(logging.INFO)
    chat_handler = logging.FileHandler("chat_log.log", encoding='UTF-8', mode='a')
    forma_string = logging.Formatter("%(asctime)s: %(message)s")
    chat_handler.setFormatter(forma_string)
    log_info.addHandler(chat_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter("%(asctime)s: %(message)s"))
    stream_handler.setLevel(logging.DEBUG)
    log_er.addHandler(stream_handler)

    file_handler = logging.FileHandler("error_log.log", encoding='UTF-8', mode='a')
    file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    file_handler.setLevel(logging.DEBUG)
    log_er.addHandler(file_handler)

    log_er.setLevel(logging.DEBUG)


configure_logging()


def catch_error(text_er: str) -> Any:
    '''
        Ловим ошибки, если нет обьекта на сервере
        :param text_er: Текст ошибки
    '''

    def catch_error_(func):
        def wrapper(*args, **kwargs):
            try:
                res = func(*args, **kwargs)
                return res
            except Exception as ex:
                text = f"func={func.__name__}:  args={args} kwargs={kwargs} json пришел без ключа={ex}"
                if text_er:
                    log_er.debug(text + "\n" + text_er)
                else:
                    log_er.debug(text)

        return wrapper

    return catch_error_


def repeat(func) -> Any:
    '''Повтор функции func запросов к серверу при ошибки'''

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as er:
            return func(*args, **kwargs)

    return wrapper
