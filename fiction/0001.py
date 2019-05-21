# encoding:utf-8

import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urlparse
import sys
import getopt
from pymongo import MongoClient

base_url = 'https://www.xbiquge6.com/'


def getBookInfo(fiction_id):
    bookInfo = {}
    url = base_url + fiction_id + '/'
    result = requests.get(url=url)
    soup = BeautifulSoup(result.content, 'html5lib')
    book_name = soup.select("#info > h1")[0].string
    author = soup.select("#info > p")[0].string.split("：")[-1]
    bookInfo['name'] = book_name
    bookInfo['author'] = author
    return bookInfo


def getChapter(fiction_id):
    url = base_url + fiction_id + '/'
    result = requests.get(url=url)
    soup = BeautifulSoup(result.content, 'html5lib')
    chapterList = soup.select("#list > dl > dd > a")
    chapter_ids = []
    chapters = []
    for chapter in chapterList:
        chapter_id = str(urlparse(chapter['href']).path.split("/")[-1].split(".")[0])
        chapter_name = chapter.string
        chapter_ids.append(chapter_id)
        chapters.append({"id": chapter_id, "name": chapter_name})
    chapters = [chapter_ids, chapters]
    return chapters


def getContent(fiction_id, chapter_id):
    url = base_url + fiction_id + '/' + chapter_id + '.html'
    result = requests.get(url=url)
    soup = BeautifulSoup(result.content, 'html5lib')
    chapter_content = str(soup.select("#content")[0])
    # print(html.escape(chapter_content))
    # return chapter_content
    print(chapter_content)


def connMonGo():
    client = MongoClient('localhost', username='fiction', password='', authSource='fictions',
                         authMechanism='SCRAM-SHA-256')
    db = client['fictions']
    collection = db['fictions']
    return collection


def saveMonGoDB(data):
    try:
        data = data
        collection = connMonGo()
        collection.insert_one(data)
    except Exception as e:
        print(e)
    # return True


def runFirst(fiction_id):
    book_info = getBookInfo(fiction_id)
    chapters = getChapter(fiction_id)[1]
    book_name = book_info['name']
    book_author = book_info['author']
    data = {
        "name": book_name,
        "author": book_author,
        "source": [{"name": "xbiquge6", "id": fiction_id, "status": 1}],
        "chapters": chapters,
        "created_at": int(time.time()),
        "updated_at": int(time.time())
    }
    saveMonGoDB(data)


def star():
    fiction_id = ''
    chapter_id = ''
    run_first = False
    run_update = False
    get_chapter_content = False
    if len(sys.argv) < 2:
        print("缺少参数 -t 请检查后重试")
        sys.exit(2)
    try:
        opts, args = getopt.getopt(sys.argv[1:], "t:fuc:")
    except getopt.GetoptError:
        print("0001.py -t <fiction_id>")
        print("0001.py -t <fiction_id> -f")
        print("0001.py -t <fiction_id> -u")
        print("0001.py -t <fiction_id> -c <fiction_chapter_id>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-t':
            fiction_id = arg
        if opt == '-f':
            run_first = True
        elif opt == '-u':
            run_update = True
        if opt == '-c':
            chapter_id = arg
            get_chapter_content = True
    if run_first:
        runFirst(fiction_id)
    if run_update:
        getChapter(fiction_id)
    if get_chapter_content:
        getContent(fiction_id, chapter_id)


if __name__ == '__main__':
    star()
