import urllib.request as req
from bs4 import BeautifulSoup


def process_page(content):
    bs = BeautifulSoup(content, features="html.parser")
    arr = bs.find_all('div', class_='table-list-cell')
    arr = arr[::2]
    for i in range(len(arr)):
        title = arr[i].select('.message.js-navigation-open')[0].string
        link = arr[i].find_all(name='a', attrs={'href': True})[1].attrs['href']
        one_item = (title, link)
        print(one_item)


def craw(url):
    try:
        resp = req.urlopen(url, timeout=15)
        content = resp.read().decode('utf-8')
        process_page(content)
        return 0
    except Exception as e:
        print(e)
    return -1


ret_code = 1
url = 'https://github.com/PaddlePaddle/Paddle/commits/develop'
ret_code = craw(url)

if ret_code == 0:
    print("处理结束")

while ret_code == -1:
    for i in range(1, 4):
        print('请求超时，第%s次重复请求' % i)
        ret_code = craw(url)
        if ret_code == 0:
            print("处理结束")
            break
    if ret_code == -1:
        print('妈呀，重试3次后还是不行耶，请检查这个url：【%s】还能访问吗？或者多重试运行此工具脚本' % url)
        ret_code = 1
