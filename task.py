# coding=gbk
from queue import *
import threading
import time
from linkparser import *
import random
import db
import log
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
                try:
                    print('get obj from que:', t, obj)
                except UnicodeEncodeError:
                    print('++++++++++++++++++++++++++++++++++++++++++++++++jap character')
                break
        if obj == None:
            print('res empty')
        return obj

class task():
    def __init__(self, argRun):
        self.depth = argRun.depth
        self.thrNum = argRun.thrNum
        self.maxRetry = 10
        self.seedUrl = argRun.seedurl
        self.ignoreSiteList = ('safedog',)
        self.keyObj = argRun.key #('欧美','喜剧','冰冰','周迅')
        self.keyQue = Queue()
        self.taskQue = Queue()
        self.resQueArray = queArray()

    def distributeKey(self, keyObj):
        log.log.log(1, 'distributing key to all threads')
        for i in range(self.thrNum):
            self.keyQue.put(keyObj)

    def stopAllThread(self):
        log.log.log(1, 'sending quit signal to all threads')
        for i in range(self.thrNum):
            quitSignal = (None, -1)
            # trigger thread to stop
            self.taskQue.put(quitSignal)

    def recordLink(self, link, content, db):
        try:
            print('main thread record link:', link, content)
            db.recordLink(link, content)
        except UnicodeEncodeError:
            log.log.log(5, 'encode issue')

    def subTask(self):
        i = threading.get_ident()
        log.log.log(1, 'sub thread start')

        keyObj = self.keyQue.get()
        print(keyObj)
        fltr = filter()
        quit = False
        while quit != True:
            taskObj = self.taskQue.get()
            print('recv task', taskObj, 'at thr', i)

            link, level = taskObj
            if level == -1: # recv quit signal from main thread
                print('depth achived, notify main task thread qui', i)
                quit = True # flag for thread termination
                resObj = (None, None, level, quit)
                # resQue.put(resObj) # notify main thread
                self.resQueArray.insertSpecialObj(resObj) # notify main thread
            elif link != None:
                print('proc task obj here, get page and analysis link')
                # prevent simultaneously access leads to anti intrusion behavior by host
                time.sleep(random.randint(0, self.thrNum+1))
                p = page()
                file = p.pageLoader(link)
                if file != None:
                    host = p.info.netloc
                    parser = MyHTMLParser()
                    parser.parse(file, p.info.scheme + '://' + host)
                    parser.send(level + 1, quit, self.resQueArray, keyObj, fltr, host)
        # end of while
        time.sleep(2)
        log.log.log(1, 'sub thread end')

    def run(self):
        log.log.log(1, 'main task start')
        fltr = filter()
        db.createDB()
        self.resQueArray.create(self.thrNum)

        # start threads
        log.log.log(1, 'start sub threads')
        for i in range(self.thrNum):
            thr = threading.Thread(target=self.subTask)
            thr.start()

        thrQuitNum = self.thrNum
        quit = False
        resWaitTimeoutRetry = self.maxRetry

        # send key to all threads
        self.distributeKey(self.keyObj)

        level = 0
        taskObj = (self.seedUrl, level)
        print('set init task:', taskObj)
        self.taskQue.put(taskObj) # send init task

        while quit != True:
            resObj = self.resQueArray.getObj()
            if resObj != None:
                resWaitTimeoutRetry = self.maxRetry # reset retry times
                link, content, level, thrQuit = resObj

                if level < self.depth  and level != -1 and link != None:
                    print('main thread proc data, level', level)
                    ignore = False
                    for ignoreSite in self.ignoreSiteList:
                        if link.find(ignoreSite) != -1:
                            ignore = True
                            print('ignore link:', link, 'match:', ignoreSite)
                            break
                    if ignore != True: # proc resource here
                        if fltr.isDataExists(link) != True:
                            self.recordLink(link, content, db)
                            taskObj = (link, level)
                            self.taskQue.put(taskObj)

                if thrQuit == True: # a thread quit
                    thrQuitNum = thrQuitNum - 1
                if thrQuitNum == 0: # all threads quit
                    quit = True
            elif quit != True: # resource queue is empty, and quit flag isn't set
                if resWaitTimeoutRetry == 0: # wait long enough, trigger all thread to quit
                    print('kill all thread', thrQuitNum)
                    self.stopAllThread()
                    time.sleep(1)
                elif self.taskQue.empty() != True: # still has task undone, maybe all threads are busy, wait 1 sec
                    time.sleep(1)
                else: # all task done, resource is empty, start quit countdown
                    print('all task done, resource is empty, start quit countdown', resWaitTimeoutRetry)
                    resWaitTimeoutRetry = resWaitTimeoutRetry - 1
                    time.sleep(1)
        # end of while, ready to quit main thread

        thr.join()
        print('------searchResult------:')
        db.printDB()
        log.log.log(1, 'main task end.')
        db.delRecord(None, None)
