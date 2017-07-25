from PyQt5.QtWidgets import *
from PyQt5.QtCore import QStringListModel,Qt,QDate
from PyQt5 import QtGui
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
import bcrypt
from types import MethodType


class ManagerUser(QWidget):
	def __init__(self,conn,cur):
		super().__init__()
		self.conn=conn
		self.cur=cur
		self.initUI()

	def initUI(self):
		btn=QPushButton('加载用户',self)
		btn.clicked.connect(self.btn_event)

		self.sqlcolumn=['name','user_type','line_name','note','only_note','modify_data','manager_gzdm','delete_record','flow_opt','flow_state','out_file','data_count','exemption']

		action=QAction('删除该用户',self)
		action.triggered.connect(self.delete_row)

		self.table=QTableWidget(0,13,self)
		self.table.setHorizontalHeaderLabels(['姓名','分类','线别','登记','产线','修改记录','故障代码管理','删除记录','流转登记','流转状态','文件导出','数据统计','参考声明'])
		self.table.addAction(action)
		self.table.setContextMenuPolicy(Qt.ActionsContextMenu)
		self.table.itemChanged.connect(self.item_changed)

		btn_add=QPushButton('添加用户',self)
		btn_add.clicked.connect(self.adduser_event)
		glayout=QGridLayout()
		# glayout.addWidget()
		glayout.addWidget(btn,0,0,alignment=Qt.AlignRight)
		glayout.addWidget(btn_add,0,1,alignment=Qt.AlignRight)

		vlayout=QVBoxLayout(self)
		vlayout.addLayout(glayout)
		vlayout.addWidget(self.table)
		self.setLayout(vlayout)
		self.show()
	def adduser_event(self):
		self.win=AddUser(self.table,self.conn,self.cur)

	def delete_row(self):
		if self.table.currentItem() is None:
			print('delete row')
			return

		self.cur.execute("delete from user_sc_D where name=%s",(self.table.item(self.table.currentRow(),0).text()))
		self.conn.commit()
		self.table.removeRow(self.table.currentRow())


	def item_changed(self,item):
		print('changed')
		self.cur.execute('update user_sc_D set '+self.sqlcolumn[item.column()]+'='+'%s where name=%s',(item.text(),self.table.item(item.row(),0).text()))
		self.conn.commit()


	def btn_event(self):
		self.cur.execute("select name,user_type,line_name,note,only_note,modify_data,manager_gzdm,delete_record,flow_opt,flow_state,out_file,data_count,exemption from user_sc_D")
		li=self.cur.fetchall()
		self.table.setRowCount(len(li))
		self.table.itemChanged.disconnect(self.item_changed)

		li_row=0
		
		for i in li:
			li_cloumn=0
			for j in i:
				if li_cloumn==0:
					self.table.setItem(li_row,li_cloumn,QTableWidgetItem(str(j)))
					self.table.item(li_row,li_cloumn).setFlags(Qt.ItemIsSelectable|Qt.ItemIsDragEnabled|Qt.ItemIsDropEnabled|Qt.ItemIsUserCheckable|Qt.ItemIsEnabled|Qt.ItemIsTristate)

				else:
					self.table.setItem(li_row,li_cloumn,QTableWidgetItem(str(j)))
					
				li_cloumn+=1
			li_row+=1

		self.table.itemChanged.connect(self.item_changed)

class AddUser(QWidget):
	def __init__(self,table,conn,cur):
		super().__init__()
		self.table=table
		self.conn=conn
		self.cur=cur
		self.initUI()

	def initUI(self):
		label_name=QLabel('姓名：',self)
		label_password=QLabel('密码：',self)
		label_partment=QLabel('密码：',self)
		self.line_edit_name=QLineEdit(self)
		self.line_edit_password=QLineEdit(self)
		self.line_edit_partment=QLineEdit(self)
		self.line_edit_password.setEchoMode(QLineEdit.Password)
		self.line_edit_partment.setEchoMode(QLineEdit.Password)  
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
		if password!=partment:
			QMessageBox(text='   密码不一致！   ',parent=self).show()
			return
		hashpw=bcrypt.hashpw(password.encode('ascii'),bcrypt.gensalt())
		try:
			self.cur.execute("insert into user_sc_D (name,password) values (%s,%s)",(name,hashpw))
			self.conn.commit()
			self.table.setRowCount(self.table.rowCount()+1)
			self.table.setItem(self.table.rowCount()-1,0,QTableWidgetItem(name))
	
			self.close()
			QMessageBox(text='   录入成功！   ',parent=self).show()
		except:
			QMessageBox(text='   录入失败！   ',parent=self).show()
			return