import requests
from bs4 import BeautifulSoup
from collections import deque
import re
import jieba
import sqlite3

#获取url源代码
def gethtmltext(url):
    r = requests.get(url)
    r.encoding = r.apparent_encoding
    return r.text

#构建数据库

conn = sqlite3.connect('bilibili.db')
c = conn.cursor()
c.execute('drop table doc')
c.execute('create table doc (id int primary key,link text)')#doc表：存储网页的链接 主键：id ；属性：url
c.execute('drop table word')
c.execute('create table word (term varchar(25) primary key,list text)')#word表：倒排表 主键：关键词；属性：id列表
conn.commit()
conn.close()

url = "https://www.bilibili.com/newlist.html"
urllist = []
urllist.append(url)
for i in range(1000):
    urllist.append(url+ '?page='+ str(i+2))
#队列存放视频的url
queue = deque()
for url in urllist:
    content = gethtmltext(url)
    #正则表达式，匹配下属网站域名
    m = re.findall(r'<a href=\"([0-9a-zA-Z\_\/\.\%\?\=\-\&]+)\" target=\"_blank\" class=\"title\" vid=\"[0-9]+\">', \
                       content, re.I)

    #加入队列
    for i in m:
        i = "https://www.bilibili.com" + i
        queue.append(i)

count = 0
#处理提取文本，构建数据库
while queue:
    new_url = queue.popleft()
    count += 1
    new_content = gethtmltext(new_url)
    soup = BeautifulSoup(new_content, "html.parser")
    title = soup.h1.text
    title = ' '.join(title.split())
    #分词
    seg = jieba.cut_for_search(title)
    seglist = list(seg)
    #存储数据
    connect = sqlite3.connect("bilibili.db")
    c = connect.cursor()
    c.execute('insert into doc values(?,?)', (count, new_url))

    #建立词表
    for word in seglist:
        c.execute('select list from word where term=?', (word,))
        result = c.fetchall()
        if len(result) == 0:
            doclist = str(count)
            c.execute('insert into word values(?,?)', (word, doclist))
        else:
            doclist = result[0][0]
            doclist += ' ' + str(count)
            c.execute('update word set list=? where term=?', (doclist, word))




    connect.commit()
    connect.close()

