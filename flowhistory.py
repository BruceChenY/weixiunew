from PyQt5.QtWidgets import *

'''
详细流转信息界面
'''
class WinFlowDetail(QWidget):
	def __init__(self,tablename,condition,query_type,cur,conn):
		super().__init__()
		self.tablename=tablename
		self.condition=condition
		self.query_type=query_type
		self.cur=cur
		self.conn=conn
		self.initUI()

	def initUI(self):
		self.table_columns=['主型号','系列号','批次','计划ID',\
			'临时产品编码','不良现象','记录人','不良原因','维修人',\
			'维修接收时间','维修接收人','产线接收时间','产线接收人']
		self.table=QTableWidget(0,13,self)
		self.table.setHorizontalHeaderLabels(self.table_columns)
		vlayout=QVBoxLayout(self)
		vlayout.addWidget(self.table)
		self.setLayout(vlayout)
		self.setWindowTitle('流转信息表')
		self.show()
		self.query_event()

	def query_event(self):
		if self.query_type=='计划号':
			self.cur.execute("select main_model,serial_num,batch_num,project_num,product_id,fault_name,note_person,service_result,\
				service_person,in_time,in_person,out_time,out_person from "+self.tablename+" where project_num=%s",(self.condition))
		elif self.query_type=='产品编码':
			self.cur.execute("select main_model,serial_num,batch_num,project_num,product_id,fault_name,note_person,service_result,\
				service_person,in_time,in_person,out_time,out_person from "+self.tablename+" where product_id=%s",(self.condition))
		else:
			pass
		li=self.cur.fetchall()
		self.conn.commit()
		self.table.setRowCount(len(li))
		rowcount=0
		for i in li:
			columncount=0
			for j in i:
				self.table.setItem(rowcount,columncount,QTableWidgetItem(str(j)))
				columncount+=1
			rowcount+=1
			