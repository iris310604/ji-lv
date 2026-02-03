import sys
import requests
import re
import json
from DrissionPage import  ChromiumPage
from tqdm import tqdm
import os

def get_from_args():
    if len(sys.argv) > 1:
        get_video_url = sys.argv[1]
        return get_video_url
    else:
        print('未输入网址')
        return None

#打开浏览器监听特定接口
dp = ChromiumPage()
dp.listen.start('proxyhttp')
a = get_from_args()
dp.get(a)
resp = dp.listen.wait()
#获取文本以及视频链接
json_data = resp.response.body
v_info = json.loads(json_data['vinfo'])
m3u8_url = v_info['vl']['vi'][0]['ul']['ui'][-1]['url']
title = v_info['vl']['vi'][0]['ti']
m3u8 = requests.get(m3u8_url).text
ts_list = re.findall(',\n(.*?)\n#', m3u8)
ts_name = '/'.join(m3u8_url.split('/')[:-1]) + '/'
#确保保存文件夹存在
os.makedirs('视频', exist_ok=True)
#遍历每个视频链接将其追加写入
for ts in tqdm(ts_list):
    ts_url = ts_name + ts
    ts_content = requests.get(ts_url).content
    with open('视频\\' + title + '.mp4', 'ab') as f:
        f.write(ts_content)

