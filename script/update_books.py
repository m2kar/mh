import imp
from spider import update_book
import makemd
import os
import json
if __name__ == "__main__":
    # crawl_book()
    # Glens.crawl_book("https://www.g-lens.com/comic/308", "dpcq", True)
    with open(os.path.join("db", "site.json"), encoding="utf8") as fr:
        site = json.load(fr)
    for book in site["books"]:
        update_book(**book)
        makemd.make_book(book["book_id"])
