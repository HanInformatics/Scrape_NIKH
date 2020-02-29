#coding: utf-8
#2019.10, jek.cl.nlp@gmail.com

import pdb
import requests
import dataset
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time, platform
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
system_name = platform.system()

if system_name == 'Linux':
    browser = webdriver.Firefox()
else: # Windows, Darwin(Mac)
    browser = webdriver.Chrome()

def scrape_vids(req_id, tablename):
    browser.get(base_url+req_id)

    # if only there is more(전체보기)
    try:
        folder = browser.find_element_by_class_name('btnWline')
        if folder :
            folder.click() # unfold
            time.sleep(2)
    except Exception as e:
        print(e)
    lis = browser.find_elements_by_class_name('dl_liCont')
    v_ids = []
    for item in lis:
        v_id = item.get_attribute('id')
        title = item.find_element_by_tag_name('a').text
        p_date = item.find_element_by_class_name('dlP01').text
        v_url = urljoin(base_url, v_id)
        a_record= {'url' : v_url, 'pid': req_id, 'mid': v_id, 'title': title, 'p_date': p_date, 'last_seen' : datetime.now() }
        v_ids.append((req_id, v_id, title))
        db[tablename].upsert(a_record, ['url'])

    return v_ids

def scrape_articles(base_url, vid_mid_list, article_table):
    for (vid, mid, title) in vid_mid_list:
        print(vid, mid, title)
        m_url = urljoin(base_url, mid)
        scrape_article(base_url, mid, article_table)
    return

def scrape_article(base_url, article_id, article_table):
    req_url = base_url + article_id
    r = requests.get(req_url)
    soup = BeautifulSoup(r.text, 'html.parser')

    article_soup=soup.find(class_='dl_data_pru')
    body_soup = soup.find_all('div', attrs={'style':'margin-left:20px;'})
    article = {}
    article['hoi'] = article_id
    #--article['body'] = body_soup[0].get_text(strip=True)
    lines_body = body_soup[0].find_all('div', attrs={'style':'text-align:justify;word-break:break-all;'})
    body_text = ''
    for line in lines_body:
        body_text += line.get_text() + ' '
    article['body'] = body_text
    #++
    meta = article_soup.find('table').find('tbody').find_all('tr')
    assert len(meta) > 6, 'all have 7 tds'
    try:
        article['title'] = meta[0].find('td').get_text(strip=True)
        article['p_date'] = meta[4].find('td').get_text(strip=True)
        article['appendix'] = meta[6].find('td').get_text(strip=True)
    except Exception as e:
        print(e)

    #XXX:
    cs_soup = soup.find(class_= 'csdan')
    texts = cs_soup.find('div').get_text('|')
    article['csdan'] = texts

    db[article_table].upsert(article, ['hoi'])
    return

def do_a_periodical(top_id):
    ids_table = 'urls_title_%s' %top_id
    article_table = 'article_body_%s' %top_id

    db.query("drop table if exists %s" %(ids_table))
    db.query("drop table if exists %s" %(article_table))

    vids=scrape_vids(top_id, ids_table) #browser.get(...)
    print('volume #:', len(vids))
    scrape_articles(base_url, vids, article_table)
    browser.quit()

if __name__ == "__main__":

    import os
    ddir ='armistic_data'
    if not os.path.exists(ddir): os.mkdir(ddir)

    try:
        db = dataset.connect('sqlite:///%s/armistice.sqlite3' %ddir)
        base_url = 'http://db.history.go.kr/id/'
        #for i in range(1,11): #XXX: server protects multi requests
        for i in range(10,11): #XXX: server protects multi requests
            top_id= 'pn_'+ str(i).zfill(3)
            print('%s' %top_id)
            try:
                do_a_periodical(top_id)
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)

