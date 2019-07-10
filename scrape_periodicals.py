#coding: utf-8
#2018.10, jek.cl.nlp@gmail.com

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

def get_periodical_list(meta_url, tablename):
    browser.get(meta_url)
    span = browser.find_element_by_class_name('btnWline')
    if span:
        span.click()
        time.sleep(2)

    b_list=browser.find_elements_by_class_name('tbl_bbs_list')
    assert len(b_list) == 1
    p_list=b_list[0].find_elements_by_tag_name('tbody')[0].find_elements_by_tag_name('tr')
    for p in p_list:
        a = p.find_element_by_tag_name('a')
        a_href = a.get_attribute('href')
        tds= p.find_elements_by_tag_name('td')
        assert len(tds) > 1
        p_date=tds[1].text
        title = a.text
        url_id = a_href.split(',')[1].replace("'", '') #javascript:goItemView('ma', 'ma_087', '')
        print(title, '\t', url_id, p_date)
        a_record = {'top_id':url_id, 'title':title, 'p_date':p_date}
        db[tablename].upsert(a_record, ['top_id'])

    '''if span :
        span.click()
        time.sleep(2)'''
    #browser.quit()
    return len(p_list) # it should be 83 in 2019.6


def scrape_vids(req_id, tablename):
    #db.query("drop table %s" %(tablename))
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
    for item in lis:
        v_id = item.get_attribute('id')
        title = item.find_element_by_class_name('expandable').text
        p_date = item.find_element_by_class_name('dlP01').text
        v_url = urljoin(base_url, v_id)
        a_record= {'url' : v_url, 'pid': req_id, 'mid': v_id, 'title': title, 'p_date': p_date, 'last_seen' : datetime.now() }
        db[tablename].upsert(a_record, ['url'])

    return len(lis)

def scrape_mids(top_id, tablename):
    top_url = base_url + top_id
    browser.get(top_url)
    try:
        folder = browser.find_element_by_class_name('btnWline')
        if folder:
            folder.click()
            time.sleep(3)
    except Exception as e:
        print(e)

    ids_title = []
    lis = browser.find_elements_by_class_name('dl_liCont')
    for i, li in enumerate(lis, 1):
        p_id = li.get_attribute('id')
        p_date = li.find_element_by_class_name('dlP01').text
        li_strong = li.find_element_by_tag_name('strong')
        print(p_id, li_strong.text)
        li_strong.click() #unfold
        time.sleep(3)
        #XXX: javascript function onclick="retrieveListItemLevelChild('ma_013_0010',0)
        sub_li = browser.find_elements_by_xpath("//ul[@parentid='%s']/li"%p_id)
        for sli in sub_li:
            a = sli.find_element_by_tag_name('a')
            a_href = a.get_attribute('href')
            title = a.text
            s_id = a_href.split(',')[1].replace('"', '')
            v_url = urljoin(base_url, s_id)
            a_record= {'url' : v_url, 'pid': p_id, 'mid': s_id, 'title': title, 'p_date': p_date, 'last_seen' : datetime.now() }
            db[tablename].upsert(a_record, ['url'])
            ids_title.append((p_id, s_id, title))
        li_strong.click() #fold
        time.sleep(3)
    browser.quit()
    return ids_title

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
    article['body'] = body_soup[0].get_text(strip=True)
    meta = article_soup.find('table').find('tbody').find_all('tr')
    try:
        article['title'] = meta[0].find('td').get_text(strip=True)
        article['p_date'] = meta[1].find('td').get_text(strip=True)
        if len(meta) > 2 : article['subtitle'] = meta[2].find('td').get_text(strip=True)
        #if there's no author, meta[] ends with [3], otherwise, with[4]
        if len(meta) > 3:
            meta_name = meta[3].find('th').get_text(strip=True)
            if meta_name == '필자':
                article['author'] = meta[3].find('td').get_text(strip=True)
                if len(meta)> 4: article['a_type'] = meta[4].find('td').get_text(strip=True)
            else:
                article['author'] = ''
                article['a_type'] = meta[3].find('td').get_text(strip=True)

        db[article_table].upsert(article, ['hoi'])
    except Exception as e:
        print(e)
    return

def do_a_periodical(top_id):
    ids_table = 'urls_title_%s' %top_id
    article_table = 'article_body_%s' %top_id
    vnum=scrape_vids(top_id, ids_table)
    print('volum #:', vnum)
    ids_title=scrape_mids(top_id, ids_table)
    scrape_articles(base_url, ids_title, article_table)


if __name__ == "__main__":

    import os
    ddir ='data'
    if not os.path.exists(ddir): os.mkdir(ddir)
    db = dataset.connect('sqlite:///%s/2mperiodicals.db' %ddir)
    meta_url ='http://db.history.go.kr/item/level.do?itemId=ma'

    try:
        get_periodical_list(meta_url, 'top_meta')
    except Exception as e:
        print(e)
        exit()

    try:
        #below are the same with base_url + top_id
        # http://db.history.go.kr/item/level.do?sort=levelId&dir=ASC&start=1&limit=20&page=1&pre_page=1&setId=-1&prevPage=0&prevLimit=&itemId=ma&types=&synonym=off&chinessChar=on&brokerPagingInfo=&levelId=ma_001&position=-1
       # http://db.history.go.kr/item/level.do?sort=levelId&dir=ASC&start=1&limit=20&page=1&pre_page=1&setId=-1&prevPage=0&prevLimit=&itemId=ma&types=&synonym=off&chinessChar=on&brokerPagingInfo=&levelId=ma_013&position=-1
        base_url = 'http://db.history.go.kr/id/'
        #for i in range(1,96):
        for i in range(31,32):
            top_id = format(i, '03d')
            try:
                do_a_periodical('ma_%s' %top_id)
            except Exception as e:
                print(e)
            print('ma_%s' %top_id)
    except Exception as e:
        print(e)

