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

class FinishLevel():
	def __init__(self,tablename):
		self.tablename=tablename
		self.li_A=[]
		self.li_B=[]
		self.li_C=[]

		self.dic_A={}
		self.dic_B={}
		self.dic_C={}

		self.dic={}


	def flush(self):
		self.li_A=[]
		self.li_B=[]
		self.li_C=[]

		cur.execute("select project_num from "+self.tablename+" where service_result is null or state='维修' group by project_num")
		li=cur.fetchall()
		conn.commit()
		print('list of project_num:',li)
		today=datetime.datetime.now().date()

		for i in li:
			if i[0].replace(' ','')=='':
				continue
			finished_time=self.plan_num_event(i[0])
			print('计划ID:',i[0],'  完成时间：',finished_time)
			
			if finished_time is None:
				QMessageBox(text='   接口服务器异常！  ',parent=self).show()
				return 'fail'
			li_date=finished_time.split(' ')
			li_date=li_date[0].split('/')
			year=int(li_date[0])
			month=int(li_date[1])
			day=int(li_date[2])
			finished_date=datetime.date(year,month,day)
			print('完成日期：',finished_date)
			day_count= (finished_date-today).days
			if day_count<=0:
				self.li_A.append(i[0])
			elif day_count==1:
				self.li_B.append(i[0])
			else:
				self.li_C.append(i[0])
		return 'ok'

	def get_level(self):
		return self.li_A,self.li_B,self.li_C

	def plan_num_event(self,project_num):
		time.sleep(0.05)
		if re.match(r'^[\s]{0,}$',project_num):
			return

		s=project_num+'MD5'+project_num+'dj'

		m=hashlib.md5(s.encode('ascii')).hexdigest()
		print(m)
		s='http://192.168.30.230/jiekou/OrderInfoGet_ById/?id='+project_num+'&CheckCode='+m
		try:
			r=requests.get(s,timeout=2)
		except:
			QMessageBox(text='   数据获取失败！  ',parent=self).show()
			return
		j=r.json()[0]
		if len(j)==0:
			QMessageBox(text='   查询不到该计划id！  ',parent=self).show()
			return	

		self.dic[project_num]=[j['启动时间'],j['完成时间']]
		return j['完成时间']



'''
查看所有待维修机，并按颜色分级显示紧急程度,
'''
class WinWaitService(QWidget):
	def __init__(self,tablename,finished_level,title):
		super().__init__()
		self.tablename=tablename
		self.finished_level=finished_level
		self.title=title
		self.initUI()
	def initUI(self):
		btn=QPushButton('详细信息',self)
		btn.clicked.connect(self.btn_event)
		self.table_columns=['主型号','系列号','批次','计划ID',\
			'制程状态','临时产品编码','不良现象','记录人','记录日期',\
			'流转单号','状态']
		self.table=QTableWidget(0,11,self)
		self.table.horizontalHeader().setSortIndicator(0, Qt.AscendingOrder)
		self.table.horizontalHeader().setSortIndicatorShown(True)
		self.table.horizontalHeader().sectionClicked.connect(self.table.sortByColumn)
		self.data_process_count()
		vlayout=QVBoxLayout(self)
		vlayout.addWidget(btn,alignment=Qt.AlignRight)
		vlayout.addWidget(self.table)
		self.setLayout(vlayout)
		self.show()

	def data_process_detail(self):
		li_A,li_B,li_C=self.finished_level.get_level()
		cur.execute("select main_model,serial_num,batch_num,project_num,process_state,product_id,fault_class2,\
			note_person,note_date,in_time,state from "+self.tablename+" \
			where service_result is null and state<>'完成'")
		li=cur.fetchall()
		conn.commit()
		self.table.setRowCount(0)
		self.table.setColumnCount(11)
		self.table.setHorizontalHeaderLabels(self.table_columns)
		rowcount=0
		if self.title=='待维修(全部)':
			self.setWindowTitle(self.title)
			print('待维修(全部)')
			for i in li:
				self.table.setRowCount(self.table.rowCount()+1)
				columncount=0
				for j in i:
					
					self.table.setItem(rowcount,columncount,QTableWidgetItem(str(j)))
					if i[3] in li_A:
						self.table.item(rowcount,columncount).setBackground(QBrush(QColor(255,100,100)))
					elif i[3] in li_B:
						self.table.item(rowcount,columncount).setBackground(QBrush(QColor(255,230,80)))
					elif i[3] in li_C:
						self.table.item(rowcount,columncount).setBackground(QBrush(QColor(150,200,255)))
					else:
						pass
					columncount+=1
				rowcount+=1
		elif self.title=='待维修(当天完成计划)':
			self.setWindowTitle(self.title)
			print('待维修(当天完成计划)')
			for i in li:
				if i[3] in li_A:
					self.table.setRowCount(self.table.rowCount()+1)
					columncount=0
					for j in i:

						self.table.setItem(rowcount,columncount,QTableWidgetItem(str(j)))				
						columncount+=1
					rowcount+=1
		elif self.title=='待维修(明天天完成计划)':
			self.setWindowTitle(self.title)
			print('待维修(明天天完成计划)')
			for i in li:
				if i[3] in li_B:
					self.table.setRowCount(self.table.rowCount()+1)
					columncount=0
					for j in i:						
						self.table.setItem(rowcount,columncount,QTableWidgetItem(str(j)))				
						columncount+=1
					rowcount+=1
		elif self.title=='待维修(后天及以后完成计划)':
			self.setWindowTitle(self.title)
			print('待维修(后天及以后完成计划)')
			for i in li:
				if i[3] in li_C:
					self.table.setRowCount(self.table.rowCount()+1)
					columncount=0
					for j in i:						
						self.table.setItem(rowcount,columncount,QTableWidgetItem(str(j)))				
						columncount+=1
					rowcount+=1
		else:
			pass

	def btn_event(self):
		sender = self.sender()
		if sender.text()=='详细信息':
			self.data_process_detail()
			sender.setText('统计信息')
		else:
			self.data_process_count()
			sender.setText('详细信息')

	def data_process_count(self):
		print('统计信息处理')
		self.table.setRowCount(0)
		self.table.setColumnCount(5)
		self.table.setHorizontalHeaderLabels(['线别','计划ID','数量','启动时间','结束时间'])

		cur.execute("select note_person,project_num from "+self.tablename+" where state<>'完成' and \
			service_result is null")

		li=cur.fetchall()
		conn.commit()
		if len(li)==0:
			return


		keys=self.finished_level.dic.keys()
		li_A,li_B,li_C=self.finished_level.get_level()

		li_temp=[]
		if self.title=='待维修(全部)':
			self.setWindowTitle(self.title)
			li_temp=li
		elif self.title=='待维修(当天完成计划)':
			self.setWindowTitle(self.title)
			for i in li:
				if i[1] in li_A:
					li_temp.append(i)

		elif self.title=='待维修(明天天完成计划)':
			self.setWindowTitle(self.title)
			for i in li:
				if i[1] in li_B:
					li_temp.append(i)
		elif self.title=='待维修(后天及以后完成计划)':
			self.setWindowTitle(self.title)
			for i in li:
				if i[1] in li_C:
					li_temp.append(i)
		else:
			pass


		if len(li_temp)==0:
			return
		self.dfa=pd.DataFrame(np.array(li_temp),columns=['A','B'])
		li_line=self.dfa['A'].drop_duplicates().tolist()
		for i in li_line:
			li_id=self.dfa[self.dfa['A']==i]['B'].drop_duplicates().tolist()
			df_temp=self.dfa[self.dfa['A']==i]
			for j in li_id:
				df_count=df_temp[df_temp['B']==j]
				count=df_count.shape[0]
				self.table.setRowCount(self.table.rowCount()+1)
				self.table.setItem(self.table.rowCount()-1,0,QTableWidgetItem(i))
				self.table.setItem(self.table.rowCount()-1,1,QTableWidgetItem(j))
				self.table.setItem(self.table.rowCount()-1,2,QTableWidgetItem(str(count)))
		print(self.finished_level.dic)
		
		for i in range(self.table.rowCount()):
			if self.table.item(i,1).text() not in keys:
				continue
			self.table.setItem(i,3,QTableWidgetItem(self.finished_level.dic[self.table.item(i,1).text()][0]))
			self.table.setItem(i,4,QTableWidgetItem(self.finished_level.dic[self.table.item(i,1).text()][1]))

			if self.table.item(i,1).text() in li_A:
				for j in range(5):
					self.table.item(i,j).setBackground(QBrush(QColor(255,100,100)))
			elif self.table.item(i,1).text() in li_B:
				for j in range(5):
					self.table.item(i,j).setBackground(QBrush(QColor(255,230,80)))
			elif self.table.item(i,1).text() in li_C:
				for j in range(5):
					self.table.item(i,j).setBackground(QBrush(QColor(150,200,255)))
			else:
				pass

		
'''
流转单
'''
class WinFlowList(QWidget):
	def __init__(self,tablename):
		super().__init__()
		self.tablename=tablename
		self.initUI()

	def initUI(self):
		self.comb_type=QComboBox(self)
		self.comb_type.addItems(['全部','未完成','已完成'])
		label_date=QLabel('日期',self)
		self.date_line=QDateEdit(QDate.currentDate(),self)
		self.table=QTableWidget(0,6,self)
		self.table.setHorizontalHeaderLabels(['流转单号','转入维修时间','完成时间','耗时','总数量','剩余数量'])
		self.table.cellDoubleClicked.connect(self.double_event)

		btn_flush=QPushButton('刷新',self)
		btn_flush.clicked.connect(self.flush_event)
		hlayout=QHBoxLayout()
		hlayout.addWidget(label_date,alignment=Qt.AlignRight)
		hlayout.addWidget(self.date_line,alignment=Qt.AlignRight)
		hlayout.addWidget(self.comb_type,alignment=Qt.AlignRight)
		hlayout.addWidget(btn_flush,alignment=Qt.AlignRight)

		vlayout=QVBoxLayout(self)
		vlayout.addLayout(hlayout)

		vlayout.addWidget(self.table)
		self.setLayout(vlayout)
		self.show()

	def double_event(self,row,column):
		self.winflawpart=WinFlowPart(self.table.item(row,0).text(),self.tablename)

	def flush_event(self):
		self.table.setRowCount(0)
		set_all=set()
		set_no=set()
		set_yes=set()
		s1=self.date_line.date().toString("yyyy-MM-dd")
		s2=self.date_line.date().addDays(1).toString("yyyy-MM-dd")
		cur.execute("select in_time from "+self.tablename+" where in_time>=%s and in_time<%s group by in_time",(s1,s2))
		li_all=cur.fetchall()
		conn.commit()
		for i in li_all:
			set_all.add(i[0])
		cur.execute("select in_time from "+self.tablename+" where in_time>=%s and in_time<%s and state<>'完成' group by in_time",(s1,s2))
		li_no=cur.fetchall()
		conn.commit()
		for i in li_no:
			set_no.add(i[0])
		set_yes=set_all-set_no

		if self.comb_type.currentText()=='全部':
			self.table.setRowCount(len(set_all))
			rowcount=0
			for i in set_all:
				if i in set_yes:
					cur.execute("select max(out_time),count(id) from "+self.tablename+" where in_time=%s",(i))

					li_temp=cur.fetchall()
					max_time=li_temp[0][0]
					conn.commit()
					self.table.setItem(rowcount,0,QTableWidgetItem(str(i)))
					self.table.setItem(rowcount,1,QTableWidgetItem(str(i)))
					self.table.setItem(rowcount,2,QTableWidgetItem(str(max_time)))
					dl=time.strptime(str(i)[0:19],'%Y-%m-%d %H:%M:%S')
					dm=time.strptime(str(max_time)[0:19],'%Y-%m-%d %H:%M:%S')
					dm=datetime.datetime(*dm[:6])
					dl=datetime.datetime(*dl[:6])
					hour=(dm-dl).seconds/3600
					hour=round(hour,2)
					self.table.setItem(rowcount,3,QTableWidgetItem(str(hour)))
					self.table.setItem(rowcount,4,QTableWidgetItem(str(li_temp[0][1])))
					self.table.setItem(rowcount,5,QTableWidgetItem('0'))
					rowcount+=1
				else:
					cur.execute("select count(id) from "+self.tablename+" where in_time=%s",(i))
					li_temp=cur.fetchall()
					count_all=li_temp[0][0]
					cur.execute("select count(id) from "+self.tablename+" where in_time=%s and state='维修'",(i))
					li_temp=cur.fetchall()
					count_lave=li_temp[0][0]
					self.table.setItem(rowcount,0,QTableWidgetItem(str(i)))
					self.table.setItem(rowcount,1,QTableWidgetItem(str(i)))
					self.table.setItem(rowcount,4,QTableWidgetItem(str(count_all)))
					self.table.setItem(rowcount,5,QTableWidgetItem(str(count_lave)))
					rowcount+=1


		elif self.comb_type.currentText()=='未完成':
			self.table.setRowCount(len(set_no))
			rowcount=0
			for i in set_no:
				cur.execute("select count(id) from "+self.tablename+" where in_time=%s",(i))
				li_temp=cur.fetchall()
				count_all=li_temp[0][0]
				cur.execute("select count(id) from "+self.tablename+" where in_time=%s and state='维修'",(i))
				li_temp=cur.fetchall()
				count_lave=li_temp[0][0]
				self.table.setItem(rowcount,0,QTableWidgetItem(str(i)))
				self.table.setItem(rowcount,1,QTableWidgetItem(str(i)))
				self.table.setItem(rowcount,4,QTableWidgetItem(str(count_all)))
				self.table.setItem(rowcount,5,QTableWidgetItem(str(count_lave)))
				rowcount+=1
		else:	#已完成
			self.table.setRowCount(len(set_yes))
			rowcount=0
			for i in set_yes:
				
				cur.execute("select max(out_time),count(id) from "+self.tablename+" where in_time=%s",(i))
				li_temp=cur.fetchall()
				max_time=li_temp[0][0]
				conn.commit()
				self.table.setItem(rowcount,0,QTableWidgetItem(str(i)))
				self.table.setItem(rowcount,1,QTableWidgetItem(str(i)))
				self.table.setItem(rowcount,2,QTableWidgetItem(str(max_time)))
				dl=time.strptime(str(i)[0:19],'%Y-%m-%d %H:%M:%S')
				dm=time.strptime(str(max_time)[0:19],'%Y-%m-%d %H:%M:%S')
				dm=datetime.datetime(*dm[:6])
				dl=datetime.datetime(*dl[:6])
				hour=(dm-dl).seconds/3600
				hour=round(hour,2)
				self.table.setItem(rowcount,3,QTableWidgetItem(str(hour)))
				self.table.setItem(rowcount,4,QTableWidgetItem(str(li_temp[0][1])))
				self.table.setItem(rowcount,5,QTableWidgetItem('0'))
				rowcount+=1


'''
流转状态统计界面
'''
class WinFlowState(QWidget):
	def __init__(self,tablename,cur1,conn1):
		global cur,conn
		super().__init__()
		cur=cur1
		conn=conn1
		self.tablename=tablename
		self.finished_level=FinishLevel(self.tablename)
		self.initUI()

	def initUI(self):

		def label_event(s):
			self.winwaitservice=WinWaitService(self.tablename,self.finished_level,title='待维修(全部)')

		def label_event_A(s):
			self.winwaitservice=WinWaitService(self.tablename,self.finished_level,title='待维修(当天完成计划)')

		def label_event_B(s):
			self.winwaitservice=WinWaitService(self.tablename,self.finished_level,title='待维修(明天天完成计划)')

		def label_event_C(s):
			self.winwaitservice=WinWaitService(self.tablename,self.finished_level,title='待维修(后天及以后完成计划)')
		def label_event_in(s):
			self.winin=WinWaitIn(self.tablename,self.finished_level)
		def label_event_out(s):
			self.winin=WinWaitOut(self.tablename,self.finished_level)
		def label_event_error(s):
			self.winerror=WinFlowError(self.tablename)

		def label_event_lave(s):
			self.winlave=WinLave(self.tablename,self.finished_level)


		label_date_start=QLabel('开始日期(含)',self)
		label_date_end=QLabel('结束日期(含)',self)
		self.date_edit_start=QDateEdit(QDate.currentDate(),self)
		self.date_edit_end=QDateEdit(QDate.currentDate(),self)
		
		btn=QPushButton('刷新',self)
		btn.clicked.connect(self.btn_event)
		layout_date=QHBoxLayout()
		layout_date.addStretch(1)
		layout_date.addWidget(label_date_start)
		layout_date.addWidget(self.date_edit_start)
		layout_date.addStretch(1)
		
		layout_date.addWidget(label_date_end)
		layout_date.addWidget(self.date_edit_end)
		# layout_date.addWidget(self.comb_type)
		layout_date.addWidget(btn)

		tabwidget=QTabWidget(self)


		win_flow_count=WinFlowCount(cur,conn,self.tablename)
		win_flow_count_by_date=WinFlowCountByDate(cur,conn,self.tablename)
		win_flow_list=WinFlowList(self.tablename)
		
		tabwidget.addTab(win_flow_count,'当天流转统计')
		tabwidget.addTab(win_flow_count_by_date,'流转统计查询')
		tabwidget.addTab(win_flow_list,'流转单')


		label_all=QLabel('登记不良总数：',self)
		label_count=QLabel('待修(总数)：',self)
		label_count.setCursor(QCursor(Qt.PointingHandCursor))
		label_count.setStyleSheet("QLabel{color:rgb(0,0,0,255);font-size:20px}")
		label_count.mouseReleaseEvent=label_event
		label_count_A=QLabel('待修(紧急):',self)
		label_count_A.setToolTip('当天及之前需完成的计划')
		label_count_A.setCursor(QCursor(Qt.PointingHandCursor))
		label_count_A.setStyleSheet("QLabel{color:rgb(255,50,50,255);font-size:20px}")
		label_count_A.mouseReleaseEvent=label_event_A
		label_count_B=QLabel('待修(加急):',self)
		label_count_B.setToolTip('明天需完成的计划')
		label_count_B.setCursor(QCursor(Qt.PointingHandCursor))
		label_count_B.setStyleSheet("QLabel{color:rgb(255,160,45,255);font-size:20px}")
		label_count_B.mouseReleaseEvent=label_event_B
		label_count_C=QLabel('待修(普通):',self)
		label_count_C.setToolTip('后天及之后需完成的计划')
		label_count_C.setCursor(QCursor(Qt.PointingHandCursor))
		label_count_C.setStyleSheet("QLabel{color:rgb(50,50,255,255);font-size:20px}")
		label_count_C.mouseReleaseEvent=label_event_C
		label_in_count=QLabel('转入维修数量：',self)
		label_out_count=QLabel('维修转出数量：',self)
		label_lave=QLabel('维修剩余数量：',self)
		label_lave.mouseReleaseEvent=label_event_lave
		label_lave.setCursor(QCursor(Qt.PointingHandCursor))
		label_lave.setStyleSheet("QLabel{color:rgb(50,10,50,255);font-size:20px}")
		# label_error=QLabel('流转异常数量：',self)
		# label_error.mouseReleaseEvent=label_event_error
		# label_error.setCursor(QCursor(Qt.PointingHandCursor))
		label_wait=QLabel('待转入维修数量：',self)
		label_wait.setCursor(QCursor(Qt.PointingHandCursor))
		label_wait.setStyleSheet("QLabel{color:rgb(240,46,140,255);font-size:20px}")
		label_wait.mouseReleaseEvent=label_event_in
		label_wait_out=QLabel('待转入产线数量：',self)
		label_wait_out.setCursor(QCursor(Qt.PointingHandCursor))
		label_wait_out.setStyleSheet("QLabel{color:rgb(10,130,10,255);font-size:20px}")
		label_wait_out.mouseReleaseEvent=label_event_out


		self.label_all1=QLabel('',self)
		self.label_count1=QLabel('',self)
		self.label_count1.setStyleSheet("QLabel{color:rgb(0,0,0,255);font-size:20px}")
		label_count.setStyleSheet("QLabel{color:rgb(0,0,0,255);font-size:20px}")
		self.label_countA1=QLabel('',self)
		self.label_countA1.setStyleSheet("QLabel{color:rgb(255,50,50,255);font-size:20px}")
		self.label_countB1=QLabel('',self)
		self.label_countB1.setStyleSheet("QLabel{color:rgb(255,160,45,255);font-size:20px}")
		self.label_countC1=QLabel('',self)
		self.label_countC1.setStyleSheet("QLabel{color:rgb(50,50,255,255);font-size:20px}")
		self.label_in_count1=QLabel('',self)
		self.label_out_count1=QLabel('',self)
		self.label_lave1=QLabel('',self)
		self.label_lave1.setStyleSheet("QLabel{color:rgb(50,10,50,255);font-size:20px}")
		# self.label_error1=QLabel('',self)
		self.label_wait1=QLabel('',self)
		self.label_wait1.setStyleSheet("QLabel{color:rgb(240,46,140,255);font-size:20px}")
		self.label_wait_out1=QLabel('',self)
		self.label_wait_out1.setStyleSheet("QLabel{color:rgb(10,130,10,255);font-size:20px}")


		glayout=QGridLayout()
		glayout.addWidget(label_all,0,0)
		glayout.addWidget(self.label_all1,0,1)
		glayout.addWidget(label_count,1,0)
		glayout.addWidget(self.label_count1,1,1)

		glayout.addWidget(label_count_A,2,0)
		glayout.addWidget(self.label_countA1,2,1)
		glayout.addWidget(label_count_B,3,0)
		glayout.addWidget(self.label_countB1,3,1)
		glayout.addWidget(label_count_C,4,0)
		glayout.addWidget(self.label_countC1,4,1)

		glayout.addWidget(label_in_count,5,0)
		glayout.addWidget(self.label_in_count1,5,1)
		glayout.addWidget(label_out_count,6,0)
		glayout.addWidget(self.label_out_count1,6,1)
		glayout.addWidget(label_lave,7,0)
		glayout.addWidget(self.label_lave1,7,1)
		# glayout.addWidget(label_error,8,0)
		# glayout.addWidget(self.label_error1,8,1)
		glayout.addWidget(label_wait,9,0)
		glayout.addWidget(self.label_wait1,9,1)
		glayout.addWidget(label_wait_out,10,0)
		glayout.addWidget(self.label_wait_out1,10,1)

		widget=QGroupBox('数量汇总',self)

		widget.setLayout(glayout)

		spliter=QSplitter(Qt.Horizontal,self)
		spliter.addWidget(tabwidget)
		spliter.addWidget(widget)

		vlayout=QVBoxLayout(self)
		vlayout.addLayout(layout_date)
		vlayout.addWidget(spliter)
		self.setLayout(vlayout)
		self.show()

	def _plan_num_event(self,project_num):
		time.sleep(0.05)
		if re.match(r'^[\s]{0,}$',project_num):
			return

		s=project_num+'MD5'+project_num+'dj'

		m=hashlib.md5(s.encode('ascii')).hexdigest()
		print(m)
		s='http://192.168.30.230/jiekou/OrderInfoGet_ById/?id='+project_num+'&CheckCode='+m
		try:
			r=requests.get(s,timeout=2)
		except:
			QMessageBox(text='   数据获取失败！  ',parent=self).show()
			return
		j=r.json()[0]
		if len(j)==0:
			QMessageBox(text='   查询不到该计划id！  ',parent=self).show()
			return
	
		return j['完成时间']



	'''
	刷新
	'''
	def btn_event(self):
		s1=self.date_edit_start.date().toString("yyyy-MM-dd")
		s2=self.date_edit_end.date().addDays(1).toString("yyyy-MM-dd")

		'''
		登记不良总数，含非在线维修
		'''
		cur.execute("select id from "+self.tablename+" where note_date>=%s and note_date<%s",(s1,s2))
		li=cur.fetchall()
		conn.commit()
		self.label_all1.setText(str(len(li)))

		cur.execute("select in_time from "+self.tablename+" where service_result is null and state<>'完成'")
		li=cur.fetchall()
		conn.commit()
		self.label_count1.setText(str(len(li)))


		today=datetime.datetime.now().date()
		state=self.finished_level.flush()
		print('计划信息更新》》》》》》》')
		if state=='fail':
			QMessageBox(text='   接口服务器异常！  ',parent=self).show()
			return
		li_A,li_B,li_C=self.finished_level.get_level()
		count_A=0
		count_B=0
		count_C=0


		cur.execute("select project_num from "+self.tablename+" where service_result is null and state<>'完成'")
		li=cur.fetchall()
		conn.commit()
		for i in li:
			if i[0] in li_A:
				count_A+=1
			elif i[0] in li_B:
				count_B+=1
			else:
				count_C+=1

		self.label_countA1.setText(str(count_A))
		self.label_countB1.setText(str(count_B))
		self.label_countC1.setText(str(count_C))



		'''
		维修日期范围内转入数量
		'''
		cur.execute("select count(id) from "+self.tablename+" where in_time>=%s and in_time<%s",(s1,s2))
		li=cur.fetchall()
		conn.commit()
		self.label_in_count1.setText(str(li[0][0]))


		'''
		维修日期范围内转出数量
		'''
		cur.execute("select count(id) from "+self.tablename+" where state='完成' and out_time>=%s and out_time<%s",(s1,s2))
		li=cur.fetchall()
		conn.commit()
		self.label_out_count1.setText(str(li[0][0]))


		'''
		维修剩余数量
		'''
		cur.execute("select count(id) from "+self.tablename+" where state='维修'")
		li=cur.fetchall()
		conn.commit()
		self.label_lave1.setText(str(li[0][0]))

		# '''
		# 流转异常数量
		# '''
		# cur.execute("select count(id) from "+self.tablename+" where state='待修' and service_result is not null")
		# li=cur.fetchall()
		# conn.commit()
		# self.label_error1.setText(str(li[0][0]))


		'''
		待转入维修数量
		'''
		cur.execute("select count(id) from "+self.tablename+" where state='待修' and service_result is null")
		li=cur.fetchall()
		conn.commit()
		self.label_wait1.setText(str(li[0][0]))



		'''
		待转入产线数量
		'''
		cur.execute("select count(id) from "+self.tablename+" where state='维修' and service_result is not null")
		li=cur.fetchall()
		conn.commit()
		self.label_wait_out1.setText(str(li[0][0]))

		
'''
待转入详细信息
'''
class WinWaitIn(QWidget):
	def __init__(self,tablename,finished_level):
		super().__init__()
		self.tablename=tablename
		self.finished_level=finished_level
		self.initUI()

	def initUI(self):
		self.table=QTableWidget(0,0,self)

		self.table.horizontalHeader().setSortIndicator(0, Qt.AscendingOrder)
		self.table.horizontalHeader().setSortIndicatorShown(True)
		self.table.horizontalHeader().sectionClicked.connect(self.table.sortByColumn)

		btn=QPushButton('详细信息',self)
		btn.clicked.connect(self.btn_event)
		vlayout=QVBoxLayout(self)
		vlayout.addWidget(btn)
		vlayout.addWidget(self.table)
		self.setLayout(vlayout)
		self.show()
		self.data_process_count()


	def btn_event(self):
		sender = self.sender()
		if sender.text()=='详细信息':
			self.data_process_detail()
			sender.setText('统计信息')
		else:
			self.data_process_count()
			sender.setText('详细信息')

	def data_process_detail(self):
		print('详细信息处理')
		cur.execute("select project_num from "+self.tablename+" where service_result is null and \
			state='待修' group by project_num")
		li=cur.fetchall()
		conn.commit()
		print('list of project_num:',li)
		today=datetime.datetime.now().date()

		self.table.setRowCount(0)
		self.table.setColumnCount(10)
		self.table.setHorizontalHeaderLabels(['主型号','系列号','批次','计划ID',\
			'临时产品编码','不良现象','记录人','记录时间','启动时间','结束时间'])

		cur.execute("select main_model,serial_num,batch_num,project_num,product_id,fault_class2,note_person,\
			note_date from "+self.tablename+" where state='待修' \
			and service_result is null")
		
		li=cur.fetchall()

		conn.commit()
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

		keys=self.finished_level.dic.keys()
		li_A,li_B,li_C=self.finished_level.get_level()
		for i in range(self.table.rowCount()):
			if self.table.item(i,3).text() not in keys:
				continue
			self.table.setItem(i,8,QTableWidgetItem(self.finished_level.dic[self.table.item(i,3).text()][0]))
			self.table.setItem(i,9,QTableWidgetItem(self.finished_level.dic[self.table.item(i,3).text()][1]))

			if self.table.item(i,3).text() in li_A:
				for j in range(10):
					self.table.item(i,j).setBackground(QBrush(QColor(255,100,100)))
			elif self.table.item(i,3).text() in li_B:
				for j in range(10):
					self.table.item(i,j).setBackground(QBrush(QColor(255,230,80)))
			elif self.table.item(i,3).text() in li_C:
				for j in range(10):
					self.table.item(i,j).setBackground(QBrush(QColor(150,200,255)))
			else:
				pass

	def data_process_count(self):
		print('统计信息处理')
		self.table.setRowCount(0)
		self.table.setColumnCount(5)
		self.table.setHorizontalHeaderLabels(['线别','计划ID','数量','启动时间','结束时间'])
		cur.execute("select note_person,project_num from "+self.tablename+" where state='待修' and \
			service_result is null")
		li=cur.fetchall()
		conn.commit()
		if len(li)==0:
			return

		self.dfa=pd.DataFrame(np.array(li),columns=['A','B'])
		li_line=self.dfa['A'].drop_duplicates().tolist()
		for i in li_line:
			li_id=self.dfa[self.dfa['A']==i]['B'].drop_duplicates().tolist()
			df_temp=self.dfa[self.dfa['A']==i]
			for j in li_id:
				df_count=df_temp[df_temp['B']==j]
				count=df_count.shape[0]
				self.table.setRowCount(self.table.rowCount()+1)
				self.table.setItem(self.table.rowCount()-1,0,QTableWidgetItem(i))
				self.table.setItem(self.table.rowCount()-1,1,QTableWidgetItem(j))
				self.table.setItem(self.table.rowCount()-1,2,QTableWidgetItem(str(count)))
		

		print(self.finished_level.dic)
		keys=self.finished_level.dic.keys()
		li_A,li_B,li_C=self.finished_level.get_level()


		for i in range(self.table.rowCount()):
			if self.table.item(i,1).text() not in keys:
				continue
			self.table.setItem(i,3,QTableWidgetItem(self.finished_level.dic[self.table.item(i,1).text()][0]))
			self.table.setItem(i,4,QTableWidgetItem(self.finished_level.dic[self.table.item(i,1).text()][1]))

			if self.table.item(i,1).text() in li_A:
				for j in range(5):
					self.table.item(i,j).setBackground(QBrush(QColor(255,100,100)))
			elif self.table.item(i,1).text() in li_B:
				for j in range(5):
					self.table.item(i,j).setBackground(QBrush(QColor(255,230,80)))
			elif self.table.item(i,1).text() in li_C:
				for j in range(5):
					self.table.item(i,j).setBackground(QBrush(QColor(150,200,255)))
			else:
				pass

'''
维修剩余详细信息
'''

class WinLave(QWidget):
	def __init__(self,tablename,finished_level):
		super().__init__()
		self.tablename=tablename
		self.finished_level=finished_level
		self.initUI()

	def initUI(self):
		self.table=QTableWidget(0,0,self)
		self.table.horizontalHeader().setSortIndicator(0, Qt.AscendingOrder)
		self.table.horizontalHeader().setSortIndicatorShown(True)
		self.table.horizontalHeader().sectionClicked.connect(self.table.sortByColumn)
		btn=QPushButton('详细信息',self)
		btn.clicked.connect(self.btn_event)
		vlayout=QVBoxLayout(self)
		vlayout.addWidget(btn)
		vlayout.addWidget(self.table)
		self.setLayout(vlayout)
		self.show()
		self.data_process_count()


	def btn_event(self):
		sender = self.sender()
		if sender.text()=='详细信息':
			self.data_process_detail()
			sender.setText('统计信息')
		else:
			self.data_process_count()
			sender.setText('详细信息')

	def data_process_detail(self):
		print('详细信息处理')
		self.table.setRowCount(0)
		self.table.setColumnCount(13)
		self.table.setHorizontalHeaderLabels(['主型号','系列号','批次','计划ID',\
			'临时产品编码','不良现象','记录人','记录时间','维修人','维修结果','维修时间','启动时间','结束时间'])

		cur.execute("select main_model,serial_num,batch_num,project_num,product_id,fault_name,note_person,\
			note_date,service_person,service_result,service_date from "+self.tablename+" where state='维修'")
		
		li=cur.fetchall()

		conn.commit()
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

		keys=self.finished_level.dic.keys()
		li_A,li_B,li_C=self.finished_level.get_level()
		for i in range(self.table.rowCount()):
			if self.table.item(i,3).text() not in keys:
				continue
			self.table.setItem(i,11,QTableWidgetItem(self.finished_level.dic[self.table.item(i,3).text()][0]))
			self.table.setItem(i,12,QTableWidgetItem(self.finished_level.dic[self.table.item(i,3).text()][1]))

			if self.table.item(i,3).text() in li_A:
				for j in range(13):
					self.table.item(i,j).setBackground(QBrush(QColor(255,100,100)))
			elif self.table.item(i,3).text() in li_B:
				for j in range(13):
					self.table.item(i,j).setBackground(QBrush(QColor(255,230,80)))
			elif self.table.item(i,3).text() in li_C:
				for j in range(13):
					self.table.item(i,j).setBackground(QBrush(QColor(150,200,255)))
			else:
				pass

	def data_process_count(self):
		print('统计信息处理')
		self.table.setRowCount(0)
		self.table.setColumnCount(6)
		self.table.setHorizontalHeaderLabels(['线别','计划ID','已修数量','待修数量','启动时间','结束时间'])
		cur.execute("select note_person,project_num,service_person from "+self.tablename+" where state='维修'")
		li=cur.fetchall()
		conn.commit()
		if len(li)==0:
			return

		self.dfa=pd.DataFrame(np.array(li),columns=['线别','计划号','维修人'])
		self.dfa=self.dfa.fillna(value='None')

		li_line=self.dfa['线别'].drop_duplicates().tolist()
		for i in li_line:
			li_id=self.dfa[self.dfa['线别']==i]['计划号'].drop_duplicates().tolist()
			df_temp=self.dfa[self.dfa['线别']==i]
			for j in li_id:
				df_count=df_temp[df_temp['计划号']==j]
				count_service=df_count[df_count['维修人']!= 'None'].shape[0]
				count_noservice=df_count[df_count['维修人']=='None'].shape[0]
				self.table.setRowCount(self.table.rowCount()+1)
				self.table.setItem(self.table.rowCount()-1,0,QTableWidgetItem(i))
				self.table.setItem(self.table.rowCount()-1,1,QTableWidgetItem(j))
				self.table.setItem(self.table.rowCount()-1,2,QTableWidgetItem(str(count_service)))
				self.table.setItem(self.table.rowCount()-1,3,QTableWidgetItem(str(count_noservice)))
		keys=self.finished_level.dic.keys()
		li_A,li_B,li_C=self.finished_level.get_level()
		for i in range(self.table.rowCount()):
			if self.table.item(i,1).text() not in keys:
				continue
			self.table.setItem(i,3+1,QTableWidgetItem(self.finished_level.dic[self.table.item(i,1).text()][0]))
			self.table.setItem(i,4+1,QTableWidgetItem(self.finished_level.dic[self.table.item(i,1).text()][1]))

			if self.table.item(i,1).text() in li_A:
				for j in range(6):
					self.table.item(i,j).setBackground(QBrush(QColor(255,100,100)))
			elif self.table.item(i,1).text() in li_B:
				for j in range(6):
					self.table.item(i,j).setBackground(QBrush(QColor(255,230,80)))
			elif self.table.item(i,1).text() in li_C:
				for j in range(6):
					self.table.item(i,j).setBackground(QBrush(QColor(150,200,255)))
			else:
				pass

'''
待转出详细信息
'''

class WinWaitOut(QWidget):
	def __init__(self,tablename,finished_level):
		super().__init__()
		self.tablename=tablename
		self.finished_level=finished_level
		self.initUI()

	def initUI(self):
		self.table=QTableWidget(0,0,self)
		self.table.horizontalHeader().setSortIndicator(0, Qt.AscendingOrder)
		self.table.horizontalHeader().setSortIndicatorShown(True)
		self.table.horizontalHeader().sectionClicked.connect(self.table.sortByColumn)
		btn=QPushButton('详细信息',self)
		btn.clicked.connect(self.btn_event)
		vlayout=QVBoxLayout(self)
		vlayout.addWidget(btn)
		vlayout.addWidget(self.table)
		self.setLayout(vlayout)
		self.show()
		self.data_process_count()


	def btn_event(self):
		sender = self.sender()
		if sender.text()=='详细信息':
			self.data_process_detail()
			sender.setText('统计信息')
		else:
			self.data_process_count()
			sender.setText('详细信息')

	def data_process_detail(self):
		print('详细信息处理')
		self.table.setRowCount(0)
		self.table.setColumnCount(13)
		self.table.setHorizontalHeaderLabels(['主型号','系列号','批次','计划ID',\
			'临时产品编码','不良现象','记录人','记录时间','维修人','维修结果','维修时间','启动时间','结束时间'])

		cur.execute("select main_model,serial_num,batch_num,project_num,product_id,fault_name,note_person,\
			note_date,service_person,service_result,service_date from "+self.tablename+" where state='维修' \
			and service_result is not null")
		
		li=cur.fetchall()

		conn.commit()
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

		keys=self.finished_level.dic.keys()
		li_A,li_B,li_C=self.finished_level.get_level()
		for i in range(self.table.rowCount()):
			if self.table.item(i,3).text() not in keys:
				continue
			self.table.setItem(i,11,QTableWidgetItem(self.finished_level.dic[self.table.item(i,3).text()][0]))
			self.table.setItem(i,12,QTableWidgetItem(self.finished_level.dic[self.table.item(i,3).text()][1]))

			if self.table.item(i,3).text() in li_A:
				for j in range(13):
					self.table.item(i,j).setBackground(QBrush(QColor(255,100,100)))
			elif self.table.item(i,3).text() in li_B:
				for j in range(13):
					self.table.item(i,j).setBackground(QBrush(QColor(255,230,80)))
			elif self.table.item(i,3).text() in li_C:
				for j in range(13):
					self.table.item(i,j).setBackground(QBrush(QColor(150,200,255)))
			else:
				pass

	def data_process_count(self):
		print('统计信息处理')
		self.table.setRowCount(0)
		self.table.setColumnCount(5)
		self.table.setHorizontalHeaderLabels(['线别','计划ID','数量','启动时间','结束时间'])
		cur.execute("select note_person,project_num from "+self.tablename+" where state='维修' and \
			service_result is not null")
		li=cur.fetchall()
		conn.commit()
		if len(li)==0:
			return

		self.dfa=pd.DataFrame(np.array(li),columns=['A','B'])
		li_line=self.dfa['A'].drop_duplicates().tolist()
		for i in li_line:
			li_id=self.dfa[self.dfa['A']==i]['B'].drop_duplicates().tolist()
			df_temp=self.dfa[self.dfa['A']==i]
			for j in li_id:
				df_count=df_temp[df_temp['B']==j]
				count=df_count.shape[0]
				self.table.setRowCount(self.table.rowCount()+1)
				self.table.setItem(self.table.rowCount()-1,0,QTableWidgetItem(i))
				self.table.setItem(self.table.rowCount()-1,1,QTableWidgetItem(j))
				self.table.setItem(self.table.rowCount()-1,2,QTableWidgetItem(str(count)))
		keys=self.finished_level.dic.keys()
		li_A,li_B,li_C=self.finished_level.get_level()
		for i in range(self.table.rowCount()):
			if self.table.item(i,1).text() not in keys:
				continue
			self.table.setItem(i,3,QTableWidgetItem(self.finished_level.dic[self.table.item(i,1).text()][0]))
			self.table.setItem(i,4,QTableWidgetItem(self.finished_level.dic[self.table.item(i,1).text()][1]))

			if self.table.item(i,1).text() in li_A:
				for j in range(5):
					self.table.item(i,j).setBackground(QBrush(QColor(255,100,100)))
			elif self.table.item(i,1).text() in li_B:
				for j in range(5):
					self.table.item(i,j).setBackground(QBrush(QColor(255,230,80)))
			elif self.table.item(i,1).text() in li_C:
				for j in range(5):
					self.table.item(i,j).setBackground(QBrush(QColor(150,200,255)))
			else:
				pass


'''
流转异常详细记录
'''
class WinFlowError(QWidget):
	def __init__(self,tablename):
		super().__init__()

		self.tablename=tablename
		self.initUI()

	def initUI(self):
		self.table=QTableWidget(0,13,self)
		self.table.setHorizontalHeaderLabels(['主型号','系列号','批次','计划ID',\
			'临时产品编码','不良现象','记录人','不良原因','维修人',\
			'维修接收时间','维修接收人','产线接收时间','产线接收人'])
		cur.execute("select main_model,serial_num,batch_num,project_num,product_id,fault_name,note_person,service_result,\
			service_person,in_time,in_person,out_time,out_person from "+self.tablename+" where state='待修' \
			and service_result is not null")
		li=cur.fetchall()
		conn.commit()
		self.table.setRowCount(len(li))
		rowcount=0
		for i in li:
			columncount=0
			for j in i:
				self.table.setItem(rowcount,columncount,QTableWidgetItem(str(j)))
				columncount+=1
			rowcount+=1
		vlayout=QVBoxLayout(self)
		vlayout.addWidget(self.table)
		self.setWindowTitle('异常记录表')
		self.show()


		
'''
流转单详细信息显示界面,流转账单界面双击显示
'''
class WinFlowPart(QWidget):
	def __init__(self,condition,tablename):
		super().__init__()
		self.condition=condition
		self.tablename=tablename
		self.initUI()

	def initUI(self):
		self.table_columns=['主型号','系列号','批次','计划ID',\
			'制程状态','临时产品编码','不良现象','记录人','记录日期',\
			'不良原因','维修人','维修日期','状态']
		self.table=QTableWidget(0,13,self)
		self.table.setHorizontalHeaderLabels(self.table_columns)
		cur.execute("select main_model,serial_num,batch_num,project_num,process_state,product_id,fault_name,\
			note_person,note_date,service_result,service_person,service_date,state from "+self.tablename+" \
			where in_time=%s",(self.condition))
		li=cur.fetchall()
		self.table.setRowCount(len(li))
		rowcount=0
		for i in li:
			columncount=0
			for j in i:
				self.table.setItem(rowcount,columncount,QTableWidgetItem(str(j)))
				columncount+=1
			rowcount+=1
		vlayout=QVBoxLayout(self)
		vlayout.addWidget(self.table)
		self.setLayout(vlayout)
		self.show()



'''
按线别，计划ID显示当天流转数量，待修数量，待转入数量
'''
class WinFlowCount(QWidget):
	def __init__(self,cur,conn,table_name):
		super().__init__()
		self.cur=cur
		self.conn=conn
		self.table_name=table_name
		self.initUI()
	def initUI(self):
		self.table=QTableWidget(0,6,self)
		self.table.setHorizontalHeaderLabels(['线别','计划ID','转入维修','待转入维修','待修','待转入产线'])
		self.table_flow_out=QTableWidget(0,3,self)
		self.table_flow_out.setHorizontalHeaderLabels(['线别','计划ID','转入产线'])
		btn_flush=QPushButton('刷新',self)
		btn_flush.clicked.connect(self.flush_event)

		btn_export=QPushButton('存储为excel',self)
		btn_export.clicked.connect(self.export_event)

		hlayout=QHBoxLayout()
		
		hlayout.addWidget(btn_export,alignment=Qt.AlignRight)
		hlayout.addWidget(btn_flush,alignment=Qt.AlignRight)

		vlayout=QVBoxLayout(self)
		vlayout.addLayout(hlayout)
		tabwidget=QTabWidget(self)
		tabwidget.addTab(self.table,'转入统计')
		tabwidget.addTab(self.table_flow_out,'转出统计')
		vlayout.addWidget(tabwidget)

		self.setLayout(vlayout)
		self.show()

	def flush_event(self):
		def date_trans(s):
			if s is None:
				return s
			if s=='None':
				return s
			str_date=str(s).split(' ')[0]
			li_date=str_date.split('-')
			year=int(li_date[0])
			month=int(li_date[1])
			day=int(li_date[2])
			return str(datetime.date(year,month,day))

		today=str(datetime.datetime.now().date())
		cur.execute("select note_person,project_num,service_result,in_time,out_time,state,out_person from "+self.table_name+" \
			where in_time >= %s or out_time>=%s or state='待修' or state='维修'",(today,today))
		li=cur.fetchall()
		conn.commit()
		if len(li)==0:
			return
		self.table.setRowCount(0)
		self.table_flow_out.setRowCount(0)
		columns=['记录人','计划ID','维修结果','转入时间','转出时间','状态','转出接受人']
		self.df=pd.DataFrame(np.array(li),columns=columns)
		# print(self.df)
		
		self.df['转入时间']=self.df['转入时间'].apply(date_trans)
		self.df['转出时间']=self.df['转出时间'].apply(date_trans)
		self.df=self.df.fillna(value='None')

		print(self.df)
		li_line=self.df['记录人'].drop_duplicates().tolist()
		for i in li_line:
			df=self.df[self.df['记录人']==i]
			li_id=df['计划ID'].drop_duplicates().tolist()
			
			for j in li_id:
				df_temp=df[df['计划ID']==j]
				count_all=0
				count_in=0
				# count_out=0
				count_wait_in=0
				count_wait_service=0
				count_wait_out=0
				# count_all=df_temp.shape[0]
				count_in=df_temp[df_temp['转入时间']==today].shape[0]
				# count_out=df_temp[df_temp['转出时间']==today].shape[0]
				count_wait_in=df_temp[df_temp['状态']=='待修'].shape[0]
				count_wait_service=df_temp[df_temp['维修结果']=='None'].shape[0]
				count_wait_out=df_temp[(df_temp['状态']=='维修')&(df_temp['维修结果']!='None')].shape[0]
				print(count_all,count_in,count_wait_in,count_wait_service,count_wait_out)
				self.table.setRowCount(self.table.rowCount()+1)
				self.table.setItem(self.table.rowCount()-1,0,QTableWidgetItem(str(i)))
				self.table.setItem(self.table.rowCount()-1,1,QTableWidgetItem(str(j)))
				self.table.setItem(self.table.rowCount()-1,2,QTableWidgetItem(str(count_in)))
				# self.table.setItem(self.table.rowCount()-1,3,QTableWidgetItem(str(count_out)))
				self.table.setItem(self.table.rowCount()-1,4-1,QTableWidgetItem(str(count_wait_in)))
				self.table.setItem(self.table.rowCount()-1,5-1,QTableWidgetItem(str(count_wait_service)))
				self.table.setItem(self.table.rowCount()-1,6-1,QTableWidgetItem(str(count_wait_out)))
				# self.table.setItem(self.table.rowCount()-1,7,QTableWidgetItem(str(count_all)))

		self.df=self.df[self.df['转出接受人'] != 'None']
		li_line=self.df['转出接受人'].drop_duplicates().tolist()
		for i in li_line:
			df=self.df[self.df['转出接受人']==i]
			li_id=df['计划ID'].drop_duplicates().tolist()
			
			for j in li_id:
				count_out=df[df['计划ID']==j].shape[0]
				self.table_flow_out.setRowCount(self.table_flow_out.rowCount()+1)
				self.table_flow_out.setItem(self.table_flow_out.rowCount()-1,0,QTableWidgetItem(str(i)))
				self.table_flow_out.setItem(self.table_flow_out.rowCount()-1,1,QTableWidgetItem(str(j)))
				self.table_flow_out.setItem(self.table_flow_out.rowCount()-1,2,QTableWidgetItem(str(count_out)))



	def export_event(self):
		if self.table.rowCount()==0:
			return
		li_df=[]

		for i in range(self.table.rowCount()):
			li_temp=[]
			for j in range(self.table.columnCount()):
				li_temp.append(self.table.item(i,j).text())
			li_df.append(li_temp)
		df=pd.DataFrame(li_df,columns=['线别','计划ID','转入维修','待转入维修','待修','待转入产线'])

		li_df_out=[]
		for i in range(self.table_flow_out.rowCount()):
			li_temp=[]
			for j in range(self.table_flow_out.columnCount()):
				li_temp.append(self.table_flow_out.item(i,j).text())
			li_df_out.append(li_temp)
		df_out=pd.DataFrame(li_df_out,columns=['线别','计划ID','转入产线'])

		filename=QFileDialog.getSaveFileName(self,'存储为','D:/流转统计','xlsx')
		if filename[0]=='':
			return
		writer = ExcelWriter(filename[0]+'.'+filename[1])
		df.to_excel(writer,sheet_name='转入维修')
		df_out.to_excel(writer,sheet_name='转入产线')


		writer.save()






'''
历史，根据日期，按线别，计划ID显示当天流转数量，待修数量，待转入数量
'''
class WinFlowCountByDate(QWidget):
	def __init__(self,cur,conn,table_name):
		super().__init__()
		self.cur=cur
		self.conn=conn
		self.table_name=table_name
		self.initUI()
	def initUI(self):
		label_date=QLabel('日期',self)
		self.date_line=QDateEdit(QDate.currentDate(),self)
		self.table=QTableWidget(0,3,self)
		self.table.setHorizontalHeaderLabels(['线别','计划ID','转入维修'])
		self.table_flow_out=QTableWidget(0,3,self)
		self.table_flow_out.setHorizontalHeaderLabels(['线别','计划ID','转入产线'])
		btn_flush=QPushButton('刷新',self)
		btn_flush.clicked.connect(self.flush_event)

		btn_export=QPushButton('存储为excel',self)
		btn_export.clicked.connect(self.export_event)

		hlayout=QHBoxLayout()
		hlayout.addWidget(label_date,alignment=Qt.AlignRight)
		hlayout.addWidget(self.date_line,alignment=Qt.AlignRight)
		hlayout.addWidget(btn_export,alignment=Qt.AlignRight)
		hlayout.addWidget(btn_flush,alignment=Qt.AlignRight)

		vlayout=QVBoxLayout(self)
		vlayout.addLayout(hlayout)
		tabwidget=QTabWidget(self)
		tabwidget.addTab(self.table,'转入统计')
		tabwidget.addTab(self.table_flow_out,'转出统计')
		vlayout.addWidget(tabwidget)

		self.setLayout(vlayout)
		self.show()

	def flush_event(self):
		def date_trans(s):
			if s is None:
				return s
			if s=='None':
				return s
			str_date=str(s).split(' ')[0]
			li_date=str_date.split('-')
			year=int(li_date[0])
			month=int(li_date[1])
			day=int(li_date[2])
			return str(datetime.date(year,month,day))

		day=self.date_line.date().toString('yyyy-MM-dd')
		day_add=self.date_line.date().addDays(1).toString('yyyy-MM-dd')
		cur.execute("select note_person,project_num,service_result,in_time,out_time,state,out_person from "+self.table_name+" \
			where (in_time >= %s and in_time < %s) or (out_time>=%s and out_time < %s)",(day,day_add,day,day_add))
		li=cur.fetchall()
		conn.commit()
		if len(li)==0:
			return
		self.table.setRowCount(0)
		self.table_flow_out.setRowCount(0)
		columns=['记录人','计划ID','维修结果','转入时间','转出时间','状态','转出接受人']
		self.df=pd.DataFrame(np.array(li),columns=columns)
		# print(self.df)
		
		self.df['转入时间']=self.df['转入时间'].apply(date_trans)
		self.df['转出时间']=self.df['转出时间'].apply(date_trans)
		self.df=self.df.fillna(value='None')

		print(self.df)

		df_in=self.df[self.df['转入时间']==day]

		li_line=df_in['记录人'].drop_duplicates().tolist()
		for i in li_line:
			df=df_in[df_in['记录人']==i]
			li_id=df['计划ID'].drop_duplicates().tolist()
			
			for j in li_id:
				df_temp=df[df['计划ID']==j]
				# count_all=0
				count_in=0
				# count_out=0
				# count_wait_in=0
				# count_wait_service=0
				# count_wait_out=0
				# count_all=df_temp.shape[0]
				count_in=df_temp[df_temp['转入时间']==day].shape[0]
				# count_out=df_temp[df_temp['转出时间']==today].shape[0]
				# count_wait_in=df_temp[df_temp['状态']=='待修'].shape[0]
				# count_wait_service=df_temp[df_temp['维修结果']=='None'].shape[0]
				# count_wait_out=df_temp[(df_temp['状态']=='维修')&(df_temp['维修结果']!='None')].shape[0]
				# print(count_all,count_in,count_wait_in,count_wait_service,count_wait_out)
				self.table.setRowCount(self.table.rowCount()+1)
				self.table.setItem(self.table.rowCount()-1,0,QTableWidgetItem(str(i)))
				self.table.setItem(self.table.rowCount()-1,1,QTableWidgetItem(str(j)))
				self.table.setItem(self.table.rowCount()-1,2,QTableWidgetItem(str(count_in)))
				# self.table.setItem(self.table.rowCount()-1,3,QTableWidgetItem(str(count_out)))
				# self.table.setItem(self.table.rowCount()-1,4-1,QTableWidgetItem(str(count_wait_in)))
				# self.table.setItem(self.table.rowCount()-1,5-1,QTableWidgetItem(str(count_wait_service)))
				# self.table.setItem(self.table.rowCount()-1,6-1,QTableWidgetItem(str(count_wait_out)))
				# self.table.setItem(self.table.rowCount()-1,7,QTableWidgetItem(str(count_all)))

		self.df=self.df[(self.df['转出接受人'] != 'None')&(self.df['转出时间']==day)]
		li_line=self.df['转出接受人'].drop_duplicates().tolist()
		for i in li_line:
			df=self.df[self.df['转出接受人']==i]
			li_id=df['计划ID'].drop_duplicates().tolist()
			
			for j in li_id:
				count_out=df[df['计划ID']==j].shape[0]
				self.table_flow_out.setRowCount(self.table_flow_out.rowCount()+1)
				self.table_flow_out.setItem(self.table_flow_out.rowCount()-1,0,QTableWidgetItem(str(i)))
				self.table_flow_out.setItem(self.table_flow_out.rowCount()-1,1,QTableWidgetItem(str(j)))
				self.table_flow_out.setItem(self.table_flow_out.rowCount()-1,2,QTableWidgetItem(str(count_out)))



	def export_event(self):
		if self.table.rowCount()==0:
			return
		li_df=[]

		for i in range(self.table.rowCount()):
			li_temp=[]
			for j in range(self.table.columnCount()):
				li_temp.append(self.table.item(i,j).text())
			li_df.append(li_temp)
		df=pd.DataFrame(li_df,columns=['线别','计划ID','转入维修'])

		li_df_out=[]
		for i in range(self.table_flow_out.rowCount()):
			li_temp=[]
			for j in range(self.table_flow_out.columnCount()):
				li_temp.append(self.table_flow_out.item(i,j).text())
			li_df_out.append(li_temp)
		df_out=pd.DataFrame(li_df_out,columns=['线别','计划ID','转入产线'])

		filename=QFileDialog.getSaveFileName(self,'存储为','D:/流转统计','xlsx')
		if filename[0]=='':
			return
		writer = ExcelWriter(filename[0]+'.'+filename[1])
		df.to_excel(writer,sheet_name='转入维修')
		df_out.to_excel(writer,sheet_name='转入产线')


		writer.save()

'''
对账
'''
class CheckCount(QWidget):
	def __init__(self,cur,conn,table_name):
		super().__init__()
		self.cur=cur
		self.conn=conn
		self.table_name=table_name
		self.li_columns=['id','计划ID','产品编码','故障分类','记录人','记录时间','故障名称','维修结果',\
			'维修人','维修日期','流转状态','维修接收人','维修接收时间','产线接收人','产线接收时间']
		self.initUI()
	def initUI(self):
		self.li=[]
		self.row=1
		self.column=0
		self.count=0
		self.current_line_edit=None

		self.lineedit=QLineEdit(self)
		self.lineedit.flag_first=True
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
		if sender.text().replace(' ','')=='':
			return
		if not sender.isModified():
			return
		sender.setModified(False)

		for i in self.li:
			if sender !=i:
				if sender.text()==i.text():
					# QMessageBox(text='   条码已存在！   ',parent=self).show()
					sender.setText('')
					return

		# sender.editingFinished.disconnect(self.editfinished)
		# sender.textChanged.connect(self.change_event)
		if sender.flag_first:
			lineedit=QLineEdit(self)
			self.current_line_edit=lineedit
			lineedit.flag_first=True
			self.li.append(sender)
			self.glayout.addWidget(lineedit,self.row,self.column)
			self.row+=1
			if self.row==20:
				self.row=0
				self.column+=1
			lineedit.editingFinished.connect(self.editfinished)
			
			lineedit.setFocus()
			self.count+=1
			self.label_count.setText(str(self.count))
			sender.flag_first=False
		else:
			self.current_line_edit.setFocus()

	# def change_event(self):
	# 	sender=self.sender()
	# 	# if sender.text()=='':
	# 	self.li.remove(sender)
	# 	sender.close()
	# 	self.count-=1
	# 	self.label_count.setText(str(self.count))
	def btn_event(self):
		li_temp=[]
		for i in self.li:
			if i.text().replace(' ','')=='':
				continue
			li_temp.append(i.text())
		self.set_nums=set(li_temp)
		self.cur.execute("select id,project_num,product_id,fault_class2,note_person,note_date,fault_name,\
			service_result,service_person,service_date,state,in_person,in_time,out_person,out_time \
			from "+self.table_name+" where state='维修'")

		li=cur.fetchall()
		conn.commit()
		li_temp=[]
		for i in li:
			li_temp.append(i[2])
		self.set_bill=set(li_temp)

		set_intersection=self.set_nums&self.set_bill

		li_nums_out=list(self.set_nums-set_intersection)
		li_bill_out=list(self.set_bill-set_intersection)

		# print('li_nums_out',li_nums_out)
		print('set_nums',self.set_nums)
		print('set_bill',self.set_bill)
		print('set_intersection',set_intersection)
		print('li_bill_out',li_bill_out)
		print('li_nums_out',li_nums_out)

		if len(li)==0:
			QMessageBox(text='   无在维修记录！  ',parent=self).show()
			return

		df=pd.DataFrame(np.array(li),columns=self.li_columns)

		li_bill_out_record=df[df['产品编码'].isin(li_bill_out)].values

		condition=''
		if len(li_nums_out)>0:
			for i in li_nums_out:

				condition+='\''+i+'\''
				if i!=li_nums_out[-1]:
					condition+=','
			condition=str(condition)
			print('condition>>>>>>>',condition)
			print('table_name>>>>>>>>>',self.table_name)
			self.cur.execute("select id,project_num,product_id,fault_class2,note_person,note_date,fault_name,\
				service_result,service_person,service_date,state,in_person,in_time,out_person,out_time \
				from "+self.table_name+" where product_id in ("+condition+")")
			li=cur.fetchall()
			conn.commit()
			if len(li)>0:
				li_nums_out_record=li 
			else:
				li_nums_out_record=[]
		else:
			li_nums_out_record=[]

		li_temp=[]
		for i in li:
			li_temp.append(i[2])
		set_temp_nums=set(li_temp)
		li_temp_nums=list(set(li_nums_out)-set_temp_nums)
		for i in li_temp_nums:
			li_nums_out_record.append(['','',i,'','','','','','','','','','','',''])
			# li_temp=[]
			# li_temp.append('')
			# li_temp.append('')
			# li_temp.append(i)
			# for x in range(12):
			# 	li_temp.append('')


		self.win_check_result=WinCheckCountResultAll(li_nums_out_record,li_bill_out_record)
	'''
	清空编号
	'''
	def clear_event(self):
		self.lineedit.close()
		for i in self.li:
			i.close()
		self.current_line_edit.close()
		self.count=0
		self.label_count.setText('0')
		self.li=[]
		self.row=1
		self.column=0
		self.lineedit=QLineEdit(self)
		self.current_line_edit=None
		self.lineedit.flag_first=True
		self.lineedit.editingFinished.connect(self.editfinished)
		self.glayout.addWidget(self.lineedit,0,0)

class WinCheckCountResultAll(QWidget):
	def __init__(self,li_nums_out,li_bill_out):
		super().__init__()
		self.li_nums_out=li_nums_out
		self.li_bill_out=li_bill_out
		self.columns=['id','计划ID','产品编码','故障分类','记录人','记录时间','故障名称','维修结果',\
			'维修人','维修日期','流转状态','维修接收人','维修接收时间','产线接收人','产线接收时间']
		btn_out_file=QPushButton('存储为excel',self)
		btn_out_file.clicked.connect(self.out_file_event)

		self.tabwidget=QTabWidget(self)

		self.check_result_nums=WinCheckCountResult(self.li_nums_out)
		self.check_result_bill=WinCheckCountResult(self.li_bill_out)

		
		self.tabwidget.addTab(self.check_result_bill,'账单错误记录')
		self.tabwidget.addTab(self.check_result_nums,'实物错误记录')

		vlayout=QVBoxLayout(self)
		vlayout.addWidget(btn_out_file,alignment=Qt.AlignRight)
		vlayout.addWidget(self.tabwidget)
		self.setLayout(vlayout)
		self.setWindowTitle('对账结果')
		self.show()



	def out_file_event(self):
		li_df=[]
		for i in range(self.check_result_nums.table.rowCount()):
			li_temp=[]
			for j in range(self.check_result_nums.table.columnCount()):
				li_temp.append(self.check_result_nums.table.item(i,j).text())
			li_df.append(li_temp)
		df_nums=pd.DataFrame(li_df,columns=self.columns)


		li_df=[]
		for i in range(self.check_result_bill.table.rowCount()):
			li_temp=[]
			for j in range(self.check_result_bill.table.columnCount()):
				li_temp.append(self.check_result_bill.table.item(i,j).text())
			li_df.append(li_temp)
		df_bills=pd.DataFrame(li_df,columns=self.columns)



		filename=QFileDialog.getSaveFileName(self,'存储为','D:/对账记录','xlsx')

		if filename[0]=='':
			return
		writer = ExcelWriter(filename[0]+'.'+filename[1])
		df_bills.to_excel(writer,sheet_name='账单错误记录')
		df_nums.to_excel(writer,sheet_name='实物错误记录')
		writer.save()

class WinCheckCountResult(QWidget):
	def __init__(self,li_out):
		super().__init__()
		self.li_out=li_out
		self.li_columns=['id','计划ID','产品编码','故障分类','记录人','记录时间','故障名称','维修结果',\
		'维修人','维修日期','流转状态','维修接收人','维修接收时间','产线接收人','产线接收时间']

		# self.cur.execute("select id,project_num,product_id,fault_class2,note_person,note_date,fault_name,\
		# 	service_result,service_person,service_date,state,in_person,in_time,out_person,out_time \
		# 	from "+self.table_name+" where state='维修'")
		self.initUI()

	def initUI(self):
		# print(self.li_out)
		
		self.table=QTableWidget(0,15,self)
		self.table.setHorizontalHeaderLabels(self.li_columns)
		self.table.setRowCount(len(self.li_out))
		rowcount=0
		for i in self.li_out:
			columncount=0
			for j in i:
				self.table.setItem(rowcount,columncount,QTableWidgetItem(str(j)))
				columncount+=1
			rowcount+=1
		vlayout=QVBoxLayout(self)
		vlayout.addWidget(self.table)
		self.setLayout(vlayout)
		self.show()






def connDB():
	# conn=pymssql.connect(host='192.168.70.3',user='Chenyong',password='147258',database='WeiXiuDB',charset='utf8')
	conn=pymysql.connect(host='127.0.0.1',user='root',password='000000',db='weixiu',charset='utf8')
	cur=conn.cursor()
	print('connect OK')
	return(conn,cur)

if __name__=='__main__':
	app=QApplication(sys.argv)
	conn,cur=connDB()
	win=CheckCount(cur,conn,'note_yd')
	# win.flush_event()
	sys.exit(app.exec_())
