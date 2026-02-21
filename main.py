import gequbao as m
import requests

def get_display_width(s):
    width = 0
    for c in s:
        if '\u4e00' <= c <= '\u9fff':
            width += 2
        else:
            width += 1
    return width

data = m.request_list(input('请输入歌名或歌手: '))
for idx, i in enumerate(data, 1):
    name = i['name']
    padding = 20 - get_display_width(name)
    print(f"{idx}. {name}{' ' * max(0, padding)}{i['singer']}")

choice = int(input('请输入编号下载: '))
if 1 <= choice <= len(data):
    song = data[choice - 1]
    filename = f"{song['name']} - {song['singer']}.mp3"
    print(f"开始下载: {filename}")
    
    with open(filename, 'wb') as f:
        f.write(requests.get(m.request_url(song['link'])).content)
    print(f"已下载: {filename}")
else:
    print("编号无效")