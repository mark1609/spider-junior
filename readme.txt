date:	
	2015-6-3
description: 
	具备基本功能的网络爬虫，从种子url出发，获取指定层次的页面信息并保存。所有接口均使用python3.4自带lib实现。
	db.py: 封装sqllite数据库保存和读取接口
	linkparser.py: 封装页面载入与分析接口
	spider-main.py: 爬虫主现场和下载解析线程调度
faults:
	尚未接受可输入参数，所有参数暂时内部固定；
	不打印log；
	存储数据库的名称固定。
problem & solve:
1.问题：
	在页面解码花的时间较多，py3.4没有chardet模块，有些页面为gzip格式，无法直接解析；
  解决：
	通过re寻找页面编码方式，url中带中文参数的自己实现通过url整体编码，替换中文字符，再整体解码的方式，使用方便（网上查到都是urllib.parse.quote的方式，如果url中有多个中文参数则需要分割后各个转码再拼装）；gzip格式的页面先解压在分析。

2.问题：
	测试时有个url中所有链接均为本服务器页面，在抓取时造成短时间内产生大量访问的效果，触发了改网站入侵检测软件（safedog）做出保护机制，将所有请求导向该软件页面。
  解决：
	考虑到这种页面属于普遍情况，即新浪网内一个页面的大部分链接都属于本网站，一般小网站也没有使用多服务器进行分流，同一pc的所有线程抓包使用的ip都相同，如果运行速度较快很容易被理解为攻击行为。
	在当前没有多个ip可用于报文捕获的情况下，在每个线程开始抓包前随机睡眠0到线程数+1秒，尽量错开访问时间；
	同时，采用资源队列表的方式代替最初实现（在本机未上传）单资源队列的实现访问目标的分散。
	即页面获取线程将页面内的链接，使用host为key进行散列，将这个链接放入资源队列数组中的某个队列，粗略认为相同host指向的ip一致，不同host的链接会分布于表里不同的队列里。
	主线程从资源表里获取链接，采用纵向遍历的方式，每次获取不同表的首节点，保存数据库后将节点写入单一任务队列，资源表共有和线程数相等的队列数量，在理想情况下，任务队列中每个窗口内（窗口长度等于线程数）节点host互异，假设线程并发获取到这些节点，访问的目标各不相同。