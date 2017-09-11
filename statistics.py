from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import _cffi_backend
import pymysql
import openpyxl
import pymssql
import _mssql
import numpy as np
import pandas as pd
import sys
import datetime
import re
import hashlib
import requests
from bcrypt import _bcrypt
import bcrypt
import time
from types import MethodType
from pandas.io.excel import ExcelWriter
from getprojectmessage import PlanMassage
from flowstate import WinFlowState,CheckCount
from flownote import WinInOut
from dataquery import *
from faultmanager import *
from manager import *
from dataprocess import WinDataProcess
from completelineedit import CompleteLineEdit
# import jieba


class WinFaultStatistics(QWidget):
	def __init__(self,cur,conn):
		super().__init__()
		self.cur=cur
		self.conn=conn
		self.pm=PlanMassage()
		self.dic_plan_mes={}
		self.li_columns=['id','线别','分类','主型号','系列号','批次','计划id','生产日期',\
			'制程状态','单板名称','临时产品编码','故障代码','不良现象','故障分类','记录人','记录日期','维修结果',\
			'不良原因','维修人','维修次数','维修日期','工时','备注','分析分类','控制制程','分析人']

		self.initUI()


	def initUI(self):
		btn_import=QPushButton('导入计划id',self)
		btn_import.clicked.connect(self.import_file)

		vlayout=QVBoxLayout(self)
		vlayout.addWidget(btn_import,alignment=Qt.AlignLeft)
		vlayout.addStretch(1)
		self.setLayout(vlayout)
		self.show()

	def import_file(self):
		fd=QFileDialog(self)
		filename=QFileDialog.getOpenFileName(self,filter="excel file(*.xlsx)")
		print(filename)
		if filename[0]=='':
			return
		try:
			df=pd.read_excel(filename[0],sheetname='Sheet1')
			li_plan_id=df['计划id'].apply(str).tolist()
			li_plan_id=list(map(lambda x:x.replace(' ',''),li_plan_id))
			li_plan_id=list(map(lambda x:x.split('.')[0],li_plan_id))
			li_plan_id=list(set(li_plan_id))
			if 'nan' in li_plan_id:
				li_plan_id.remove('nan')
	
			if '' in li_plan_id:
				li_plan_id.remove('')

			print('表格读取计划id列表',li_plan_id)
		except:
			print('数据读取失败')
			return





		# '''test'''
		# self.cur.execute("select project_num from note_yd where service_date>='2017-8-10' and \
		# 	service_date<='2017-8-16'")

		# li=cur.fetchall()
		# # print('计划id长度',len(li))
		# li_plan_id=[]
		# for i in li:
		# 	if i[0].replace(' ','')=='':
		# 		continue
		# 	li_plan_id.append(i[0])

		# # print(li_plan_id)
		# li_plan_id=list(set(li_plan_id))
		# '''test'''




		condition=''
		if len(li_plan_id)>0:
			for i in li_plan_id:

				condition+='\''+str(i)+'\''
				if i!=li_plan_id[-1]:
					condition+=','
			condition=str(condition)
		print(condition)


		self.cur.execute("select id,line_num,product_class,main_model,serial_num,batch_num,project_num,produce_date,\
			process_state,single_board_name,product_id,fault_num,fault_name,fault_class2,note_person,note_date,material_name,\
			service_result,service_person,second_service,service_date,work_hours,comment,parse_class,\
			process_control,parse_person \
			from note_jr where project_num in ("+condition+") union all\
			select id,line_num,product_class,main_model,serial_num,batch_num,project_num,produce_date,\
			process_state,single_board_name,product_id,fault_num,fault_name,fault_class2,note_person,note_date,material_name,\
			service_result,service_person,second_service,service_date,work_hours,comment,parse_class,\
			process_control,parse_person from note_yd where project_num in ("+condition+")")

		li=self.cur.fetchall()
		print('li长度\n',len(li))
		self.df=pd.DataFrame(li,columns=self.li_columns)

		print('初始df模组系类好长度',len(self.df[self.df['分类']=='模组']['系列号'].drop_duplicates().tolist()))

		'''该循环获取计划信息，生成self.dic_plan_mes字典，出现获取失败立即停止'''
		for i in li_plan_id:
			time.sleep(0.05)
			if str(i).replace(' ','')=='':
				continue
			flag,mes=self.pm.get_json(i)
			if flag=='fail':
				QMessageBox(text='   '+str(i)+'数据获取失败！,操作已停止  ',parent=self).show()
				return
			self.dic_plan_mes[str(i)]=mes
			# print(i,'\n',mes['订单类别'])

		try:
			self.df['维修次数']=self.df['维修次数'].apply(int)
		except:
			QMessageBox(text='   维修次数出现非int型,操作已停止  ',parent=self).show()
			return
		self.df_plan_mes=None
		li_plan_mes=[]
		for i in li_plan_id:
			li_temp=[]
			li_temp.append(i)
			li_temp.append(self.dic_plan_mes[i]['订单类别'])
			li_temp.append(self.dic_plan_mes[i]['主型号'])
			li_temp.append(self.dic_plan_mes[i]['型号'])
			li_temp.append(self.dic_plan_mes[i]['生产数量'])
			li_plan_mes.append(li_temp)

		self.df_plan_mes=pd.DataFrame(li_plan_mes,columns=['计划id','订单类别','主型号','型号','生产数量'])	
		self.df_plan_mes['分类']=['n']*len(self.df_plan_mes)


		'''li_product_class为数据库记录分类列不重复列表'''
		'''dic_class_plan_num为字典，key为分类，value为分类对应的计划id'''

		li_product_class=self.df['分类'].drop_duplicates().tolist()
		dic_class_plan_num={}
		for i in li_product_class:
			dic_class_plan_num[i]=self.df[self.df['分类']==i]['计划id'].drop_duplicates().tolist()
		
		if len(dic_class_plan_num)>1:
			print('根据分类的计划Id',dic_class_plan_num)
			set_temp=None
			for k,v in dic_class_plan_num:
				if set_temp is None:
					continue
				set_temp=v
				if len(set_temp&v)>0:
					QMessageBox(text='   '+str(v)+'计划分类出现重复  ',parent=self).show()
					return

		dic_plan_class={}
		for k,v in dic_class_plan_num.items():
			for i in v:
				dic_plan_class[i]=k

		for i in range(len(self.df_plan_mes)):
			if self.df_plan_mes.loc[i,'计划id'] not in dic_plan_class:

				'''
				此处需要通过弹窗显示出i计划id在维修记录中无记录，可能无不良，
				因此无法通过维修记录找到对应的产品分类
				通过弹窗人工选择分类，整机或模组
				'''
				flag,result=WinConfirmClass(i).get_result()
				if flag=='fail':
					return
				if flag=='ok':
					self.df_plan_mes.loc[i,'分类']=result
			else:
				self.df_plan_mes.loc[i,'分类']=dic_plan_class[self.df_plan_mes.loc[i,'计划id']]

		dic_class_plan_num={}
		for i in self.df_plan_mes['分类'].drop_duplicates().tolist():
			dic_class_plan_num[i]=self.df_plan_mes[self.df_plan_mes['分类']==i]['计划id'].drop_duplicates().tolist()

		# print(dic_class_plan_num)
		index=(self.df['维修次数']==1)
		# print(self.df['维修次数'])
		# print('索引',index)
		df_once=self.df[(self.df['维修次数']==1) | (self.df['维修次数']==0)]
		# print('所有一次维修记录',df_once)


		li_df=[]
		li_df.append(['源数据',self.df])
		self.dic_model_plan={}
		if '整机' in dic_class_plan_num.keys():
			df_whole=df_once[df_once['计划id'].isin(dic_class_plan_num['整机'])]
			# li_plan_class=[]
			# for i in dic_class_plan_num['整机']:
			# 	li_temp=[]
			# 	li_temp.append(i)
			# 	li_temp.append(self.dic_plan_mes[i]['订单类别'])
			# 	li_plan_class.append(li_temp)
			# df_plan_class=pd.DataFrame(li_plan_class,columns=['计划id','订单类别'])
			# li_plan_class=df_plan_class['订单类别'].drop_duplicates().tolist()

			li_plan_class=self.df_plan_mes[self.df_plan_mes['分类']=='整机']['订单类别'].drop_duplicates().tolist()

			li_result=[]
			for x in li_plan_class:
				li_plan=self.df_plan_mes[(self.df_plan_mes['分类']=='整机') & (self.df_plan_mes['订单类别']==x)]['计划id'].drop_duplicates().tolist()
				li_model=self.df_plan_mes[self.df_plan_mes['计划id'].isin(li_plan)]['主型号'].drop_duplicates().tolist()
				
				for i in li_model:
					
					li_plan_model=self.df_plan_mes[(self.df_plan_mes['计划id'].isin(li_plan)) & \
					(self.df_plan_mes['主型号']==i)]['计划id'].drop_duplicates().tolist()
					li_temp=[]
					count=0
					# li_plan_id_temp=df_whole[df_whole['主型号']==i]['计划id'].drop_duplicates().tolist()
					for j in li_plan_model:

						count+=int(self.dic_plan_mes[j]['生产数量'])
						print('各计划id及数量',j,self.dic_plan_mes[j]['生产数量'])
					self.dic_model_plan[i+x]={'型号':i,'计划id列表':li_plan_model,'投入数':count}
					count_fault=len(df_whole[(df_whole['计划id'].isin(li_plan)) & (df_whole['主型号']==i)])
					
					count_ratio=round(1-count_fault/count,3)

					li_temp.append(x)
					li_temp.append('整机')
					li_temp.append(i)
					li_temp.append(count)
					li_temp.append(count_fault)
					li_temp.append(count_ratio)
					# li_temp.append(li_plan_model)

					li_result.append(li_temp)
			df_temp=pd.DataFrame(li_result,columns=['订单类别','分类','型号','生产总数','不良数','合格率'])
			li_df.append(['整机一次合格率',df_temp])

		if '模组' in dic_class_plan_num.keys():

			df_whole=df_once[df_once['计划id'].isin(dic_class_plan_num['模组'])]
			# li_plan_class=[]
			# for i in dic_class_plan_num['模组']:
			# 	li_temp=[]
			# 	li_temp.append(i)
			# 	li_temp.append(self.dic_plan_mes[i]['订单类别'])
			# 	li_plan_class.append(li_temp)
			# df_plan_class=pd.DataFrame(li_plan_class,columns=['计划id','订单类别'])
			# li_plan_class=df_plan_class['订单类别'].drop_duplicates().tolist()

			li_plan_class=self.df_plan_mes[self.df_plan_mes['分类']=='模组']['订单类别'].drop_duplicates().tolist()

			li_result=[]

			'''循环订单类别'''
			for x in li_plan_class:
				'''li_plan为该订单类别的所有计划id'''
				# li_plan=df_plan_class[df_plan_class['订单类别']==x]['计划id'].drop_duplicates().tolist()
				li_plan=self.df_plan_mes[(self.df_plan_mes['分类']=='模组') & (self.df_plan_mes['订单类别']==x)]['计划id'].drop_duplicates().tolist()
				'''li_model为该订单类别下的所有型号'''
				li_model=df_whole[df_whole['计划id'].isin(li_plan)]['系列号'].drop_duplicates().tolist()

				print('模组li_model长度',len(li_model))
	
				for i in li_model:
					'''li_plan_model为x订单类别下i型号的所有计划id'''
					li_plan_model=df_whole[(df_whole['计划id'].isin(li_plan)) & (df_whole['系列号']==i)]['计划id'].drop_duplicates().tolist()
					li_temp=[]
					count=0
					# li_plan_id_temp=df_whole[df_whole['主型号']==i]['计划id'].drop_duplicates().tolist()
					for j in li_plan_model:
						count+=int(self.dic_plan_mes[j]['生产数量'])
					count_fault=len(df_whole[(df_whole['计划id'].isin(li_plan)) & (df_whole['系列号']==i)])
					
					count_ratio=round(1-count_fault/count,3)
					li_temp.append(x)
					li_temp.append('模组')
					li_temp.append(i)
					li_temp.append(count)
					li_temp.append(count_fault)
					li_temp.append(count_ratio)
					li_result.append(li_temp)


			df_temp=pd.DataFrame(li_result,columns=['订单类别','分类','型号','生产总数','不良数','合格率'])
			li_df.append(['模组一次合格率',df_temp])


				
		print('dic_model_plan',self.dic_model_plan)
		


		df_once=df_once[df_once['分类']=='整机'].fillna(value='None')
		for i in self.dic_model_plan.keys():
			li_result=[]
			# print(i,self.dic_model_plan[i]['计划id列表'])
			'''li_process制程状态'''
			li_process=df_once[df_once['计划id'].isin(self.dic_model_plan[i]['计划id列表'])]['制程状态'].drop_duplicates().tolist()
			li_header=['制程分类','投入数','不良数']

			li_fault_type=df_once[(df_once['计划id'].isin(self.dic_model_plan[i]['计划id列表']))]['分析分类'].drop_duplicates().tolist()
			li_header+=li_fault_type
			li_fault_type2=df_once[(df_once['计划id'].isin(self.dic_model_plan[i]['计划id列表'])) & (df_once['控制制程']!='None')]['控制制程'].drop_duplicates().tolist()
			li_header+=li_fault_type2
			li_fault_type3=df_once[(df_once['计划id'].isin(self.dic_model_plan[i]['计划id列表'])) & (df_once['分析人']!='None')]['分析人'].drop_duplicates().tolist()
			li_header+=li_fault_type3
			# li_fault_type+=li_fault_type2
			# li_fault_type+=li_fault_type3
			# print('start',li_fault_type,'end')

			for j in li_process:
				li_temp=[]
				li_temp.append(j)
				print('i数组测试',i)
				print('投入数',self.dic_model_plan[i]['投入数'])
				li_temp.append(self.dic_model_plan[i]['投入数'])
				count_fault=len(df_once[(df_once['计划id'].isin(self.dic_model_plan[i]['计划id列表'])) & (df_once['制程状态']==j)])
				li_temp.append(count_fault)

				


				for x in li_fault_type:
					count=len(df_once[(df_once['计划id'].isin(self.dic_model_plan[i]['计划id列表'])) & (df_once['制程状态']==j) & (df_once['分析分类']==x)])
					li_temp.append(count)
				for x in li_fault_type2:
					count=len(df_once[(df_once['计划id'].isin(self.dic_model_plan[i]['计划id列表'])) & (df_once['制程状态']==j) & (df_once['控制制程']==x)])
					li_temp.append(count)
				for x in li_fault_type3:
					count=len(df_once[(df_once['计划id'].isin(self.dic_model_plan[i]['计划id列表'])) & (df_once['制程状态']==j) & (df_once['分析人']==x)])
					li_temp.append(count)
				li_result.append(li_temp)

				# for x in li_result:
				# 	print(len(x))
				# 	print(x)
			if len(li_result) !=0:
				li_temp=['','','']
				for m in range(len(li_result[0])):
					
					if m<3:
						continue

					count=0
					for n in li_result:
						# print('nnn',n,'mm',m)
						count+=n[m]
					li_temp.append(round(1-count/li_result[0][1],3))
				li_result.append(li_temp)


			df_temp=pd.DataFrame(li_result,columns=li_header)

			li_df.append([i,df_temp])


		
		filename=QFileDialog.getSaveFileName(self,'存储为','D:/数据统计','xlsx')
		if filename[0]=='':
			return
		writer = ExcelWriter(filename[0]+'.'+filename[1])

		for i in li_df:
			i[1].to_excel(writer,sheet_name=i[0])
		writer.save()

class WinConfirmClass(QDialog):
	def __init__(self,plan_id):
		super().__init__()
		self.plan_id=plan_id
		self.flag='fail'
		self.result=''
		self.initUI()

	def initUI(self):
		label_mes=QLabel('该计划id无法找到产品分类，请手动选择',self)
		label_plan=QLabel('计划id：'+str(self.plan_id),self)
		self.comb_class=QComboBox(self)
		self.comb_class.addItems(['整机','模组'])
		btn_confirm=QPushButton('确定',self)
		btn_confirm.clicked.connect(self.confirm)
		vlayout=QVBoxLayout(self)
		vlayout.addWidget(label_mes)
		vlayout.addWidget(label_plan)
		vlayout.addWidget(self.comb_class)
		vlayout.addWidget(btn_confirm)
		self.setLayout(vlayout)
		self.show()
		self.exec()

	def confirm(self):
		self.flag='ok'
		self.result=self.comb_class.currentText()
		self.close()

	def get_result(self):
		return self.flag,self.result



def connDB():
	conn=pymssql.connect(host='192.168.70.3',user='Chenyong',password='147258',database='WeiXiuDB',charset='utf8')
	# conn=pymysql.connect(host='127.0.0.1',user='root',password='000000',db='weixiu',charset='utf8')
	cur=conn.cursor()
	print('connect OK')
	return(conn,cur)

if __name__=='__main__':
	app=QApplication(sys.argv)
	conn,cur=connDB()
	win=WinFaultStatistics(cur,conn)
	sys.exit(app.exec_())