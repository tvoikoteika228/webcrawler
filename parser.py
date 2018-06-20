import argparse
from bs4 import BeautifulSoup
from urllib.request import urlopen
import sqlite3
import ssl

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

if pars.arg == 'load':
    page = urlopen(pars.url)
    html = BeautifulSoup(page, "html.parser")
    print(html.prettify())
    arr = []
    for link in html.find_all('a'):
        if link.has_attr('href') and not link['href'].startswith('/') and not link['href'].startswith('mailto'):
            arr.append(link['href'])
    a = -1
    for i in arr:
        a += 1
        print(i)
        code = urlopen(i).getcode()
        if code not in [200, 301]:
            continue
        pageopen = urlopen(i)
        pageopen = BeautifulSoup(pageopen, "html.parser")
        title = pageopen.html.head.title.text
        cursor.execute("insert into urls (source, url, title, html) values (?,?,?,?)", (pars.url, i, title, str(pageopen)))
        print('OK')
elif pars.arg == 'get':
    cursor.execute("select url, title from urls where source=? limit ?",(pars.url, pars.number))
    answ = cursor.fetchall()
    for i in range(int(pars.number)):
        print(f"{answ[i][0]}: {answ[i][1]}")


table.commit()
cursor.close()