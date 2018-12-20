#coding: utf-8
#2018.10, jek.cl.nlp@gmail.com

import requests
import dataset
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def get_periodical_list(meta_url, tablename):
    r = requests.get(meta_url)
    soup = BeautifulSoup(r.text, 'html.parser')
    p_lis = soup.find('tbody').find_all('tr')
    for p in p_lis:
        atts = p.find_all('td')
        title = atts[0].get_text(strip=True)
        p_date = atts[1].get_text(strip=True)
        url_xx = p.find(class_='c_pitb ellip').find('a').get('href')
        url_id = url_xx.split(',')[1].strip().strip("'")
        a_record = {'top_id':url_id, 'title':title, 'p_date':p_date}
        db[tablename].upsert(a_record, ['top_id'])
    return len(p_lis)

def scrape_vids(req_id, tablename):
    #db.query("drop table %s" %(tablename))
    req_url = base_url + req_id
    r = requests.get(req_url)
    soup = BeautifulSoup(r.text, 'html.parser')
    p_id=soup.find('ul', class_='data_list_step step01').get('parentid')

    lis = soup.find_all('div', attrs={'class':'dl_liCont'})
    v_ids = [item.get('id') for item in lis]
    for item in lis:
        v_id = item.get('id')
        title = item.find(class_='expandable').get_text(strip=True)
        p_date = item.find(class_='dlP01').get_text(strip=True)
        v_url = urljoin(base_url, v_id)
        a_record= {'url' : v_url, 'pid': p_id, 'vid': v_id, 'title': title, 'p_date': p_date, 'last_seen' : datetime.now() }
        db[tablename].upsert(a_record, ['url'])
    return v_ids

def scrape_mids_in_js(top_id):
    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys
    import time, platform
    system_name = platform.system()
    outfile_name = top_id + '.url.txt'
    outfile = open(outfile_name, 'w', encoding='utf-8')
    if system_name == 'Linux':
        browser = webdriver.Firefox()
    else: # Windows, Darwin(Mac)
        browser = webdriver.Chrome()
    top_url = base_url + top_id
    browser.get(top_url)
    lis = browser.find_elements_by_class_name('dl_liCont')
    for i, li in enumerate(lis, 1):
        li_id = li.get_attribute('id')
        li_strong = li.find_element_by_tag_name('strong')
        print(li_id, li_strong.text) #fold
        li_strong.click()
        time.sleep(2)
        #XXX: javascript function onclick="retrieveListItemLevelChild('ma_013_0010',0)
        sub_li = browser.find_elements_by_xpath("//ul[@parentid='%s']/li"%li_id)
        for sli in sub_li:
            a = sli.find_element_by_tag_name('a')
            a_href = a.get_attribute('href')
            print(li_id,'\t', a.text, '\t', a_href, file=outfile)

        li_strong.click() #unfold
        time.sleep(2)
    browser.quit()
    outfile.close()
    return outfile_name

def make_vid_mid_title(infn):
    import re, sys
    ids_title = []
    infile = open(infn, 'r', encoding='utf-8')
    for l in infile:
        tab = l.strip().split('\t')
        if len(tab) != 3 :
            print('You should never see this:', l, file=sys.stderr)
            exit()
        part=tab[2][tab[2].find('javascript'):]
        mid = part.split('","')
        #print(tab[0], mid[1], tab[1])
        ids_title.append((tab[0], mid[1], tab[1])) # (vid, mid, title)
    infile.close()
    return ids_title

def put_vid_mid(base_url, vid_mid_list, ids_table, article_table):
    for (vid, mid, title) in vid_mid_list:
        print(vid, mid, title)
        mi_url = urljoin(base_url, mid)
        a_record = {'url': mi_url, 'vid': vid, 'mid': mid, 'title': title, 'last_seen':datetime.now()}
        db[ids_table].upsert(a_record, ['url'])
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
    meta = article_soup.find('table').find('tbody').find_all('tr')
    try:
        article['title'] = meta[0].find('td').get_text(strip=True)
        article['p_date'] = meta[1].find('td').get_text(strip=True)
        article['subtitle'] = meta[2].find('td').get_text(strip=True)
        article['a_type'] = meta[3].find('td').get_text(strip=True)

        article['body'] = body_soup[0].get_text(strip=True)
        db[article_table].upsert(article, ['hoi'])
    except Exception as e:
        print(e)
    return

def do_a_periodical(top_id):
    ids_table = 'urls_title_%s' %top_id
    article_table = 'article_body_%s' %top_id
    scrape_vids(top_id, ids_table)
    id_fn=scrape_mids_in_js(top_id)
    ids_title = make_vid_mid_title(id_fn)
    put_vid_mid(base_url, ids_title, ids_table, article_table)


if __name__ == "__main__":

    import os
    ddir ='data'
    if not os.path.exists(ddir): os.mkdir(ddir)
    db = dataset.connect('sqlite:///%s/mperiodicals.db' %ddir)
    meta_url ='http://db.history.go.kr/item/level.do?itemId=ma'

    try:
        get_periodical_list(meta_url, 'top_meta')
    except Exception as e:
        print(e)
    exit()

    base_url = 'http://db.history.go.kr/id/'
    for i in range(1,96):
        top_id = format(i, '03d')
        try:
            do_a_periodical('ma_%s' %top_id)
        except Exception as e:
            print(e)
        print('ma_%s' %top_id)
