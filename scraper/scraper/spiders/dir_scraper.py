#!/usr/bin/env python
from scrapy.spider import Spider
from scrapy.selector import Selector
import json
from scraper.items import Website
import os
from HTMLParser import HTMLParser
from BeautifulSoup import BeautifulSoup
import nltk
import string
import unicodedata

dirs = []
common_words = []
with open('/home/sathya/github/scraper/scraper/spiders/words.txt', 'rb') as txtfile:
    wordline = txtfile.read()
    common_words = wordline.split(',')
class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)
    
def stripAllTags( html ):
    if html is None:
	return None
    soup = BeautifulSoup(html)
    for elem in soup.findAll(['script', 'style']):
	elem.extract()
    return unicode(soup)

class DmozSpider(Spider):
    name = "dmoz"
    start_urls = []
    count = 0
    i = 0
    flag = 1
    
    with open('/home/sathya/github/scraper/output.json', 'r') as json_file:
        for json_line in json_file:
	    count += 1	    
	    if count>289000:
		    #if not(count%100 == 0) and flag == 1:			
		    #else:
		if not(count%10 == 0):
			flag = 0
			#count += 1
		else:
			json_data = json.loads(json_line)
  			url = json_data['url']
			dirs.append(json_data['topic'])
			start_urls.append(url)
	with open('/home/sathya/count','wb') as txt:
		txt.write(str(len(start_urls)))
    #for a in start_urls:
        #print a

        def parse(self, response):
	    fd = nltk.FreqDist()
	    punct = set(string.punctuation)
	    self.i += 1
	    titles = Selector(response=response).xpath('//title/text()').extract()
            filename = response.url.split("/")[-2]
	    filedir = dirs[self.i - 1] + '/' + filename
	    filedir = 'Top' + '/' + filedir.split('/')[1] + '-' + filedir.split('/')[2]
	    print dirs[self.i - 1]
	    print filedir
	    temp = stripAllTags(response.body)
	    s = MLStripper()
	    s.feed(temp)
	    pure_body = s.get_data()
	    pure_body = pure_body.lower()
	    pure_body = unicodedata.normalize('NFKD', pure_body).encode('ASCII', 'ignore')
	    for word in nltk.regexp_tokenize(pure_body, pattern=r'\.|(\s+)', gaps = True):
		if word not in punct and word not in common_words:
		    fd.inc(word)
	    freq_tuples = fd.items()
	    if not(os.path.exists(filedir)):
		os.makedirs(filedir)
	    filedir = filedir + '/' + filename
            with open(filedir, 'wb') as f:
		f.write('@attribute ' + filedir.split('/')[1] + ' {0,1}\n\n' + '@data\n')
		f.write('\n')
		for title in titles:
		    f.write(title.encode('utf-8').strip())
		f.write('\n')
                for item in freq_tuples:
		    i = 0
		    while i < item[1]:
			i+=1
			f.write(item[0] + '\n')
