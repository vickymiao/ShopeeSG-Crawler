# -*- coding: utf-8 -*-
import scrapy
import json
import urllib
import requests
import csv
import pandas as pd



class GoodsItem(scrapy.Item):
    itemid = scrapy.Field()
    shopid = scrapy.Field()
    price= scrapy.Field()
    price_max = scrapy.Field()
    liked_count = scrapy.Field()
    price_min = scrapy.Field()
    rating_star = scrapy.Field()
    rating_all = scrapy.Field()
    rating_count = scrapy.Field()
    hashtag_list = scrapy.Field()
    catid = scrapy.Field()
    categories = scrapy.Field()
    ctime = scrapy.Field()
    sold = scrapy.Field()
    currency = scrapy.Field()




allowed_domains = ['shopee.sg']
category_list_url = "https://mall.shopee.sg/api/v2/category_list/get"
subcategory_list_url = "https://mall.shopee.sg/api/v2/subcategory_list/get?catid="
search_items = "https://mall.shopee.sg/api/v2/search_items?by=pop&limit=50&order=desc&page_type=search"
get_url = "https://mall.shopee.sg/api/v2/item/get?"

response_cat = urllib.request.urlopen(category_list_url)

url_1 = []
url_2 = []
url_3 = []
diclist = []

# get category id

def parse(response_cat):
    data_list = json.loads(response_cat.read())['data']['category_list']
    for data in data_list:
        url_1.append(subcategory_list_url + str(data['catid']))
    return url_1

parse(response_cat)


# get item id
def parse_subcategory(response_sub):
    data_list = json.loads(response_sub.read())['data']['category_list']
    for data in data_list:
        url_2.append(search_items + "&newest=0&match_id={}".format(data['catid']))
    return url_2

for i in url_1:
    response_sub = urllib.request.urlopen(i)
    parse_subcategory(response_sub)


# go to item page
def parse_search(response_item):
    data_list = json.loads(response_item.read())['items']
    if len(data_list) == 0:
        return
    for data in data_list:
        cat_id = data['catid']
        url_3.append(get_url + "itemid={}&shopid={}".format(data['itemid'], data['shopid']))

for i in url_2:
    response_item = urllib.request.urlopen(i)
    parse_search(response_item)


# get item info
def parse_items(sub):
    data_list = json.loads(sub.read())['item']
    item = GoodsItem()
    item['itemid'] = data_list['itemid']
    item['shopid'] = data_list['shopid']
    item['price'] = data_list['price']
    item['liked_count'] = data_list['liked_count']
    item['rating_star'] = data_list['item_rating']['rating_star']
    item['rating_all'] = data_list['item_rating']['rating_count'][0]
    item['rating_count'] = ',' .join(map(str,data_list['item_rating']['rating_count']))
    item['hashtag_list'] = ','.join(data_list['hashtag_list'])
    item['catid'] = data_list['catid']
    categories = []
    countt = 1
    for catId in data_list['categories']:
        if countt >= 0:
            categories.append(catId['catid'])
            countt -= 1
    item['categories'] = categories
    item['ctime'] = data_list['ctime']
    solds = 0
    for sold in data_list['models']:
        solds += sold['sold']
    item['sold'] = solds
    diclist.append(item)
    return diclist

for i in url_3:
    sub = urllib.request.urlopen(i)
    parse_items(sub)

shopee = pd.DataFrame(diclist)
path=''
shopee.to_csv(path)
