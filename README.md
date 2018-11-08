# VideoCrawer
视频爬取脚本

## 环境
- python3
- scrapy
- pywin32
- pymongo
- twisted

## 爬取结构
title 标题
name 名字
video_url 爱奇艺视频页
h5_url 破解播放页（可自行打开播放）
resource_url 破解资源下载链接(需自行研究格式播放)

## 爬取爱奇艺所有视频
命令：scrapy crawl iqiyi_all
爬取并存文件：scrapy crawl iqiyi_all -o iqiyi.json
爬取爱奇艺的所有视频极为缓慢

## 爬取爱奇艺单个视频
命令：scrapy crawl iqiyi_single
