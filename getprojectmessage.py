import requests
import hashlib

class PlanMassage():
	def __init__(self):
		pass
	def get_json(self,project_id):
		project_id=str(project_id)
		s=project_id+'MD5'+project_id+'dj'
		m=hashlib.md5(s.encode('ascii')).hexdigest()
		print(m)
		s='http://192.168.30.230/jiekou/OrderInfoGet_ById/?id='+project_id+'&CheckCode='+m
		try:
			r=requests.get(s,timeout=2)
		except:
			return 'fail','数据获取失败'
		j=r.json()
		if len(j)==0:
			return 'fail','查询不到该计划id'
		li=j[0]
		return 'ok',li

	def get_by_key(self,project_id,key):
		state,value=self.get_json(project_id)
		if state=='fail':
			return state,value
		return 'ok',str(value[key])




if __name__=='__main__':
	pm=PlanMassage()
	state,value=pm.get_json(7479)
	print(type(value))
	print(state,value)
	state,value=pm.get_json(100000)
	print(state,value)
	state,value=pm.get_by_key(7479,'事业部')
	print(state,value)
	state,value=pm.get_by_key(100000,'事业部')
	print(state,value)
