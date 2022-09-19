# -*- coding: utf-8 -*-
"""
Created on Mon Sep  5 21:43:28 2022

@author: jamsb
"""

import requests
import re
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont
import random
from tkinter import Label
from tkinter import Tk
from tkinter import ttk, filedialog
import os
#import time



def getPinyinAndEnglish(num, word, manualEnglish, manualPinyin): #returns pin and eng
    url = 'https://www.mdbg.net/chinese/dictionary?page=worddict&wdrst=0&wdqb='+word
    r = requests.get(url)
    html = r.text;
    divIdx = 1 #default idx (0th does not contain information)
    #regex
    regEngDiv = 'class="defs">.*?<'
    regEng = '(?<=>).*?(?=\s*<)'
    regDiv = 'class="pinyin".*?</div>'
    regPin = '(?<=mpt\d">).+?(?=</span>)'
    
    divs = re.findall(regDiv, html)
    for idx, d in enumerate(divs):
        if f"'{word}|" in d:
            divIdx = idx
            break
    eng = re.findall(regEng, re.findall(regEngDiv, html)[divIdx-1])[0]
    if num in manualEnglish: eng = manualEnglish[num]
    div = divs[divIdx]
    pinyins = re.findall(regPin, div)
    pin = ""
    for pinyin in pinyins:
        pin+=pinyin+" "
    if num in manualPinyin: pin = manualPinyin[num]
    return (pin, eng)

def makeCanvas(lessonNum): #perform one time setup
    canvas = Canvas("_Lesson "+str(lessonNum)+".pdf", pagesize = LETTER)
    pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
    pdfmetrics.registerFont(TTFont('Chonburi-Regular', 'Chonburi-Regular.ttf'))
    return canvas
    
def newPage(canvas, lessonNum, pageNum): #add lesson, name, and page number to a new page
    canvas.setFont('Times-Roman', 16)
    canvas.drawString(40, 750, "Lesson "+str(lessonNum))
    canvas.drawString(500, 750, "James Mallek")
    canvas.drawString(580, 20, str(pageNum))


def createWorksheet(vocabList): #details below
    #parses vocab list
    #calls setup function
    #iterates through vocab and writes to pdf
    #saves pdf
    #creates txt file with English in random order
    englishList = []
    manualEnglish = {}
    manualPinyin = {}
    regManual = '(?<=:).*?(?=:)|(?<=:).*?(?=\n)|(?<=:).*?$'
    for idx in range(len(vocabList)):
        if ':' in vocabList[idx]:
            manualInputs = re.findall(regManual, vocabList[idx])
            for i, m in enumerate(manualInputs):
                if i==0 and m:
                    manualEnglish[idx-1] = m
                elif i==1 and m:
                    manualPinyin[idx-1] = m.replace(':', '')
            vocabList[idx] = vocabList[idx][:vocabList[idx].find(':')]
    vocabList = [j.replace('\n', '') for j in vocabList]
    lessonNum = vocabList[0]
    canvas = makeCanvas(lessonNum)
    newPage(canvas, lessonNum, 1)
    k = 0
    pageNum = 1
    progress.config(text=f'0 of {len(vocabList)-1} words processed')
    progress.pack()
    for idx, hanzi in enumerate(vocabList[1:]):
        win.update_idletasks()
        win.update()
        if not vocabList:
            return
        #formatting
        yStart = 700
        yIncrement = 135
        textToLineSpace = 75
        lineToLineSpace = 50
        x = 60
        xTextSpace = 100
        lineWidth = 500
        
        img_file = "practiceLine.png"
        canvas.drawImage(img_file, x, yStart-textToLineSpace-yIncrement*k, width=lineWidth, preserveAspectRatio=True, mask='auto')
        canvas.drawImage(img_file, x, yStart-textToLineSpace-lineToLineSpace-yIncrement*k, width=lineWidth, preserveAspectRatio=True, mask='auto')
        pinyin, english = getPinyinAndEnglish(idx, hanzi, manualEnglish, manualPinyin)
        englishList.append(english)
        canvas.setFont('STSong-Light', 16)
        canvas.drawString(x, yStart-yIncrement*k, hanzi)
        canvas.setFont('Chonburi-Regular', 16)
        canvas.drawString(x+xTextSpace, yStart-yIncrement*k, pinyin)
        canvas.setFont('Times-Roman', 16)
        canvas.drawString(x+3*xTextSpace, yStart-yIncrement*k, english)
        k+=1
        progress.config(text=f'{idx+1} of {len(vocabList)-1} words processed')
        if k==5:
            pageNum+=1
            canvas.showPage()
            newPage(canvas, lessonNum, pageNum)
            k=0
    progress.config(text='Saving Files')
    canvas.save()
    random.shuffle(englishList)
    with open(f'_Lesson {lessonNum} English.txt', 'w') as f:
        for eng in englishList:
            f.write(eng)
            f.write('\n')
        f.close()
    progress.config(text='Files Saved')

def readVocabAndCreateWorksheet(): #read vocab sheet and call createWorksheet()
    if filePath == "": return []
    lines = []
    with open(filePath, encoding="utf8") as f:
        lines = f.readlines()
    createWorksheet(lines)
    
def open_file(): #get txt file and call readVocabAndCreateWorksheet()
   global filePath
   file = filedialog.askopenfile(mode='r', filetypes=[('Text Files', '*.txt')])
   if file:
      filePath =  str(os.path.abspath(file.name))
      readVocabAndCreateWorksheet()
   filePath = ""    

#gui
win = Tk()
win.geometry("700x300")
win.title('Practice Generator')
filePath = ""

title = Label(win, text='Practice Generator', font='Georgia 16')
title.pack(pady=20)
label = Label(win, text="Select .txt file to read", font=('Georgia 10'))
label.pack(pady=0)
noteMsg = 'txt files formatting notes:\n'
noteMsg+= 'The first line of the txt file must be the lesson number.\n'
noteMsg+= 'All lines after should contain a vocabulary word.\n'
noteMsg+= 'Manual English/Pinyin can be added in the format:\n'
noteMsg+= '汉字:English:Pinyin or\n'
noteMsg+= '汉字:English or\n'
noteMsg+= '汉字::Pinyin'
note = Label(win, text=noteMsg, font=('Georgia 10'))
ttk.Button(win, text="Browse", command=open_file).pack(pady=0)
note.pack(pady=5)
progress = Label(win, text='', font='Georgia 10')
win.mainloop()