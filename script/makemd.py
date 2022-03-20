import json
import os
import sys


def make_chapter(book_dir, chapter):
    with open(os.path.join(book_dir, f'{chapter["chapter_order"]}.md'), "w", encoding="utf8") as fwc:
        fwc.write("# {chapter_name}\n".format(**chapter))
        for image in chapter["images"]:
            fwc.write(f"![]({image})\n")
        pre = int(chapter["chapter_order"])-1
        if pre == 0:
            pre = "README"
        fwc.write(f"[【上一章】](./{pre}.md)\n")
        fwc.write(f"[【目录】](./README.md)\n")
        next = int(chapter["chapter_order"])+1
        fwc.write(f"[【下一章】](./{next}.md)\n")


def make_book(book_id):
    with open(os.path.join("db", book_id+".json"), encoding="utf8") as fr:
        book = json.load(fr)
    book_dir = os.path.join("books", book_id)
    if not os.path.exists(book_dir):
        os.mkdir(book_dir)
    with open(os.path.join(book_dir, "README.md"), "w", encoding="utf8") as fw:
        fw.write(
            f'# {book["book_name"]}\n![]({book["cover_url"]})\n'
        )
        for chapter in book["chapters"]:
            fw.write(
                f'{chapter["chapter_order"]}. [{chapter["chapter_name"]}](./{chapter["chapter_order"]}.md)\n')
            make_chapter(book_dir, chapter)
        fw.write("\n")
        fw.write("[【主页】](../../README.md)")


if __name__ == "__main__":
    make_book(sys.argv[1])
