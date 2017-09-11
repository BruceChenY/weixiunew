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

'''
流转登记界面，
'''
class WinInOut(QWidget):
	def __init__(self,cur,conn,user_name,tablename,managerlimit,):
		super().__init__()
		self.cur=cur
		self.conn=conn
		self.user_name=user_name
		self.managerlimit=managerlimit
		self.tablename=tablename
		self.pm=PlanMassage()
		self.initUI()

	def initUI(self):
		self.li=[]
		self.row=1
		self.column=0
		self.count=0
		self.lineedit=QLineEdit(self)
		self.lineedit.editingFinished.connect(self.editfinished)
		self.label_count=QLabel('0',self)

		btn=QPushButton('提交',self)
		btn.clicked.connect(self.btn_event)
		btn_clear=QPushButton('清空',self)
		btn_clear.clicked.connect(self.clear_event)

		self.glayout=QGridLayout()
		self.glayout.addWidget(self.lineedit,0,0)
		hlayout=QHBoxLayout()
		hlayout.addWidget(self.label_count,alignment=Qt.AlignRight)
		hlayout.addWidget(btn_clear,alignment=Qt.AlignRight)
		hlayout.addWidget(btn,alignment=Qt.AlignRight)

		vlayout=QVBoxLayout(self)
		vlayout.addLayout(self.glayout)
		vlayout.addStretch(1)
		vlayout.addLayout(hlayout)
		self.setLayout(vlayout)
		self.show()

	def editfinished(self):
		sender=self.sender()
		if sender.text()=='':
			return
		if not sender.isModified():
			return
		sender.setModified(False)
		for i in self.li:
			if sender.text()==i.text():
				# QMessageBox(text='   条码已存在！   ',parent=self).show()
				sender.setText('')
				return
		# if sender in self.li:
		# 	sender.setText('')
		# 	return

		'''
		根据产线账号和维修账号的不同，分别查询不同的状态
		'''
		if self.managerlimit.get_limit('产线登记'):
			self.cur.execute("select id,service_result,project_num from "+self.tablename+" where product_id=%s and state='维修'",(sender.text()))
			li=self.cur.fetchall()
			self.conn.commit()
			if len(li)==0:
				QMessageBox(text='   查询不到该条码或此机不在当前流程！   ',parent=self).show()
				sender.setText('')
				return
			if li[0][1] is None:
				QMessageBox(text='   该机维修结果未登记！   ',parent=self).show()
				sender.setText('')
				return

			project_num=li[0][2].replace(' ','')
			if project_num=='':
				return		
			status,value=self.pm.get_json(project_num)
			if status=='fail':
				sender.setStyleSheet("background-color:rgb(255,255,255,255)")
			if status!='fail':
				finished_time=value['完成时间']
				li_date=finished_time.split(' ')
				li_date=li_date[0].split('/')
				year=int(li_date[0])
				month=int(li_date[1])
				day=int(li_date[2])
				finished_date=datetime.date(year,month,day)

				today=datetime.datetime.now().date()
				day_count= (finished_date-today).days
				if day_count<=0:
					sender.setStyleSheet("background-color:rgb(255,100,100,255)")
				elif day_count==1:
					sender.setStyleSheet("background-color:rgb(255,230,80,255)")
				else:
					sender.setStyleSheet("background-color:rgb(150,200,255,255)")

		else:
			self.cur.execute("select id,project_num from "+self.tablename+" where product_id=%s and state='待修'",(sender.text()))
			li=self.cur.fetchall()
			self.conn.commit()
			if len(li)==0:
				QMessageBox(text='   现象未登记或此机不在当前流程！   ',parent=self).show()
				sender.setText('')
				return

			project_num=li[0][1].replace(' ','')
			if project_num=='':
				return		
			status,value=self.pm.get_json(project_num)
			if status=='fail':
				sender.setStyleSheet("background-color:rgb(255,255,255,255)")
			if status!='fail':
				finished_time=value['完成时间']
				li_date=finished_time.split(' ')
				li_date=li_date[0].split('/')
				year=int(li_date[0])
				month=int(li_date[1])
				day=int(li_date[2])
				finished_date=datetime.date(year,month,day)

				today=datetime.datetime.now().date()
				day_count= (finished_date-today).days
				if day_count<=0:
					sender.setStyleSheet("background-color:rgb(255,100,100,255)")
				elif day_count==1:
					sender.setStyleSheet("background-color:rgb(255,230,80,255)")
				else:
					sender.setStyleSheet("background-color:rgb(150,200,255,255)")

		sender.editingFinished.disconnect(self.editfinished)
		sender.textChanged.connect(self.change_event)
		self.lineedit=QLineEdit(self)
		
		self.li.append(sender)
		self.glayout.addWidget(self.lineedit,self.row,self.column)
		self.row+=1
		if self.row==20:
			self.row=0
			self.column+=1
		self.lineedit.editingFinished.connect(self.editfinished)
		
		self.lineedit.setFocus()
		self.count+=1
		self.label_count.setText(str(self.count))

	def change_event(self):
		sender=self.sender()
		# if sender.text()=='':
		self.li.remove(sender)
		sender.close()
		self.count-=1
		self.label_count.setText(str(self.count))

	'''
	提交的处理对应产线账号和维修账号分别处理
	'''
	def btn_event(self):
		now=str(datetime.datetime.now())[0:19]
		number=0
		self.conn.commit()
		try:
			if self.managerlimit.get_limit('产线登记'):
				for i in self.li:
					self.cur.execute("update "+self.tablename+" set out_time=%s,state='完成',out_person=%s where product_id=%s and state='维修'"\
						,(now,self.user_name,i.text()))
					number+=1
				QMessageBox(text='   转入成功   数量：'+str(number),parent=self).show()
			else:
				for i in self.li:
					self.cur.execute("update "+self.tablename+" set in_time=%s,state='维修',in_person=%s where product_id=%s and state='待修'"\
						,(now,self.user_name,i.text()))
					number+=1
				QMessageBox(text='   创建单号：'+now+'   数量：'+str(number),parent=self).show()
			self.conn.commit()
		except:
			self.conn.rollback()
			QMessageBox(text='   提交失败，请清空重试  ',parent=self).show()
		self.lineedit.close()
		for i in self.li:
			i.close()
		self.li=[]
		self.row=1
		self.column=0
		self.lineedit=QLineEdit(self)
		self.lineedit.editingFinished.connect(self.editfinished)
		self.glayout.addWidget(self.lineedit,0,0)
		self.count=0
		self.label_count.setText('0')

	'''
	清空编号
	'''
	def clear_event(self):
		self.lineedit.close()
		for i in self.li:
			i.close()
		self.count=0
		self.label_count.setText('0')
		self.li=[]
		self.row=1
		self.column=0
		self.lineedit=QLineEdit(self)
		self.lineedit.editingFinished.connect(self.editfinished)
		self.glayout.addWidget(self.lineedit,0,0)