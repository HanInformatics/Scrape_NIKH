#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 원작:마소리스(masoris@gmail.com)'
# 갱신:jek.cl.nlp@gmail.com

from __future__ import print_function
import sys, os.path

#Definitions
def preface(): #Print Preface and Prepare Programme
    print('hanja2hangul converter')
    global file_mode
    if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]) :
        file_mode = 1
    else:
        file_mode = 0

def command(a): #Analyzing Command and Get Result
    global looping, useuni, reverse
    #Commands
    if(a.lower()=='exit' or a =='종료'):
        looping = False
        return
    elif(a == '목록'):
        for i in range(0, len(dic0)):
            print (dic0[i]+'\t'+dic1[i])
        return
    elif(a == '정변환'):
        reverse = False
        print( '한자를 한글로 변환합니다')
        return
    elif(a == '역변환'):
        reverse = True
        print( '한글을 한자로 변환합니다 (시험용)')
        return
    elif(a == '방식'):
        setmode()
        return

    convert_interactive(a)

def _unicode(a):
    global useuni
    if(useuni == True):
        for i in range(0, len(dicuni0)):
            a = a.replace(dicuni0[i], dicuni1[i])
    return a

def convert(a): #Convert Hanja to Hangul
    a=_unicode(a)
    if reverse == True:
        for i in range(0, len(dic0)):
            a = a.replace(dic1[i], dic0[i])
    else:
        for i in range(0, len(dic0)):
            a = a.replace(dic0[i], dic1[i])
    return a

def convert_interactive(a):
    result('出力'+str(times)+'> '+convert(a))

def result(s): #Print Message to Screen and File
    print(s)

def convert_file(infn, outfn):
    import tqdm #pip install tqdm
    with open(infn, 'r', encoding='utf-8') as f:
        outfile = open(outfn, 'w', encoding='utf-8')
        lines = f.readlines()
        num = range(1, len(lines)+1)
        for n in tqdm.tqdm(num, desc='processing'):
            outfile.write(convert(lines[n-1]))
        outfile.close()

def readdic(dicfilename = 'dic1.txt'): #Add Dictionary to dic0, dic1
    global dic0, dic1

    dic = open(dicfilename, 'r', encoding='utf-8')
    while(True):
        line = dic.readline()
        if len(line) == 0:
            break
        if line.find('\t') == -1:
            continue

        line = line.replace('\n','')
        if line[0] == '#':
            continue

        splited = line.rsplit('\t')
        if len(splited) <= 1:
            continue
        if len(splited[0]) == 0 or len(splited[1]) == 0:
            continue

        dic0.append(splited[0])
        dic1.append(splited[1])

#Check if it correctly read file
#        for i in range(0, len(dic0)):
#        print( dic0[i])
#        print( dic1[i])
    dic.close()
    print( dicfilename+'을 읽어 들임')


def setmode(mode=-1):
    global dicuni0, dicuni1, dic0, dic1, useuni, reverse

    #Prepare Unicode Normalization Algorithm Dictionaries
    readdic('dic0.txt')
    dicuni0 = dic0
    dicuni1 = dic1
    dic0 = []
    dic1 = []
    useuni = False
    reverse = False

    #Select Mode
    if(mode == -1):
        print( '변환하고자 하는 방식을 선택하세요')
        print( '1. 다용도 한자-한글 변환 시스템 (권장)')
        print( '2. 유니코드 대표음으로 변환 (MS Word)')
        print( '3. 유니코드 정규화 알고리즘 적용 후 한글로 변환 (위키백과)')
        print( '4. 두음법칙 비적용 한글로 변환 (문화어)')
        print( '5. 한자에 정규화 알고리즘 적용 시키기')
        s = input()
        if s != '':
            i = int(s)
        else:
            i = 1
    else:
        i = mode

    #Apply Mode
    if(i == 1):
        readdic('dic4.txt')
        readdic('dic3.txt')
        readdic('dic2.txt')
    elif(i == 2):
        readdic('dic3.txt')
        readdic('dic2.txt')
    elif(i == 3):
        readdic('dic4.txt')
        readdic('dic1.txt')
        useuni = True
    elif(i == 4):
        readdic('dic1.txt')
    elif(i == 5):
        readdic('dic0.txt')

    result('총 '+str(len(dic0))+' 개 데이터 읽')


#Set Variations
looping = True
inp = '' #inputed command or hanja.
times = 0 #The number of looping times
dic0 = [] #Dictionary0
dic1 = [] #Dictionary1
dicuni0 = [] #Unicode Normalization Algorithm Dictionary0
dicuni1 = [] #Unicode Normalization Algorithm Dictionary1
useuni = False #Use Unicode Normalization Algorithm before Converting
reverse = False #Reverse Converting

#Start Programme
preface() #set file_mode
setmode(1)

if file_mode:
    print('input file is', sys.argv[1])
    print('output file will be', sys.argv[1] + '.han')
    convert_file(sys.argv[1], sys.argv[1]+'.han')
else:
    print( 'interactive mode 명령어: 종료(exit), 방식, 정변환, 역변환, 목록')
    while(looping):
        times = times + 1
        inp = input('\n入力'+str(times)+'> ')
        command(str(inp))
#End Programme


