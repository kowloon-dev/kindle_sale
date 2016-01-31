#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import config_import as ci
import log_control
from sqlite_query import SqlQuery
import datetime
import traceback

class SaleCheck:

    def __init__(self):
        try:
            self.base_url = ci.base_url
            self.log_dir = ci.log_dir
            self.currency_symbol = ci.currency_symbol
            self.today = datetime.date.today()
        except:
            err = "Read config failed.\n"
            log_control.logging.error(err + traceback.format_exc())
            raise

        # Creating a SQL instance
        self.sql = SqlQuery()

    def sale_check(self, id, asin, title, price, price_today, discount_rate):

        log_control.logging.debug("Started.")

        # Initializing variables
        item_logfile = ""
        sale_check_result = ""
        url = ""
        discount_today = ""

        # Constructing item-price logfile
        item_logfile = self.log_dir + asin + ".csv"

        if price is not None:
            # Calculating today's discount rate
            discount_today = round((((price - price_today) / price) * 100))

            f = open(item_logfile, mode="a", encoding="utf-8")
            f.write(str(self.today) + "," + str(price) + "," + str(discount_today) + "\n")
            f.close()

            # Deciding whether "today's discount rate" is greater than or equal "threshold rate"
            if discount_today >= discount_rate:

                url = self.base_url + asin + "/"

                # Constructing mail report text
                line1 = title + " ("+ asin +")\n"
                line2 = "登録価格: ¥" + str(price) + "\n"
                line3 = "本日価格: ¥" + str(price_today) + "\n"
                line4 = "値引率: " + str(discount_today) + "%\n"
                line5 = url + " \n"
                line6 = "\n"
                sale_check_result = line1+line2+line3+line4+line5+line6

                log_control.logging.debug(asin + title + " sale has detected. result:\n" + sale_check_result)

                # Execute query to activate "This item has reported" flag
                try:
                    self.sql.update_flag(id)
                    return sale_check_result
                except:
                    log_control.logging.error(asin + title + " update_flag failed.")
                    raise
            else:
                # If "today's discount rate" is less than "threshold rate", return with nothing
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
