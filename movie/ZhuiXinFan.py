# encoding:utf-8

import requests
from bs4 import BeautifulSoup
import threadpool
import sys
import getopt

s = requests.session()


def tvLists():
    basicUrl = 'http://www.zhuixinfan.com/main.php?mod=viewall&action=tvplay&area=1&alpha=&orderby=fp_date&sort=DESC&inajax=1'
    r = s.get(url=basicUrl)
    tmpData = (((r.text).replace('<?xml version="1.0" encoding="utf-8"?>', '')).replace("<root><![CDATA[", "")).replace("]]></root>", "")
    soup = BeautifulSoup(tmpData, "lxml")
    tvs = soup.select("tr")
    for tv in tvs:
        href = tv.select(".td2 > a")[1]['href']
        name = tv.select(".td2 > a")[1].string
        status = tv.select(".td4")[0].string
        print(href,name,status)


def searchTv(pid):
    basicUrl = "http://www.zhuixinfan.com/viewtvplay-" + str(pid) + ".html"
    r = s.get(url=basicUrl)
    soup = BeautifulSoup(r.content, 'html5lib')
    downData = soup.select("#ajax_tbody > tr")
    downUrls = []
    for i in downData:
        downUrl = "http://www.zhuixinfan.com/" + i.select(".td2 > a")[0]['href']
        downUrls.append(downUrl)
    pool = threadpool.ThreadPool(len(downUrls) if len(downUrls) < 4 else 4)
    tasks = threadpool.makeRequests(downPage, downUrls)
    [pool.putRequest(task) for task in tasks]
    pool.wait()


def downPage(downUrl):
    downDataUrl = []
    r = s.get(url=downUrl)
    soup = BeautifulSoup(r.content, 'html5lib')
    name = soup.select("#pdtname")[0].string
    downDataUrl.append(name)
    if soup.select("#emule_url"):
        downDataUrl.append(soup.select("#emule_url")[0].string)
    if soup.select("#torrent_url"):
        downDataUrl.append(soup.select("#torrent_url")[0].string)
    print(name + " 下载地址：" + downDataUrl[2])


def star():
    run_search = False
    tv_id = ''
    if len(sys.argv) < 2:
        print("缺少参数 -t 请检查后重试")
        sys.exit(2)
    try:
        opts, args = getopt.getopt(sys.argv[1:], "t:")
    except getopt.GetoptError:
        print("ZhuiXinFan.py -t <tv_id>")
        sys.exit(2)
    for opt, arg in opts:
        if opt in '-t':
            tv_id = arg
            run_search = True
    if run_search:
        searchTv(tv_id)


if __name__ == '__main__':
    star()
