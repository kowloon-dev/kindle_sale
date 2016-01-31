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
            self.currency_symbol = ci.currency_symbol
        except:
            err = "Read config failed.\n"
            log_control.logging.error(err + traceback.format_exc())
            raise

    def get_price(self,asin):

        # Initializing variables
        price = ""
        url = ""
        get_result = ""
        soup = ""
        scraped_code = ""
        price_textline = ""

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

        # seek textline contains "currency simbol"(ex. in US:$, in Japan:￥)
        for line in scraped_code:
            if line.find(self.currency_symbol) >= 0:
                price_textline = line
                break
            else:
                price_textline = ""

        if len(price_textline) == 0:
            log_control.logging.error(asin + " Extracting price_textline failed.")
            return

        # divide textline by currency simbol, and pick up second element
        price = price_textline.split(self.currency_symbol)[1]

        # remove carriage return
        price = price.replace("\n","")

        # remove comma
        price = price.replace(",","")

        # remove space
        price = price.replace(" ","")

        try:
            # If succeeded, return with price
            price = int(price)
            log_control.logging.debug(asin + " Extracting price succeeded.")
            return price
        except:
            # If failed, return with nothing
            log_control.logging.error(asin + " Extracting price failed.")
            return
