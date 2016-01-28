#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import config_import as ci
import log_control
import sqlite3
import traceback


class SqlQuery:
    def __init__(self):
        try:
            self.db = ci.db
            self.item_table = ci.item_table
        except:
            err = "Read config failed.\n"
            log_control.logging.error(err + traceback.format_exc())
            raise

    # テーブルへのアイテム登録時に実行される関数
    def initial_regist(self, title, asin, discount_rate):

        log_control.logging.debug("SqlQuery.initial_regist: Started.")

        # Initializing variables
        dupecheck_query = ""
        dupecheck_result = ""
        dupecheck_err = ""
        regist_query = ""
        regist_err = ""

        # Connect SQLite3
        self.conn = sqlite3.connect(self.db)
        self.cur = self.conn.cursor()

        # Construct SQL query
        dupecheck_query = "SELECT id,asin FROM " + self.item_table + " WHERE asin = '" + asin + "'"
        log_control.logging.debug("dupecheck_query: " + dupecheck_query)

        # Query execute
        try:
            self.cur.execute(dupecheck_query)
            dupecheck_result = self.cur.fetchone()
            log_control.logging.debug("dupecheck_query success.")
        except:
            dupecheck_err = "dupecheck_query failed.\n"
            log_control.logging.error(dupecheck_err + traceback.format_exc())
            raise

        if dupecheck_result is None:
            # 重複無しの場合は新規登録クエリに進む
            regist_query = "INSERT INTO " + self.item_table + "(asin, title, discount_rate)" \
                        "VALUES ('" + asin + "', '" + title + "', " + discount_rate + ")"

            log_control.logging.debug("regist_query: " + regist_query)

            # Query execute
            try:
                self.cur.execute(regist_query)
                self.cur.fetchall()
                self.conn.commit()
                log_control.logging.debug("regist_query success.")
            except:
                regist_err = "regist_query failed.\n"
                log_control.logging.error(regist_err + traceback.format_exc())
                raise
            finally:
                self.conn.close()
        else:
            for id in dupecheck_result:
                dupe_msg = "[ERROR] 当該アイテムはID:" + str(id) + "でDBに登録済みです。\n"
                return dupe_msg

    # 既存の全レコードをDBから取得する際に使用される関数
    def select_all_item(self):

        log_control.logging.debug("SqlQuery.select_all_item: Started.")

        # Initializing variables
        all_item_query = ""
        all_item_result = ""
        all_item_err = ""

        self.conn = sqlite3.connect(self.db)
        self.cur = self.conn.cursor()

        all_item_query = "SELECT id,asin,title,price,discount_rate,flag FROM " + self.item_table + \
                " WHERE flag is 0"
        log_control.logging.debug("Query: " + all_item_query)

        try:
            self.cur.execute(all_item_query)
            all_item_result = self.cur.fetchall()
            log_control.logging.debug("Query success.")
            return all_item_result
        except:
            all_item_err = "Query failed.\n"
            log_control.logging.error(all_item_err + traceback.format_exc())
            raise
        finally:
            self.conn.close()

    # 通知済みのレコードをDBから取得する際に使用される関数
    def sale_noticed_item(self):

        log_control.logging.debug("Started.")

        # Initializing variables
        sale_noticed_query = ""
        sale_noticed_result = ""
        sale_noticed_err = ""

        self.conn = sqlite3.connect(self.db)
        self.cur = self.conn.cursor()

        sale_noticed_query = "SELECT id,asin,title,price,discount_rate,flag FROM " + self.item_table + \
                " WHERE flag is 1"
        log_control.logging.debug("Query: " + sale_noticed_query)

        try:
            self.cur.execute(sale_noticed_query)
            sale_noticed_result = self.cur.fetchall()
            log_control.logging.debug("Query success.")
            return sale_noticed_result
        except:
            sale_noticed_err = "Query failed.\n"
            log_control.logging.error(sale_noticed_err + traceback.format_exc())
            raise
        finally:
            self.conn.close()


    # 初回のセールチェック時にpriceカラムに現在価格を格納する関数
    def update_price(self, id, price):

        log_control.logging.debug("Started.")

        # Initializing variables
        update_price_query = ""
        update_price_err = ""

        # Connect SQLite3
        self.conn = sqlite3.connect(self.db)
        self.cur = self.conn.cursor()

        # Construct SQL query
        update_price_query = "UPDATE " + self.item_table + " SET price = " + str(price) + " WHERE id = " + str(id)
        log_control.logging.debug("Query: " + update_price_query)

        # Query execute
        try:
            self.cur.execute(update_price_query)
            self.cur.fetchall()
            self.conn.commit()
            log_control.logging.debug("Query success.")
        except:
            update_price_err = "Query failed.\n"
            log_control.logging.error(update_price_err + traceback.format_exc())
            raise
        finally:
            self.conn.close()

    # セールを検知したアイテムについて、報告済みのフラグを立てる関数
    def update_flag(self, id):

        log_control.logging.debug("Started.")

        # Initializing variables
        update_flag_query = ""
        update_flag_err = ""

        # Connect SQLite3
        self.conn = sqlite3.connect(self.db)
        self.cur = self.conn.cursor()

        # Construct SQL query
        update_flag_query = "UPDATE " + self.item_table + " SET flag = 1 WHERE id = " + str(id)
        log_control.logging.debug("Query: " + update_flag_query)

        # Query execute
        try:
            self.cur.execute(update_flag_query)
            self.cur.fetchall()
            self.conn.commit()
            log_control.logging.debug("Query success.")
        except:
            update_flag_err = "Query failed.\n"
            log_control.logging.error(update_flag_err + traceback.format_exc())
            raise
        finally:
            self.conn.close()
