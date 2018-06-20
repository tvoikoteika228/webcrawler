import argparse
from bs4 import BeautifulSoup
from urllib.request import urlopen
import sqlite3
import ssl
import time
from memory_profiler import memory_usage


start_time = time.time()
ssl._create_default_https_context = ssl._create_unverified_context

parser = argparse.ArgumentParser()
subparser = parser.add_subparsers(dest = 'arg')
parser1 = subparser.add_parser('load')
parser1.add_argument('url')
parser2 = subparser.add_parser('get')
parser2.add_argument('url')
parser2.add_argument('-n', '--number')
pars = parser.parse_args()

table = sqlite3.connect('database.db')
cursor = table.cursor()
url = pars.url
if pars.arg == 'load':
    page = urlopen(url)
    html = BeautifulSoup(page, "html.parser")
    arr = []
    for link in html.find_all('a'):
        if link.has_attr('href') and not link['href'].startswith('/') and not link['href'].startswith('mailto'):
            arr.append(link['href'])
    a = -1
    for i in arr:
        a += 1
        code = urlopen(i).getcode()
        if code not in [200, 301]:
            continue
        pageopen = urlopen(i)
        pageopen = BeautifulSoup(pageopen, "html.parser")
        title = pageopen.html.head.title.text
        cursor.execute("insert into urls (source, url, title, html) values (?,?,?,?)", (url, i, title, str(pageopen)))
    print("ok, execution time: {a}s, peak memory usage:{b} Mb".format(a=int(time.time() - start_time),b=int(max(memory_usage()))))
elif pars.arg == 'get':
    number = pars.number
    if(number == None):
        number = 9999999999
    cursor.execute("select url, title from urls where source=? limit ?", (url, number))
    answ = cursor.fetchall()
    for i in range(len(answ)):
        print(f"{answ[i][0]}: {answ[i][1]}")
table.commit()
cursor.close()
