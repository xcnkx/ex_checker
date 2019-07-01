import requests
import csv
import pandas as pd
from urllib.request import urlopen
from bs4 import BeautifulSoup
import ssl
import os
ssl._create_default_https_context = ssl._create_unverified_context
from urllib.parse import urljoin

# USER = os.environ.get("WE_USER")
USER = "m5221102"

# PASSWD = os.environ.get("WE_PASS")
PASSWD = "WGfTgJ4l"

import argparse    # 1. argparseをインポート

parser = argparse.ArgumentParser(
    description='Web engineering downloader from tsi system for TAs.')    # 2. パーサを作る

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
            "id": self._USER,
            "password": self._PASS,
            "session": "login"
        }

        self._proxies = {

            'http': 'socks5://127.0.0.1:' + socks5_port,
            'https': 'socks5://127.0.0.1:' + socks5_port

        }

    # action
    def login(self, url_login="http://cseng.u-aizu.ac.jp:4080/WE19STD6/tsi/"):
        # url_login = "http://sealpv2.u-aizu.ac.jp/login/index.php"
        if int(args.proxy) != 0:
            res = self.session.post(
                url_login, data=self._login_info, proxies=self._proxies)
            res.raise_for_status()  # エラーならここで例外を発生させる
        else:
            res = self.session.post(
                url_login, data=self._login_info)
            res.raise_for_status()  # エラーならここで例外を発生させる

        print(res.text)
        return res

    def get_uploaded_table(self, url="http://cseng.u-aizu.ac.jp:4080/WE19STD6/tsi/", res = session):

        soup = BeautifulSoup(res.text, "html.parser")
        password = soup.find("input", attrs={"type":"hidden", "name": "password"})
        get_up_info = {
            "id": self._USER,
            "password": password["value"],
            "session": "login"
        }


        if int(args.proxy) != 0:
            res = self.session.post(url, data= ,proxies=self._proxies)
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
if __name__ == "__main__":
    c = crawler(USER, PASSWD)

    res = c.login()
    c.get_uploaded_table(res=res)
    # df_list = c.get_dataframes()
    #
    # df = c.format_df(df_list[0])
    # ex = args.ex
    #
    # calculator = calculator(df=df, ex=ex)
    #
    # score_table = pd.concat(
    #     [df.iloc[:-2, 0], calculator.calculate_score()], axis=1)
    # score_table_s = score_table.sort_values(by=['Surname First name'])
    # score_table_s.reset_index(drop=True, inplace=True)
    # print(score_table_s)