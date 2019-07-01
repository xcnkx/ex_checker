import requests
import csv
import pandas as pd
from urllib.request import urlopen
from bs4 import BeautifulSoup
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
from urllib.parse import urljoin

USER = "m5221102"
PASSWD = "Cnkamia222"

import argparse    # 1. argparseをインポート

parser = argparse.ArgumentParser(
    description='Software Engineering revision calculation grading app.')    # 2. パーサを作る

# 3. parser.add_argumentで受け取る引数を追加していく
parser.add_argument('-ex', nargs='*', type=int, required=True)    # オプション引数（指定しなくても良い引数）を追加
parser.add_argument('-p', '--proxy', default='0')

args = parser.parse_args()    # 4. 引数を解析


class crawler():

    # メールアドレスとパスワードの指定
    _USER = ""
    _PASS = ""
    _socks5_port = ""

    # セッションを開始
    session = requests.session()
    # ログイン

    def __init__(self, user, passwd, socks5_port=args.proxy):
        self._USER = user
        self._PASS = passwd
        self._socks5_port = socks5_port

        self._login_info = {
            "username": self._USER,
            "password": self._PASS,
            # "back": "index.php",
            "rememberusername": "1"
        }
        self._proxies = {

            'http': 'socks5://127.0.0.1:' + socks5_port,
            'https': 'socks5://127.0.0.1:' + socks5_port

        }

    # action
    def login(self, url_login="http://sealpv2.u-aizu.ac.jp/login/index.php"):
        # url_login = "http://sealpv2.u-aizu.ac.jp/login/index.php"
        if int(args.proxy) != 0:
            res = self.session.post(
                url_login, data=self._login_info, proxies=self._proxies)
            res.raise_for_status()  # エラーならここで例外を発生させる
        else:
            res = self.session.post(
                url_login, data=self._login_info)
            res.raise_for_status()  # エラーならここで例外を発生させる
        return res

    def get_html(self, url="http://sealpv2.u-aizu.ac.jp/grade/report/grader/index.php?id=9"):

        if int(args.proxy) != 0:
            res = self.session.get(url, proxies=self._proxies)
            return res.text
        else:
            res = self.session.get(url)
            return res.text

    def get_dataframes(self):
        df_list = pd.read_html(self.get_html())
        return df_list

    def format_df(self, df):
        columns = df.columns

        for i, col in enumerate(columns):
            df = df.rename(columns={columns[i]: df.iloc[1, i]})

        df_ = df.drop([0, 1], axis=0)
        df__ = df_.iloc[:, 1:].shift(-1, axis=1)
        df_.iloc[:, 1:] = df__
        df_.replace('-', 0, inplace=True)
        df_.reset_index(drop=True, inplace=True)
        return df_


class calculator:

    def __init__(self, df, ex=[]):
        self.df = df
        self.ex = ex

    def calculate_score(self):
        score = pd.DataFrame([], columns=['score'], index=range(len(df) - 2))

        for i in range(len(df) - 2):
            total = 0
            for j in self.ex:
                total += (float(df.iloc[i, j + 1]) + 100) / 2
                score.iloc[i, 0] = total / len(args.ex)
        score.replace(50, 0, inplace=True)
        return score


if __name__ == "__main__":

    c = crawler(USER, PASSWD)

    c.login()
    df_list = c.get_dataframes()

    df = c.format_df(df_list[0])
    ex = args.ex

    calculator = calculator(df=df, ex=ex)

    score_table = pd.concat(
        [df.iloc[:-2, 0], calculator.calculate_score()], axis=1)
    score_table_s = score_table.sort_values(by=['Surname First name'])
    score_table_s.reset_index(drop=True, inplace=True)
    print(score_table_s)
