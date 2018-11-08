# -*- encoding: utf-8 -*-

import scrapy
from scrapy.utils.project import get_project_settings
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError
import re
from .crackutils import CrackUtils

from ..items import AlbumItem, VideoItem


class IqiyiAllSpider(scrapy.Spider):
    name = "iqiyi_all"

    def __init__(self):
        scrapy.spiders.Spider.__init__(self)
        self.global_settings = get_project_settings()
        self.type_id_list = self.global_settings['CRAWLER']['type_id_list']
        self.re_type_id = re.compile(self.global_settings['CRAWLER']['re_type_id'])
        self.url_template = self.global_settings['CRAWLER']['url_template']

    def __del__(self):
        scrapy.spiders.Spider.__del__(self)

    def __aiqiyi_url(self, type_id):
        def get_url(data_key):
            return self.url_template % (type_id, data_key)

        return get_url

    def start_requests(self):
        urls = []
        for tid in self.type_id_list:
            get_url = self.__aiqiyi_url(tid)
            urls.append(get_url(1))
        for url in urls:
            yield scrapy.Request(url=url, callback=self.main_list_parse, errback=self.errback_httpbin)

    def main_list_parse(self, response):
        for sel in response.xpath('//div[@class="wrapper-piclist"]/ul/li'):
            item = AlbumItem()
            item['level'] = 1
            item['title'] = sel.xpath('div[2]/div[1]/p/a/text()').extract_first()
            item['img_url'] = sel.xpath('div[1]/a/img/@src').extract_first()
            item['main_url'] = sel.xpath('div[2]/div[1]/p/a/@href').extract_first()
            item['type_id'] = 0
            update_status = sel.xpath('div[1]/a/div/div/p/span/text()').extract_first().strip()
            item['status'] = 1 if update_status[0] == u'共' else 0

            if item['title'] is not None and item['main_url'] is not None:
                yield item
                yield scrapy.Request(response.urljoin(item['main_url']), callback=self.video_list_parse,
                                     errback=self.errback_httpbin)

        no_page = response.xpath('//span[@class="curPage"]/following-sibling::span[@class="noPage"]').extract_first()
        # to crawl next page
        if no_page is None:
            next_page_url = response.xpath('//div[@class="mod-page"]/a[last()]/@href').extract_first()
            # print('visit next page url: ', next_page_url)
            yield scrapy.Request(response.urljoin(next_page_url), callback=self.main_list_parse,
                                 errback=self.errback_httpbin)

    def video_list_parse(self, response):
        lis = response.css('div.piclist-wrapper ul.site-piclist li')
        for sel in lis:
            item = VideoItem()
            item['title'] = response.css('div.info-intro h1[itemprop=name] a::attr(title)').extract_first().strip()
            item['name'] = sel.css('div.site-piclist_info a::text').extract_first().strip()
            item['video_url'] = sel.css('div.site-piclist_info a::attr(href)').extract_first()
            item = CrackUtils.video_crack(item)
            print(item)
            yield item

    def errback_httpbin(self, failure):
        # log all failures
        self.logger.error(repr(failure))

        # in case you want to do something special for some errors,
        # you may need the failure's type:
        if failure.check(HttpError):
            # these exceptions come from HttpError spider middleware
            # you can get the non-200 response
            response = failure.value.response
            self.logger.error('HttpError on %s', response.url)

        elif failure.check(DNSLookupError):
            # this is the original request
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)
