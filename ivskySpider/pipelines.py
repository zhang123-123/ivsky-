# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


class IvskyspiderPipeline(object):
    def process_item(self, item, spider):
        return item

import hashlib
from scrapy.utils.python import to_bytes
from scrapy.http import Request
from scrapy.pipelines.images import ImagesPipeline


class IvskyPipeline(ImagesPipeline):
    # 重写get_media_requests方法用于判断高清图和缩略图的存储路径
    def get_media_requests(self, item, info):
        list1 = []
        for x in item.get(self.images_urls_field, []):
            if "/t/" in x:
                list1.append(Request(x, meta={"path_name": f"{item['path_name']}/small", "img_name": item["img_name"]}))
            elif "/pre/" in x:
                list1.append(Request(x, meta={"path_name": f"{item['path_name']}/big", "img_name": item["img_name"]}))
        return list1

    def item_completed(self, results, item, info):
        if isinstance(item, dict) or self.images_result_field in item.fields:
            item[self.images_result_field] = [x for ok, x in results if ok]
        return item

    def file_path(self, request, response=None, info=None):
        path_name = request.meta["path_name"]
        img_name = request.meta["img_name"]
        return f"{path_name}/{img_name}"

