import re
from bs4 import BeautifulSoup
from urllib import request, parse


class CrackUtils:

    @staticmethod
    def video_crack(item):
        get_url = 'http://www.wq114.org/x2/tong.php?url=%s' % item['video_url']
        get_movie_url = 'http://www.wq114.org/x2/api.php'
        head = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 4.1.1; Nexus 7 Build/JRO03D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166  Safari/535.19',
            'Referer': get_url
        }
        get_url_req = request.Request(url=get_url, headers=head)
        get_url_response = request.urlopen(get_url_req)
        get_url_html = get_url_response.read().decode('utf-8')
        bf = BeautifulSoup(get_url_html, 'lxml')
        a = str(bf.find_all('script'))
        pattern = re.compile("url    : '(.+)',", re.IGNORECASE)
        allPattern = pattern.findall(a)
        if len(allPattern) == 0:
            raise Exception
        url = allPattern[0]
        get_movie_data = {
            'up': '0',
            'url': '%s' % url,
        }
        get_movie_req = request.Request(url=get_movie_url, headers=head)
        get_movie_data = parse.urlencode(get_movie_data).encode('utf-8')
        get_movie_response = request.urlopen(get_movie_req, get_movie_data)
        get_movie_html = get_movie_response.read().decode('utf-8')
        respJson = eval(get_movie_html)
        item['h5_url'] = str(respJson['url']).replace("\/", "/")
        item = CrackUtils.resource_crack(item)
        return item

    @staticmethod
    def resource_crack(item):
        get_url = item['h5_url']
        if str(get_url).endswith(".m3u8") or str(get_url).endswith(".mp4"):
            item['resource_url'] = get_url
            return item
        head = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 4.1.1; Nexus 7 Build/JRO03D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166  Safari/535.19',
            'Referer': get_url
        }
        get_url_req = request.Request(url=get_url, headers=head)
        get_url_response = request.urlopen(get_url_req)
        get_url_html = get_url_response.read().decode('utf-8')
        bf = BeautifulSoup(get_url_html, 'lxml')
        a = str(bf.find_all('script'))
        pattern = re.compile("hls.loadSource\('(.+)'\)", re.IGNORECASE)
        resourceAll = pattern.findall(a)
        if len(resourceAll) > 0:
            url = str(pattern.findall(a)[0]).replace("\/", "/")
            item['resource_url'] = url
        return item
