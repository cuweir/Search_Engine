import requests
from bs4 import BeautifulSoup
import sqlite3
import jieba
import math

conn = sqlite3.connect('bilibili.db')
c = conn.cursor()
c.execute('select count(*) from doc')

N = 1 + c.fetchall()[0][0]#文档总数

terms = input('请输入关键词：')
seg = jieba.cut_for_search(terms)
score = {}#文档号：得分

'''
tf-idf算法：
    tf：词频，词条t在文档d中出现的频率
    idf：逆向文件频率，文件总数除以该词条出现的文件数
'''
for word in seg:
    print('查询词：', word)
    #计算score
    tf = {}
    c.execute('select list from word where term=?', (word,))
    result = c.fetchall()
    if len(result) > 0:
        doclist = result[0][0]
        doclist = doclist.split(' ')
        doclist = [int(x) for x in doclist]
        df = len(set(doclist))
        idf = math.log(N / df)#逆向文件频率
        #print('idf:', idf)
        for num in doclist:
            if num in tf:
                tf[num] += 1
            else:
                tf[num] = 1


        for num in tf:
            if num in score:
                score[num] = score[num] + tf[num] * idf
            else:
                score[num] = tf[num] * idf

sortedlist = sorted(score.items(), key = lambda d:d[1], reverse = True)#按照得分从高到低排列

cnt = 0

for num, docscore in sortedlist:
    cnt += 1
    c.execute('select link from doc where id=?', (num,))
    url = c.fetchall()[0][0]
    print(url)

    try:
        r = requests.get(url)
        content = r.text
        r.encoding = r.apparent_encoding
    except:
        print('404 not found')
        continue

    soup = BeautifulSoup(content, 'html.parser')
    title = soup.h1.text
    print(title)

    if cnt > 20:
        break
if cnt == 0:
    print('无搜索结果！')


