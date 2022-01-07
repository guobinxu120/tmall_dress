# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy import signals
import xlsxwriter
import os, csv
from collections import OrderedDict

class tmall_dressScraperPipeline(object):
    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline


    def spider_opened(self, spider):
        pass

    def spider_closed(self, spider):
        if spider.name == 'tmall_dress_spider' or spider.name == 'tmall_dress_spider_one_line' or spider.name == 'tmall_dress_spider_with_fabric':
        # pass
            filepath = 'output/' + spider.file_name
            if os.path.isfile(filepath):
                os.remove(filepath)
            # workbook = xlsxwriter.Workbook(filepath)
            workbook = xlsxwriter.Workbook(filepath, {'strings_to_urls': False})
            sheet = workbook.add_worksheet('sheet')
            data = spider.result_data_list
            headers = spider.field_names
            flag =True
            # headers = []
            print('---------------Writing in file----------------------')
            print('total row: ' + str(len(data)))
            bold = workbook.add_format({'bold': True})

            for index, value in enumerate(data.keys()):
                if flag:
                    for col, val in enumerate(headers):
                        # headers.append(val)
                        sheet.write(index, col, val)
                    flag = False
                for col, key in enumerate(headers):
                    # try:
                        if key in data[value].keys():
                            if data[value][key] == '0pcs' or data[value][key] == 0:
                                sheet.write(index+1, col, data[value][key], bold)
                            else:
                                sheet.write(index+1, col, data[value][key])
                        else:
                            sheet.write(index+1, col, '')
                    # except:
                    #     continue
                print('row :' + str(index))

            workbook.close()

    def process_item(self, item, spider):

        return item
