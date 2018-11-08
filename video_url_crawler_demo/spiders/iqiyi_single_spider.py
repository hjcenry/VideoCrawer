# -*- coding: utf-8 -*-
import scrapy

from video_url_crawler_demo.items import VideoItem
from video_url_crawler_demo.spiders.crackutils import CrackUtils


# example:
# scrapy crawl iqiyi_single -a videoUrl=https://www.iqiyi.com/v_19rr2plzqs.html
class IqiyiSingleSpider(scrapy.Spider):
    name = 'iqiyi_single'
    videoUrl = ""

    def __init__(self, videoUrl=None, *args, **kwargs):
        super(IqiyiSingleSpider, self).__init__(*args, **kwargs)
        if videoUrl is None:
            raise Exception
        else:
            self.videoUrl = videoUrl
            self.start_urls = [videoUrl]

    def parse(self, response):
        item = VideoItem()
        item['video_url'] = self.videoUrl
        item = CrackUtils.video_crack(item)
        print(item)
        yield item
