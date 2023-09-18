import re

import requests

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
}


def get_redirected_url(short_url):
    try:
        response = requests.get(short_url, headers=HEADERS, allow_redirects=True)
        final_url = response.url
        return final_url
    except requests.exceptions.RequestException as e:
        print(f"发生错误：{e}")
        return None


def get_photo_id_by_short_url(short_url):
    """
    从快手短连接获取视频id
    """
    # 获取跳转后的地址
    redirected_url = get_redirected_url(short_url)

    if redirected_url:

        match_photo_id = re.search(r"photoId=([^&]+)", redirected_url)

        if match_photo_id:
            return match_photo_id.group(1)

        match_photo = re.search(r"/photo/([^/?]+)", redirected_url)

        if match_photo:
            return match_photo.group(1)
