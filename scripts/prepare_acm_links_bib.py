#!/usr/bin/python
import sys, os, operator, re, subprocess
from pybtex.database.input import bibtex
import pycurl

if __name__ == "__main__":
	p = os.path.abspath(os.path.dirname(__file__))
	if(os.path.abspath(p+"/..") not in sys.path):
		sys.path.append(os.path.abspath(p+"/.."))
	os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")

from django.db import connection
from algorithm.utils import *
from db.session import *


'''
@author: anant bhardwaj
@date: Feb 12, 2013

script for preparing ACM Links and bib
'''
c = pycurl.Curl()

def preapre_bib(doi):
	e = re.findall('\d+',doi)
	url = '"http://dl.acm.org/downformats.cfm?id=%s&parent_id=%s' %(e[3], e[2])
	url = url + '&expformat=bibtex&CFID=324869272&CFTOKEN=80726242" \
	-H "Pragma: no-cache" -H "Accept-Charset: ISO-8859-1,utf-8;q=0.7,*;q=0.3" \
	-H "Accept-Encoding: gzip,deflate,sdch" -H "Host: dl.acm.org" \
	-H "Accept-Language: en-US,en;q=0.8" -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) \
	AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.65 Safari/537.31" -H \
	"Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8" -H \
	"Referer: http://dl.acm.org/citation.cfm?doid=2470654.2466419" \
	-H "Cookie: __atssc=twitter%3B5; picked=2470654,prox; CFID=324869272; CFTOKEN=80726242; \
	IP_CLIENT=5267471; SITE_CLIENT=3699424; __atuvc=29%7C18; cffp_mm=0" \
	-H "Connection: keep-alive" -H "Cache-Control: no-cache"'
	cmd = 'curl ' + url
	p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell = True)
	out, err = p.communicate()
	out = str(out.strip())
	print out
	return out
	


def reset_bib():
	f = open('data/doi.txt')
	data =  f.read().split('\n')

	data = map(lambda x: x.strip(), data)
	f = open('data/bib_raw.txt', 'w')
	raw_bib = ''
	for d in data:
		raw_bib = raw_bib + preapre_bib(d) + "\n\n"
	f.write(raw_bib)


reset_bib()


