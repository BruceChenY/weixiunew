from PyQt5.QtWidgets import *
from PyQt5.QtCore import QStringListModel,Qt,QDate,QPoint
from PyQt5 import QtGui
import pymysql
import numpy as np
import pandas as pd
import sys
import datetime
import re
from flowhistory import WinFlowDetail
from pandas.io.excel import ExcelWriter

class WinDataProcess(QWidget):
	def __init__(self,cur,conn,managerlimit,sql_table_name):
		
		super().__init__()
		self.df=None
		self.dic={}
		self.cur=cur
		self.conn=conn
		self.managerlimit=managerlimit
		self.sql_table_name=sql_table_name
		self.li_sqlcolumn=['id','line_num','product_class','main_model','serial_num','batch_num','project_num','produce_date',\
				'process_state','single_board_name','product_id','fault_num','fault_name','fault_class2','note_person','note_date','material_name',\
				'service_result','service_person','second_service','service_date','work_hours','comment','parse_class',\
				'process_control','parse_person','fail_correct','cause_parse']
		self.table_columns=['ID','线别','分类','主型号','系列号','批次','计划ID','生产日期',\
			'制程状态','单板名称','临时产品编码','故障代码','不良现象','故障分类','记录人','记录日期','维修结果',\
			'不良原因','维修人','维修次数','维修日期','工时','备注','分析分类','控制制程','分析人','分析错误纠正','错误原因']
		self.columns=['ID','线别','分类','主型号','系列号','批次','计划ID','生产日期',\
			'制程状态','单板名称','临时产品编码','故障代码','不良现象','故障分类','记录人','记录日期','维修结果',\
			'不良原因','维修人','维修次数','维修日期','工时','备注','分析分类','控制制程','分析人','分析错误纠正','错误原因']
		self.initUI()

	def initUI(self):
		btn_export=QPushButton('导出excel')
		btn_export.clicked.connect(self.export_event)
		label_date_start=QLabel('开始日期(含)',self)
		label_date_end=QLabel('结束日期(含)',self)
		self.date_edit_start=QDateEdit(QDate.currentDate(),self)
		self.date_edit_end=QDateEdit(QDate.currentDate(),self)
		btn=QPushButton('刷新',self)
		btn.clicked.connect(self.flush_event)
		layout_date=QHBoxLayout()
		layout_date.addWidget(btn_export)
		layout_date.addStretch(1)
		layout_date.addWidget(label_date_start)

		layout_date.addWidget(self.date_edit_start)

		layout_date.addStretch(1)
		layout_date.addWidget(label_date_end)
		layout_date.addWidget(self.date_edit_end)

		check_filter=QCheckBox('筛选',self)
		check_filter.setCheckState(0)
		check_filter.stateChanged.connect(self.check_filter_event)

		layout_date.addStretch(1)
		layout_date.addWidget(check_filter)
		layout_date.addStretch(1)

		btn_fault_count=QPushButton('故障现象统计',self)
		btn_fault_count.clicked.connect(self.fault_count_event)
		layout_date.addWidget(btn_fault_count)
		layout_date.addStretch(1)
		layout_date.addWidget(btn)
		groupbox_date=QGroupBox('维修日期范围',self)
		groupbox_date.setLayout(layout_date)
		if not self.managerlimit.get_limit('输出文件'):
			btn_export.setEnabled(False)
		

		self.table=QTableWidget(0,28,self)
		self.table.setHorizontalHeaderLabels(self.table_columns)
		self.table.setAlternatingRowColors(True)
		# self.table.setStyleSheet("background-color:rgb(255, 170, 255);")
		self.table.setStyleSheet("alternate-background-color:rgb(200, 255, 255);")
		self.table.cellDoubleClicked.connect(self.cellDoubleClicked)

		self.table.itemChanged.connect(self.item_changed)
		# self.table.setSelectionBehavior(QAbstractItemView.SelectRows)

		# self.table.horizontalHeader().sectionClicked.connect(self.headerclicked)

		action_delete=QAction('删除',self)
		action_delete.triggered.connect(self.delete_record)
		self.table.addAction(action_delete)
		self.table.setContextMenuPolicy(Qt.ActionsContextMenu)

		action_flow_detail_product=QAction('该机流转信息',self)
		action_flow_detail_product.triggered.connect(self.flow_detail_product)
		self.table.addAction(action_flow_detail_product)


		action_flow_detail_project=QAction('该计划流转信息',self)
		action_flow_detail_project.triggered.connect(self.flow_detail_project)
		self.table.addAction(action_flow_detail_project)

		self.table.setContextMenuPolicy(Qt.ActionsContextMenu)


		# self.tjtable=QTableWidget(2,10,self)
		# splitter=QSplitter(Qt.Vertical,self)
		# splitter.addWidget(self.table)
		# splitter.addWidget(self.tjtable)


		layout=QVBoxLayout()
		layout.addWidget(groupbox_date)
		# layout.addWidget(self.table)
		# layout.addWidget(self.tjtable)
		layout.addWidget(self.table)

		# layout.addStretch(1)
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

		filename=QFileDialog.getSaveFileName(self,'存储为','D:/维修记录','xlsx')

		if filename[0]=='':
			return
		writer = ExcelWriter(filename[0]+'.'+filename[1])
		df.to_excel(writer,sheet_name='维修记录')
		writer.save()


	def fault_count_event(self):
		if self.table.rowCount()==0:
			return
		li=[]

		for i in range(self.table.rowCount()):
			if self.table.item(i,12).text()=='None':
				continue
			li_temp=[]
			li_temp.append(self.table.item(i,3).text())
			li_temp.append(self.table.item(i,12).text())
			li.append(li_temp)
		if len(li)==0:
			return
		self.win_fault_count=WinFaultCount(li)



	def update_table(self,li):
		self.table.itemChanged.disconnect(self.item_changed)
		self.table.setRowCount(0)
		self.table.setRowCount(len(li))
		rowcount=0
		for i in li:
			columncount=0
			for j in i:
				self.table.setItem(rowcount,columncount,QTableWidgetItem(str(j)))
				columncount+=1
			rowcount+=1

		self.table.itemChanged.connect(self.item_changed)


	def flow_detail_product(self):
		s=self.table.item(self.table.currentRow(),10).text()
		s=s.replace(' ','')
		if s=='' or s=='None':
			return
		self.winflowdetailproduct=WinFlowDetail(self.sql_table_name,s,'产品编码',self.cur,self.conn)

	def flow_detail_project(self):
		s=self.table.item(self.table.currentRow(),6).text()
		s=s.replace(' ','')
		if s=='' or s=='None':
			return
		self.winflowdetailproduct=WinFlowDetail(self.sql_table_name,s,'计划号',self.cur,self.conn)

	def delete_record(self):
		if not self.managerlimit.get_limit('登记'):
			QMessageBox(text='   无删除权限！  ',parent=self).show()
			return
		if self.managerlimit.get_limit('产线登记'):		
			self.cur.execute("select note_person,service_person,service_result,state from "+self.sql_table_name+" where \
				id=%s",(self.table.item(self.table.currentRow(),0).text()))
			li=self.cur.fetchall()[0]
			if li[3] != '待修':
				QMessageBox(text='   已转出，不可删除！  ',parent=self).show()
				return
			if self.managerlimit.get_name()==li[0]:
				self.cur.execute("delete from "+self.sql_table_name+" where id=%s",(self.table.item(self.table.currentRow(),0).text()))
				self.table.removeRow(self.table.currentRow())
				self.conn.commit()
			else:
				QMessageBox(text='   不可删除！  ',parent=self).show()
				return
		else:
			if not self.managerlimit.get_limit('删除记录'):
				QMessageBox(text='   无权限，不可删除！  ',parent=self).show()
				return
			self.cur.execute("delete from "+self.sql_table_name+" where id=%s",(self.table.item(self.table.currentRow(),0).text()))
			self.table.removeRow(self.table.currentRow())		
			self.conn.commit()

	def item_changed(self,item):
		self.cur.execute('update '+self.sql_table_name+' set '+self.li_sqlcolumn[item.column()]+'='+'%s where id=%s',(item.text(),self.table.item(item.row(),0).text()))
		self.conn.commit()
		# self.btn_event_updfa()
		print('changed OK')

	def cellDoubleClicked(self,row,column):
		print('cellDoubleClicked')

		if not self.managerlimit.get_limit('登记'):
			QMessageBox(text='   无修改权限！  ',parent=self).show()
			return

		if column==0 or column==18:
			QMessageBox(text='   该列不可编辑！  ',parent=self).show()
			return

		self.cur.execute("select note_person,service_person,service_result,state from "+self.sql_table_name+" where \
			id=%s",(self.table.item(self.table.currentRow(),0).text()))
		li=self.cur.fetchall()[0]
		self.conn.commit()
		if self.managerlimit.get_limit('产线登记'):
			if self.managerlimit.get_name() != li[0]:
				QMessageBox(text='   无修改权限！  ',parent=self).show()
				return
			if li[3]!='待修':
				QMessageBox(text='   已转出，不可修改！  ',parent=self).show()
				return

		else:
			if li[3]=='待修':
				QMessageBox(text='   未转入，不可修改！  ',parent=self).show()
				return
			if self.managerlimit.get_name() != li[1]:
				if not self.managerlimit.get_limit('修改数据'):
					QMessageBox(text='   无修改权限！  ',parent=self).show()
					return


	def flush_event(self):
	
		s1=self.date_edit_start.date().toString("yyyy-MM-dd")
		s2=self.date_edit_end.date().addDays(1).toString("yyyy-MM-dd")

		self.cur.execute('select id,line_num,product_class,main_model,serial_num,batch_num,project_num,produce_date,\
			process_state,single_board_name,product_id,fault_num,fault_name,fault_class2,note_person,note_date,material_name,\
			service_result,service_person,second_service,service_date,work_hours,comment,parse_class,\
			process_control,parse_person,fail_correct,cause_parse \
			from '+self.sql_table_name+' where service_date >= %s and service_date < %s or service_date is Null',(s1,s2))

		li=self.cur.fetchall()
		self.conn.commit()


		self.update_table(li)


		self.create_df()
		self.create_dic()

	# def btn_event_updfa(self):
	# 	try:
	# 		s1=self.date_edit_start.date().toString("yyyy-MM-dd")
	# 		s2=self.date_edit_end.date().addDays(1).toString("yyyy-MM-dd")
	# 		print(s1,s2)
	# 		# try:
	# 		self.cur.execute('select id,line_num,product_class,main_model,serial_num,batch_num,project_num,produce_date,\
	# 			process_state,single_board_name,product_id,fault_num,fault_name,fault_class2,note_person,note_date,material_name,\
	# 			service_result,service_person,second_service,service_date,work_hours,comment,parse_class,\
	# 			process_control,parse_person,fail_correct,cause_parse \
	# 			from '+self.sql_table_name+' where service_date >= %s and service_date < %s or service_date is Null',(s1,s2))
				
	# 		li=self.cur.fetchall()
	# 		# print(li)
	# 		li_row=0
	# 		cloumns=list(map(str,list(range(28))))
	# 		self.dfa=pd.DataFrame(np.array(li),columns=cloumns)
	# 	except:
	# 		pass


	def headerclicked(self,index):
		self.winselectfilter=WinSelectFilter(self.df,self.columns,index,self.dic,self.table,self)

	# def headerclicked(self,a):
	# 	print(self)
	# 	print('headerclicked',a)
	# 	if self.dfa is None:
	# 		return
	# 	self.win_select=win_select(a,self.dfa,self.dic)
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

class WinFaultCount(QWidget):
	def __init__(self,li):
		super().__init__()
		self.li=li
		self.initUI()
	def initUI(self):
		self.table=QTableWidget(0,3,self)
		self.table.setHorizontalHeaderLabels(['型号','故障现象','数量'])
		vlayout=QVBoxLayout(self)
		vlayout.addWidget(self.table)
		self.setLayout(vlayout)
		self.show()
		self.data_count()
	def data_count(self):
		df=pd.DataFrame(np.array(self.li),columns=['A','B'])
		li_line=df['A'].drop_duplicates().tolist()
		for i in li_line:
			li_id=df[df['A']==i]['B'].drop_duplicates().tolist()
			df_temp=df[df['A']==i]
			for j in li_id:
				df_count=df_temp[df_temp['B']==j]
				count=df_count.shape[0]
				self.table.setRowCount(self.table.rowCount()+1)
				self.table.setItem(self.table.rowCount()-1,0,QTableWidgetItem(i))
				self.table.setItem(self.table.rowCount()-1,1,QTableWidgetItem(j))
				self.table.setItem(self.table.rowCount()-1,2,QTableWidgetItem(str(count)))

class WinSelectFilter(QWidget):
	def __init__(self,df,columns,column,dic,table,father):
		super().__init__()
		'''columns为表头列表，column为所选表头列int，dic为全局选择字典，table为所筛选的表格'''
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
		self.btn_commit=QPushButton('确定',self)
		self.check_all.clicked.connect(self.clicked_all)
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


	'''单击全选触发事件'''
	def clicked_all(self):
		sender = self.sender()
		if sender.checkState()==1:
			sender.setCheckState(2)

	'''单击全选后全选框的状态将改变所有选框的状态，并计算确定按钮是否可用'''
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

	'''单个选择框状态的改变将会改变全局字典，并计算全选框的状态'''
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
		'''循环检查全部单选框状态，计算全选框的状态'''
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


	'''确定按钮事件，根据单选框的状态修改全局dic的值'''
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
		self.father.update_table(li)

	'''过滤算法，先算出numpy列表（布尔值），再根据numpy算出df'''
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