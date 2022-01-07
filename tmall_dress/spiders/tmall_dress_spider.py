# -*- coding: utf-8 -*-
import scrapy, csv
from scrapy.exceptions import CloseSpider
from scrapy import Request
# from urlparse import urlparse
from json import loads
from datetime import date
from collections import OrderedDict
import re, requests, random

class tmall_dressSpider(scrapy.Spider):

    name = "tmall_dress_spider"

    use_selenium = True
    field_names = ['Product Code', 'url']
    file_name = 'tmall_dress_result.xlsx'
    result_data_list = {}
    total_count = 0

    proxy_text = requests.get('https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list.txt').text
    list_proxy_temp = proxy_text.split('\n')

    list_proxy = []
    for line in list_proxy_temp:
        if line.strip() !='' and (line.strip()[-1] == '+' or line.strip()[-1] == '-'):
            ip = line.strip().split(':')[0].replace(' ', '')
            port = line.split(':')[-1].split(' ')[0]
            list_proxy.append('http://'+ip+':'+port)
###########################################################

    def __init__(self, *args, **kwargs):
        super(tmall_dressSpider, self).__init__(*args, **kwargs)

###########################################################
    def start_requests(self):


        f2 = open('input_data/input_1.csv')

        csv_items = csv.DictReader(f2)
        proxy = random.choice(self.list_proxy)

        for i, row in enumerate(csv_items):
            if not row['URL']:
                continue

            yield scrapy.Request(row['URL'], callback=self.parse, meta={'code': row['PRODUCT CODE'], 'url': row['URL'], 'proxy':proxy}, errback=self.errCall)
            break
        f2.close()

###########################################################

    def parse(self, response):
        if 'tmall.com' in response.url:
            skuMaps = response.text.split('"skuMap":')
            if len(skuMaps) > 1:
                skuProps = response.text.split('"skuList":')
                skuProps = skuProps[-1].split('],"def')[0] + ']'
                prop_json_data = loads(skuProps)

                skuIdList = []
                color_list = []
                prop_data = OrderedDict()
                for p in prop_json_data:
                    names = p['names']
                    sku_id = p['skuId']
                    skuIdList.append(sku_id)
                    prop_data[sku_id] = names

                skuMaps = skuMaps[-1].split(',"salesProp"')[0]
                json_data = loads(skuMaps)

                # for key in json_data.keys():
                #     data = json_data[key]
                #     skuid = data['skuId']
                #     price = data['price']
                #     stock = data['stock'] + 'pcs'
                #
                #     color = prop_data[skuid].split(' ')[-1]
                #     size = prop_data[skuid].split(' ')[0]
                #     if 'Color {}'.format(str(i + 1)) not in self.field_names:
                #         self.field_names.append('Color {}'.format(str(i + 1)))
                #     item['Color {}'.format(str(i + 1))] = key.split('&g')[0]
                #
                #     if 'Size {}'.format(str(i + 1)) not in self.field_names:
                #         self.field_names.append('Size {}'.format(str(i + 1)))
                #     item['Size {}'.format(str(i + 1))] = key.split('&g')[1]
                #
                #     if 'Price {}'.format(str(i + 1)) not in self.field_names:
                #         self.field_names.append('Price {}'.format(str(i + 1)))
                #     item['Price {}'.format(str(i + 1))] = price
                #
                #     if 'Quantity {}'.format(str(i + 1)) not in self.field_names:
                #         self.field_names.append('Quantity {}'.format(str(i + 1)))
                #     item['Quantity {}'.format(str(i + 1))] = str(count) + 'pcs'

            else:
                proxy = random.choice(self.list_proxy)
                yield scrapy.Request(response.meta['url'], callback=self.parse, meta={'code': response.meta['code'], 'url': response.meta['url'], 'proxy':proxy}, errback=self.errCall)


        else:
            skuMaps = response.text.split('"skuMap":')
            if len(skuMaps) > 1:
                skuProps = response.text.split('"skuProps":')
                skuProps = skuProps[-1].split(',\n')[0]
                prop_json_data = loads(skuProps)
                prop_type = []
                for p in prop_json_data[0]['value']:
                    prop_type.append(p['name'])

                # print(prop_type)
                prop_size = []
                for p in prop_json_data[1]['value']:
                    prop_size.append(p['name'])
                # print(prop_size)  &g

                skuMaps = skuMaps[-1].replace('t;', '')
                skuMaps = skuMaps.split(';')[0].split(',\n')[0]

                price = response.xpath('//div[@class="obj-sku"]/div[@class="obj-content"]/table/tr/td[@class="price"]/span/em[@class="value"]/text()').extract_first()

                main_image = response.xpath('//div[@class="tab-pane"]/div/a/img/@src').extract_first()
                small_images = response.xpath('//div[@id="dt-tab"]/div/ul/li/div/a/img/@src').extract()
                title = response.xpath('//div[@id="mod-detail-title"]/h1/text()').extract_first()
                detail = response.xpath('//div[@id="mod-detail-attributes"]/div/table/tbody/tr/td[@class="de-feature"]/text()').extract()

                json_data = loads(skuMaps)
                saleCount_list = []

                recharging_data = {}

                for pt in prop_type:
                    item = OrderedDict()
                    for h in self.field_names:
                        item[h] = ''

                    item['Product Code'] = response.meta['code']
                    item['url'] = response.meta['url']
                    for i, ps in enumerate(prop_size):
                        key = pt + '&g' + ps
                        # print(key)
                        count = json_data[key]['canBookCount']




                        if 'Color {}'.format(str(i + 1)) not in self.field_names:
                            self.field_names.append('Color {}'.format(str(i + 1)))
                        item['Color {}'.format(str(i + 1))] = key.split('&g')[0]

                        if 'Size {}'.format(str(i + 1)) not in self.field_names:
                            self.field_names.append('Size {}'.format(str(i + 1)))
                        item['Size {}'.format(str(i + 1))] = key.split('&g')[1]

                        if 'Price {}'.format(str(i + 1)) not in self.field_names:
                            self.field_names.append('Price {}'.format(str(i + 1)))
                        item['Price {}'.format(str(i + 1))] = price

                        if 'Quantity {}'.format(str(i + 1)) not in self.field_names:
                            self.field_names.append('Quantity {}'.format(str(i + 1)))
                        item['Quantity {}'.format(str(i + 1))] = str(count) + 'pcs'

                    self.total_count += 1
                    print('Total Count: ' + str(self.total_count))

                    self.result_data_list[str(self.total_count)] = item
            else:
                proxy = random.choice(self.list_proxy)
                yield scrapy.Request(response.meta['url'], callback=self.parse, meta={'code': response.meta['code'], 'url': response.meta['url'], 'proxy':proxy}, errback=self.errCall)

        

    def errCall(self, response):
        # try:
        #     if response.value.response.xpath('//pre/text()').extract_first() != 'Retry later\n':
        #         print('no result: {}'.format(response.request.meta['ean']))
        #         return
        # except:
        #     pass
        ban_proxy = response.request.meta['proxy']
        if '154.16.' in ban_proxy:
            ban_proxy = ban_proxy.replace('http://', 'http://eolivr4:bntlyy3@')
        if ban_proxy in self.list_proxy:
            self.list_proxy.remove(ban_proxy)
        if len(self.list_proxy) < 1:
            proxy_text = requests.get('https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list.txt').text
            list_proxy_temp = proxy_text.split('\n')
            self.list_proxy = []
            for line in list_proxy_temp:
                if line.strip() !='' and (line.strip()[-1] == '+' or line.strip()[-1] == '-'):
                    ip = line.strip().split(':')[0].replace(' ', '')
                    port = line.split(':')[-1].split(' ')[0]
                    self.list_proxy.append('http://'+ip+':'+port)

        proxy = random.choice(self.list_proxy)
        # response.request.meta['proxy'] = proxy
        print ('err proxy: ' + proxy)
        if not 'errpg' in response.request.url :
            yield Request(response.request.url,
                          callback=self.parse,
                          meta={'proxy': proxy, 'code':response.request.meta['code'], 'url':response.request.meta['URL']},
                          dont_filter=True,
                          errback=self.errCall)
