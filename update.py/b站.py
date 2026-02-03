import sys
import subprocess
import requests
import re
import json
import os

def get_from_args():
    if len(sys.argv) > 1:
        get_video_url = sys.argv[1]
        return get_video_url
    else:
        print('未输入网址')
        return None

def get_response(url, params=None):
    headers = {
        "cookie": "'自己电脑的cookie加密部分'",
        "referer": "https://www.bilibili.com/",
        "user-agent": "'自己的申请部分，和cookie部分一样查找接口寻找'"
    }
    response = requests.get(url=url, params=params, headers=headers)
    return response

def get_info():
    url = get_from_args()
    html = get_response(url).text
    title = re.findall('<h1 data-title="(.*?)" title=', html)[0]
    info = re.findall(r'<script>\window.__playinfo__=(.*?)</script>', html)[0]
    json_data = json.loads(info)
    # print(json_data)
    #视频地址
    video_url = json_data['data']['dash']['video'][0]['baseUrl']
    #音频地址
    audio_url = json_data['data']['dash']['audio'][0]['baseUrl']
    return title, video_url, audio_url

def clean_filename(filename):
    """
    清理文件名中的非法字符
    """
    #Windows文件名中不允许的字符
    illegal_chars = r'[\\/:*?"<>|]'
    #替换非法字符为空
    cleaned = re.sub(illegal_chars, '', filename)
    return cleaned

def save(title, video_url, audio_url):
    #清理文件名
    cleaned_title = clean_filename(title)
    #确保目录存在
    os.makedirs('缓存过渡', exist_ok=True)
    os.makedirs('视频', exist_ok=True)
    #获取视频音频
    video_content = get_response(video_url).content
    audio_content = get_response(audio_url).content
    #保存数据
    with open('缓存过渡\\' + cleaned_title + '.mp4', 'wb') as video:
        video.write(video_content)
    with open('缓存过渡\\' + cleaned_title + '.mp3', 'wb') as audio:
        audio.write(audio_content)
    #准备合并的文件
    cmd = [
        'ffmpeg.exe',
        '-i', f'缓存过渡\\{cleaned_title}.mp4',
        '-i', f'缓存过渡\\{cleaned_title}.mp3',
        '-c:v', 'copy',
        '-c:a', 'aac',
        f'视频\\{cleaned_title}.mp4'
    ]
    #合并
    subprocess.run(cmd)
    #删除过渡文件
    if os.path.exists(f'视频\\{cleaned_title}.mp4'):
        os.remove(f'缓存过渡\\{cleaned_title}.mp4')
        os.remove(f'缓存过渡\\{cleaned_title}.mp3')

def main():
    title, video_url, audio_url = get_info()
    save(title, video_url, audio_url)

if __name__ == '__main__':
    main()




