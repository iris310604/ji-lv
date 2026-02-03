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
        "cookie": "buvid_fp_plain=undefined; DedeUserID=375532154; DedeUserID__ckMd5=14cd4de2c3fac0d7; rpdid=0zbfVGk4SW|uDwONZYH|4F5|3w1TCp5X; enable_feed_channel=ENABLE; hit-dyn-v2=1; fingerprint=57245b014fa42eb3eab98c0c25230bae; buvid_fp=57245b014fa42eb3eab98c0c25230bae; LIVE_BUVID=AUTO4517475717218179; header_theme_version=OPEN; theme-avatar-tip-show=SHOWED; SESSDATA=c27dd78d%2C1772265574%2C58de5%2A92CjCcW7TG6tD6cMJDpHCtjB07bQag32enz5aaCSEqk1MbY7QpfNA9pCzEMDD95xsHQPMSVlJJSzhQVUNfQWxxRlR0ekF5Qjc0aFhzLTBlUFdjQ2ZpTmwtcmszSWRZZVBqVWlOMTMwbEZiZUlLY0FhQ3VWblZoQkF1M0NWd1g2OHExMENScnljdjlRIIEC; bili_jct=f0c068ba252b4aef694d6631a5025367; _uuid=E7AC5EFD-A165-DB89-4C9B-A4A6BCFA239857889infoc; enable_web_push=DISABLE; buvid3=BCD4519E-C603-5A0B-09B7-57CC4CA2C21088993infoc; b_nut=1763439088; theme-tip-show=SHOWED; PVID=1; buvid4=65A7A5CF-5808-B78F-FEA9-120064506D3993513-022090911-hJCNkYFrXXr7sMf8XWMeBw%3D%3D; home_feed_column=5; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njk2ODcxNDgsImlhdCI6MTc2OTQyNzg4OCwicGx0IjotMX0.wC06KPz3rDoVOqxz5r0jt8JDGL95pUt2OamfSfuIYw0; bili_ticket_expires=1769687088; bmg_af_switch=1; bmg_src_def_domain=i1.hdslb.com; bp_t_offset_375532154=1163188529438654464; CURRENT_QUALITY=80; browser_resolution=1912-948; sid=52r5ot99; CURRENT_FNVAL=2000; bsource=search_bing; b_lsid=1AE82060_19C08E05E40",
        "referer": "https://www.bilibili.com/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0"
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
    # print(title)
    # print(video_url)
    # print(audio_url)
    return title, video_url, audio_url

def clean_filename(filename):
    """清理文件名中的非法字符"""
    # Windows文件名中不允许的字符
    illegal_chars = r'[\\/:*?"<>|]'
    # 替换非法字符为下划线
    cleaned = re.sub(illegal_chars, '', filename)
    return cleaned

def save(title, video_url, audio_url):
    # 清理文件名
    cleaned_title = clean_filename(title)
    # 确保目录存在
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
    # 删除过渡文件
    if os.path.exists(f'视频\\{cleaned_title}.mp4'):
        os.remove(f'缓存过渡\\{cleaned_title}.mp4')
        os.remove(f'缓存过渡\\{cleaned_title}.mp3')

def main():
    title, video_url, audio_url = get_info()
    save(title, video_url, audio_url)

if __name__ == '__main__':
    main()



