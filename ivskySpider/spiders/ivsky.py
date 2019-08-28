# -*- coding: utf-8 -*-
import scrapy
from urllib.parse import urljoin
from ..items import IvskyItem


class IvskySpider(scrapy.Spider):
    name = 'ivsky'
    allowed_domains = ['ivsky.com']
    start_urls = ['https://www.ivsky.com/']
    custom_settings = {
        "ROBOTSTXT_OBEY": False,
        "CONCURRENT_REQUESTS": 4,
        "DOWNLOAD_DELAY": 1,
        "COOKIES_ENABLED": False,
        "DOWNLOADER_MIDDLEWARES": {
            # 引用自定义的user_agent文件中的类UserAgentMiddleware
            'ivskySpider.rand_agent.UserAgentMiddleware': 543,
            # 将scrapy库中UserAgentMiddleware取空
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None
        },
        "ITEM_PIPELINES": {
            'ivskySpider.pipelines.IvskyPipeline': 300,
        },
        # 图片下载
        # 图片存储路径
        "IMAGES_STORE": "天堂图片网",
        # 图片下载地址
        "IMAGES_URLS_FIELD": "img_url",
    }

    def parse(self, response):
        yield scrapy.Request(
            url=response.url,
            callback=self.parse_nav,
            dont_filter=True,
            meta={}
        )

    def parse_nav(self, response):
        navs = response.xpath("//ul[@id='menu']/li")[1:]
        for nav in navs:
            nav_title = nav.xpath("a/text()").get()
            nav_href = nav.xpath("a/@href").get()
            if not nav_title or not nav_href:
                continue
            nav_href = urljoin(response.url, nav_href)
            print(nav_title, nav_href)
            yield scrapy.Request(
                url=nav_href,
                callback=self.parse_big_cate,
                dont_filter=True,
                meta={
                    "nav_title": nav_title
                }
            )

    def parse_big_cate(self, response):
        big_cates = response.xpath("//ul[contains(@class, 'menu')]/li")[1:]
        for big_cate in big_cates:
            big_cate_title = big_cate.xpath("a/text()").get()
            big_cate_href = big_cate.xpath("a/@href").get()
            if not big_cate_title or not big_cate_href:
                continue
            big_cate_href = urljoin(response.url, big_cate_href)
            print(big_cate_title, big_cate_href)
            meta = response.meta
            meta["big_cate_title"] = big_cate_title
            yield scrapy.Request(
                url=big_cate_href,
                callback=self.parse_small_cate,
                dont_filter=True,
                meta={
                    "meta": meta
                }
            )
            break

    def parse_small_cate(self, response):
        small_cates = response.xpath("//div[@class='sline']/div/a")
        for small_cate in small_cates:
            small_cate_title = small_cate.xpath("text()").get()
            small_cate_href = small_cate.xpath("@href").get()
            if not small_cate_title or not small_cate_href:
                continue
            small_cate_href = urljoin(response.url, small_cate_href)
            print(small_cate_title, small_cate_href)
            meta = response.meta["meta"]
            meta["small_cate_title"] = small_cate_title
            yield scrapy.Request(
                url=small_cate_href,
                callback=self.parse_all_page,
                dont_filter=True,
                meta={
                    "meta": meta,
                    "page": 1,
                    "url": small_cate_href
                }
            )

    def parse_all_page(self, response):
        meta = response.meta
        page = meta["page"]
        img_infos = response.xpath("//img")
        for img_info in img_infos:
            img_name = img_info.xpath("@alt").get()
            img_url = img_info.xpath("@src").get()
            if not img_name or not img_url:
                continue
            img_url = "http:" + img_url if not img_url.startswith("http") else img_url
            print(img_name, img_url)
            small_img_url = img_url
            big_img_url = img_url.replace("/t/", "/pre/")
            item = IvskyItem()
            item["img_url"] = [small_img_url, big_img_url]
            item["path_name"] = f"{meta['meta']['nav_title']}/{meta['meta']['big_cate_title']}/{meta['meta']['small_cate_title']}/{img_name}"
            item["img_name"] = small_img_url.split("/")[-1]
            yield item
        if img_infos:
            page += 1
            page_url = meta["url"] + f"index_{page}.html"
            print(page_url)
            yield scrapy.Request(
                url=page_url,
                callback=self.parse_all_page,
                dont_filter=True,
                meta={
                    "meta": meta["meta"],
                    "page": page,
                    "url": meta["url"]
                }
            )
        else:
            print("到达最后一页")

    def parse_one_page(self, response):
        pass
