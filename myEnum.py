class MyEnum():
    def __init__(self, names):
        for i, x in enumerate(names):
            self.__dict__[x] = i+1

    def __getitem__(self, item):
        if not isinstance(item, int):
            raise TypeError(f'myEnum: неверный тип ключа {item}')
        for k, v in self.__dict__.items():
            if v == item:
                return k
        raise KeyError(f'myEnum: ключа {item} нет в этом перечислении')

    def synonym(self, old, new):
        try:
            self.__dict__[new] = getattr(self, old)
        except AttributeError:
            raise AttributeError('myEnum: такого имени нет в этом перечислении')

    def __setattr__(self, key, value):
        raise AttributeError('Denied.')

    def append(self, name, value=None):
        if value is None:
            value = max(self.__dict__.values()) + 1
        try:
            getattr(self, name)
        except AttributeError:
            pass
        else:
            raise AttributeError(f'myEnum: такое имя уже есть {name}')

        try:
            self[value]
        except KeyError:
            pass
        else:
            raise AttributeError(f'myEnum: такое значение уже есть.\n'
                                 f'Вы можете назначить синоним на это значение: '
                                 f'State.synonym(State[{value}], "{name}")')

        self.__dict__[name] = value

    def __str__(self):
        return self.__dict__.__str__()


if __name__ == '__main__':
    State = MyEnum(
        names=(
            'начало',
            'инфа',
            'после_инфы',
            'заголовок',
            'данные',
        )
    )

    print(State.инфа)
    State.synonym('инфа', 'info')
    print(State.info)

    State.synonym(State[3], 'info1')
    print(State.info1)

    State.append('5i')
    print(State)
