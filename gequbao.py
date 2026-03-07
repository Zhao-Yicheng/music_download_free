from typing import Any
from lxml import etree as etree

import requests
import re
requests.packages.urllib3.disable_warnings()


headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
}

def request_list(name,headers = headers):
    response = requests.get(f"https://www.gequbao.com/s/{name}",headers=headers)
    tree = etree.HTML(response.text)
    song_rows = tree.xpath('//div[contains(@class, "row no-gutters py-2d5 border-top align-items-center")]')
    song_list = []
    for row in song_rows:
        song_info = {
            "name": row.xpath('.//span[@class="text-primary font-weight-bold h6 mb-0 text-truncate"]/text()')[0].strip(),
            "singer": row.xpath('.//small[@class="text-jade font-weight-bold text-truncate"]/text()')[0].strip(),
            "link": 'https://www.gequbao.com/'+row.xpath('.//a[@class="hover-zoom d-block text-decoration-none"]/@href')[0]
        }
        song_list.append(song_info)

    data = song_list
    return data


def request_music_url(link,headers = headers):
    '''
    返回值为*.mp3
    '''
    print('正在访问'+link)
    html = requests.get(link,headers=headers).text
    # 提取play_id
    print('提取play_id',end=': ')
    play_id=html[html.find("play_id")+20:html.find("play_id")+88]
    if len(play_id)!=68:
        raise RuntimeError("未找到play_id")
    print(play_id)

    print('正在请求mp3')
    url = "https://www.gequbao.com/api/play-url"
    data = {"id": play_id}
    jsondata=requests.post(url, data=data, headers=headers, verify=False).json()
    print('返回数据：'+str(jsondata))
    print('mp3地址：'+jsondata["data"]["url"])
    return jsondata["data"]["url"]

