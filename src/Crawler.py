import urllib.request
import re
from socket import timeout


def get_page(url):
    user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
    headers = {'User-Agent': user_agent,
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
    text = None
    for i in range(5):
        try:
            req = urllib.request.Request(url, headers=headers)
            response = urllib.request.urlopen(req, timeout=10)
            text = response.read().decode('gbk')
            break
        except timeout as e:
            print(e)
            continue
    return text


rex2 = r'<div class=\'tishi\'>(.*?)<\/div>'
rex = r'dateArr = (.*?);'
rex1 = r'\'(.*?)\''
r = re.compile(rex)
r1 = re.compile(rex1)
r2 = re.compile(rex2)
