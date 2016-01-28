#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import config_import as ci
import log_control
import requests
import time
from bs4 import BeautifulSoup
import random
import traceback


class GetPrice:

    def __init__(self):
        try:
            self.base_url = ci.base_url
            self.price_tag = ci.price_tag
            self.price_class = ci.price_class
            self.retry_sleep_min = ci.retry_sleep_min
            self.retry_sleep_max = ci.retry_sleep_max
            self.retry_max = ci.retry_max
        except:
            err = "Read config failed.\n"
            log_control.logging.error(err + traceback.format_exc())
            raise

    def get_price(self,asin):

        # ASIN番号からWebページURLを生成
        url = self.base_url + asin + "/"

        retry_count = 0
        while True:
            # 商品ページのコードを取得
            log_control.logging.debug(asin + " 商品ページGET開始 URL: " + url)
            get_result = requests.get(url)

            # ステータスコードが200もしくはリトライ回数の上限に達したらループを抜ける
            if get_result.status_code == 200:
                log_control.logging.debug(asin + " GET成功(STATUS CODE= " + str(get_result.status_code) + ")")
                break
            elif retry_count >= self.retry_max:
                log_control.logging.error(asin + " リトライ回数の上限に到達しました. 本アイテムの価格取得を断念します.")
                break

            log_control.logging.debug(asin + " GET失敗(STATUS CODE= " + str(get_result.status_code) + "). リトライ待機...")

            # リトライカウントを加算し変数get_resultを空にしてからランダム時間スリープ
            retry_count += 1
            get_result = ""
            time.sleep(random.randint(self.retry_sleep_min,self.retry_sleep_max))

        # BeautifulSoupでHTMLをパースし、価格部分のコードを抽出
        soup = BeautifulSoup(get_result.text, "html.parser")
        scraped_code = soup.find("b", class_="priceLarge")

        # コードの各行を精査し、文字「￥」の含まれる行を探す
        #     見つけたら変数price_textlineに格納してループを抜ける
        #     見つからない場合は変数price_textlineの中身を空に維持
        for line in scraped_code:
            if line.find("￥") >= 0:
                price_textline = line
                break
            else:
                price_textline = ""

        if len(price_textline) == 0:
            log_control.logging.error(asin + " 価格の含まれる行を検出できませんでした.")
            return

        #  文字「￥」で価格の行を分割し、2番目の要素(文字「￥」より後ろの要素)を取り出し
        price = price_textline.split("￥")[1]

        # 改行文字を除去
        price = price.replace("\n","")

        # カンマを除去
        price = price.replace(",","")

        # スペースを除去
        price = price.replace(" ","")

        try:
            price = int(price)
            log_control.logging.debug(asin + " 価格の抽出に成功しました.")
            return price
        except:
            # 失敗した場合は空の戻り値を返す
            log_control.logging.error(asin + " 価格の抽出に失敗しました.")
            return
