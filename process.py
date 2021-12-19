import pandas as pd
import matplotlib.pyplot as plt
import os
import re
from scipy.integrate import simps
import numpy as np
from numpy import trapz
import math

from scaner import parser
from math import log10, floor


class ProcessFile:


    @staticmethod
    def round_sig(x, sig=3):
        return round(x, sig - int(floor(log10(abs(x)))) - 1)

    @staticmethod
    def split(df) :
        down = df[~df['Potential (V)'].diff().fillna(0).ge(0)].sort_values('Potential (V)')
        up = df[df['Potential (V)'].diff().fillna(0).ge(0)].sort_values('Potential (V)')
        return up, down

    @staticmethod
    def uncharge(down, m) :
        dV = down['Potential (V)'].max() - down['Potential (V)'].min()
        dT = down['Time (s)'].max() - down['Time (s)'].min()
        i = down['Current (A)'].abs().median()
        Cw = i*dT/dV/m

        Ew = 0.5 * Cw * dV**2 / 3600    # Wh/g
        Pw = 3600 * Ew / dT         # W/g

        down['Potential (V)'] -= down['Potential (V)'].min()

        sdown = simps(down['Potential (V)'], x=down['Time (s)'])
        if math.isnan(sdown):
            sdown = trapz(down['Potential (V)'], x=down['Time (s)'])
        # if sdown1 > dV*dT/2:
        #    sdown1 = dV*dT - sdown1
        Ci = 2*i*sdown/dV/dV/m

        Ei = i * sdown / 3600 / m   # Wh/g
        Pi = 3600 * Ei / dT         # W/g
        return Cw, Ci, Ew, Pw, Ei, Pi

    @staticmethod
    def vax(df, v, m):
        minA = df['Current (A)'].min()
        # up1 = up.sort_values('Potential (V)')
        # down1 = down.sort_values('Potential (V)')

        #down = df[df['Current (A)'].le(0)]
        #up = df[df['Current (A)'].ge(0)]
        iMin = df['Current (A)'].min()
        df['Current (A)'] -= df['Current (A)'].min()
        down = df[~df['Potential (V)'].diff().fillna(0).ge(0)].sort_values('Potential (V)')
        up = df[df['Potential (V)'].diff().fillna(0).ge(0)].sort_values('Potential (V)')

        # plt.plot(up['Potential (V)'], up['Current (A)'], 'g')
        # plt.plot(down['Potential (V)'], down['Current (A)'], 'o')
        # plt.show()

        sup = simps(up['Current (A)']-minA, x=up['Potential (V)'])
        if math.isnan(sup):
            sup = trapz(up['Current (A)']-minA, x=up['Potential (V)'])
        sdown = simps(down['Current (A)']-minA, x=down['Potential (V)'])
        if math.isnan(sdown):
           sdown = trapz(down['Current (A)']-minA, x=down['Potential (V)'])
        
        square = (sup - sdown)

        # print(f'{file} цикл={step} масса={m}г скорость={v}')
        C = square / ((df['Potential (V)'].max() - df['Potential (V)'].min()) * 2 * v * m)
        x = 0
        delta = (up.loc[(up['Potential (V)'] - x).abs().sort_values().head(3).index]['Current (A)'].mean() -
                      down.loc[(down['Potential (V)'] - x).abs().sort_values().head(3).index]['Current (A)'].mean()) \
                * 1e6

        return C, delta

    def VAT(self, cycle: int, df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
        self.ax.plot(df['Potential (V)'], df['Current (A)'], label=str(cycle))  # , 'g')
        if cycle == 1:
            self.ax.set_xlabel('напряжение (В)')
            self.ax.set_ylabel('ток (А)')
        v = self.v
        if not v:
            v = abs((df.iloc[-10]['Potential (V)'] - df.iloc[-20]['Potential (V)']) /
                    (df.iloc[-10]['Time (s)'] - df.iloc[-20]['Time (s)']))
        # ax.legend(['Potential (V)'], loc='upper left')
        # print('Расчет по ВАХ')
        if df['Potential (V)'].iloc[10] < 0:
            df['Potential (V)'] = - df['Potential (V)']
            df['Current (A)'] = - df['Current (A)']
        c, delta = self.vax(df, v, self.m)
        columns = ['cycle', 'ΔV, V/s', 'C/m, F/g', 'ΔA(V=0),μA']
        data = pd.DataFrame([[cycle, v, c, delta]], columns=columns)
        return data, columns

    def Ione(self, cycle: int, df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
        lst = df[df['Time (s)'] - df['Time (s)'].shift() < 0].index.tolist()
        for i in lst:
            time = df.loc[:i-1,'Time (s)'].max()
            df.loc[i:, 'Time (s)'] += time

        self.ax.plot(df['Time (s)'], df['Potential (V)'], label=str(cycle))  # , 'g')

        if cycle == 1:
            self.ax.set_xlabel('время (с)')
            self.ax.set_ylabel('напряжение (V)')

        # if df['Potential (V)'].iloc[10] < 0:
        #    df['Potential (V)'] = - df['Potential (V)']
        #    df['Current (A)'] = - df['Current (A)']

        lst = df.index[df['Current (A)'] * df['Current (A)'].shift() < 0].tolist()
        lst = [0] + lst + [len(df)]
        cnt = 0
        time = 0
        data = []
        for i, j in zip(lst, lst[1:]):
            section = df[i:j + (cnt % 2)].copy()
            cnt = cnt + 1
            if cnt % 2:
                continue
            if section.iloc[1]['Potential (V)'] < 0:
                section['Potential (V)'] = - section['Potential (V)']
            data.append([f'{cycle}.{cnt//2}', *self.uncharge(section.copy(), self.m)])

        columns = ['cycle',
                   'C/m \\,F/g', 'C/m ∫,F/g',
                   'E/m \\,Wh/g', 'P/m ∫,W/g',
                   'E/m ∫,Wh/g', 'P/m ∫,W/g'
                   ]
        data = pd.DataFrame(data, columns=columns)
        return data, columns


    def Ivv(self, cycle: int, df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
        if cycle == 1:
            self._time = 0
            self.ax.set_xlabel('время (с)')
            self.ax.set_ylabel('напряжение (V)')

        if cycle > 1 and df.loc[0, 'Time (s)'] < self._time:
            df['Time (s)'] += self._time
        self._time = df['Time (s)'].max()

        self.ax.plot(df['Time (s)'], df['Potential (V)'], label=str(cycle))  # , 'g')

        columns = ['cycle',
                   'C/m \\,F/g', 'C/m ∫,F/g',
                   'E/m \\,Wh/g', 'P/m ∫,W/g',
                   'E/m ∫,Wh/g', 'P/m ∫,W/g'
                   ]
        if cycle % 2:
            data = pd.DataFrame(columns=columns)
            return data, columns

        if df.iloc[1]['Potential (V)'] < 0:
            df['Potential (V)'] = - df['Potential (V)']

        data = pd.DataFrame([[cycle//2, *self.uncharge(df, self.m)]], columns=columns)
        return data, columns

    #   processFile body
    def __init__(self, file, m, v, ax):

        self.time = None
        cycle = 0
        self.m = m
        self.v = v
        self.ax = ax

    #    print(f'{file} цикл={step} масса={m*1e3}мг скорость=', end='')
        plt.style.use('ggplot')

        for rec in parser(file):

            df = pd.DataFrame(rec.data, columns=rec.head)

            if not cycle:
                # первый цикл - определяем тип файла
                median = df['Current (A)'].abs().median()
                s = ((df['Current (A)'].abs() - median).abs() < .1 * median).sum()
                if s > .75 * len(df):
                    lst = df.index[df['Current (A)'] * df['Current (A)'].shift() < 0].tolist()
                    if lst:
                        factory = self.Ione
                        print('разряд')
                    else:
                        factory = self.Ivv
                        print('пила')
                else:
                    factory = self.VAT
                    print('vax')

            cycle += 1

            data, columns = factory(cycle, df)
            if cycle == 1:
                self.resFile = data
            else:
                # data = pd.DataFrame([data], columns=columns)
                self.resFile = pd.concat([self.resFile, data], axis=0)
        # print(resFile.round(10).to_string(index=False))


    def __str__(self):
        pd.set_option('display.max_columns', 500)
        pd.set_option('display.width', 1000)
        return self.resFile.round(10).to_string(index=False)

"""
        up, down = split(df)
        # C = df['Current (A)'].abs()*df['Time (s)'].diff()/np.absolute(df['Potential (V)'].diff())

        
        if rt == 'VAX':
            ax.plot(df['Potential (V)'], df['Current (A)'], label=str(cycle))   # , 'g')
            ax.set_xlabel('напряжение (В)')
            ax.set_ylabel('ток (А)')
            # ax.legend(['Potential (V)'], loc='upper left')
            # print('Расчет по ВАХ')
            res = vax(v)
            resFile = pd.concat([resFile, res], axis=0, sort=False)
        elif rt == 'I':
            # print('Расчет по току разряда')
            ax.plot(df['Time (s)'], df['Potential (V)'], label=str(cycle))   # , 'g')
            ax.set_xlabel('время (с)')
            ax.set_ylabel('напряжение (В)')
            # ax.legend(['Potential (V)'], loc='upper left')

            res = current()
            resFile = pd.concat([resFile, res], axis=0)
            """

if __name__ == '__main__' :
    fig, ax = plt.subplots()
    print(ProcessFile(r'C:\Users\kazah\Downloads\700-1_100mVs.txt', 1, 0, ax))
    # print(ProcessFile(r'C:\Users\kazah\Downloads\0017-3 100mVs_-800_800mV.txt', 1, 0, ax))
    # print(ProcessFile(r'c:\Work\Алёна\31.01.20\01.txt ', 1, 0, ax))
    # plt.show()