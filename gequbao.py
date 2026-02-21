from typing import Any


import requests
import re
requests.packages.urllib3.disable_warnings()


headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
}

def request_list(name,headers = headers):
    response = requests.get(f"https://www.gequbao.com/s/{name}")
    pattern = re.compile(
    r'<a href="(/music/\d+)" target="_blank"[^>]+title="([^-]+)\s*-\s*([^"]+)">',
    re.IGNORECASE | re.DOTALL
)
    results = pattern.findall(response.text)
    data_set=set()
    for link, song_name, singer in results:
        song_name = song_name.replace("&amp;", "&").strip()
        singer = singer.replace("&amp;", "&").strip()
        full_link = f"https://www.gequbao.com{link}"
        data_set.add((song_name, singer, full_link))
    data=[{"name": name, "singer": singer, "link": link} for name, singer, link in data_set]
    return data


def request_url(link,headers = headers):
    '''
    返回值为*.mp3
    '''
    html = requests.get(link,headers=headers).text
# 提取play_id
    match = re.findall(r'\\u0022play_id\\u0022:\\u0022(.*?)\\u0022', html, re.DOTALL)
    if match!=[]:
        play_id=match[0]
    else:
        raise RuntimeError("未找到play_id")
    url = "https://www.gequbao.com/api/play-url"
    data = {"id": play_id}
    headers = {"User-Agent": "Mozilla/5.0"}
    jsondata=requests.post(url, data=data, headers=headers, verify=False).json()
    return jsondata["data"]["url"]


