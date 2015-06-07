import sqlite3
import log
dbName = "linkDB.db"
dbTabName = "linkInfo"

def createDB():
    conn = sqlite3.connect(dbName)
    with conn:
        c = conn.cursor()
        cmd = "create table if not exists " + dbTabName + " (link text, content text)"
        #print(cmd)
        c.execute(cmd)

def fetchRecord(link, content):
    with sqlite3.connect(dbName) as conn:
        c = conn.cursor()
        if link != None and content != None:
            info = (link, content,)
            c.execute("select * from linkInfo where link=? and content=?", info)
        elif link != None:
            info = (link,)
            c.execute("select * from linkInfo where link=?", info)
        elif content != None:
            info = (content,)
            c.execute("select * from linkInfo where content=?", info)
        else:
            c.execute("select * from linkInfo")
        result = c.fetchall()
        if link is None and content is None:
            try:
                print('fetch record for:', link, content, result)
            except UnicodeEncodeError:
                log.log.log(5,'exotic character')
        return(result)

def recordLink(link, content):
    if link is None or content is None:
        #print('invalid link or content')
        return
    with sqlite3.connect(dbName) as conn:
        c = conn.cursor()
        #redundant = fetchRecord(link, content)
        #if len(redundant) != 0:
            #print('redundant record:', link, content)
            #return
        info = (link, content)
        c.execute("insert into linkInfo values (?,?)",info)
        #print('add record: ', link, content)
        conn.commit()

def delRecord(link, content):
    with sqlite3.connect(dbName) as conn:
        #print('deleting record: ', link, content)
        c = conn.cursor()
        if link != None and content != None:
            info = (link, content,)
            c.execute("delete from linkInfo where link=? and content=?", info)
        elif link != None:
            info = (link,)
            c.execute("delete from linkInfo where link=?", info)
        elif content != None:
            info = (content,)
            c.execute("delete from linkInfo where content=?", info)
        else:
            c.execute("delete from linkInfo")
        conn.commit()

def printDB():
    fetchRecord(None,None)
##def test():
##    createDB(dbName)
##    recordLink('linka', 'news')
##    recordLink('linkb', 'movie')
##    recordLink('linkc', 'music')
##    #print(fetchRecord('linkb',None))
##    ##fetchRecord(None,'music')
##    ##fetchRecord('linka','news')
##    ##fetchRecord('linkb','news')
##    recordLink('linkdc', 'music-all')
##    print('-------',fetchRecord(None,None))
##    delRecord('linkb',None)
##    print('-------',fetchRecord(None,None))
##    delRecord(None,'news')
##    print('-------',fetchRecord(None,None))
##    delRecord('linkcde','news')
##    print('-------',fetchRecord(None,None))
##    delRecord('linkc','music')
##    print('-------',fetchRecord(None,None))
##    delRecord(None,None)
##    print('-------',fetchRecord(None,None))

#test()
