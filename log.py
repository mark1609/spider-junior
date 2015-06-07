
import logging

class myLog():
    def __init__(self):
        self.loglevel = 1

    def init(self, logfileName, loglevel):
        self.loglevel = loglevel
        logging.basicConfig(filename=logfileName,
                            filemode='w',
                            level=logging.DEBUG,
                            format='%(asctime)s %(thread)d %(message)s')
        logging.debug('test start')

    def log(self, level, msg):
        if level <= self.loglevel:
            try:
                logging.debug(msg.encode('utf-8'))
            except UnicodeEncodeError:
                logging.debug('exotic character')

    def logKeyObj(self, level, msg, keyObj):
        if keyObj != None:
            for key in keyObj:
                msg = msg + key
        else:
            msg = msg + ' None'
        self.log(level, msg)

    def logTaskObj(self, level, msg, taskObj):
        link, depth = taskObj
        if link != None and depth != None:
            msg = msg + str(depth) + ' url: ' + link
            self.log(level, msg)

    def logResObj(self, level, msg, resObj):
        link, content, depth, quit = resObj
        if link == None:
            link = 'None'
        if content == None:
            content = 'None'
        msg = msg + ' '+ link + ' ' + content + ' ' + str(depth) + ' ' + str(quit)
        self.log(level, msg)

    def logRecordLink(self, level, msg, link, content):
        msg = msg +  ' '+ link + ' ' + content
        self.log(level, msg)

    def logOpenUrl(self, level, msg, url):
        msg = msg + ' ' + url
        self.log(level, msg)

    def logMsgWithIntValue(self, level, msg, value):
        msg = msg + ' ' + str(value)
        self.log(level, msg)



log = myLog()
