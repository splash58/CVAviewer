import re
import pandas as pd
from myEnum import MyEnum

class Scaner:
    def __init__(self, fileName):
        self.fileName = fileName
        pass


def parser(fileName):

    State = MyEnum(
        (
            'начало',
            'инфа',
            'после_инфы',
            'заголовок',
            'данные',
        )
    )
    state = State.начало
    ret = type('', (), {})()
    ret.head = []
    ret.data = []

    with open(fileName) as f:
        for line in f:
            line = line.strip()
            if state == State.начало:
                if line.startswith('Time (s),') or line.startswith('Время, с.,'):
                    line = re.split(r'\s{3,}', line)
                    ret.head = list(map(lambda s:  s.strip().strip(',')
                                                    .replace('Время, с.', 'Time (s)')
                                                    .replace('Потенциал, В', 'Potential (V)')
                                                    .replace('Ток, А', 'Current (A)'),
                                        line))
                    state = State.инфа
                continue
            elif state == State.инфа:
                if line == '':
                    yield ret
                    ret.head = []
                    ret.data = []
                    state = State.начало
                else:
                    line = line.strip().replace(',', '.')
                    ret.data.append(list(map(float,
                                              map(str.strip, re.split(r'\s+', line)))))

    if ret.head and ret.data:
        yield ret


if __name__ == '__main__':
    import pandas as pd

    for rec in parser(r'c:\Users\publi\Downloads\1-100.txt'):
        df = pd.DataFrame(rec.data, columns=rec.head)
        print(df)