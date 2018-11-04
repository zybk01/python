# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractor import LinkExtractor
import threading
import os
import re
from scrapy import Item,Field
import time

class transitem(Item):
    path= Field()
    list=Field()
    repath=Field()

def atoi(s):
 s = s[::-1]
 num = 0
 for i, v in enumerate(s):
  for j in range(0, 10):
   if v == str(j):
      num += j * (10 ** i)
 return num




class AhthorSpider(scrapy.Spider):
    name = 'ahthor'
    allowed_domains = ['kanunu8.com']
    # start_urls=input('start_urls:').strip()
    start_urls = 'http://www.kanunu8.com/author2.html'
    path = 'E:/Python/Novel1'
    path1= 'E:/Python/Novel1/Crawled.txt'
    path2 = 'E:/Python/Novel1/Failed.txt'
    numm =[]
    signal='y'
    i=0
    j=0
    threads = []
    log=[]
    loaded=[]
    crawled=[]
    crawled.append(start_urls)
    loaded.append(start_urls)
    def start_requests(self):
        isExists = os.path.exists(self.path1)
        if isExists:
            f=open(self.path1,'r',encoding='utf-8')
            self.crawled=f.readlines()
        self.signal = input('crawl mode(y for list,n for author:)')
        if self.signal=='y':
            yield scrapy.Request(self.start_urls, callback=self.callload,
                                 headers={'User-Agent': 'Mozilla/5.0'},
                                 dont_filter=True)
        else:
            request = scrapy.Request(self.start_urls, callback=self.parse,
                                     headers={'User-Agent': 'Mozilla/5.0'},
                                     dont_filter=True)
            path = self.path
            request.meta['item'] = path
            yield request

    def parse(self, response):
        # try :
        self.crawled.append(response.url)
        path=response.meta['item']

        # except Exception as e:
        #     print(e)
        font = response.xpath('//font/text()[3]').extract()[0]
        title=response.xpath('/html/head/title/text()').extract()[0]
        title = re.findall(r'(.*?) -', title)[0]
        title = title.replace(':','-')
        title = title.replace('：', '-')
        title = title.strip()
        title=title.strip('\t')
        if self.signal=='y':
            path=path
            repath = path
        else:
            path=path+'/'+title
            repath = path
            self.signal='y'
        # repath = path
        localnumm=[]
        localnumm.append(title)

        if font == '>文章内容':
            path=repath + '/' + title
            localnumm.append(path)
            isExists = os.path.exists(path)
            if not isExists:
                os.makedirs(path)
        link = LinkExtractor(restrict_xpaths='//*[@cellspacing="1"]//a')
        link = link.extract_links(response)
        number = 0
        # for sel in link:
        #     if sel.url in self.loaded:
        #         pass
        #     else:
        #         self.loaded.append(sel.url)
        #         number = number + 1
        localnumm.append(response.url)
        localnumm.append(number)

        for sel in link:
            if sel.url in self.loaded:
                pass
            else:
                self.loaded.append(sel.url)
                number=number+1
                localnumm[3] = number
                self.i=self.i+1

                # print(sel.url)
                titem=transitem()
                titem['repath']=repath
                titem['path']=path
                titem['list']=localnumm
                request=scrapy.Request(sel.url, callback=self.download_parse,
                                     headers={'User-Agent': 'Mozilla/5.0'},
                                     dont_filter=True)
                request.meta['item']=titem
                yield request

        self.numm.append(localnumm)

    def callload(self,response):

        link = LinkExtractor(restrict_xpaths='//*[@cellspacing="1"]//a')
        link = link.extract_links(response)
        for urllist in link:
            url=urllist.url
            if url in self.loaded:
                pass
            else:
                self.loaded.append(url)

                request = scrapy.Request(url, callback=self.parse,
                                         headers={'User-Agent': 'Mozilla/5.0'},
                                         dont_filter=True)
                path = self.path + '/'+urllist.text
                request.meta['item'] = path
                yield request
            time.sleep(2)


    def download_parse(self, response):
        self.j = self.j + 1
        self.crawled.append(response.url)
        # print('shiteater' + 'NO.%d' % self.j )
        path = response.meta['item']['path']
        nuum = response.meta['item']['list']
        repath=response.meta['item']['repath']
        try:
            font = response.xpath('//font/text()[3]').extract()[0]
        except:
            title = response.xpath('//font/text()').extract()[0]
            content = response.xpath('//p/text()').extract()
            url = response.url
            url = re.findall(r'([0-9]+).html', url)[0].strip()
            nuum.append(atoi(url))
            f = open(path+'/{}.txt'.format(url), 'w+', encoding='utf-8')
            f.write(title)
            f.write('\n')
            for contenta in content:
                contenta = contenta.replace('\r\n', "\n")
                f.write(contenta)
            f.close()
        else:
            nuum[3]=nuum[3]-1
            if font=='>文章内容':
                request = scrapy.Request(response.url, callback=self.parse,
                                     headers={'User-Agent': 'Mozilla/5.0'},
                                     dont_filter=True)
                request.meta['item'] = repath
                yield request

    def close(self, reason):
        failedurl=[]
        for list in self.numm:
            num=list[4:]
            num.sort()
            if list[3]==(len(list[4:])):
                try:
                    f = open(list[1]+'/{}.txt'.format(list[0]), 'a', encoding='utf-8')
                except FileNotFoundError as e:
                    print(e)
                else:
                    for j in num:
                        str1 = ".txt"
                        name = (list[1]+'/'+str(j) + str1)
                        try:
                            fa = open(name, encoding='utf-8')
                        except FileNotFoundError as e:
                            print(e)
                        # fa = open('{}.txt'.format("i"), 'w')
                        else:
                            contenta = fa.read()
                            f.write('\n\n\n\n')
                            f.write(contenta)
                            fa.close()
                            os.remove(name)
                    f.close()
                    isExists = os.path.exists(list[1]+'/{}.txt'.format(list[0]))
                    if isExists:
                        if os.path.getsize(list[1]+'/{}.txt'.format(list[0])) == 0:
                            os.remove(list[1]+'/{}.txt'.format(list[0]))
            else:
                failedurl.append(list[1]+'_'+list[0]+'_'+list[2])

        # yield self.crawled
        f = open(self.path1, 'w+', encoding='utf-8')
        for clist in self.crawled:
            f.write(clist)
            f.write('\n')
        f.close()
        f = open(self.path2, 'w+', encoding='utf-8')
        for clist in failedurl:
            f.write(clist)
            f.write('\n')
        f.close()


        closed = getattr(self, 'closed', None)
        if callable(closed):
            return closed(reason)
