import hashlib
import requests

def fun(d):
	s=str(d)+'MD5'+str(d)+'dj'
	print(s)
	m=hashlib.md5(s.encode('ascii')).hexdigest()
	print(m)
	s='http://192.168.10.138:8011/jiekou/OrderInfoGet_ById/?id='+str(d)+'&CheckCode='+m
	r=requests.get(s)
	print(r.text)

while True:
	d=input()
	text=fun(int(d))
