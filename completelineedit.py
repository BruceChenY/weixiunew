from PyQt5.QtWidgets import *
from PyQt5.QtCore import QStringListModel,Qt,QDate,QPoint
from PyQt5 import QtGui
from PyQt5.QtGui import *
import sys
import jieba

class CompleteLineEdit(QLineEdit):
	def __init__(self,parent):
		super().__init__(parent)
		print('super type000',type(super()))
		
		self.listView = QListView(self)
		self.listView.setWindowFlags(Qt.ToolTip)
		self.listView.setFocus()
		self.model=QStringListModel(self)
		self.textChanged.connect(self.setCompleter)
		self.listView.clicked.connect(self.completeText)
	def setModel(self,li_model):
		self.li_model=li_model

	def setText(self,text):
		QLineEdit.setText(self,text)
		if not self.listView.isHidden():
			self.listView.hide()

	def focusOutEvent(self,e):
		if (not self.listView.isHidden()) and (not self.listView.hasFocus()):
			self.listView.hide()
		QLineEdit.focusOutEvent(self,e)

	def keyPressEvent(self,e):
		if (not self.listView.isHidden()):
			key = e.key()
			count = self.listView.model().rowCount();
			currentIndex = self.listView.currentIndex();

			if (Qt.Key_Down == key):
			# 按向下方向键时，移动光标选中下一个完成列表中的项
				row = currentIndex.row() + 1
				if (row >= count):
					row = 0
				index = self.listView.model().index(row, 0)
				self.listView.setCurrentIndex(index)
			elif (Qt.Key_Up == key):
				# 按向下方向键时，移动光标选中上一个完成列表中的项
				row = currentIndex.row() - 1
				if (row < 0):
					row = count - 1
				index = self.listView.model().index(row, 0);
				self.listView.setCurrentIndex(index)
			elif (Qt.Key_Escape == key):
				# 按下Esc键时，隐藏完成列表
				self.listView.hide()
			elif (Qt.Key_Enter == key or Qt.Key_Return == key):
				# 按下回车键时，使用完成列表中选中的项，并隐藏完成列表
				if (currentIndex.isValid()):
					text = self.listView.currentIndex().data()
					self.setText(text)

				self.listView.hide()
			else:
				# 其他情况，隐藏完成列表，并使用QLineEdit的键盘按下事件
				self.listView.hide()
				QLineEdit.keyPressEvent(self,e)

		else:
			QLineEdit.keyPressEvent(self,e)
			print('super type',type(super()))



	def setCompleter(self,text):
		print(text)
		if text.replace(' ','')=='':
			self.listView.hide()
			return


		# if ((len(text) > 1) and (not self.listView.isHidden())):
		# 	return

		# 如果完整的完成列表中的某个单词包含输入的文本，则加入要显示的完成列表串中
	
		

		# li=[]
		# for i in self.li_model:
		# 	if text in i:
		# 		li.append(i)
		text=text.upper()
		li=[]
		flag=True
		seg_list=jieba.cut(text)
		seg_list=list(seg_list)
		for i in self.li_model:
			for j in seg_list:
				if j==' ':
					continue
				if j not in i:
					flag=False
					break
			if flag:
				li.append(i)
				print(i)
			else:
				flag=True

		self.model.setStringList(li)
		self.listView.setModel(self.model)

		if (self.model.rowCount() == 0):
			return


		# Position the text edit
		self.listView.setMinimumWidth(self.width())
		self.listView.setMaximumWidth(self.width())
		p=QPoint(0,self.height())

		x = self.mapToGlobal(p).x()
		y = self.mapToGlobal(p).y() + 1

		self.listView.move(x, y)
		self.listView.show()


	def completeText(self,index):
		# print('index type',type(index))
		# print('dic index',dir(index))
		text = index.data()
		self.setText(text)
		self.listView.hide()

if __name__=='__main__':
	app=QApplication(sys.argv)
	w=QWidget()

	com=CompleteLineEdit(w)
	com.setModel(['123','456','中文','文章','更换'])
	vlayout=QVBoxLayout(w)
	vlayout.addWidget(com)
	w.setLayout(vlayout)
	w.show()
	sys.exit(app.exec_())