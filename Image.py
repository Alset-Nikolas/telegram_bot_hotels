class Image:
    def __init__(self, id_: int, url: str):
        '''
        Обьект картинка
        :param id_: id картинки
        :param url: url картинки
        '''
        self.id_ = id_
        self.size = 'z'
        self.url = url.format(size=self.size)

    def __str__(self):
        return f"{self.url}"
