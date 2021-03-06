# coding=gbk
from html.parser import HTMLParser
import urllib.request
import urllib.parse
import db
import re
import zlib
import array
import socket
import log

class filter():
    def __init__(self):
        self.dict = {}

    def isDataExists(self, data):
        key = hash(data)
        if key in self.dict:
            return True
        self.dict[key] = data

class page():
    def init(self, url):
        self.charset = None
        self.pageStr = None
        self.info = urllib.parse.urlparse(url)
        self.length = 0

        if self.info.scheme == 'http':
            log.log.logOpenUrl(4, 'open url:', url)
            #print(type(url),url.encode('gbk'))
            #print(urllib.parse.quote("公积金信息披露",encoding='GBK') )
            d = url.encode('gbk', 'ignore') # procedure below for shitty url like this: "http://tags.news.sina.com.cn/公积金"
            a = array.array('b')
            #a.frombytes(d)
            #print(a)
            ctr = 0
            for c in d:
                if c <= 127:
                    a.append(c)
                else:
                    if ctr == 0:
                        a.append(37)
                    ctr = (ctr+1)%2
                    x = hex(c)
                    u = int(x[2],16)
                    if u < 10:
                        a.append(u+48)
                    else:
                        a.append(u+87)
                    u = int(x[3],16)
                    if u < 10:
                        a.append(u+48)
                    else:
                        a.append(u+87)
            #print(a)
            k = a.tobytes()
            #print(k)

            e = k.decode('gbk')
            #print('eeeeee',e)
            try:
                self.f = urllib.request.urlopen(e,None,timeout=1) # open url
                self.length = self.f.length
            except socket.timeout:
                log.log.log(5, 'socket timeout on open')
                return -1
            except urllib.error.URLError:
                log.log.log(5, 'url error')
                return -1
            except ConnectionResetError:
                log.log.log(5, 'connection reset')
                return -1

            try:
                self.pageBytes = self.f.read()
            except socket.timeout:
                log.log.log(5, 'socket timeout on read')
                return -1
            #print(self.f.headers.get_content_length())
            return 0
        else:
            log.log.log(5, 'unknown url scheme')
            return -1

    def getCharset(self):
        hdr = self.f.headers
        charset = hdr.get_content_charset() # get charset from header first
        if charset != None:
            self.charset = charset
            return
        hdrStr = hdr.as_string().replace('\n', ' ')
        #print('hdrstr', hdrStr)

        if hdrStr.find('gzip') != -1: # page been compressed
            log.log.log(2, 'decompress gzip data')
            self.pageBytes = zlib.decompress(self.pageBytes, 16+zlib.MAX_WBITS) # decompress data

        # here self.pageBytes are ready for decoding
        #print(self.pageBytes.find('charset='))

        Array = array.array("B")
        #print(tmpHdr)
        for c in self.pageBytes:
            if c < 127:
                Array.append(c)
        #print(Array)
        d = Array.tobytes()

        #print(d)

            #print(tmpHdr[i])
        #tmpHdr.
        #print('hhh')
        a = d.decode().replace('\n', ' ')
        #print('hhddddh')
        #b = a.replace('\n', ' ')
        #print('ddddddddddd',b)
        #c = b
        #print(type(c),c.find("charset"))
        #print(type(c),c.find("charset"),c)
        pos = a.find("charset")
        e = a[pos:pos+50]
        #print(e)

        #print(tmpHdrStr)#.replace('\n', ' ')
        #print('------------------',tmpHdr, tmpHdrStr)
        m = re.match('.*charset=(\S+)"', e)
        if m != None:
            #print(m.group(1))
            self.charset = m.group(1)
            if self.charset == 'gb2312':
                self.charset = 'gbk'
        else:
            self.charset = 'utf-8'

        #print('charset:', self.charset,"------")
        #self.charset='gbk'
        return
    def pageLoader(self, url):
        ret = self.init(url)
        if ret != -1:
            self.getCharset()
            self.pageStr = self.pageBytes.decode(self.charset,'ignore')
        return self.pageStr
    
class MyHTMLParser(HTMLParser):
    def init(self, prefix):
        self.link = None
        self.dict = {}
        self.prefix = prefix
        
    def handle_starttag(self, tag, attrs):
        for attr in attrs:
            if attr[0] == 'href' and attr[1] != None:
                if attr[1].endswith('.css'):
                    self.link = None
                elif attr[1].startswith('/'):
                    self.link = self.prefix + attr[1]
                else:
                    self.link = attr[1]
                
    def handle_data(self, data):
        data = data.lstrip('\n \t')
        self.dict[self.link] = data.rstrip('\n \t')
        self.link = None

    def parse(self, data, prefix):
        self.init(prefix)
        self.feed(data)

    def matchKey(self, content, keyObj):
        if keyObj == None:
            return True
        for key in keyObj:
            if content.find(key) != -1:
                return True
        return False

    def send(self, level, quit, queueArray, keyObj, fltr, host, statQue):
        bulkStat = 0
        for link, content in self.dict.items():
            if link != None and len(link)>0 and content != None and len(content)>0:
                if fltr.isDataExists(link) != True and self.matchKey(content, keyObj) == True:
                    obj = (link, content, level, quit)
                    queueArray.insert(host, obj)
                    bulkStat = bulkStat + 1
                    try:
                        log.log.logResObj(4, 'enqueue: ', obj)
                    except UnicodeEncodeError:
                        log.log.log(5, 'exotic character')
        statObj = (level, bulkStat)
        statQue.put(statObj)

    def record(self):
        db.createDB()
        for link, content in self.dict.items():            
            if link != None and len(link) > 0 and content != None and len(content) > 0:                
                print(link, content)
                db.recordLink(link, content)
        db.printDB()
