# -*- coding: utf-8 -*-

import config_import as ci
import log_control
from flask import Flask, render_template, request, redirect, url_for
from item_search import ItemSearch
from sqlite_query import SqlQuery
from jinja2 import FileSystemLoader

# Run Flask
app = Flask(__name__,static_folder=ci.flask_static_path)
app.jinja_loader = FileSystemLoader(ci.flask_templates_path)

# Import base URL for Kindle item
base_url = ci.base_url

# Routing
@app.route('/kindle_sale/')
def index():

    log_control.logging.debug("/.index: Started.")

    pagetitle = "Kindleセール通知 管理画面"
    text = "Kindleセール通知 管理画面"
    item_list_msg = "セール通知済みアイテム"

    # 登録済みアイテムを格納する変数を用意
    item_list = ""

    # SQLite実行用のインスタンスを生成
    sql = SqlQuery()
    # セール通知済みのアイテムリストを取得
    try:
        sale_noticed_result = sql.sale_noticed_item()
    except:
        raise

    for id,asin,title,price,discount_rate,flag in sale_noticed_result:

        # ASIN番号からWebページURLを生成
        url = base_url + asin + "/"

        item_list = item_list + "<tr><td><a href=" + url + ">" + title + "</a></td>" \
                    "<td>" + str(price) + "</td>" \
                    "<td>" + str(discount_rate) + "</td></tr>\n"

    return render_template('index.html',
                           text=text,
                           pagetitle=pagetitle,
                           item_list_msg=item_list_msg,
                           item_list=item_list)


@app.route('/kindle_sale/register', methods=['POST', 'GET'])
def post():

    log_control.logging.debug("/register.post: Started.")

    pagetitle = "アイテムの登録"

    # 検索結果格納用の変数を用意
    search_result = ""

    if request.method == 'POST':
        keyword = request.form['keyword']

        # ItemSearchクラスのインスタンスを作成
        itemsearch = ItemSearch()

        # 検索メソッド"item_search"を実行し、結果をxmlで受け取る
        response = itemsearch.item_search(keyword)
        for item in response:
            try:
                # 検索結果からタイトルその他のパラメタを取得
                title = item.find('title').text
                asin = item.find('asin').text
                binding = item.find('binding').text

                #タイトルにカテゴリ情報( "Kindle版" 等)を連結
                title = title + " [" + binding + "]"
                url = base_url + asin + "/"

                # 値引率を指定させるためのプルダウンメニュー
                pulldown = "<select name=discount_rate[]>\n" \
                           "<option value=\"\">-</option>\n"
                for rate in range(10, 101, 10):
                    pulldown = pulldown + "<option>" + str(rate) + "\n"

                # hidden属性でPOSTするASIN及びタイトル
                asin_post = "<input type=hidden name=asin[] value=\""+asin+"\">"
                title_post = "<input type=hidden name=title[] value=\"" + title + "\">"

                # "キーワード"もしくは"ASIN番号"のいずれかが結果に含まれているか検査し
                # 無関係なエントリを除外
                if keyword in title or keyword in asin:
                    search_result = search_result + "<tr><td><a href=" + url + ">" + title + "</a></td>" \
                                                    "<td>" + pulldown + asin_post + title_post + "</td></tr>\n"
            except:
                # パラメタの取得が失敗した場合はそのエントリを無視して次に進む
                pass

        return render_template('regist.html',
                               text = '"' + keyword + '"の検索結果', pagetitle=pagetitle, search_result= search_result)
    else:
        # POST以外で遷移してきた時はIndexページにリダイレクト
        return redirect(url_for('index'))


@app.route('/kindle_sale/register_exec', methods=['POST'])
def register_exec():

    log_control.logging.debug("/register_exec: Started.")

    pagetitle = "Kindleセール通知 管理画面"
    text = "Kindleセール通知 管理画面"
    registered_msg = "以下のアイテムを登録完了しました。"
    regist_err_msg = "以下のアイテムの登録に失敗しました。"

    # 登録完了したアイテム/失敗したアイテムの格納先を作成
    registered_item = ""
    regist_err_item = ""

    if request.method == 'POST':
        # POSTされた値を取得
        title_list = request.form.getlist('title[]')
        asin_list = request.form.getlist('asin[]')
        discount_rate_list = request.form.getlist('discount_rate[]')

        # SQLite実行用のインスタンスを生成
        sql = SqlQuery()

        for (title, asin, discount_rate) in zip(title_list, asin_list, discount_rate_list):

            # POST値のdiscount_rateに有効な値がセットされているアイテムのみ、新規登録実行
            if len(str(discount_rate)) > 0:
                sql_result = sql.initial_regist(title, asin, discount_rate)

                log_control.logging.debug("initial_result sql result:\n" + str(sql_result))

                #if len(str(sql_result)) > 0:
                if sql_result is not None:
                    regist_err_item = regist_err_item + "<li>" + title + "<br>" + str(sql_result) +"</li>\n"
                else:
                    registered_item = registered_item + "<li>" + title + "</li>\n"

        return render_template('index.html',
                                text=text,
                                pagetitle=pagetitle,
                                registered_msg=registered_msg,
                                regist_err_msg=regist_err_msg,
                                registered_item=registered_item,
                                regist_err_item=regist_err_item)
    else:
        # POST以外で遷移してきた時はIndexページにリダイレクト
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
