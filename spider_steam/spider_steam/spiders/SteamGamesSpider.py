from lxml import html
import re

import requests
import scrapy
from ..items import *


class SteamgamesspiderSpider(scrapy.Spider):
    name = 'SteamGamesSpider'
    allowed_domains = {'steam.com'}
    start_urls = []
    categories = [
        'minecraft',
        'horror',
        'cats'
    ]
    empty_data = "---"

    def __init__(self):
        super().__init__()
        pages = ['page=1', 'page=2']
        for cat in self.categories:
            for page in pages:
                url = 'https://store.steampowered.com/search/?sort_by=&sort_order=0&supportedlang=english&'
                url += 'term=' + cat + '&' + page
                data = requests.get(url).content.decode('utf-8')
                response = html.document_fromstring(data)
                self.start_urls += response.xpath('//span[@class="title"]/ancestor::a/@href')

    def parse(self, response):
        item = SpiderSteamItem()

        name = response.xpath('//div[@class="apphub_AppName"]/text()').extract()
        reviews = response.xpath('//div[@class="subtitle column all"]/following-sibling::div[1]/meta[@itemprop="reviewCount"]/@content').extract()
        score = response.xpath('//div[@class="subtitle column all"]/following-sibling::div[1]/span/text()').extract()
        date = response.xpath('//div[text()="Released"]/following-sibling::div/text()').extract()
        developer = response.xpath('//div[text()="Developer"]/following-sibling::div[1]/a/text()').extract()

        user_tags = response.xpath('//div[text()="Popular user-defined tags for this product:"]/following-sibling::div[1]/a/text()').extract()
        user_tags = list(map(self.clean_data, user_tags))

        price = response.xpath('//div[contains(@class, "price")]/text()').extract()
        platforms = response.xpath('//div[@class="game_area_purchase_platform"]')

        category = response.xpath('//div[@class="blockbg"]//text()').extract()[3:-3:2]

        ##################

        name = self.get_first(name)
        reviews = self.get_first(reviews, "0 reviews")
        score = self.get_first(score, "0 reviews")
        date = self.get_first(date, self.empty_data)
        developer = self.get_first(developer, self.empty_data)
        price = self.get_first(price, self.empty_data)
        platforms = self.get_first(platforms, self.empty_data)

        if (date != self.empty_data):
            date = self.clean_data(date)
            if (date[1].isdigit()):
                date = [date[0] + date[1]] + date[2:].split(",")
            else:
                date = [date[0]] + date[1:].split(",")

        if (price != self.empty_data):
            price = self.clean_data(price)
            price = price[:-3]

        if (platforms != self.empty_data):
            platforms = platforms.extract()
            platforms = html.document_fromstring(platforms)
            platforms = platforms.xpath("//span/@class")
            platforms = ", ".join(platforms)


        item["name"] = name
        item["category"] = " ".join(category)
        item["reviews"] = reviews
        item["score"] = score
        item["date"] = date
        item["developer"] = developer
        item["user_tags"] = ", ".join(user_tags)
        item["price"] = price
        item["platforms"] = platforms

        return item

    def get_first(self, lst, label=""):
        if lst:
            return lst[0]
        else:
            return label

    def clean_data(self, data):
        exp = re.compile(f"[\t\s\n\r]")
        return re.sub(exp, "", data)