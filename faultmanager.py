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
故障代码管理界面
'''
class WinFaultEdit(QWidget):
	def __init__(self,cur1,conn1,tablename):
		global cur,conn
		super().__init__()
		cur=cur1
		conn=conn1
		self.tablename=tablename
		self.initUI()


	def initUI(self):
		btn_flush=QPushButton('刷新',self)
		btn_flush.clicked.connect(self.flush_event)
		btn_add=QPushButton('添加',self)
		btn_add.clicked.connect(self.add_event)
		self.sql_column_name=['12345','dm','disc','wx']
		self.table=QTableWidget(0,4,self)
		self.table.setHorizontalHeaderLabels(['id','故障代码','故障名称','故障分类'])
		self.table.itemChanged.connect(self.item_changed)
		action_delete=QAction('删除',self)
		action_delete.triggered.connect(self.delete_record)
		self.table.addAction(action_delete)
		self.table.setContextMenuPolicy(Qt.ActionsContextMenu)
		self.table.cellDoubleClicked.connect(self.cellDoubleClicked)
		hlayout=QHBoxLayout()
		
		hlayout.addWidget(btn_flush)
		hlayout.addStretch(1)
		hlayout.addWidget(btn_add)
		hlayout.addStretch(1)
		vlayout=QVBoxLayout(self)
		vlayout.addLayout(hlayout)
		vlayout.addWidget(self.table)
		self.setLayout(vlayout)
		self.show()

	def flush_event(self):
		print('flush_event')
		self.table.itemChanged.disconnect(self.item_changed)
		cur.execute("select id,dm,disc,wx from "+self.tablename)
		li=cur.fetchall()
		self.df=pd.DataFrame(np.array(li),columns=['id','dm','name','type'])
		self.df=self.df.sort(['dm'])
		li=self.df.values.tolist()
		conn.commit()
		self.table.setRowCount(len(li))
		rowcount=0
		for i in li:
			columncount=0
			for j in i:
				self.table.setItem(rowcount,columncount,QTableWidgetItem(str(j)))
				columncount+=1
			rowcount+=1
		self.table.itemChanged.connect(self.item_changed)
	def add_event(self):
		print('add_event')
		self.win_add_fault=AddFault(self.table,conn,cur,self.tablename,self)
	def item_changed(self,item):
		if item.column()==1:
			cur.execute("select * from "+self.tablename+" where dm=%s",(item.text()))
			li=cur.fetchall()
			conn.commit()
			if len(li)>0:
				QMessageBox(text='   该不良代码已存在！   ',parent=self).show()
				self.flush_event()
				return
		cur.execute('update '+self.tablename+' set '+self.sql_column_name[item.column()]+'='+'%s where \
			id=%s',(item.text(),self.table.item(item.row(),0).text()))
		conn.commit()
		# self.btn_event_updfa()
		print('changed OK')

	def delete_record(self):
		cur.execute("delete from "+self.tablename+" where id=%s",(self.table.item(self.table.currentRow(),0).text()))
		conn.commit()
		self.table.removeRow(self.table.currentRow())

	def cellDoubleClicked(self,row,column):
		if column==0:
			QMessageBox(text='   该列不可编辑！  ',parent=self).show()
			return


class AddFault(QWidget):
	def __init__(self,table,conn,cur,tablename,parent):
		super().__init__()
		self.table=table
		self.conn=conn
		self.cur=cur
		self.tablename=tablename
		self.parent=parent
		self.initUI()

	def initUI(self):
		label_name=QLabel('故障代码：',self)
		label_password=QLabel('故障名称：',self)
		label_partment=QLabel('故障分类：',self)
		self.line_edit_name=QLineEdit(self)
		self.line_edit_password=QLineEdit(self)
		self.line_edit_partment=QLineEdit(self)
		# self.line_edit_password.setEchoMode(QLineEdit.Password)
		# self.line_edit_partment.setEchoMode(QLineEdit.Password)  
		btn=QPushButton('确认添加',self)
		btn.clicked.connect(self.btn_event)

		glayout=QGridLayout(self)
		glayout.addWidget(label_name,0,0)
		glayout.addWidget(label_password,1,0)
		glayout.addWidget(label_partment,2,0)

		glayout.addWidget(self.line_edit_name,0,1)
		glayout.addWidget(self.line_edit_password,1,1)
		glayout.addWidget(self.line_edit_partment,2,1)
		glayout.addWidget(btn,3,0,1,2)

		self.show()

	def btn_event(self):
		name=self.line_edit_name.text()
		password=self.line_edit_password.text()
		partment=self.line_edit_partment.text()

		if re.match(r'^[\s]{0,}$',name):
			return
		if re.match(r'^[\s]{0,}$',password):
			return
		if re.match(r'^[\s]{0,}$',partment):
			return

		cur.execute("select * from "+self.tablename+" where dm=%s",(name))
		li=cur.fetchall()
		conn.commit()
		if len(li)>0:
			QMessageBox(text='   该不良代码已存在！   ',parent=self).show()
			return
		try:
			self.cur.execute("insert into "+self.tablename+" (dm,disc,wx) values (%s,%s,%s)",(name,password,partment))
			self.conn.commit()
			self.parent.flush_event()
			# self.table.setRowCount(self.table.rowCount()+1)

			# self.table.setItem(self.table.rowCount()-1,1,QTableWidgetItem(name))
			# self.table.setItem(self.table.rowCount()-1,2,QTableWidgetItem(password))
			# self.table.setItem(self.table.rowCount()-1,3,QTableWidgetItem(partment))
	
			self.close()
			QMessageBox(text='   录入成功！   ',parent=self).show()
		except:
			QMessageBox(text='   录入失败！   ',parent=self).show()
			return