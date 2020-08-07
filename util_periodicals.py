#coding: utf-8
#2018.10
import dataset
import re

def txt2table(fn, cols, dbname, tablename):
    db = dataset.connect('sqlite:///%s' %dbname)
    infile = open(fn, 'r', encoding='utf-8')
    lines = infile.readlines()
    infile.close()

    idx = 0
    for l in lines:
        tab = l.split('\t')
        if len(tab) < len(cols) :
            print('txt file columns !=', cols)
            return
        record = {}
        for i, col in enumerate(cols) :
            record[col] = tab[i]
        record['idx'] = idx
        idx += 1

        db[tablename].upsert(record, ['idx'])


def table2txt(dbname, tablename, cols='', fn=''):
    db = dataset.connect('sqlite:///%s' %dbname)
    if fn != '':
        outfile = open(fn, 'w', encoding='utf-8')
    else:
        outfile = open(tablename +'.txt', 'w', encoding='utf-8')

    records = db[tablename].all()
    if cols != '':
        for rec in records:
            item = []
            for col in cols :
                if rec[col] == None: rec[col]=''
                item.append(re.sub(r"[\n\t]+", " ", rec[col])) # for armistice talks'''
            outfile.write('%s\n' %('\t'.join(item)))
    else:
        items = []
        for rec in records :
            item = [str(val).strip() for col, val in rec.items()]
            items.append(item) 
        for item in items:
            outfile.write('%s\n' %('\t'.join(item)))
    outfile.close()


def xlsx2table(dbname, tablename, fn):
    import pandas as pd
    import sqlite3 #pandas.to_sql() uses sqlite3 or sqlalchemy
    condb = sqlite3.connect(dbname)
    idata = pd.read_excel(fn, dtype=str) #without dtype(str), '00001' is to be '1'
    idata.to_excel('tmp.xlsx')
    idata.to_sql(name=tablename, con=condb, if_exists='replace') #'fail', 'replace'. 'append'
    condb.close()
    return

def table2xlsx(dbname, tablename, fn):
    #sudo pip3 install openpyxl
    import pandas as pd
    db = dataset.connect('sqlite:///%s' %dbname)
    records = db[tablename].all()
    columns = db[tablename].columns
    all_rec = [rec for rec in records]
    odata = pd.DataFrame(all_rec, columns=columns)
    outfile = pd.ExcelWriter(fn)
    odata.to_excel(outfile, 'meta')
    outfile.save()

if __name__ == "__main__":
    try:
        #table2txt('data/Gaebyeok.sqlite3', 'article_body_ma_013', ['p_date', 'author', 'body'], 'ma_013.txt')
        #table2txt('data/Gaebyeok.sqlite3', 'article_body_ma_031', ['p_date', 'author', 'body'], 'ma_031.txt')
        #table2txt('../armistice.sqlite3', 'article_body_pn_001')
        for i in range(1,11): 
            table2txt('../armistice.sqlite3', 'article_body_pn_'+str(i).zfill(3), \
            ['hoi', 'title','p_date', 'appendix', 'csdan'], 'article_body_pn_' + str(i).zfill(3) + '.txt')
        '''
        xlsx2table('data/kdb.db', 'students', 'students.xlsx')
        '''
    except Exception as e:
        print(e)
