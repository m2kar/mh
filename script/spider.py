import imp
import json
import os
from urllib import response
import requests
from bs4 import BeautifulSoup
import time
import re
import makemd

proxy = {"http_proxy": "http://localhost:8088",
         "https_proxy": "http://localhost:8088"}
db_dir = os.path.join("db")


class Book():
    def __init__(self, book_id, book_name, src_url, src="", cover_url="", force_clean=False) -> None:
        self.book_id = book_id
        if os.path.exists(self.db_file) and not force_clean:
            book = self.load_db()
            self.last_chapter_order = int(
                book["chapters"][-1]["chapter_order"])
        else:
            book = {
                'book_id': book_id,
                'book_name': book_name,
                'src': src,
                'src_url': src_url,
                'chapters': [],
                'cover_url': cover_url
            }
            self.last_chapter_order = 0
        self.book = book

    @property
    def db_file(self):
        return os.path.join(db_dir, self.book_id+".json")

    def load_db(self):
        with open(self.db_file, "r", encoding="utf8") as fp:
            book = json.load(fp)
        self.book = book
        return book

    def save_db(self):
        with open(self.db_file, "w", encoding="utf8") as fp:
            json.dump(self.book, fp, ensure_ascii=False, indent=2)


class Glens(Book):
    def __init__(self, book_id, book_name, src_url, src="g-lens.com", cover_url="", force_clean=False) -> None:
        super().__init__(book_id, book_name, src_url, src, cover_url, force_clean)

    def update_book(self,):
        print(f"start update book {self.book_id} {self.book['book_name']}")

        headers = {
            'authority': 'www.g-lens.com',
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cookie': 'pid=17620354; mc_comic_read=d91aJyjdJtGDwz9GzUf3Lbp-96r%2F7XMDY9mKseFPHcytnPCZ-BIo'
        }

        response = requests.request(
            "GET", self.book["src_url"], headers=headers, proxies=proxy)
        soup = BeautifulSoup(response.content, "html.parser")
        # 获得章节列表
        alist = soup.select("div.catalog-list > ul.clearfix > li > a")
        for i, a in enumerate(alist, 1):
            # 增量更新
            if i <= self.last_chapter_order:
                continue

            # 章节必备属性
            chapter = {
                "chapter_name": a.text.strip(),
                "chapter_order": i,
                "chapter_url": "https://www.g-lens.com"+a.attrs["href"],
                "images": []
            }
            chapter_response = requests.request(
                "GET", chapter["chapter_url"], headers=headers, proxies=proxy)
            chapter_soup = BeautifulSoup(
                chapter_response.content, "html.parser")
            # 修正章节名
            chapter["chapter_name"] = chapter_soup.select_one(
                ".read-pos").contents[0]
            # 添加图片
            for img in chapter_soup.select("ul.comic-list > li > img "):
                chapter["images"].append(img.attrs["data-echo"])
            # add_chapter(**chapter)
            print(f"chapter {i} success")
            self.book["chapters"].append(chapter)
            self.save_db()
        print(
            f"update book done :{self.book_id} {self.book['book_name']} chapters:{len(self.book['chapters'])}")


class Maofly(Book):
    def __init__(self, book_id, book_name, src_url, src="", cover_url="", force_clean=False) -> None:
        super().__init__(book_id, book_name, src_url, src, cover_url, force_clean)

    def update_book(self):

        headers = {
            'authority': 'www.maofly.com',
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'referer': 'https://www.maofly.com/manga/5575/94896_7.html',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7',
            'cookie': 'is_pull=true; XSRF-TOKEN=eyJpdiI6IkZ4dGxHdDREdTBSeERKM0tKMDIwdEE9PSIsInZhbHVlIjoieVRkMzkrUjkzYTEveUJLUDdJa1FOeEdmZ2tYMUVkSlRXZXpaNlRnV1R2R09TT2JQTldtaTJvY1VLR2dTVDI4Uzg2VmY3R0tmMWJOSTJ1NFUxaXk5UEYzZDlhb2NXMkhsVDNLY25CL2ZjVm9ZOEhFamVLdHJaUk9VVmJFcDh0M24iLCJtYWMiOiJiZDA4ZGFhZWU5ZTczYmM4MzBjMzRlNTJmZWYwNjI2M2U5ZjNjMDMxOTkwNjVkYTk3NGZkZGM3ZTMzNWU4NDE2In0%3D; laravel_session=eyJpdiI6Ijk0aUFFWnpPWW5SL0Q1NDVvNkFxbmc9PSIsInZhbHVlIjoieWM2eWt4azI1ajY5M0huNEZ6VWpFc1J1d09HNUF5ZVB2SytjbUdLU2Z0b25MWmhpaExjOG1SaEhwUWpxL3oybHpjaEltTjh4azBzZW11MWpoc1JOajlxajcvVlVYWEF6RzJMeGVFSmthemk2ZFBPOTd2RmluZURpM2VQak9xeFUiLCJtYWMiOiIwODIxNmI2YTE3ZTUxNDkyMDZhNDBkYTRlMGJlY2M2ZjZmY2M5ZmEwNDYwYTE0NWM2MDhkNjcyYmZjNGQ2Mzg0In0%3D'
        }

        response = requests.request(
            "GET", self.book["src_url"], headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")

        import lzstring
        lz = lzstring.LZString()
        alist = soup.select("ol.links-of-books > li > a")
        for i, a in enumerate(alist, 1):
            if i <= self.last_chapter_order:
                continue
            chapter = {
                "chapter_name": a.text.strip(),
                "chapter_order": i,
                "chapter_url": a.attrs["href"],
                "images": []
            }
            chapter_response = requests.request(
                "GET", chapter["chapter_url"], headers=headers, proxies=proxy)
            chapter_soup = BeautifulSoup(
                chapter_response.content, "html.parser")
            # chapter["chapter_name"] = chapter_soup.select_one(
            #     ".read-pos").contents[0]
            # chapter_soup.s
            img_data = re.findall(
                r"img_data = \"([\w/=+]*)\"", chapter_response.text)[0]

            for img in lz.decompressFromBase64(img_data).split(","):
                chapter["images"].append(
                    "https://mao.mhtupian.com/uploads/"+img)
            print(f"chapter {i} success")
            self.book["chapters"].append(chapter)
            self.save_db()
        print(
            f"update book done :{self.book_id} {self.book['book_name']} chapters:{len(self.book['chapters'])}")


class Baozimh(Book):
    def __init__(self, book_id, book_name, src_url, src="", cover_url="", force_clean=False) -> None:
        super().__init__(book_id, book_name, src_url, src, cover_url, force_clean)

    def update_book(self):
        headers = {
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Referer': 'https://www.google.com.hk/',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7'
        }
        response = requests.request(
            "GET", self.book["src_url"], headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")
        alist = soup.select("#chapter-items a") + \
            soup.select("#chapters_other_list a")
        for i, a in enumerate(alist, 1):
            if i <= self.last_chapter_order:
                continue

            chapter = {
                "chapter_name": a.text.strip(),
                "chapter_order": i,
                "chapter_url": "https://cn.baozimh.com"+a.attrs["href"],
                "images": []
            }
            chapter_response = requests.request(
                "GET", chapter["chapter_url"], headers=headers, proxies=proxy)
            chapter_soup = BeautifulSoup(
                chapter_response.content, "html.parser")
            # chapter["chapter_name"] = chapter_soup.select_one(
            #     ".read-pos").contents[0]
            for img in chapter_soup.select(".comic-contain img"):
                chapter["images"].append(img.attrs["src"])
            # add_chapter(**chapter)
            print(f"chapter {i} success")
            self.book["chapters"].append(chapter)
            self.save_db()
        print(
            f"update book done :{self.book_id} {self.book['book_name']} chapters:{len(self.book['chapters'])}")


# 添加新源类：仿照`class Glens`，继承Book类编写爬虫，并在`update_book`中更新`router`
def update_book(**kwargs):
    router = {
        "maofly.com": Maofly,
        "g-lens.com": Glens,
        "baozimh.com": Baozimh
    }
    router[kwargs["src"]](**kwargs).update_book()
