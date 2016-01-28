#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import config_import as ci
import log_control
from bottlenose import api
from bs4 import BeautifulSoup
import traceback

class ItemSearch:

    def __init__(self):
        try:
            self.access_key_id = ci.access_key_id
            self.secret_key = ci.secret_key
            self.associate_tag = ci.associate_tag
            self.search_index = ci.search_index
            self.item_page = ci.item_page
            self.region = ci.region
            self.amazon = api.Amazon(self.access_key_id, self.secret_key,
                                 self.associate_tag, Region=self.region)
        except:
            err = "Read config failed.\n"
            log_control.logging.error(err + traceback.format_exc())
            raise


    # 特定アイテムの詳細を取得する関数(ItemLookupをコール)
    def item_lookup(self, itemid):
        # 受け取ったItemIDを変数に格納
        self.itemid = itemid

        # 検索を実行
        response = self.amazon.ItemLookup(ItemId=self.itemid,ResponseGroup="ItemAttributes")
        soup = BeautifulSoup(response, "lxml")
        return soup.findAll('item')

    # キーワードに基づきアイテムを検索する関数(ItemSearchをコール)
    def item_search(self, keyword):
        # 受け取ったKeywordを変数に格納
        self.keyword = keyword

        # 検索を実行
        response = self.amazon.ItemSearch(SearchIndex=self.search_index,Keywords=self.keyword,
                                          ItemPage=self.item_page, ResponseGroup="Medium")
        soup = BeautifulSoup(response, "lxml")
        return soup.findAll('item')
