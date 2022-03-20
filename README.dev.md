# 漫画站

## 文件说明
- db/: 数据库
- db/site.json: 主站配置
- db/example-book.json: 示例书配置
- db/*other.json: 漫画书
- script/: 脚本
- script/spider.py: 爬虫，生成对应的db
- script/makemd.py: 根据db生成文件夹和.md文档

## 使用方法
### 更新
1. 更新列表

```bash
python script/update_books.py
```

2. 推送
```
git add books
git commit -m "update xxx "
git push
```

### 添加新书
1. 修改`db/site.json`,在`books`中添加新书
2. 如支持该源，则按照上述更新步骤更新
3. 如不支持该源，修改script/spider.py, 仿照`class Glens`，继承Book类编写爬虫，并在`update_book`中更新`router`
