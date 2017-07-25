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

'''
产品信息栏，根据计划ID获取信息，设置内容，获取内容，设置widget是否使能

'''

class ProductBaseMassage(QGroupBox):
	def __init__(self,li_product_type=['整机','模组','单板'],dic_main_model={},dic_model={},li_process_status=[],li_line_name=[]):
		super().__init__('产品信息')
		self.parent=None
		self.li_product_type=li_product_type
		self.dic_main_model=dic_main_model
		self.dic_model=dic_model
		self.li_process_status=li_process_status
		self.li_line_name=li_line_name
		self.dic_widget={}
		self.li_comb=['产品分类','主型号','系列号','线别','制程状态','事业部']
		self.li_line=['单板名称','计划ID','批次']
		self.li_date=['生产日期']
		self.initUI()
		self.show()
	def initUI(self):
		label_product_type=QLabel('产品分类',self)
		label_main_model=QLabel('主型号',self)
		label_model=QLabel('系列号',self)
		label_batch=QLabel('批次',self)
		label_board_name=QLabel('单板名称',self)
		label_process_status=QLabel('制程状态',self)
		label_project_num=QLabel('计划ID',self)
		label_produce_date=QLabel('生产日期',self)
		label_line_name=QLabel('线别',self)
		label_partment=QLabel('事业部',self)

		self.comb_product_type=QComboBox(self)
		self.comb_main_modle=QComboBox(self)
		self.comb_model=QComboBox(self)
		self.comb_process_status=QComboBox(self)
		self.comb_line_name=QComboBox(self)
		self.comb_partment=QComboBox(self)
		self.line_board_name=QLineEdit(self)
		self.line_project_num=QLineEdit(self)
		self.line_batch=QLineEdit(self)
		self.line_produce_date=QDateEdit(QDate.currentDate(),self)

		self.dic_widget['产品分类']=self.comb_product_type
		self.dic_widget['主型号']=self.comb_main_modle
		self.dic_widget['系列号']=self.comb_model
		self.dic_widget['线别']=self.comb_line_name
		self.dic_widget['制程状态']=self.comb_process_status
		self.dic_widget['单板名称']=self.line_board_name
		self.dic_widget['计划ID']=self.line_project_num
		self.dic_widget['批次']=self.line_batch
		self.dic_widget['生产日期']=self.line_produce_date
		self.dic_widget['事业部']=self.comb_partment

		self.comb_product_type.setEditable(True)
		self.comb_main_modle.setEditable(True)
		self.comb_model.setEditable(True)
		self.comb_process_status.setEditable(True)
		self.comb_line_name.setEditable(True)
		self.comb_partment.setEditable(True)

		self.comb_product_type.addItems(self.li_product_type)
		
		
		self.comb_process_status.addItems(self.li_process_status)
		self.comb_line_name.addItems(self.li_line_name)
		self.comb_partment.addItems(['移动','金融'])
		self.comb_main_modle.addItems(self.dic_main_model[self.comb_partment.currentText()])
		self.comb_model.addItems(self.dic_model[self.comb_main_modle.currentText()])

		self.line_project_num.editingFinished.connect(self.project_num_finished)
		self.line_project_num.textChanged.connect(self.project_num_textChanged)
		self.comb_product_type.currentIndexChanged[str].connect(self.product_type_changed)
		self.comb_partment.currentIndexChanged[str].connect(self.partmen_changed)
		self.comb_main_modle.currentIndexChanged[str].connect(self.main_model_changed)
		# self.comb_main_modle.editTextChanged.connect(self.main_model_changed)
		# self.comb_model.editTextChanged.connect(self.model_changed)
		# self.line_batch.textChanged.connect(self.batch_changed)


		glayout=QGridLayout(self)
		glayout.addWidget(label_project_num,0,0,alignment=Qt.AlignRight)
		glayout.addWidget(self.line_project_num,0,1)
		glayout.addWidget(label_batch,0,2,alignment=Qt.AlignRight)
		glayout.addWidget(self.line_batch,0,3)
		glayout.addWidget(label_main_model,0,4,alignment=Qt.AlignRight)
		glayout.addWidget(self.comb_main_modle,0,5)
		glayout.addWidget(label_model,0,6,alignment=Qt.AlignRight)
		glayout.addWidget(self.comb_model,0,7)
		glayout.addWidget(label_product_type,1,0,alignment=Qt.AlignRight)
		glayout.addWidget(self.comb_product_type,1,1)
		glayout.addWidget(label_process_status,1,2,alignment=Qt.AlignRight)
		glayout.addWidget(self.comb_process_status,1,3)
		glayout.addWidget(label_line_name,1,4,alignment=Qt.AlignRight)
		glayout.addWidget(self.comb_line_name,1,5)
		glayout.addWidget(label_produce_date,1,6,alignment=Qt.AlignRight)
		glayout.addWidget(self.line_produce_date,1,7)
		glayout.addWidget(label_board_name,2,0,alignment=Qt.AlignRight)
		glayout.addWidget(self.line_board_name,2,1)
		glayout.addWidget(label_partment,2,2,alignment=Qt.AlignRight)
		glayout.addWidget(self.comb_partment,2,3)

		glayout.setColumnStretch(0,1)
		glayout.setColumnStretch(1,4)
		glayout.setColumnStretch(2,1)
		glayout.setColumnStretch(3,4)
		glayout.setColumnStretch(4,1)
		glayout.setColumnStretch(5,4)
		glayout.setColumnStretch(6,1)
		glayout.setColumnStretch(7,4)

		self.line_project_num.setFocus()

		self.setLayout(glayout)

'''
只有维修员账号初始化时调用此方法，目的是在此有一个对结果登记栏的引用，
当事业部发生改变时能够改变结果登记栏故障现象自动匹配的内容
'''
	def add_parent(self,parent):
		self.parent=parent
		
	def main_model_changed(self,main_model):
		print('main_model>>>>>',main_model)
		if main_model=='':
			return
		self.comb_model.clear()
		self.comb_model.addItems(self.dic_model[main_model])

	def set_content(self,dic_widget):
		for key,value in dic_widget.items():
			if key in self.li_comb:
				self.dic_widget[key].setCurrentText(value)
			if key in self.li_line:
				self.dic_widget[key].setText(value)
			if key in self.li_date:
				self.dic_widget[key].setDate(QDate(int(value[0:4]),int(value[5:7]),int(value[8:10])))

		if '事业部' in dic_widget.keys():
			self.change_parent_fault_model(dic_widget['事业部'])

	def get_content(self):
		dic={}
		for key,value in self.dic_widget.items():
			if key in self.li_comb:
				dic[key]=value.currentText().replace(' ','')
			if key in self.li_line:
				dic[key]=value.text().replace(' ','')
			if key in self.li_date:
				dic[key]=value.date().toString("yyyy-MM-dd")
		return dic


	def project_num_finished(self):
		project_num=self.line_project_num.text().replace(' ','')
		print(project_num)
		print(type(project_num))
		if project_num=='':			
			return
		pm=PlanMassage()
		status,value=pm.get_json(project_num)
		if status=='fail':
			dic={}
			dic['主型号']=''
			dic['系列号']=''
			dic['批次']=''
			self.set_content(dic)
			self.set_widget_enable(True)
			return
		dic={}
		dic['主型号']=value['主型号']
		dic['系列号']=value['型号']
		dic['批次']=value['生产批次']
		dic['事业部']=value['事业部']

		self.set_widget_enable(False)

		test_dic=self.get_content()
		print(test_dic,'>>>>')


		self.set_content(dic)
		self.comb_product_type.setFocus()


	'''
	用于将基本信息的计划ID相关的部件使能或去使能
	'''
	def set_widget_enable(self,flag):
		self.dic_widget['主型号'].setEnabled(flag)
		self.dic_widget['系列号'].setEnabled(flag)
		self.dic_widget['批次'].setEnabled(flag)
		self.dic_widget['事业部'].setEnabled(flag)

	def set_enable_all(self,flag):
		# self.set_widget_enable(flag)
		self.dic_widget['计划ID'].setEnabled(flag)
		self.dic_widget['产品分类'].setEnabled(flag)
		self.dic_widget['制程状态'].setEnabled(flag)
		self.dic_widget['线别'].setEnabled(flag)
		self.dic_widget['生产日期'].setEnabled(flag)
		self.dic_widget['单板名称'].setEnabled(flag)



	def project_num_textChanged(self,text):
		if text=='':
			dic={}
			dic['主型号']=''
			dic['系列号']=''
			dic['批次']=''
			self.set_content(dic)
			self.set_widget_enable(True)

	def partmen_changed(self,text):
		# self.line_project_num.setText('')
		print(text,'?????')
		self.comb_main_modle.clear()
		self.comb_main_modle.addItems(self.dic_main_model[text])
		self.change_parent_fault_model(text)
		# def main_model_changed(self):
		# 	self.line_project_num.setText('')
		# def model_changed(self):
		# 	self.line_project_num.setText('')
		# def batch_changed(self):
		# 	self.line_project_num.setText('')

	def change_parent_fault_model(self,text):
		if self.parent is not None:
			self.parent.change_fault_name(text)
	


	def product_type_changed(self,text):
		if text=='模组':
			dic={}
			dic['制程状态']='组件'
		else:
			dic={}
			dic['制程状态']='整机组装'
		self.set_content(dic)


class ProductFaultMassage(QGroupBox):
	def __init__(self,product_base,li_fault,note_record):
		super().__init__('现象登记')

		self.li_fault=li_fault
		self.product_base=product_base
		self.note_record=note_record
		self.li_btn=[]

		self.initUI()
		
		self.show()
	def initUI(self):
		label_product_num=QLabel('产品编码',self)
		label_fault=QLabel('不良现象',self)
		label_note_count=QLabel('登记数量:',self)

		glayout=QGridLayout(self)
		hlayout=QHBoxLayout()

		self.line_product_num=QLineEdit(self)
		self.line_note_count=QLineEdit(self)
		self.line_note_count.setEnabled(False)
		for i in self.li_fault:
			btn=QPushButton(i,self)
			btn.clicked.connect(self.btn_event)
			hlayout.addWidget(btn)
		glayout.addWidget(label_product_num,0,0)
		glayout.addWidget(self.line_product_num,0,1)
		glayout.addWidget(label_fault,1,0)
		glayout.addLayout(hlayout,1,1)
		glayout.addWidget(label_note_count,0,2)
		glayout.addWidget(self.line_note_count,0,3)


	def btn_event(self):
		global user_name
		note_person=user_name
		note_time=str(datetime.datetime.now())[0:19]
		sender=self.sender()
		
		product_num=self.line_product_num.text().replace(' ','')
		if product_num=='':
			QMessageBox(text=' 临时编号未填写！',parent=self).show()
			return

		dic_base_massage=self.product_base.get_content()
		if dic_base_massage['计划ID']=='':
			QMessageBox(text=' 计划ID未填写！',parent=self).show()
			return
		fault_type=sender.text()
		project_num=dic_base_massage['计划ID']
		main_model=dic_base_massage['主型号']
		model=dic_base_massage['系列号']
		line_name=dic_base_massage['线别']
		process_status=dic_base_massage['制程状态']
		partment=dic_base_massage['事业部']
		board_name=dic_base_massage['单板名称']
		batch=dic_base_massage['批次']
		produce_date=dic_base_massage['生产日期']
		product_type=dic_base_massage['产品分类']

		if partment=='金融':
			sql_table_name='note_jr'
		if partment=='移动':
			sql_table_name='note_yd'
		if partment !='金融' and partment !='移动':
			QMessageBox(text=' 事业部填写错误！',parent=self).show()
			return

		cur.execute("select project_num,product_id,fault_class2,line_num,note_person,note_date from "+sql_table_name+" \
			where product_id=%s and service_result is null",(product_num))
		li=cur.fetchall()
		conn.commit()
		if len(li)>=1:
			li_header=['计划ID','临时编码','故障分类','线别','记录人','记录时间']
			self.massage=Massage(li,header='该机存在已登记且未维修的记录',msgtype='table',table_header=li_header,parent=self)
			return
		cur.execute("select id from "+sql_table_name+" \
			where product_id=%s and state='维修'",(product_num))
		li=cur.fetchall()
		if len(li)>=1:
			QMessageBox(text=' 该机状态在维修，请先转入！',parent=self).show()
			return
		cur.execute("INSERT INTO "+sql_table_name+" (main_model, serial_num,batch_num, line_num, \
					process_state, product_class, produce_date, project_num, product_id,note_person, note_date,\
					fault_class2,single_board_name,state) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,\
					%s, %s, %s, %s)",(main_model,model,batch,line_name,process_status,product_type,\
					produce_date,project_num,product_num,note_person,note_time,fault_type,\
					board_name,'待修'))
		conn.commit()
		self.line_product_num.setText('')
		self.line_product_num.setFocus()
		self.note_record.set_table([project_num,main_model,line_name,process_status,fault_type,note_person,\
			note_time,'','',''])


class ProductServiceMassage(QGroupBox):
	def __init__(self,product_base,view_work_hour,note_record,li_fault_jr=[],li_fault_yd=[]):
		super().__init__('现象登记')

		self.li_fault_jr=li_fault_jr
		self.li_fault_yd=li_fault_yd
		self.product_base=product_base
		self.note_record=note_record
		self.view_work_hour=view_work_hour
		self.note_type='插入'
		self.record_id=''
		self.dic_old_base_massage={}
		self.product_base.add_parent(self)
		self.initUI()
		
		self.show()
	def initUI(self):
		label_product_num=QLabel('产品编码',self)
		label_fault_name=QLabel('不良现象',self)
		label_fault_cause=QLabel('不良原因',self)
		label_service_result=QLabel('维修结果',self)
		label_comment=QLabel('备注',self)
		label_work_hour=QLabel('维修工时',self)

		self.line_product_num=QLineEdit(self)
		self.line_fault_name=QLineEdit(self)
		self.line_fault_cause=QLineEdit(self)
		self.line_comment=QLineEdit(self)
		self.line_work_hour=QLineEdit(self)
		self.comb_service_result=QComboBox(self)
		self.comb_service_result.setEditable(True)
		self.comb_service_result.addItems(['修复','报废'])

		strmodel_jr=QStringListModel(self)
		strmodel_jr.setStringList(self.li_fault_jr)
		self.completer_jr = QCompleter(self)
		self.completer_jr.setCaseSensitivity(Qt.CaseInsensitive)
		self.completer_jr.setModel(strmodel_jr)
	

		strmodel_yd=QStringListModel(self)
		strmodel_yd.setStringList(self.li_fault_yd)
		self.completer_yd = QCompleter(self)
		self.completer_yd.setCaseSensitivity(Qt.CaseInsensitive)
		self.completer_yd.setModel(strmodel_yd)

		self.line_fault_name.setCompleter(self.completer_yd)


		btn_more=QPushButton('故障表',self)
		btn_large_note=QPushButton('批量录入',self)
		btn_commit=QPushButton('提交',self)
		self.line_product_num.editingFinished.connect(self.product_num_finish)
		self.line_product_num.textChanged.connect(self.product_num_changed)

		
		btn_more.clicked.connect(self.more_event)
		btn_large_note.clicked.connect(self.large_note_event)
		btn_commit.clicked.connect(self.commit_event)

		glayout=QGridLayout(self)
		glayout.addWidget(label_product_num,0,0,alignment=Qt.AlignRight)
		glayout.addWidget(label_fault_name,1,0,alignment=Qt.AlignRight)
		glayout.addWidget(label_fault_cause,2,0,alignment=Qt.AlignRight)
		glayout.addWidget(label_service_result,3,0,alignment=Qt.AlignRight)
		glayout.addWidget(label_comment,0,4,alignment=Qt.AlignRight)
		glayout.addWidget(label_work_hour,1,4,alignment=Qt.AlignRight)
		glayout.addWidget(self.line_product_num,0,1,1,2)
		glayout.addWidget(self.line_fault_name,1,1,1,2)
		glayout.addWidget(self.line_fault_cause,2,1,1,2)
		glayout.addWidget(self.comb_service_result,3,1,1,2)
		glayout.addWidget(self.line_comment,0,5,1,2)
		glayout.addWidget(self.line_work_hour,1,5,1,2)
		glayout.addWidget(btn_more,1,3,alignment=Qt.AlignLeft)
		glayout.addWidget(btn_large_note,3,4,alignment=Qt.AlignRight)
		glayout.addWidget(btn_commit,3,6,alignment=Qt.AlignRight)

	def change_fault_name(self,partment):
		if partment=='金融':
			self.line_fault_name.setCompleter(self.completer_jr)
		if partment=='移动':
			self.line_fault_name.setCompleter(self.completer_yd)


	def product_num_finish(self):
		# self.line_fault_name.setFocus()
		if not self.line_product_num.isModified():
			return
		self.line_product_num.setModified(False)
		print('product-num-finish')

		procuct_num=self.line_product_num.text().replace(' ','')
		if procuct_num=='':
			return
		self.dic_old_base_massage=self.product_base.get_content()

		cur.execute("select id,project_num,batch_num,main_model,serial_num,product_class,process_state,\
		 line_num,produce_date,single_board_name,fault_class2,state,partment from note_jr where product_id=%s \
		 and service_result is null union \
		 select id,project_num,batch_num,main_model,serial_num,product_class,process_state,\
		 line_num,produce_date,single_board_name,fault_class2,state,partment from note_yd where product_id=%s \
		 and service_result is null",(procuct_num,procuct_num))
		li=cur.fetchall()
		print('project_num_finish',li)
		conn.commit()
		if len(li)==0:
			self.note_type='插入'
			self.line_fault_name.setText('')
			self.product_base.set_enable_all(True)	
			self.query_history_record(procuct_num)	
			return

		if len(li)==1:
			self.note_type='更新'

			record_id=li[0][0]
			self.record_id=str(record_id)
			project_num=li[0][1]
			batch=li[0][2]
			main_model=li[0][3]
			model=li[0][4]
			product_type=li[0][5]
			process_status=li[0][6]
			line_name=li[0][7]
			produce_date=str(li[0][8])
			board_name=li[0][9]
			fault_class=li[0][10]
			state=li[0][11]
			partment=li[0][12]

			dic={}
			dic['计划ID']=project_num
			dic['批次']=batch
			dic['主型号']=main_model
			dic['系列号']=model
			dic['产品分类']=product_type
			dic['制程状态']=process_status
			dic['线别']=line_name
			dic['生产日期']=produce_date
			dic['单板名称']=board_name
			dic['事业部']=partment
			print(dic)
			
			self.product_base.set_content(dic)
			self.line_fault_name.setText(fault_class)
			self.product_base.set_widget_enable(False)
			self.product_base.set_enable_all(False)

			self.query_history_record(procuct_num)
			if state=='待修':
				QMessageBox(text=' 请先将该机转入后再登记结果！',parent=self).show()
				return


	def query_history_record(self,procuct_num):
		cur.execute("select project_num,line_num,main_model,product_class,process_state,\
		 fault_class2,fault_name,service_person,service_date from note_jr where product_id=%s and service_result is not null union \
		 select project_num,line_num,main_model,product_class,process_state,\
		 fault_class2,fault_name,service_person,service_date from note_yd where product_id=%s and service_result is not null",(procuct_num,procuct_num))
		li=cur.fetchall()
		conn.commit()
		if len(li)>0:
			li_header=['计划ID','线别','型号','分类','制程状态','故障分类','故障名称','维修人','维修日期']
			self.massage=Massage(li,header='该机维修记录',msgtype='table',table_header=li_header,parent=self)

	def product_num_changed(self,text):

		if text.replace(' ','')=='':
			print('text changed 调用')
			self.product_base.set_enable_all(True)
			self.product_base.set_content(self.dic_old_base_massage)
			self.line_product_num.setText('')
			self.line_fault_name.setText('')
			self.line_fault_cause.setText('')
			self.comb_service_result.setCurrentText('修复')
			self.line_comment.setText('')
			self.line_work_hour.setText('')
			self.record_id=''
			self.note_type='插入'

	def more_event(self):
		if self.product_base.get_content()['事业部']=='移动':
			self.choose_fault=ChooseFault(self.li_fault_yd,self.line_fault_name)
		if self.product_base.get_content()['事业部']=='金融':
			self.choose_fault=ChooseFault(self.li_fault_jr,self.line_fault_name)
	def large_note_event(self):
		pass
	def commit_event(self):
		if self.line_fault_name.text().replace(' ','')=='':
			QMessageBox(text=' 不良现象未填写！',parent=self).show()
			return
		if self.line_fault_cause.text().replace(' ','')=='':
			QMessageBox(text=' 不良原因未填写！',parent=self).show()
			return
		if self.comb_service_result.currentText().replace(' ','')=='':
			QMessageBox(text=' 维修结果未填写！',parent=self).show()
			return
		if self.line_work_hour.text().replace(' ','')=='':
			QMessageBox(text=' 维修工时未填写！',parent=self).show()
			return
		try:
			int(self.line_work_hour.text().replace(' ',''))
		except:
			QMessageBox(text=' 维修工时填写错误！',parent=self).show()
			return
		if self.note_type=='插入':
			self.note_insert()
		if self.note_type=='更新':
			self.note_update()
		dic=self.get_content()
		

	def parse_fault(self):
		fault_num=''
		fault_name=''
		fault_type=''
		text=self.line_fault_name.text()
		li_split=text.split('+')
		for i in li_split:
			li_split_temp=i.split(',')
			if len(li_split_temp)==3:
				fault_num+=li_split_temp[0]
				fault_type+=li_split_temp[1]
				fault_name+=li_split_temp[2]
				if i !=li_split[-1]:
					fault_num+='+'
					fault_type+='+'
					fault_name+='+'
			else:
				fault_name+=i
				if i !=li_split[-1]:
					fault_name+='+'
		return fault_num,fault_type,fault_name
	def get_content(self):
		dic=self.product_base.get_content()
		dic['产品编码']=self.line_product_num.text()
		dic['故障代码'],dic['故障分类'],dic['故障名称']=self.parse_fault()
		dic['不良原因']=self.line_fault_cause.text()
		dic['维修结果']=self.comb_service_result.currentText()
		dic['备注']=self.line_comment.text()
		dic['维修工时']=self.line_work_hour.text()
		return dic
	def note_insert(self):
		dic=self.get_content()
		service_time=str(datetime.datetime.now())[0:19]
		if dic['事业部']=='金融':
			table_name='note_jr'
		if dic['事业部']=='移动':
			table_name='note_yd'
		if dic['产品编码']=='':
			cur.execute("INSERT INTO "+table_name+" (main_model, serial_num,batch_num, line_num, \
					process_state, product_class, produce_date, project_num, product_id, fault_num,\
					 fault_name,service_result, work_hours, service_person,\
					  service_date, note_person, note_date, comment, second_service,fault_class,\
					  fault_class2,material_name,single_board_name,state)\
					   VALUES (%s, %s, %s, %s, %s, %s, %s, %s,\
					    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,\
					     %s, %s, %s,%s,%s)",(dic['主型号'],dic['系列号'],dic['批次'],dic['线别'],\
					     dic['制程状态'],dic['产品分类'],dic['生产日期'],\
					     dic['计划ID'],dic['产品编码'],dic['故障代码'],dic['故障名称'],dic['不良原因'],\
					     dic['维修工时'],user_name,service_time,user_name,service_time,dic['备注'],'1',\
					     dic['故障分类'],dic['故障分类'],dic['维修结果'],dic['单板名称'],''))
			conn.commit()
			self.note_record.set_table([dic['计划ID'],dic['主型号'],dic['线别'],dic['制程状态'],dic['故障名称'],\
				'','',dic['不良原因'],user_name,str(datetime.datetime.now())[0:19]])
			self.view_work_hour.flush_event()
			self.data_init()
		if dic['产品编码']!='':
			# cur.execute("select state from "+table_name+" where product_id=%s \
			#  and service_result is null",(dic['产品编码']))
			# li=cur.fetchall()
			# state=li[0][0]
			# if state=='待修':
			# 	QMessageBox(text=' 请先将该机转入后再登记结果！',parent=self).show()
			# 	return
			
			cur.execute("select count(id) from "+table_name+" where product_id=%s and \
				project_num=%s",(dic['产品编码'],dic['计划ID']))
			li=cur.fetchall()
			service_count=str(li[0][0]+1)
			cur.execute("INSERT INTO "+table_name+" (main_model, serial_num,batch_num, line_num, \
					process_state, product_class, produce_date, project_num, product_id, fault_num,\
					 fault_name,service_result, work_hours, service_person,\
					  service_date, note_person, note_date, comment, second_service,fault_class,\
					  fault_class2,material_name,single_board_name,state)\
					   VALUES (%s, %s, %s, %s, %s, %s, %s, %s,\
					    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,\
					     %s, %s, %s,%s,%s)",(dic['主型号'],dic['系列号'],dic['批次'],dic['线别'],\
					     dic['制程状态'],dic['产品分类'],dic['生产日期'],\
					     dic['计划ID'],dic['产品编码'],dic['故障代码'],dic['故障名称'],dic['不良原因'],\
					     dic['维修工时'],user_name,service_time,user_name,service_time,dic['备注'],service_count,\
					     dic['故障分类'],dic['故障分类'],dic['维修结果'],dic['单板名称'],''))
			conn.commit()
			self.note_record.set_table([dic['计划ID'],dic['主型号'],dic['线别'],dic['制程状态'],dic['故障名称'],\
				'','',dic['不良原因'],user_name,str(datetime.datetime.now())[0:19]])
			self.view_work_hour.flush_event()
			self.data_init()

	def note_update(self):
		dic=self.get_content()
		if dic['事业部']=='金融':
			table_name='note_jr'
		if dic['事业部']=='移动':
			table_name='note_yd'
		cur.execute("select state from "+table_name+" where product_id=%s \
		 and service_result is null",(dic['产品编码']))
		li=cur.fetchall()
		conn.commit()
		print(li)
		state=li[0][0]
		if state=='待修':
			QMessageBox(text=' 请先将该机转入后再登记结果！',parent=self).show()
			return
		
		cur.execute("select count(id) from "+table_name+" where product_id=%s and \
			project_num=%s",(dic['产品编码'],dic['计划ID']))
		li=cur.fetchall()
		conn.commit()
		service_count=str(li[0][0])
		service_time=str(datetime.datetime.now())[0:19]
		cur.execute("update "+table_name+" set service_result=%s, \
			service_person=%s, service_date=%s, comment=%s,\
			 work_hours=%s,material_name=%s,second_service=%s,\
			fault_num=%s,fault_name=%s,fault_class=%s \
			WHERE id=%s",(dic['不良原因'],user_name,service_time,dic['备注'],\
				dic['维修工时'],dic['维修结果'],service_count,dic['故障代码'],\
				dic['故障名称'],dic['故障分类'],self.record_id))
		conn.commit()
		self.note_record.set_table([dic['计划ID'],dic['主型号'],dic['线别'],dic['制程状态'],dic['故障名称'],\
			'','',dic['不良原因'],user_name,str(datetime.datetime.now())[0:19]])
		self.view_work_hour.flush_event()
		self.data_init()

	def data_init(self):
		self.line_product_num.setText('')
		self.line_fault_name.setText('')
		self.line_fault_cause.setText('')
		self.comb_service_result.setCurrentText('修复')
		self.line_comment.setText('')
		self.line_work_hour.setText('')
		self.product_base.set_enable_all(True)
		self.record_id=''
		self.note_type='插入'
		self.product_base.set_content(self.dic_old_base_massage)



class ViewWorkHour(QWidget):
	def __init__(self):
		super().__init__()
		self.initUI()

	def initUI(self):
		label_work_hour=QLabel('工时合计:',self)
		self.label_hour_count=QLabel('',self)
		btn_flush=QPushButton('刷新',self)
		btn_flush.clicked.connect(self.flush_event)
		hlayout=QHBoxLayout(self)
		hlayout.addWidget(label_work_hour)
		hlayout.addWidget(self.label_hour_count)
		hlayout.addWidget(btn_flush)
		hlayout.addStretch(1)
		self.setLayout(hlayout)
		self.show()
	def flush_event(self):
		date=datetime.datetime.now().date()
		date1=date+datetime.timedelta(1)
		cur.execute("select sum(work_hours) from note_jr where service_person=%s and service_date>=%s \
			and service_date<%s",(user_name,str(date),str(date1)))
		li=cur.fetchall()
		print('>>>>>>li1',li)
		h1=li[0][0]
		if h1 is None:
			h1=0
		conn.commit()

		cur.execute("select sum(work_hours) from note_yd where service_person=%s and service_date>=%s \
			and service_date<%s",(user_name,str(date),str(date1)))
		li=cur.fetchall()
		print('>>>>>>li2',li)
		h2=li[0][0]
		if h2 is None:
			h2=0
		conn.commit()
		self.label_hour_count.setText(str(h1+h2))

class ViewNoteRocord(QWidget):
	def __init__(self):
		super().__init__()
		self.initUI()
	def initUI(self):
		self.table=QTableWidget(0,10,self)
		self.table.setHorizontalHeaderLabels(['计划ID','型号','线别','制程状态','不良现象','记录人',\
			'录入日期','不良原因','维修人','维修日期'])
		vlayout=QVBoxLayout(self)
		vlayout.addWidget(self.table)
		self.setLayout(vlayout)
		self.show()
	def set_table(self,li_content):
		rowcount=self.table.rowCount()
		self.table.setRowCount(rowcount+1)
		columncount=0
		for i in li_content:
			self.table.setItem(rowcount,columncount,QTableWidgetItem(i))
			columncount+=1

'''
选择故障代码界面
'''
class ChooseFault(QScrollArea):
	def __init__(self,li,lineedit):
		super().__init__()
		self.lineedit=lineedit
		self.licontext=li
		self.initUI()
	def initUI(self):
		widget=QWidget()		
		grid = QGridLayout(widget)	
		m=len(self.licontext)//7+1
		li=[(i,j) for j in range(7) for i in range(m)]
		z=zip(self.licontext,li)
		for x,y in z:
			label=QLabel(str(x),widget)
			label.mouseReleaseEvent=MethodType(self.label_event,label)
			grid.addWidget(label,*y)
		self.setStyleSheet("QLabel:hover{color:rgb(150,150,150,255);}") 
		
		widget.setLayout(grid)
		self.setWidget(widget)
		self.move(0,0)
		self.setWindowTitle('故障代码表')
		self.setWindowState(Qt.WindowMaximized)
		self.show()
	def label_event(self,label,e):
		old_text=self.lineedit.text()
		if len(old_text)>8 and old_text[-1]=='+':
			self.lineedit.setText(old_text+label.text())
		else:
			self.lineedit.setText(label.text())
		self.lineedit.setFocus()
		# self.lineedit.setModified(True)
		self.close()

class QueryByProductNum(QWidget):
	def __init__(self):
		super().__init__()
		self.li_table_header=['ID','线别','产品分类','主型号','系列号','单板名称','计划ID','生产日期','批次',\
		'制程状态','产品编码','故障代码','故障名称','故障分类','登记人','登记日期','不良原因','维修结果','工时',\
		'维修人','维修日期','备注','维修次数','原因分析','分析人','分析分类','制程控制','错误原因','事业部','流转状态',\
		'转入维修时间','维修接收人','转入产线时间','产线接收人']
		self.initUI()

	def initUI(self):
		label_product_num=QLabel('产品编码',self)
		self.line_product_num=QLineEdit(self)
		btn_query=QPushButton('查询',self)
		btn_query.clicked.connect(self.query_event)
		self.table=QTableWidget(0,len(self.li_table_header),self)
		self.table.setHorizontalHeaderLabels(self.li_table_header)
		hlayout=QHBoxLayout()
		hlayout.addStretch(1)
		hlayout.addWidget(label_product_num)
		hlayout.addWidget(self.line_product_num,alignment=Qt.AlignRight)
		hlayout.addWidget(btn_query,alignment=Qt.AlignRight)
		vlayout=QVBoxLayout(self)
		vlayout.addLayout(hlayout)
		vlayout.addWidget(self.table)
		self.setLayout(vlayout)
		self.show()


	def query_event(self):
		product_num=self.line_product_num.text()
		if product_num.replace(' ','')=='':
			return
		cur.execute("select id,line_num,product_class,main_model,serial_num,single_board_name\
			,project_num,produce_date,batch_num,process_state,product_id,fault_num\
			,fault_name,fault_class2,note_person,note_date,service_result,material_name,work_hours\
			,service_person,service_date,comment,second_service,cause_parse,parse_person,parse_class\
			,process_control,fail_correct,partment,state,in_time,in_person,out_time,out_person from note_jr \
			where product_id=%s union \
			select id,line_num,product_class,main_model,serial_num,single_board_name\
			,project_num,produce_date,batch_num,process_state,product_id,fault_num\
			,fault_name,fault_class2,note_person,note_date,service_result,material_name,work_hours\
			,service_person,service_date,comment,second_service,cause_parse,parse_person,parse_class\
			,process_control,fail_correct,partment,state,in_time,in_person,out_time,out_person from note_yd \
			where product_id=%s",(product_num,product_num))
		li=cur.fetchall()
		conn.commit()
		self.table.setRowCount(0)
		if len(li)==0:
			return
		self.table.setRowCount(len(li))
		rowcount=0
		for i in li:
			columncount=0
			for j in i:
				self.table.setItem(rowcount,columncount,QTableWidgetItem(str(j)))
				columncount+=1
			rowcount+=1

class Massage(QDialog):
	def __init__(self,content,title='警告',header='',msgtype='msg',table_header=[],parent=None):
		super().__init__(parent)
		self.content=content
		self.title=title
		self.header=header
		self.msgtype=msgtype
		self.table_header=table_header

		self.initUI()
	def initUI(self):
		vlayout=QVBoxLayout(self)
		if self.msgtype=='msg':
			label_content=QLabel(self.content,self)
			vlayout.addWidget(label_content)
		if self.msgtype=='table':
			label_header=QLabel(self.header,self)
			table=QTableWidget(len(self.content),len(self.table_header),self)
			table.setHorizontalHeaderLabels(self.table_header)
			vlayout.addWidget(label_header)
			vlayout.addWidget(table)
			rowcount=0
			for i in self.content:
				columncount=0
				for j in i:
					table.setItem(rowcount,columncount,QTableWidgetItem(str(j)))
					columncount+=1
				rowcount+=1
		btn=QPushButton('确定',self)
		btn.clicked.connect(self.close)
		vlayout.addWidget(btn,alignment=Qt.AlignCenter)
		self.setLayout(vlayout)
		self.setWindowTitle(self.title)
		self.show()
		self.exec()

class WinNote(QWidget):
	def __init__(self):
		super().__init__()
		self.initUI()

	def initUI(self):
		dic_main_model={}
		dic_model={}
		cur.execute("select xinghao,xiliehao from xiliehao")
		li=cur.fetchall()
		df=pd.DataFrame(np.array(li),columns=['型号','系列号'])
		dic_main_model['金融']=df['型号'].drop_duplicates().tolist()
		for i in dic_main_model['金融']:
			dic_model[i]=df[df['型号']==i]['系列号'].tolist()


		cur.execute("select xinghao,xiliehao from xiliehao_yd")
		li=cur.fetchall()
		df=pd.DataFrame(np.array(li),columns=['型号','系列号'])
		dic_main_model['移动']=df['型号'].drop_duplicates().tolist()
		for i in dic_main_model['移动']:
			dic_model[i]=df[df['型号']==i]['系列号'].tolist()

		
		if managerlimit.get_limit('产线登记'):
			cur.execute("select name from process")
			li=cur.fetchall()
			conn.commit()
			li_process=[]
			for i in li:
				li_process.append(i[0])
			cur.execute("select line_name from user_sc_D where name=%s",(user_name))
			li=cur.fetchall()
			conn.commit()
			line_name=li[0][0]


			base_massage=ProductBaseMassage(li_process_status=li_process,li_line_name=[line_name],dic_main_model=dic_main_model,dic_model=dic_model)
			note_record=ViewNoteRocord()
			cur.execute("select fault from fault_class")
			li=cur.fetchall()
			conn.commit()
			li_fault_class=[]
			for i in li:
				li_fault_class.append(i[0])
			fault_massage=ProductFaultMassage(base_massage,li_fault_class,note_record)
			vlayout=QVBoxLayout(self)
			vlayout.addWidget(base_massage)
			vlayout.addWidget(fault_massage)
			vlayout.addWidget(note_record)
			self.setLayout(vlayout)
			self.show()


		else:
			cur.execute("select name from process")
			li=cur.fetchall()
			conn.commit()
			li_process=[]
			for i in li:
				li_process.append(i[0])
			cur.execute("select name from line_name")
			li=cur.fetchall()
			conn.commit()
			li_line_name=[]
			for i in li:
				li_line_name.append(i[0])
			base_massage=ProductBaseMassage(li_process_status=li_process,li_line_name=li_line_name,dic_main_model=dic_main_model,dic_model=dic_model)
			note_record=ViewNoteRocord()
			li_fault_jr=[]
			li_fault_yd=[]
			cur.execute('select * from gzdm')
			for i in cur.fetchall():
				li_fault_jr.append(str(i[0]+','+i[2]+','+i[1]))
			conn.commit()
			cur.execute('select * from gzdm_yd')
			for i in cur.fetchall():
				li_fault_yd.append(str(i[0]+','+i[2]+','+i[1]))
			conn.commit()
			li=cur.fetchall()
			li_fault_class=[]
			for i in li:
				li_fault_class.append(i[0])
			view_work_hour=ViewWorkHour()
			service_massage=ProductServiceMassage(base_massage,view_work_hour,note_record,li_fault_jr,li_fault_yd)
			vlayout=QVBoxLayout(self)
			vlayout.addWidget(base_massage)
			vlayout.addWidget(service_massage)
			vlayout.addWidget(view_work_hour)
			vlayout.addWidget(note_record)
			self.setLayout(vlayout)
			self.show()

class ManageLimit():
	def __init__(self):
		self.dic={}
		cur.execute("select note,only_note,modify_data,manager_gzdm,ad,delete_record,flow_opt,\
			flow_state,out_file,data_count,exemption from user_sc_D where name=%s",(user_name))
		li=cur.fetchall()[0]
		conn.commit()
		li_key=['登记','产线登记','修改数据','故障代码管理','管理员','删除记录','流转操作','流转状态',\
		'输出文件','数据统计','免责声明']
		for i in range(len(li_key)):
			self.dic[li_key[i]]=str(li[i])
	def get_limit(self,text):
		if self.dic[text]=='1':
			return True
		else:
			return False
	def get_name(self):
		return user_name

'''
主窗口
'''
class MainWidget(QWidget):
	def __init__(self):
		super().__init__()
		self.initUI()


	def initUI(self):
		m_list=QListWidget(self)	
		stack=QStackedWidget()
							
		tabwidget=QTabWidget()	
		m_list.addItem('维修登记')	
		if managerlimit.get_limit('登记'):
			winnote=WinNote()
			tabwidget.addTab(winnote,'在线维修')
		win_data_process_jr=WinDataProcess(cur,conn,managerlimit,'note_jr')
		win_data_process_yd=WinDataProcess(cur,conn,managerlimit,'note_yd')
		win_query_by_product_num=QueryByProductNum()
		tabwidget.addTab(win_data_process_jr,'金融数据查询')	
		tabwidget.addTab(win_data_process_yd,'移动数据查询')
		tabwidget.addTab(win_query_by_product_num,'以产品编码查询')
		stack.addWidget(tabwidget)
		

		if managerlimit.get_limit('流转操作'):
			m_list.addItem('流转登记')
			tabwidget_flow=QTabWidget()
			tab_flow_jr=WinInOut(cur,conn,user_name,'note_jr',managerlimit)
			tab_flow_yd=WinInOut(cur,conn,user_name,'note_yd',managerlimit)
			tabwidget_flow.addTab(tab_flow_jr,'金融')
			tabwidget_flow.addTab(tab_flow_yd,'移动')
			stack.addWidget(tabwidget_flow)
		if managerlimit.get_limit('流转状态'):
			m_list.addItem('流转状态')
			tabwidget_flow_state=QTabWidget()
			tab_state_jr=WinFlowState('note_jr',cur,conn)
			tab_state_yd=WinFlowState('note_yd',cur,conn)
			check_count_jr=CheckCount(cur,conn,'note_jr')
			check_count_yd=CheckCount(cur,conn,'note_yd')
			tabwidget_flow_state.addTab(tab_state_jr,'金融')
			tabwidget_flow_state.addTab(tab_state_yd,'移动')
			tabwidget_flow_state.addTab(check_count_jr,'对账金融')
			tabwidget_flow_state.addTab(check_count_yd,'对账移动')
			stack.addWidget(tabwidget_flow_state)


		m_list.addItem('数据统计')
		tabwidget_process=QTabWidget()
		frame_pivot=PivotView()
		frame_pivot1=PivotView1()
		frame_pivot.hide()
		frame_pivot1.hide()
		self.frame_query=DataQuery(cur,conn,frame_pivot,frame_pivot1,managerlimit)
		tabwidget_process.addTab(self.frame_query,'数据查询')
		if managerlimit.get_limit('数据统计'):
			
			tabwidget_process.addTab(frame_pivot,'数据统计')
			tabwidget_process.addTab(frame_pivot1,'数据统计1')
			frame_pivot.show()
			frame_pivot1.show()
		stack.addWidget(tabwidget_process)

		if managerlimit.get_limit('管理员'):
			m_list.addItem('系统管理')
			win_user=ManagerUser(conn,cur)
			tabwidget_user=QTabWidget()
			tabwidget_user.addTab(win_user,'用户管理')
			stack.addWidget(tabwidget_user)

		if managerlimit.get_limit('故障代码管理'):
			m_list.addItem('故障代码')
			win_fault_jr=WinFaultEdit(cur,conn,'gzdm')
			win_fault_yd=WinFaultEdit(cur,conn,'gzdm_yd')
			tabwidget_fault=QTabWidget()
			tabwidget_fault.addTab(win_fault_jr,'金融故障代码')
			tabwidget_fault.addTab(win_fault_yd,'移动故障代码')

			stack.addWidget(tabwidget_fault)

		m_list.setCurrentRow(0)
		label2=QLabel('label2')
		stack.addWidget(label2)
		label3=QLabel('label3')
		stack.addWidget(label3)
		stack.sizeHint()

		m_list.setMaximumWidth(60)

		hlayout=QHBoxLayout(self)
		hlayout.addWidget(m_list)
		hlayout.addWidget(stack)
		# hlayout.setStretchFactor(m_list,1)
		# hlayout.setStretchFactor(stack,20)
		m_list.currentRowChanged.connect(stack.setCurrentIndex)
		
		self.setLayout(hlayout)



'''
主程序窗口
'''

class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.initUI()

	def initUI(self):
		self.widget=MainWidget()
		self.setCentralWidget(self.widget)
		menubar=self.menuBar()
		# if managerlimit.get_limit('输出文件'):
		# 	outfile_jr=QAction('输出到excel（金融）',self)
		# 	outfile_jr.triggered.connect(self.outfile_event_jr)
			
		# 	filemenu=menubar.addMenu('文件')
		# 	filemenu.addAction(outfile_jr)
		# 	outfile_yd=QAction('输出到excel（移动）',self)
		# 	outfile_yd.triggered.connect(self.outfile_event_yd)
		# 	menubar=self.menuBar()
		# 	# filemenu=menubar.addMenu('文件')
		# 	filemenu.addAction(outfile_yd)
		# 	outfile_pivot=QAction('输出到excel（数据统计）',self)
		# 	outfile_pivot.triggered.connect(self.outfile_pivot)
		# 	menubar=self.menuBar()
		# 	filemenu.addAction(outfile_pivot)

		setmenu=menubar.addMenu('设置')
		modify_password=QAction('修改密码',self)
		modify_password.triggered.connect(self.modify_password)
		setmenu.addAction(modify_password)

		self.setWindowTitle('维修登记软件'+version+'--'+user_name)
		
		# self.resize(800,500)
		self.show()
	# def outfile_event_jr(self):
	# 	print('outfile')
	# 	# print(self.widget.win_tab2.dfa_temp)
	# 	if self.widget.win_tab2.dfa_temp is None:
	# 		return
	# 	else:
	# 		df=self.widget.win_tab2.dfa_temp
	# 		df.columns=self.widget.win_tab2.table_columns
	# 		print(df)
	# 		filename=QFileDialog.getSaveFileName(self,'存储为','D:/维修明细(金融)','xlsx')
	
	# 		if filename[0]=='':
	# 			return
	# 		df.to_excel(filename[0]+'.'+filename[1],sheet_name='维修明细')

	# def outfile_event_yd(self):
	# 	print('outfile')
	# 	# print(self.widget.win_tab2.dfa_temp)
	# 	if self.widget.win_tab2_yd.dfa_temp is None:
	# 		return
	# 	else:
	# 		df=self.widget.win_tab2_yd.dfa_temp
	# 		df.columns=self.widget.win_tab2_yd.table_columns
	# 		print(df)
	# 		filename=QFileDialog.getSaveFileName(self,'存储为','D:/维修明细(移动)','xlsx')

	# 		if filename[0]=='':
	# 			return
	# 		df.to_excel(filename[0]+'.'+filename[1],sheet_name='维修明细')
	# def outfile_pivot(self):
	# 	print('outfile')
	# 	# print(self.widget.win_tab2.dfa_temp)
	# 	if self.widget.frame_query.dfa_temp is None:
	# 		return

	# 	else:
	# 		df=self.widget.frame_query.dfa_temp
	# 		df.columns=self.widget.frame_query.table_columns
	# 		filename=QFileDialog.getSaveFileName(self,'存储为','D:/维修明细数据统计','xlsx')

	# 		if filename[0]=='':
	# 			return
	# 		writer = ExcelWriter(filename[0]+'.'+filename[1])
	# 		df.to_excel(writer,sheet_name='维修明细')
	# 		df=self.widget.frame_query.df_pivot
	# 		df.to_excel(writer,sheet_name='数据统计')
	# 		df=self.widget.frame_query.df_pivot1
	# 		df.to_excel(writer,sheet_name='数据统计1')
	# 		writer.save()
	def modify_password(self):
		self.win_modify_password=WinModifyPassword()


'''
修改密码界面
'''
class WinModifyPassword(QWidget):
	def __init__(self):
		super().__init__()
		self.initUI()
	def initUI(self):
		label_old=QLabel('旧密码',self)
		label_new=QLabel('新密码',self)
		label_new1=QLabel('新密码',self)
		self.line_old=QLineEdit(self)
		self.line_new=QLineEdit(self)
		self.line_new1=QLineEdit(self)
		self.line_old.setEchoMode(QLineEdit.Password)
		self.line_new.setEchoMode(QLineEdit.Password)
		self.line_new1.setEchoMode(QLineEdit.Password)
		btn=QPushButton('确认修改',self)
		btn.clicked.connect(self.btn_event)
		glayout=QGridLayout(self)
		glayout.addWidget(label_old,0,0)
		glayout.addWidget(self.line_old,0,1)
		glayout.addWidget(label_new,1,0)
		glayout.addWidget(self.line_new,1,1)
		glayout.addWidget(label_new1,2,0)
		glayout.addWidget(self.line_new1,2,1)
		glayout.addWidget(btn,3,0,1,2,alignment=Qt.AlignCenter)
		self.setLayout(glayout)
		self.show()

	def btn_event(self):
		global user_name
		cur.execute("select password from user_sc_D")
		password_true=cur.fetchall()[0][0]
		conn.commit()

		if self.line_new.text()!=self.line_new1.text():
			QMessageBox(text='   密码不一致！  ',parent=self).show()
			return
		password=self.line_new.text()
		password_old=self.line_old.text()
		if not bcrypt.checkpw(password_old.encode('ascii'),password_true.encode('ascii')):
			QMessageBox(text='   原密码错误！  ',parent=self).show()
			return
		hashpw=bcrypt.hashpw(password.encode('ascii'),bcrypt.gensalt())
		cur.execute("update user_sc_D set password=%s where name=%s",(hashpw,user_name))
		conn.commit()
		self.close()
		QMessageBox(text='   密码修改成功！  ',parent=self).show()


'''
登录窗口
'''
class LoginFrame(QWidget):
	def __init__(self):
		super().__init__()
		self.initUI()


	def initUI(self):
		self.text_name=QLineEdit(self)
		self.text_name.setPlaceholderText(u'用户名')
		# self.text_name.textChanged[str].connect(self.textchange)
		self.text_pw =QLineEdit(self)  
		self.text_pw.setEchoMode(QLineEdit.Password)
		self.text_pw.setPlaceholderText(u'密码')
		self.btn=QPushButton('登录',self)
		self.btn.clicked.connect(self.login)

		hbox=QHBoxLayout()
		hbox.addStretch(2)
		hbox.addWidget(self.btn)
		hbox.addStretch(2)

		layout =QVBoxLayout()
		layout.addWidget(self.text_name)  
		layout.addWidget(self.text_pw)
		layout.addLayout(hbox)

		self.setLayout(layout)
		self.setWindowTitle('用户登录')
		self.setFixedSize(200,100)
		self.show()
	def textchange(self,text):
		print(text)

	def login(self):
		global li_user,name,user_name,managerlimit
		nameloc=self.text_name.text()
		password=self.text_pw.text()
		print('read OK')
		cur.execute("select password from user_sc_d where name=%s",(nameloc))
		li_user=cur.fetchall()
		conn.commit()
		if len(li_user)==0:
			self.text_pw.setText('')
			self.text_pw.setPlaceholderText(u'用户名或密码错误')
			return

		print('query OK')
		
		print(li_user)
		print(len(li_user))

		if bcrypt.checkpw(password.encode('ascii'),li_user[0][0].encode('ascii')):
			# print(li_user)
			print('登录成功')
			name=nameloc
			user_name=nameloc
			self.close()
			managerlimit=ManageLimit()
			self.win=MainWindow()
		else:
			self.text_pw.setText('')
			self.text_pw.setPlaceholderText(u'用户名或密码错误')
	def keyPressEvent(self,event):
		if event.key()==Qt.Key_Enter or event.key()==Qt.Key_Return:
			self.login()

def connDB():
	conn=pymssql.connect(host='192.168.70.3',user='Chenyong',password='147258',database='WeiXiuDB',charset='utf8')
	# conn=pymysql.connect(host='127.0.0.1',user='root',password='000000',db='weixiu',charset='utf8')
	cur=conn.cursor()
	print('connect OK')
	return(conn,cur)

if __name__=='__main__':
	app=QApplication(sys.argv)

	conn,cur=connDB()
	user_name=''
	managerlimit=None

	version='4.01'
	run_flag=True
	cur.execute("select version_num_l,version_num_h from version_control")
	li=cur.fetchall()
	conn.commit()
	version_l=float(li[0][0])
	version_h=float(li[0][1])
	version_curr=float(version)
	q=QWidget()
	if version_curr<version_l:
		QMessageBox(text='   软件版本过低,请选择最新版本！  ',parent=q).show()
		run_flag=False
	if version_curr>=version_h:
		QMessageBox(text='   由于该版本存在严重缺陷,请使用低版本软件！  ',parent=q).show()
		run_flag=False

	if run_flag:
		logframe=LoginFrame()
	sys.exit(app.exec_())

