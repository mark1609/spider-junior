import argparse
import log

class arg():
    def __init__(self):
        self.seedurl = 'http://www.sina.com.cn/'
        self.depth = 2
        self.logfile = 'spiderlog.log'
        self.thrNum = 10
        self.dbfile = 'linkdb'
        self.key = None
        self.loglevel = 1
        self.testself = False

    def print(self):
        print(self.seedurl, self.depth, self.logfile, self.loglevel,
              self.thrNum, self.dbfile, self.testself, self.key)

def argParse():
    parser = argparse.ArgumentParser(description='internet spider')
    parser.add_argument('-l', metavar='loglevel', help='log level', nargs=1, type=int, default=5, choices=range(1, 6))
    parser.add_argument('-d', metavar='depth', help='depth of spider', nargs=1, type=int, default=2, choices=range(1,))
    parser.add_argument('-thread', metavar='number', help='number of threads', nargs=1, type=int, default=10, choices=range(1,))
    parser.add_argument('-u', metavar='url', help='seed url', nargs=1, type=str, default='http://www.sina.com.cn/')
    parser.add_argument('-f', metavar='logfile', help='log file', nargs=1, type=str, default='spider.log')
    parser.add_argument('-dbfile', metavar='dbfile', help='database file', nargs=1, type=str, default='spider.db')
    parser.add_argument('-testself', help='run self test', action='store_true')
    parser.add_argument('-key', help='content you interested', nargs='*', default=None)
    return parser.parse_args()

def initParam(argRun):
    args = argParse()
    argRun.loglevel = args.l
    argRun.logfile = args.f
    log.log.init(argRun.logfile, argRun.loglevel)

    argRun.depth = args.d
    argRun.thrNum = args.thread
    argRun.seedurl = args.u
    argRun.dbfile = args.dbfile
    argRun.testself = args.testself
    argRun.key = args.key
    log.log.log(1, 'arguments load complete')
