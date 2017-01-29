#!/usr/bin/python
# -*- coding: UTF-8 -*-

import time
import Queue
import argparse
import requests
import threading
import os, sys
from FileDialog import *

if sys.version_info[0] == 2:
    from Tkinter import *
    from tkFont import Font
    from ttk import *
    #Usage:showinfo/warning/error,askquestion/okcancel/yesno/retrycancel
    from tkMessageBox import *
    #Usage:f=tkFileDialog.askopenfilename(initialdir='E:/Python')
    #import tkFileDialog
    #import tkSimpleDialog
else:  #Python 3.x
    from tkinter import *
    from tkinter.font import Font
    from tkinter.ttk import *
    from tkinter.messagebox import *
    #import tkinter.filedialog as tkFileDialog
    #import tkinter.simpledialog as tkSimpleDialog    #askstring()

top = Tk()
default_value = StringVar()
default_value.set("dict/dict.txt")

def hello():  
    print "hello!"
def selectDict():
    fd = LoadFileDialog(top)
    default_value.set(fd.go())
def _start(scanSite, scanDict, scanOutput, threadNum):
    scan = Dirscan(scanSite, scanDict, scanOutput, threadNum)

    for i in range(threadNum):
        t = threading.Thread(target=scan.run)
        t.setDaemon(True)
        t.start()

    while True:
        if threading.activeCount() <= 1 :
            break
        else:
            try:
                time.sleep(0.1)
            except KeyboardInterrupt, e:
                print '\n[WARNING] User aborted, wait all slave threads to exit, current(%i)' % threading.activeCount()
                scan.STOP_ME = True 

class Dirscan(object):

    def __init__(self, scanSite, scanDict, scanOutput,threadNum):
        print 'Dirscan is running!'
        self.scanSite = scanSite if scanSite.find('://') != -1 else 'http://%s' % scanSite
        print 'Scan target:',self.scanSite
        self.scanDict = scanDict
        self.scanOutput = scanSite.rstrip('/').replace('https://', '').replace('http://', '')+'.txt' if scanOutput == 0 else scanOutput
        truncate = open(self.scanOutput,'w')
        truncate.close()
        self.threadNum = threadNum
        self.lock = threading.Lock()
        self._loadHeaders()
        self._loadDict(self.scanDict)
        self._analysis404()
        self.STOP_ME = False

    def _loadDict(self, dict_list):
        self.q = Queue.Queue()
        with open(dict_list) as f:
            for line in f:
                if line[0:1] != '#':
                    self.q.put(line.strip())
        if self.q.qsize() > 0:
            print 'Total Dictionary:',self.q.qsize()
        else:
            print 'Dict is Null ???'
            quit()

    def _loadHeaders(self):
        self.headers = {
            'Accept': '*/*',
            'Referer': 'http://www.baidu.com',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; ',
            'Cache-Control': 'no-cache',
        }
    def _analysis404(self):
        notFoundPage = requests.get(self.scanSite + '/songgeshigedashuaibi/hello.html', allow_redirects=False)
        self.notFoundPageText = notFoundPage.text.replace('/songgeshigedashuaibi/hello.html', '')

    def _writeOutput(self, result):
        self.lock.acquire()
        with open(self.scanOutput, 'a+') as f:
            f.write(result + '\n')
        self.lock.release()

    def _scan(self, url):
        html_result = 0
        try:
            html_result = requests.get(url, headers=self.headers, allow_redirects=False, timeout=60)
        except requests.exceptions.ConnectionError:
            # print 'Request Timeout:%s' % url
            pass
        finally:
            if html_result != 0:
                if html_result.status_code == 200 and html_result.text != self.notFoundPageText:
                    print '[%i]%s' % (html_result.status_code, html_result.url)
                    self._writeOutput('[%i]%s' % (html_result.status_code, html_result.url))

    def run(self):
        while not self.q.empty() and self.STOP_ME == False:
            url = self.scanSite + self.q.get()
            self._scan(url)
    # def _start(self):
    #     # parser = argparse.ArgumentParser()
    #     # parser.add_argument('scanSite', help="The website to be scanned", type=str)
    #     # parser.add_argument('-d', '--dict', dest="scanDict", help="Dictionary for scanning", type=str, default="dict/dict.txt")
    #     # parser.add_argument('-o', '--output', dest="scanOutput", help="Results saved files", type=str, default=0)
    #     # parser.add_argument('-t', '--thread', dest="threadNum", help="Number of threads running the program", type=int, default=60)
    #     # args = parser.parse_args()
class Application_ui(Frame):
    #这个类仅实现界面生成功能，具体事件处理代码在子类Application中。
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master.title('Form1')
        self.master.geometry('389x339')
        self.createWidgets()   
    def createWidgets(self):
        self.top = self.winfo_toplevel()
 
        self.style = Style()
 
        self.TabStrip1 = Notebook(self.top)
        self.TabStrip1.place(relx=0.021, rely=0.021, relwidth=0.957, relheight=0.956)
 
        self.TabStrip1__Tab1 = Frame(self.TabStrip1)
        self.TabStrip1__Tab1Lbl = Label(self.TabStrip1__Tab1)
        self.TabStrip1__Tab1Lbl.place(relx=0.1,rely=0.5)
        self.TabStrip1.add(self.TabStrip1__Tab1, text='目录扫描')

        Label(self.TabStrip1__Tab1, text="ScanSite").grid(row=0,sticky=W, padx=3, pady=3)
        Label(self.TabStrip1__Tab1, text="Dict").grid(row=1,sticky=W, padx=3, pady=3)
        Label(self.TabStrip1__Tab1, text="Thread").grid(row=2,sticky=W, padx=3, pady=3)
        
        u = StringVar()
        v1 = IntVar()

        e1 = Entry(self.TabStrip1__Tab1, textvariable = u).grid(row=0, column=1, padx=3, pady=3)
        e2 = Entry(self.TabStrip1__Tab1, textvariable = default_value).grid(row=1, column=1, padx=3, pady=3)
        e3 = Entry(self.TabStrip1__Tab1, textvariable = v1).grid(row=2, column=1, padx=3, pady=3)

        v2 = IntVar()
        c1 = Checkbutton(self.TabStrip1__Tab1, text = "output", variable = v2, onvalue = 1, offvalue = 0).grid(row=2, column=2, padx=3, pady=3)

        Button(self.TabStrip1__Tab1, text ="select dictionary for scanning", command = selectDict).grid(row=1, column=2, padx=3, pady=3)
        Button(self.TabStrip1__Tab1, text ="start", command = lambda : _start(u.get(),default_value.get(),v2.get(),v1.get())).grid(row=4,sticky=W, padx=3, pady=3)

        self.TabStrip1__Tab3 = Frame(self.TabStrip1)
        self.TabStrip1__Tab3Lbl = Label(self.TabStrip1__Tab3, text='Please add widgets in code.')
        self.TabStrip1__Tab3Lbl.place(relx=0.1,rely=0.5)
        self.TabStrip1.add(self.TabStrip1__Tab3, text='SQL注入扫描')
 
 
class Application(Application_ui):
    #这个类实现具体的事件处理回调函数。界面生成代码在Application_ui中。
    def __init__(self, master=None):
        Application_ui.__init__(self, master)
 
if __name__ == "__main__":
    menubar = Menu(top)    

    # create a pulldown 
    filemenu = Menu(menubar, tearoff=0)  
    filemenu.add_command(label="Open", command=hello)  
    filemenu.add_command(label="Save", command=hello)  
    filemenu.add_separator() 
    filemenu.add_command(label="Exit", command=top.quit)  
    menubar.add_cascade(label="File", menu=filemenu)  

    # create more pulldown menus  
    editmenu = Menu(menubar, tearoff=0)  
    editmenu.add_command(label="Cut", command=hello)  
    editmenu.add_command(label="Copy", command=hello)  
    editmenu.add_command(label="Paste", command=hello)  
    menubar.add_cascade(label="Edit", menu=editmenu)  

    helpmenu = Menu(menubar, tearoff=0) 
    helpmenu.add_command(label="About", command=hello)  
    menubar.add_cascade(label="Help", menu=helpmenu)  

    # display the menu  
    top.config(menu=menubar) 

    Application(top).mainloop()