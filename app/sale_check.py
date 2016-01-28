#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import config_import as ci
import log_control
from sqlite_query import SqlQuery
import traceback

class SaleCheck:

    def __init__(self):
        try:
            self.base_url = ci.base_url
        except:
            err = "Read config failed.\n"
            log_control.logging.error(err + traceback.format_exc())
            raise

        # SQL実行用のインスタンスを生成
        self.sql = SqlQuery()

    def sale_check(self, id, asin, title, price, price_today, discount_rate):

        log_control.logging.debug("Started.")

        # Initializing variables
        sale_check_result = ""
        url = ""
        discount_today = ""

        if price is not None:
            # 現時点の値引率を算出
            discount_today = round((((price - price_today) / price) * 100))

            # 現時点の値引率がDBに事前登録されている閾値以上か判定
            if discount_today >= discount_rate:

                # ASIN番号からWebページURLを生成
                url = self.base_url + asin + "/"

                # メール報告用の文章作成
                line1 = title + " ("+ asin +")\n"
                line2 = "登録価格: ¥" + str(price) + "\n"
                line3 = "本日価格: ¥" + str(price_today) + "\n"
                line4 = "値引率: " + str(discount_today) + "%\n"
                line5 = url + " \n"
                line6 = "\n"
                sale_check_result = line1+line2+line3+line4+line5+line6

                log_control.logging.debug(asin + title + " sale has detected. result:\n" + sale_check_result)

                # DBの「通知済み」フラグに1を立てるクエリーを実行
                try:
                    self.sql.update_flag(id)
                    return sale_check_result
                except:
                    log_control.logging.error(asin + title + " update_flag failed.")
                    raise
            else:
                # 現時点の値引率が閾値を下回っている場合は空のままの戻り値を返す
                log_control.logging.debug(asin + title + " sale has not detected.")
                return sale_check_result

        # DBから取得した価格(price)の中身が空の場合は"今回が初回実行"と判断し
        # 本日の価格を当該アイテムのpriceカラムにInsertして処理を終える
        else:
            # UPDATEのクエリを発行
            try:
                self.sql.update_price(id, price_today)
                return sale_check_result
            except:
                raise
