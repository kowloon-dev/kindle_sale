#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import log_control
from mail_send import MailSend
from sale_check import SaleCheck
from sqlite_query import SqlQuery
from get_price import GetPrice

# セール検出時の報告メール用の変数を作成
sale_msg = ""

# エラーメッセージ格納用のリストを作成
err_msg = []

# SQLite3実行用のインスタンスを生成
sql = SqlQuery()

# クエリを発行し、DBに登録済みのアイテムを取得
try:
    all_item = sql.select_all_item()
except:
    err_msg.append("sql.select_all_item failed.")

if 'all_item' in locals():

    # 価格取得処理のインスタンスを生成
    gp = GetPrice()

    # セール発生判定処理のインスタンスを生成
    sc = SaleCheck()

    for id,asin,title,price,discount_rate,flag in all_item:

        # セール結果を格納する変数を初期化
        sale_check_result = ""

        # 今日の価格を取得
        try:
            price_today = gp.get_price(asin)
        except:
            err_msg.append(asin + title + "get_price failed.")

        log_control.logging.debug(asin + title + " price_today: " +str (price_today))

        # 今日の価格取得に成功した場合にのみセール判定に進む
        if price_today is not None:
            # セールの有無を判定
            log_control.logging.debug(asin + title + " sale_check started.")

            sale_check_result = sc.sale_check(id,asin,title,price,price_today,discount_rate)

            if sale_check_result is not None:
                # sale_checkの戻り値に値があれば"セール発生"と見なす
                sale_msg = sale_msg + str(sale_check_result)
            else:
                # sale_checkの戻り値が全く空の場合にはセール発生無しと判定
                pass
        else:
            # 今日の価格取得の実行結果が空の場合は異常が発生したと判断
            get_price_err = (asin + title + " get_price failed.")
            log_control.logging.error(get_price_err)
            err_msg.append(get_price_err)


# リスト型で格納されているエラーメッセージをstr型で連結
err_msg = "\n".join(err_msg)

# セール検知結果(sale_msg)、エラーメッセージ(err_msg)のいずれかに値があればメール送信処理を実行
if len(sale_msg) > 0 or len(err_msg) > 0:
    # メール本文を作成
    mail_body = ""
    if len(sale_msg) > 0:
        mail_body = "Kindle本のセールを検知しました。\n\n" + sale_msg + "\n"
    if len(err_msg) > 0:
        mail_body = mail_body + "Kindle本のセール確認でエラーが発生しました。\n" \
                                "詳細はログを確認して下さい。\n" \
                                "エラーサマリ:\n"+ err_msg + "\n"

    # MailSendクラスのインスタンスを作成し、メール送信
    ms = MailSend()
    # メール送信を実行
    mail_res = ms.mail_send(mail_body)
else:
    pass




