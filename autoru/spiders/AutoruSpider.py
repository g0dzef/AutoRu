import scrapy
import pandas as pd

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from ..items import AutoruItem

import time
import json


class TestSpider(CrawlSpider):
    name = 'autoru'
    allowed_domains = ['auto.ru']
    start_urls = ['https://auto.ru/cars/all/']

    post_rule = LinkExtractor(
        restrict_css='a.Link.ListingItemTitle__link')
    pagination_rule = LinkExtractor(
        restrict_css='a.Button.Button_color_white.Button_size_s.Button_type_link.Button_width_default'
                     '.ListingPagination__next')

    rules = (
        Rule(post_rule, callback='parse_item', follow=True),
        Rule(pagination_rule, follow=True),
    )
    counter = 0

    def parse_item(self, response):
        self.counter += 1
        print(f'{self.counter} processing: ' + response.url)

        if list(response.url)[21] == 'u':

            title = response.xpath(
                '//*[@id="app"]/div/div[2]/div[3]/div[2]/div/div[2]/div/div[2]/div[1]/div[1]/h1/text()').get()

            sale_data_attributes = response.xpath(
                '//*[@id="sale-data-attributes"]/@data-bem').get()
            sale_data_attributes = json.loads(
                sale_data_attributes.replace("'", '"'))
            mileage = sale_data_attributes['sale-data-attributes']['km-age']
            model_name = sale_data_attributes['sale-data-attributes']['model']
            brand = sale_data_attributes['sale-data-attributes']['markName']
            segment = sale_data_attributes['sale-data-attributes']['segment']
            transmission = sale_data_attributes['sale-data-attributes']['transmission']
            year = sale_data_attributes['sale-data-attributes']['year']
            engine_type = sale_data_attributes['sale-data-attributes']['engine-type']
            image_url = sale_data_attributes['sale-data-attributes']['image']

            yield scrapy.Request(
                url=response.css(
                    'a.Link.SpoilerLink.CardCatalogLink.SpoilerLink_type_default::attr(href)').get(),
                callback=self.parse2,
                meta={'sell_id': response.css(
                    'div.CardHead__infoItem.CardHead__id::text').get().replace('№ ', ''),
                    'bodyType': response.xpath(
                    '//*[@id="app"]/div/div[2]/div[3]/div[2]/div/div[2]/div/div[6]/div[1]/ul/li[3]/span[2]/a/text()').get(),
                    'brand': brand,
                    'car_url': response.url,
                    'color': response.xpath(
                    '//*[@id="app"]/div/div[2]/div[3]/div[2]/div/div[2]/div/div[6]/div[1]/ul/li[4]/span[2]/a/text()').get(),
                    'description': response.css('div.CardDescriptionHTML *::text').getall(),
                    'image': 'https:' + response.css('img.ImageGalleryDesktop__image::attr(src)').get(),
                    'mileage': mileage,
                    'modelDate': year,
                    'model_name': model_name,
                    'owners': response.xpath(
                    '//*[@id="app"]/div/div[2]/div[3]/div[2]/div/div[2]/div/div[6]/div[1]/ul/li[12]/span[2]/text()').get(),
                    'licence': response.xpath(
                    '//*[@id="app"]/div/div[2]/div[3]/div[2]/div/div[2]/div/div[6]/div[1]/ul/li[13]/span[2]/text()').get(),
                    'wheel': response.xpath(
                    '//*[@id="app"]/div/div[2]/div[3]/div[2]/div/div[2]/div/div[6]/div[1]/ul/li[10]/span[2]/text()').get(),
                    'status': response.xpath(
                    '//*[@id="app"]/div/div[2]/div[3]/div[2]/div/div[2]/div/div[6]/div[1]/ul/li[11]/span[2]/text()').get(),
                    'customs': response.xpath(
                    '//*[@id="app"]/div/div[2]/div[3]/div[2]/div/div[2]/div/div[6]/div[1]/ul/li[14]/span[2]/text()').get(),
                    'exchange': response.xpath(
                    '//*[@id="app"]/div/div[2]/div[3]/div[2]/div/div[2]/div/div[6]/div[1]/ul/li[15]/span[2]/text()').get(),
                })
        else:
            pass

    def parse2(self, response):

        yield {
            'sell_id': response.meta['sell_id'],
            'body_type': response.meta['bodyType'],
            'brand': response.meta['brand'],
            'car_url': response.meta['car_url'],
            'color': response.meta['color'],
            # 'description': response.meta['description'],
            'engine_displacement': response.css('dd.list-values__value::text').get(),
            'engine_power': response.css('dd.list-values__value::text').getall()[1],
            'fuel_type': response.css('dd.list-values__value::text').getall()[3],
            'image': response.meta['image'],
            'mileage': response.meta['mileage'],
            'model_date': response.meta['modelDate'],
            'model_name': response.meta['model_name'],
            'number_of_doors': response.xpath(
                '/html/body/div[9]/div[2]/div[2]/div/div/div/div[2]/div[2]/div[3]/div[1]/div[1]/dl/dd[3]/text()').get(),
            'number_of_seats': response.xpath(
                '/html/body/div[9]/div[2]/div[2]/div/div/div/div[2]/div[2]/div[3]/div[1]/div[1]/dl/dd[4]/text()').get(),
            'parsing_unixtime': str(time.time),
            'vehicle_transmission': response.xpath(
                '/html/body/div[9]/div[2]/div[2]/div/div/div/div[2]/div[2]/div[2]/div[2]/div[1]/dl/dd[3]/text()').get(),
            'vendor': response.xpath(
                '/html/body/div[9]/div[2]/div[2]/div/div/div/div[2]/div[2]/div[3]/div[1]/div[1]/dl/dd[1]/text()').get(),
            'owners': response.meta['owners'],
            'licence': response.meta['licence'],
            'type_of_drive': response.xpath(
                '/html/body/div[9]/div[2]/div[2]/div/div/div/div[2]/div[2]/div[2]/div[2]/div[2]/dl/dd[2]/text()').get(),
            'wheel': response.meta['wheel'],
            'status': response.meta['status'],
            'customs': response.meta['customs'],
            'exchange': response.meta['exchange'],
            'consumption': response.xpath(
                '/html/body/div[9]/div[2]/div[2]/div/div/div/div[2]/div[2]/div[2]/div[2]/div[2]/dl/dd[3]/text()').get(),
        }