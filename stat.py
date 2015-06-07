from threading import *
from queue import *

class myStat():
    def __init__(self):
        self.nodeRecord = []
        self.nodeRemain = []
        self.level = 0
        self.interval = 3600
        self.quit = True
        self.que = Queue()

    def init(self, level, interval):
        self.level = level
        self.interval = interval
        self.quit = False
        for i in range(self.level):
            self.nodeRecord.append(0)
            self.nodeRemain.append(0)

    def readStatFromQue(self):
        while self.que.empty() != True:
            statObj = self.que.get()
            level, num = statObj
            self.updateNodeRemianCnd(level, num)

    def addNodeRecordCnt(self, level):
        self.nodeRecord[level-1] = self.nodeRecord[level-1] + 1

    def updateNodeRemianCnd(self, level, num):
        self.nodeRemain[level-1] = self.nodeRemain[level-1] + num

    def showProgress(self):
        self.readStatFromQue()

        print('  node  recorded (remain):')
        totalRecord = 0
        totalRemain = 0

        for i in range(self.level):
            print('  depth(%2d): %24d %22s (%d)' % (i+1, self.nodeRecord[i], ' ', self.nodeRemain[i]))
            totalRecord = totalRecord + self.nodeRecord[i]
            totalRemain = totalRemain + self.nodeRemain[i]
        print('--total recorded (remain): %10d %22s (%-d)' % (totalRecord, ' ', totalRemain))
        if self.quit != True:
            self.start()

    def start(self):
        t = Timer(self.interval, self.showProgress)
        t.start()

    def stop(self):
        self.quit = True


#stat = stat(1,3)
#stat.showProgress()
#stat.start()
