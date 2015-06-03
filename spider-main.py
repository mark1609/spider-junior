# coding=gbk
from queue import *
import threading
import time
from linkparser import *
import random
import db

depth = 3
thrNum = 3
maxRetry = 10
#seedUrl = 'http://www.k51.cn/'
ignoreSiteList = ('safedog',)
keyObj = ('欧美','喜剧','公积金')

url0 = 'http://sale.jd.com/act/4VRdmG362EbLpIx.html'
url1 = 'http://www.k51.cn/'
seedUrl = 'http://www.sina.com.cn/'
url3 = 'http://news.baidu.cooom/'
#seedUrl = 'http://news.sina.com.cn/'

taskQue = Queue()
#resQue = Queue()
keyQue = Queue()

# format of task obj: (link, level) , level also used as stop signal at value equals -1
# format of res  obj: (link, content, level, thrQuit)
# format of key  obj: (key1, key2, ... )

class queArray():
    def __init__(self):
        self.size = 0
        self.iter = 0
        self.que = []

    def create(self, size):
        self.size = size
        for i in range(size):
            q = Queue()
            self.que.append(q)

    def insertSpecialObj(self, speObj):
        self.que[0].put(speObj)

    def insert(self, keyElem, obj):
        index = hash(keyElem) % self.size
        self.que[index].put(obj)

    def getObj(self):
        obj = None
        for i in range(self.size):
            que = self.que[self.iter]
            t = self.iter
            self.iter = (self.iter + 1) % self.size
            if que.empty() != True:
                obj = que.get()
                print('get obj from que:', t, obj)
                break
        if obj == None:
            print('res empty')
        return obj

qa = queArray()
qa.create(thrNum)
resQueArray = queArray()
def recordLink(link, content, db):
    print('main thread record link:', link, content)
    db.recordLink(link, content)

def distributeKey(keyObj):
    for i in range(thrNum):
        keyQue.put(keyObj)

def stopAllThread():
    for i in range(thrNum):
        quitSignal = (None, -1)
        taskQue.put(quitSignal) # trigger thread to stop
    #end of for
        
def subTask():
    i = threading.get_ident()
    print('sub thread start', i)

    keyObj = keyQue.get()
    print(keyObj)
    fltr = filter()
    quit = False
    while quit != True:
        taskObj = taskQue.get()
        print('recv task', taskObj, 'at thr', i)

        link, level = taskObj
        if level == -1: # recv quit signal from main thread
            print('depth achived, notify main task thread qui', i)
            quit = True # flag for thread termination
            resObj = (None, None, level, quit)
            #resQue.put(resObj) # notify main thread
            resQueArray.insertSpecialObj(resObj) # notify main thread
        elif link != None:
            print('proc task obj here, get page and analysis link')
            time.sleep(random.randint(0, thrNum+1)) # prevent simultaneously access leads to anti intrusion behavior by host
            p = page()
            file = p.pageLoader(link)
            if file != None:
                host = p.info.netloc
                parser = MyHTMLParser()
                parser.parse(file, p.info.scheme + '://' + host)
                parser.send(level + 1, quit, resQueArray, keyObj, fltr, host)
    # end of while
    time.sleep(2)
    print('sub thread end', i)

def mainTask():
    print('main task start')
    fltr = filter()
    db.createDB()
    resQueArray.create(thrNum)

    print('start thr')
    for i in range(thrNum): # start threads
        thr = threading.Thread(target=subTask) 
        thr.start()

    thrQuitNum = thrNum
    quit = False
    resWaitTimeoutRetry = maxRetry

    distributeKey(keyObj) # send key to all threads

    level = 0
    taskObj = (seedUrl, level)
    print('set init task:', taskObj)
    taskQue.put(taskObj) # send init task

    while quit != True:
        resObj = resQueArray.getObj()
        if resObj != None:
            resWaitTimeoutRetry = maxRetry # reset retry times
            link, content, level, thrQuit = resObj

            if level <= depth  and level != -1 and link != None:
                print('main thread proc data, level', level)
                ignore = False
                for ignoreSite in ignoreSiteList:
                    if link.find(ignoreSite) != -1:
                        ignore = True
                        print('ignore link:', link, 'match:', ignoreSite)
                        break
                if ignore != True: # proc resource here
                    if fltr.isDataExists(link) != True:
                        recordLink(link, content, db)
                        taskObj = (link, level)
                        taskQue.put(taskObj)

            if thrQuit == True: # a thread quit
                thrQuitNum = thrQuitNum - 1
            if thrQuitNum == 0: # all threads quit
                quit = True
        elif quit != True: # resource queue is empty, and quit flag isn't set
            if resWaitTimeoutRetry == 0: # wait long enough, trigger all thread to quit
                print('kill all thread', thrQuitNum)
                stopAllThread()
                time.sleep(1)
            elif taskQue.empty() != True: # still has task undone, maybe all threads are busy, wait 1 sec
                time.sleep(1)
            else: # all task done, resource is empty, start quit countdown
                print('all task done, resource is empty, start quit countdown', resWaitTimeoutRetry)
                resWaitTimeoutRetry = resWaitTimeoutRetry - 1
                time.sleep(1)
    # end of while, ready to quit main thread

    thr.join()
    print('------searchResult------:')
    db.printDB()
    print('main task end.')
    db.delRecord(None,None)
print('test1...........')
mainTask()
