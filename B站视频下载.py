import requests
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import random
import pickle

"""
爬取B站视频如视频链接: https://www.bilibili.com/video/BV1xp4y1W74g
首先我们需要知道该视频的avid, 打开浏览器f12搜索avid即可得到
大概过程, 通过该接口: https://api.bilibili.com/x/player/pagelist?bvid=BV1xp4y1W74g,
获取该页面下的所有视频的标题和cid，
请求https://api.bilibili.com/x/player/playurl?avid={0}&cid={1}&qn=" + str(qn),得到视频的下载链接
注意该下载链接需要及时下载后面会失效，参数为avid， cid， qn, 其中qn为视频质量
"""


class BiliDownloader(object):
    def __init__(self, aid, bvid, headers, qn):
        self.aid = aid
        self.bvid = bvid
        self.video_info_api = "https://api.bilibili.com/x/player/pagelist?bvid={0}"
        self.get_download_url_api = "https://api.bilibili.com/x/player/playurl?avid={0}&cid={1}&qn=" + str(qn)
        self.headers = headers

    def get_videos_info(self):
        """
        得到视频的下载链接和标题
        :return: 数组类型如: [(视频下载链接, 标题).....]
        """
        videos = []
        response = requests.get(self.video_info_api.format(bvid),
                                headers=self.headers)
        for item in json.loads(response.text).get("data", []):
            videos.append((self.get_download_url(item.get("cid", -1)),
                           str(item.get("page")) + "." + item.get("part", "")))
        return videos

    def get_download_url(self, cid):
        """
        得到该cid下的视频下载链接，一个cid对应一个视频
        :param cid: 视频的编号
        :return: 视频为cid的下载链接
        """
        response = requests.get(self.get_download_url_api.format(self.aid, cid),
                                headers=self.headers)
        time.sleep(random.randint(1, 2))
        return json.loads(response.text)["data"]["durl"][0]["url"]

    def download(self, download_url, save_path):
        """
        下载视频
        :param download_url: 视频下载链接
        :param save_path: 保存路径
        :return: 下载成功返回路径信息，否则返回错误信息
        """
        try:
            time.sleep(random.randint(2, 10))
            response = requests.get(download_url, headers=self.headers)
            with open(save_path, 'wb') as f:
                f.write(response.content)
            return save_path
        except Exception as e:
            return e


if __name__ == '__main__':
    # B站对header有检测，所以需要构造请求头，referer必需要，否则拒绝请求下载视频的链接
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
                        Chrome/88.0.4324.96 Safari/537.36 Edg/88.0.705.56",
        "authority": "www.bilibili.com",
        "referer": "https://www.bilibili.com/"
    }
    # 一个aid, bvid对应一个视频系列，一个视频系列下有多个视频与cid对应
    video_bvid = "BV1xp4y1W74g"
    video_aid = 971294225
    # qn代表视频质量
    video_qn = 60
    # 视频的保存路径
    f_path = "C:\\Users\\ly\\Desktop\\视频下载\\{0}"
    # 在请求下载链接和标题时可能会频繁爬取导致被拒绝访问,所以临时保存一下以防万一
    save_videos_info_path = "videos_info.bin"

    bilibili = BiliDownloader(video_aid, video_bvid, headers, video_qn)
    videos_info = bilibili.get_videos_info()
    # 序列化
    with open(save_videos_info_path, "wb") as file:
        pickle.dump(videos_info, file)

    # 反序列化
    # with open(save_videos_info_path, 'rb') as file:
    #     videos_info = pickle.load(file)

    # 开启32个线程下载视频，每完成一个下载打印下载完成的路径
    with ThreadPoolExecutor(max_workers=32) as t:
        for task in as_completed([t.submit(bilibili.download, download_url, f_path.format(title + ".flv"))
                                  for download_url, title in videos_info]):
            print(task.result())
