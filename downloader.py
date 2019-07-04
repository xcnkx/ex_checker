import requests
import pandas as pd
from bs4 import BeautifulSoup
import ssl
import os
from tqdm import tqdm

ssl._create_default_https_context = ssl._create_unverified_context

USER = os.environ.get("WE_TSI_USER")

PASSWD = os.environ.get("WE_TSI_PASSWD")

import argparse  # 1. argparseをインポート

parser = argparse.ArgumentParser(
    description='Web engineering downloader from tsi system for TAs.')  # 2. パーサを作る

# 3. parser.add_argumentで受け取る引数を追加していく
parser.add_argument('-ex', nargs='*', type=int, required=True)  # オプション引数（指定しなくても良い引数）を追加
parser.add_argument('-p', '--proxy', type=int, default=0)

args = parser.parse_args()  # 4. 引数を解析

DOWNLOAD_SAVE_DIR = '/Users/Cris/Documents/WE_TA/2019/submissions/' + 'ex' + str(args.ex[0])


class crawler():
    # メールアドレスとパスワードの指定
    _USER = ""
    _PASS = ""
    _socks5_port = ""

    # セッションを開始
    res = requests.Response()
    session = requests.session()

    # ログイン

    def __init__(self, user, password, socks5_port=args.proxy):
        self._USER = user
        self._PASS = password
        self._socks5_port = socks5_port

        self.password = ''

        self._login_info = {
            "id": self._USER,
            "password": self._PASS,
            "session": "login"
        }

        self._proxies = {

            'http': 'socks5://127.0.0.1:' + str(socks5_port),
            'https': 'socks5://127.0.0.1:' + str(socks5_port)

        }

    # action
    def login(self, url_login="http://cseng.u-aizu.ac.jp:4080/WE19STD6/tsi/"):
        # url_login = "http://sealpv2.u-aizu.ac.jp/login/index.php"
        if args.proxy != 0:
            res_ = self.session.post(
                url_login, data=self._login_info, proxies=self._proxies)
            res_.raise_for_status()  # エラーならここで例外を発生させる
        else:
            res_ = self.session.post(
                url_login, data=self._login_info)
            res_.raise_for_status()
            print('test')  # エラーならここで例外を発生させる

        self.res = res_

        return res_

    def get_uploaded_table(self, url="http://cseng.u-aizu.ac.jp:4080/WE19STD6/tsi/"):

        soup = BeautifulSoup(self.res.text, "html.parser")
        password_list = soup.find_all("input", attrs={"type": "hidden", "name": "password"})
        # password_list =
        self.password = password_list[0]['value']
        get_up_info = {
            "id": self._USER,
            "password": self.password,
            "session": "menu",
            "choice": "checkuploaded",
            "x": "12",
            "y": "15"
        }

        if args.proxy != 0:
            res_uploaded = self.session.post(url, data=get_up_info, proxies=self._proxies)
            self.res = res_uploaded
            return res_uploaded.text
        elif args.proxy == 0:
            res_uploaded = self.session.post(url, data=get_up_info)
            self.res = res_uploaded
            return res_uploaded.text

    def get_files_id(self):
        soup = BeautifulSoup(self.res.text, "html.parser")

        files = soup.find_all("input", attrs={"type": "hidden", "name": "file"})
        files_id = []

        for f in files:
            files_id.append(f['value'])

        # print(files_id)
        id_df = pd.DataFrame(files_id)
        id_df = id_df.drop_duplicates()
        id_df.reset_index(drop=True, inplace=True)
        return id_df

        # for i, col in enumerate(columns):
        #     df = df.rename(columns={columns[i]: df.iloc[1, i]})
        #
        # df_ = df.drop([0, 1], axis=0)
        # df__ = df_.iloc[:, 1:].shift(-1, axis=1)
        # df_.iloc[:, 1:] = df__
        # df_.replace('-', 0, inplace=True)
        # df_.reset_index(drop=True, inplace=True)
        # return df_

    def download_file(self, file_name, file_id):
        """URL を指定してカレントディレクトリにファイルをダウンロードする
        """
        url = "http://cseng.u-aizu.ac.jp:4080/WE19STD6/tsi/"  # + file_name
        download_info = {
            "file": file_id,
            "id": self._USER,
            "password": self.password,
            "session": "downloaduploaded"
        }

        if args.proxy != 0:
            res_ = self.session.post(
                url, data=download_info, proxies=self._proxies, stream=True)
            res_.raise_for_status()  # エラーならここで例外を発生させる
        else:
            res_ = self.session.post(
                url, data=download_info, stream=True)
            res_.raise_for_status()  # エラーならここで例外を発生させる

        # save_file_name = url.split('/')[-1]

        save_file_path = os.path.join(DOWNLOAD_SAVE_DIR, file_name)

        with open(save_file_path, 'wb') as saveFile:
            saveFile.write(res_.content)


if __name__ == "__main__":
    c = crawler(USER, PASSWD)

    res = c.login()
    # print(res.text)
    uploaded_html = c.get_uploaded_table()
    # print(uploaded_html)
    files_id_df = c.get_files_id()
    df_list = pd.read_html(uploaded_html)

    # format table
    # drop columns line
    df = df_list[2].drop(0)
    # drop last 2 lines
    df.reset_index(drop=True, inplace=True)
    df = df.iloc[:, :-2]
    # add file_id column
    df['file_id'] = files_id_df
    # transform all letters to lowercase
    df_ = df.apply(lambda x: x.astype(str).str.lower())

    df_target = df[df_.iloc[:, 2].str.contains('ex' + str(args.ex[0]))]

    with tqdm(total=len(df_target)) as pbar:
        for index, student in df_target.iterrows():
            c.download_file(student[0] + "_" + student[2], student[3])
            pbar.update(1)
