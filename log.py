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
            logging.debug(msg)

log = myLog()
