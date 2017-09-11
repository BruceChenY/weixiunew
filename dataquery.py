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
import pandas.formats.format as fmt
from pandas.io.excel import ExcelWriter

class DataQuery(QWidget):
	def __init__(self,cur,conn,pivot_view,pivot_view1,managerlimit):	
		super().__init__()
		self.df=None
		self.dic={}
		self.cur=cur
		self.conn=conn
		self.managerlimit=managerlimit
		self.pivot_view=pivot_view
		self.pivot_view1=pivot_view1
		# self.name=name[0]
		# self.li_user=name
		# self.li_sqlcolumn=[ 'id','line_num','product_class','main_model','serial_num','batch_num','project_num','produce_date',\
		# 		'process_state','single_board_name','product_id','fault_num','fault_name','fault_class','note_person','note_date','pcb_name','position_symbol','material_name',\
		# 		'service_result','service_person','second_service','service_date','work_hours','comment','parse_class',\
		# 		'process_control','parse_person','fail_correct','cause_parse']
		self.table_columns=['ID','线别','分类','主型号','系列号','批次','计划ID','生产日期',\
			'制程状态','单板名称','临时产品编码','故障代码','不良现象','故障分类','记录人','记录日期','维修结果',\
			'不良原因','维修人','维修次数','维修日期','工时','备注','分析分类','控制制程','分析人','分析错误纠正',\
			'错误原因','人员分类','事业部']
		self.columns=['ID','线别','分类','主型号','系列号','批次','计划ID','生产日期',\
			'制程状态','单板名称','临时产品编码','故障代码','不良现象','故障分类','记录人','记录日期','维修结果',\
			'不良原因','维修人','维修次数','维修日期','工时','备注','分析分类','控制制程','分析人','分析错误纠正',\
			'错误原因','人员分类','事业部']
		self.initUI()

	def initUI(self):
		btn_export=QPushButton('导出excel')
		btn_export.clicked.connect(self.export_event)
		self.comb_type=QComboBox(self)
		self.comb_type.addItems(['金融','移动','全部'])
		label_date_start=QLabel('开始日期(含)',self)
		label_date_end=QLabel('结束日期(含)',self)
		self.date_edit_start=QDateEdit(QDate.currentDate(),self)
		self.date_edit_end=QDateEdit(QDate.currentDate(),self)
		btn=QPushButton('刷新',self)
		btn.clicked.connect(self.flush_event)
		layout_date=QHBoxLayout()
		layout_date.addWidget(btn_export)
		layout_date.addStretch(1)
		layout_date.addWidget(self.comb_type)
		layout_date.addStretch(1)
		layout_date.addWidget(label_date_start)
		layout_date.addWidget(self.date_edit_start)
		if not self.managerlimit.get_limit('输出文件'):
			btn_export.setEnabled(False)
		if self.managerlimit.get_limit('免责声明'):
			layout_date.addStretch(1)
			label_exemption=QLabel('数据未经审核,仅供参考！',self)
			layout_date.addWidget(label_exemption)
		layout_date.addStretch(1)

		check_filter=QCheckBox('筛选',self)
		check_filter.setCheckState(0)
		check_filter.stateChanged.connect(self.check_filter_event)

		layout_date.addWidget(label_date_end)
		layout_date.addWidget(self.date_edit_end)
		layout_date.addStretch(1)
		layout_date.addWidget(check_filter)
		layout_date.addStretch(1)
		layout_date.addWidget(btn)
		groupbox_date=QGroupBox('维修日期范围',self)
		groupbox_date.setLayout(layout_date)
		
		self.table=QTableWidget(0,30,self)
		self.table.setHorizontalHeaderLabels(self.table_columns)
		self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

		action_flow_detail_product=QAction('该机流转信息',self)
		action_flow_detail_product.triggered.connect(self.flow_detail_product)
		self.table.addAction(action_flow_detail_product)


		action_flow_detail_project=QAction('该计划流转信息',self)
		action_flow_detail_project.triggered.connect(self.flow_detail_project)
		self.table.addAction(action_flow_detail_project)

		self.table.setContextMenuPolicy(Qt.ActionsContextMenu)
		# self.table.setSelectionBehavior(QAbstractItemView.SelectRows)

		# self.table.horizontalHeader().sectionClicked.connect(self.headerclicked)
		self.table.setAlternatingRowColors(True)
		# self.table.setStyleSheet("background-color:rgb(255, 170, 255);")
		self.table.setStyleSheet("alternate-background-color:rgb(200, 255, 255);")

		# self.tjtable=QTableWidget(2,10,self)

		# splitter=QSplitter(Qt.Vertical,self)
		# splitter.addWidget(self.table)
		# splitter.addWidget(self.tjtable)


		layout=QVBoxLayout()
		layout.addWidget(groupbox_date)

		# layout.addWidget(self.table)
		# layout.addWidget(self.tjtable)
		# layout.addWidget(splitter)

		# layout.addStretch(1)
		layout.addWidget(self.table)
		self.setLayout(layout)
		self.show()

	def export_event(self):
		if self.table.rowCount()==0:
			return
		li_df=[]
		for i in range(self.table.rowCount()):
			li_temp=[]
			for j in range(self.table.columnCount()):
				li_temp.append(self.table.item(i,j).text())
			li_df.append(li_temp)
		df=pd.DataFrame(li_df,columns=self.columns)

		filename=QFileDialog.getSaveFileName(self,'存储为','D:/维修明细数据统计','xlsx')


		if filename[0]=='':
			return
		writer = ExcelWriter(filename[0]+'.'+filename[1])
		df.to_excel(writer,sheet_name='维修记录')
		self.df_pivot.to_excel(writer,sheet_name='数据统计')
		self.df_pivot1.to_excel(writer,sheet_name='数据统计1')

		writer.save()


	def flow_detail_product(self):
		table_type=self.table.item(self.table.currentRow(),29).text()
		if table_type=='金融':
			table_name='note_jr'
		if table_type=='移动':
			table_name='note_yd'

		s=self.table.item(self.table.currentRow(),10).text()
		s=s.replace(' ','')
		if s=='' or s=='None':
			return
		self.winflowdetailproduct=WinFlowDetail(table_name,s,'产品编码',self.cur,self.conn)

	def flow_detail_project(self):
		table_type=self.table.item(self.table.currentRow(),29).text()
		if table_type=='金融':
			table_name='note_jr'
		if table_type=='移动':
			table_name='note_yd'

		s=self.table.item(self.table.currentRow(),6).text()
		s=s.replace(' ','')
		if s=='' or s=='None':
			return
		self.winflowdetailproduct=WinFlowDetail(table_name,s,'计划号',self.cur,self.conn)


	def flush_event(self):
	
		# try:

		print('disconnect OK')
		s1=self.date_edit_start.date().toString("yyyy-MM-dd")
		s2=self.date_edit_end.date().addDays(1).toString("yyyy-MM-dd")

		if self.comb_type.currentText()=='金融':

			self.cur.execute('select id,line_num,product_class,main_model,serial_num,batch_num,project_num,produce_date,\
				process_state,single_board_name,product_id,fault_num,fault_name,fault_class2,note_person,note_date,material_name,\
				service_result,service_person,second_service,service_date,work_hours,comment,parse_class,\
				process_control,parse_person,fail_correct,cause_parse,u.user_type,partment \
				from '+'note_jr'+' innor join user_sc_C as u on service_person=u.name where service_date >= %s and service_date < %s or service_date is Null',(s1,s2))
		elif self.comb_type.currentText()=='移动':
			self.cur.execute('select id,line_num,product_class,main_model,serial_num,batch_num,project_num,produce_date,\
				process_state,single_board_name,product_id,fault_num,fault_name,fault_class2,note_person,note_date,material_name,\
				service_result,service_person,second_service,service_date,work_hours,comment,parse_class,\
				process_control,parse_person,fail_correct,cause_parse,u.user_type,partment \
				from '+'note_yd'+' innor join user_sc_C as u on service_person=u.name where service_date >= %s and service_date < %s or service_date is Null',(s1,s2))
		else:
			self.cur.execute('select id,line_num,product_class,main_model,serial_num,batch_num,project_num,produce_date,\
				process_state,single_board_name,product_id,fault_num,fault_name,fault_class2,note_person,note_date,material_name,\
				service_result,service_person,second_service,service_date,work_hours,comment,parse_class,\
				process_control,parse_person,fail_correct,cause_parse,u.user_type,partment \
				from '+'note_jr'+' innor join user_sc_C as u on service_person=u.name where service_date >= %s and service_date < %s or service_date is Null union '+\
				'select id,line_num,product_class,main_model,serial_num,batch_num,project_num,produce_date,\
				process_state,single_board_name,product_id,fault_num,fault_name,fault_class2,note_person,note_date,material_name,\
				service_result,service_person,second_service,service_date,work_hours,comment,parse_class,\
				process_control,parse_person,fail_correct,cause_parse,u.user_type,partment \
				from '+'note_yd'+' innor join user_sc_C as u on service_person=u.name where service_date >= %s and service_date < %s or service_date is Null',(s1,s2,s1,s2))

		li=self.cur.fetchall()
		self.conn.commit()
		if len(li)==0:
			return

		

		cloumns=list(map(str,list(range(30))))
		try:
			df=pd.DataFrame(np.array(li),columns=cloumns)
		except:
			return
		df['21']=(df['21']/60)
		df['21']=df['21'].apply(round,args=(3,))
		print(df)

		li=df.values
		self.table.setRowCount(len(li))

		li_row=0
		for i in li:
			li_cloumn=0
			for j in i:
				self.table.setItem(li_row,li_cloumn,QTableWidgetItem(str(j)))
				li_cloumn+=1
			li_row+=1

		self.create_df()
		self.create_dic()

		self.update_pivot(self.df.copy())
		
	def check_filter_event(self,state):
		if state==0:
			self.table.horizontalHeader().sectionClicked.disconnect(self.headerclicked)
			self.flush_event()
		if state==2:
			self.table.horizontalHeader().sectionClicked.connect(self.headerclicked)

	def create_df(self):
		len_row=self.table.rowCount()
		len_column=self.table.columnCount()
		li_data=[]
		for i in range(len_row):
			li_temp=[]
			for j in range(len_column):
				li_temp.append(self.table.item(i,j).text())
			li_data.append(li_temp)

		self.df=pd.DataFrame(li_data,columns=self.columns)
		# print(self.df)

	def create_dic(self):
		self.df['工时']=self.df['工时'].apply(str)
		for i in self.columns:
			dic_temp={}
			li=self.df[i].drop_duplicates().tolist()
			for j in li:
				dic_temp[j]=1
			self.dic[i]=dic_temp
		print('dic>>>>>',self.dic)


	def headerclicked(self,index):
		self.winselectfilter=WinSelectFilter(self.df,self.columns,index,self.dic,self.table,self)

	# def headerclicked(self,a):
	# 	if self.dfa is None:
	# 		return
	# 	self.win_select=win_select(a,self.dfa,self.dic)

	def update_pivot(self,df_temp):
		df_temp['工时']=df_temp['工时'].apply(float)
		self.pivot_view.table.setRowCount(0)
		self.pivot_view.table.setColumnCount(0)
		self.df_pivot=pd.pivot_table(df_temp,index=['事业部','计划ID','人员分类'],values='工时',columns=['分类'],aggfunc=[len,np.sum],margins=True)
		formatter = fmt.ExcelFormatter(self.df_pivot)
		formatted_cells = formatter.get_formatted_cells()
		li=[]
		for i in formatted_cells:
			li.append(i)
		self.pivot_view.table.setRowCount(self.df_pivot.shape[0]+1)
		self.pivot_view.table.setColumnCount(self.df_pivot.shape[1]+3)
		for i in li:
			self.pivot_view.table.setItem(i.row,i.col,QTableWidgetItem(str(i.val)))
			print(i.row,i.col,i.val)

		self.pivot_view1.table.setRowCount(0)
		self.pivot_view1.table.setColumnCount(0)
		self.df_pivot1=pd.pivot_table(df_temp,index=['维修人','事业部'],values='工时',columns=['分类'],aggfunc=[len,np.sum],margins=True)
		formatter = fmt.ExcelFormatter(self.df_pivot1)
		formatted_cells = formatter.get_formatted_cells()
		li=[]
		for i in formatted_cells:
			li.append(i)
		self.pivot_view1.table.setRowCount(self.df_pivot1.shape[0]+1)
		self.pivot_view1.table.setColumnCount(self.df_pivot1.shape[1]+2)
		for i in li:
			self.pivot_view1.table.setItem(i.row,i.col,QTableWidgetItem(str(i.val)))
			print(i.row,i.col,i.val)


class WinSelectFilter(QWidget):

	def __init__(self,df,columns,column,dic,table,father):
		super().__init__()
		self.df=df
		self.columns=columns
		self.column=column
		self.dic=dic
		self.table=table
		self.father=father
		self.li_checkbox=[]

		layout=QVBoxLayout()

		self.check_all=QCheckBox('全选',self)
		self.check_all.setCheckState(2)
		self.check_all.setTristate(False)
		self.check_all.stateChanged.connect(self.statechanged_all)
		self.check_all.clicked.connect(self.clicked_all)
		self.btn_commit=QPushButton('确定',self)
		self.btn_commit.clicked.connect(self.commit_event)
		layout.addWidget(self.check_all)

		li_item=self.filter_data_temp()[self.columns[self.column]].drop_duplicates().tolist()
		len_off=0
		len_on=0
		len_li=len(li_item)
		li_item.sort()
		for i in li_item:
			c=QCheckBox(str(i),self)
			if self.dic[self.columns[self.column]][i]==1:
				c.setCheckState(2)
				len_on+=1
			if self.dic[self.columns[self.column]][i]==0:
				c.setCheckState(0)
				len_off+=1
			self.li_checkbox.append(c)
			c.stateChanged.connect(self.statechanged)
			layout.addWidget(c)

		if len_off==len_li:
			self.check_all.setCheckState(0)
		if len_on==len_li:
			self.check_all.setCheckState(2)
		if len_on<len_li and len_off<len_li:
			self.check_all.setCheckState(1)
	
		widget=QWidget(self)
		widget.setLayout(layout)
		# widget.setMinimumHeight(600)
		scroll=QScrollArea(self)
		scroll.setWidget(widget)
		# scroll.setMaximumHeight(600)
		layout_scroll=QVBoxLayout()
		layout_scroll.addWidget(scroll)
		layout_scroll.addWidget(self.btn_commit,alignment=Qt.AlignCenter)
		self.setLayout(layout_scroll)
		self.show()

	def clicked_all(self):
		sender = self.sender()
		if sender.checkState()==1:
			sender.setCheckState(2)

	def statechanged_all(self,state):
		print(self.check_all.isTristate())
		if state==2:
			self.btn_commit.setEnabled(True)
			for i in self.li_checkbox:
				i.setCheckState(2)
		if state==0:
			self.btn_commit.setEnabled(False)
			for i in self.li_checkbox:
				i.setCheckState(0)
		if state==1:
			self.btn_commit.setEnabled(True)

	def statechanged(self,state):
		sender = self.sender()
		print(sender.text())
		# if sender.checkState==2:
		# 	self.dic[self.columns[column]][sender.text()]=1
		# if sender.checkState==0:
		# 	self.dic[self.columns[column]][sender.text()]=0
		len_li=len(self.li_checkbox)
		len_off=0
		len_on=0
		for i in self.li_checkbox:
			if i.checkState()==2:
				len_on+=1
			if i.checkState()==0:
				len_off+=1
		if len_off==len_li:
			self.check_all.setCheckState(0)
		if len_on==len_li:
			self.check_all.setCheckState(2)
		if len_on<len_li and len_off<len_li:
			self.check_all.setCheckState(1)
		print('KKKKKKKKKKKKK')
		print(len_li)
		print(len_off)
		print(len_on)

		

	def commit_event(self):
		if self.check_all.checkState()==2:
			for i in self.dic[self.columns[self.column]].keys():
				self.dic[self.columns[self.column]][i]=1
		if self.check_all.checkState()==1:
			for i in self.li_checkbox:
				if i.checkState()==2:
					self.dic[self.columns[self.column]][i.text()]=1
				if i.checkState()==0:
					self.dic[self.columns[self.column]][i.text()]=0
			print('diccccccccc',self.dic[self.columns[self.column]])
		self.filter_data()

		self.close()



	def filter_data_temp(self):
		li=self.columns.copy()
		li.pop(self.column)
		df=self.filter_base(li)
		return df

	def filter_data(self):
		df=self.filter_base(self.columns.copy())
		li=df.values
		self.table.setRowCount(0)
		self.table.setRowCount(len(li))
		rowcount=0
		for i in li:
			columncount=0
			for j in i:
				self.table.setItem(rowcount,columncount,QTableWidgetItem(str(j)))
				columncount+=1
			rowcount+=1
		self.father.update_pivot(df.copy())

	def filter_base(self,li_column):
		print(li_column)
		df_judge=self.df['ID']!='S'
		for i in li_column:
			li_temp=[]
			dic_temp=self.dic[i]
			for j in dic_temp.keys():
				if dic_temp[j]==1:
					li_temp.append(j)
			df_judge=self.df[i].isin(li_temp)&df_judge
		df=self.df[df_judge]
		return df


class PivotView(QWidget):
	def __init__(self):
		super().__init__()
		self.initUI()

	def initUI(self):


		self.table=QTableWidget(0,0,self)


		vlayout=QVBoxLayout(self)

		vlayout.addWidget(self.table)
		self.setLayout(vlayout)
		self.show()

class PivotView1(QWidget):
	def __init__(self):
		super().__init__()
		self.initUI()

	def initUI(self):


		self.table=QTableWidget(0,0,self)


		vlayout=QVBoxLayout(self)

		vlayout.addWidget(self.table)
		self.setLayout(vlayout)
		self.show()