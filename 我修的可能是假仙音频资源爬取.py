import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

"""
爬取我修的可能是假仙FM音频
目标网址: https://www.ishuyin.com/show-23681.html
下载地址, url: http://mp3.aikeu.com/23681/268.m4a
23681代表为我修的可能是假仙的内容,268代表我修的可能是假仙第268集
"""


def download(url, path):
    try:
        r = requests.get(url)
        with open(path, "wb") as f:
            f.write(r.content)
        return path
    except Exception as e:
        return path + "失败:" + e


if __name__ == '__main__':
    """
    start: 开始下载位置,1代表第1集
    end: 结束下载位置, 1471代表第1471集结束
    f_url: 下载链接
    f_path: 保存地址
    """
    start = 1
    end = 1471
    f_url = "http://mp3.aikeu.com/23681/{0}.m4a"
    f_path = r"../下载/{0}.m4a"

    # 开启64个线程下载，下载成功打印路径信息，否则打印失败信息
    with ThreadPoolExecutor(max_workers=64) as t:
        for i in as_completed([t.submit(download, f_url.format(i), f_path.format(i))
                               for i in range(start, end + 1)]):
            print(i.result())
