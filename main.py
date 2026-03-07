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
for i in range(len(data)):
    song = data[i]
    name = song['name']
    padding = 20 - get_display_width(name)
    print(f"{i+1}. {name}{' ' * max(0, padding)}{song['singer']}")

choice = int(input('请输入编号下载: '))
if 1 <= choice <= len(data):
    song = data[choice - 1]
    filename = f"{song['name']} - {song['singer']}.mp3"
    music_url = m.request_music_url(song['link'])
    print(f"开始下载: {filename}")
    response = requests.get(music_url,headers=m.headers)
    with open(filename, 'wb') as f:
        f.write(response.content)
    print(f"已下载: {filename}")
else:
    print("编号无效")