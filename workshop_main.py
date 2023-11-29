import sys
from workshop_interface import *
from PyQt5 import QtCore, QtGui, QtWidgets, QtSql
from PyQt5.QtWidgets import QSizePolicy, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, QDate
from datetime import date
import DB_work
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigToolBar

class MplCanvas(FigureCanvas):
    def __init__(self, fig, parent=None):
        self.fig = fig
        FigureCanvas.__init__(self, self.fig)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

class MyWin(QtWidgets.QMainWindow):
    def __init__(self, parent = None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Список для хранения услуг
        self.name_of_services = []
        # Переменная, хранящая выборку из таблицы services БД workshop.db
        select = DB_work.select_all('workshop.db', 'services')
        # Добавление названия услуг в список

        for names in select:
            self.name_of_services.append(names[1])

        # Добавление списка услуг в combobox
        self.ui.comboBox.addItems(self.name_of_services)

        # Переключение между вкладками с помощью кнопок навигации
        self.ui.pushButton.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(0))
        self.ui.pushButton_2.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(1))
        self.ui.pushButton_3.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(2))
        
        # Подключение функций к пунктам меню
        self.ui.action_4.triggered.connect(lambda:self.close())
        self.ui.action_2.triggered.connect(self.open)
        self.ui.action.triggered.connect(self.draw_chart)

        # Установка иконок к кнопкам навигации
        self.ui.pushButton.setIcon(QIcon('Icons\\home2.png'))
        self.ui.pushButton.setIconSize(QSize(35, 35))
        self.ui.pushButton_2.setIcon(QIcon('Icons\\shopping_cart.png'))
        self.ui.pushButton_2.setIconSize(QSize(35, 35))
        self.ui.pushButton_3.setIcon(QIcon('Icons\\pie_chart.png'))
        self.ui.pushButton_3.setIconSize(QSize(35, 35))

        # Установка минимальной даты для выбора (устанавливает текущую дату)
        self.ui.dateEdit.setMinimumDate(QDate(date.today()))
        # Подключение функции к combobox'у
        self.ui.comboBox.currentIndexChanged.connect(self.cbb_changed)
        # Подключение функции к кнопке оформления заказа
        self.ui.pushButton_4.clicked.connect(self.place_order)


    # Функция, срабатывающая при изменении значения в combobox'е
    def cbb_changed(self):
        self.ui.amount_lbl.setText('')
        # Выборка из базы данных
        db_select = DB_work.select_name_n_price(self.ui.comboBox.itemText(self.ui.comboBox.currentIndex()))
        nes_detail = db_select[0][2]
        detail_amount = DB_work.select_detail_count(nes_detail)
        if detail_amount == 0:
           self.ui.amount_lbl.setText(f"Количество товара на складе: {detail_amount}")
            
        # Установка текста(название услуги + цена)
        self.ui.service_lbl.setText(f'{db_select[0][0]}         {db_select[0][1]}')
        # Установка текста(название детали + цена)
        self.ui.good_lbl.setText(f'{db_select[0][2]}            {db_select[0][3]}')
        # Установка текста итоговой цены
        self.ui.label_6.setText(f'{db_select[0][1] + db_select[0][3]}')

    def place_order(self):
        try:
            surname_value = self.ui.lineEdit.text()
            if surname_value.isalpha():
                db_select = DB_work.select_name_n_price(self.ui.comboBox.itemText(self.ui.comboBox.currentIndex()))
                nes_detail = db_select[0][2]
                detail_amount = DB_work.select_detail_count(nes_detail)
                if detail_amount == 0:
                    surname = self.ui.lineEdit.text()
                    service = self.ui.comboBox.itemText(self.ui.comboBox.currentIndex())
                    date = self.ui.dateEdit.date()
                    total = self.ui.label_6.text()
                    return
                
                DB_work.add_data(surname, service, date.toPyDate(), total)
                DB_work.update_data(nes_detail)

            else:
                self.ui.lineEdit.clear()
                self.warning = QMessageBox.warning(self, 'Ошибка', "Фамилия должна содержать только буквы", QMessageBox.Ok)
                
                
        
        except:
            self.warning = QMessageBox.warning(self, 'Ошибка', "Возникла непредвиденная ошибка", QMessageBox.Ok)

    def closeEvent(self, event):
        if self.warning == QMessageBox.Ok:
            event.accept()
        
        

    def open(self):
        try:
            con = QtSql.QSqlDatabase.addDatabase('QSQLITE')
            con.setDatabaseName('workshop.db')
            con.open()

            stm = QtSql.QSqlTableModel()
            stm.setTable('consumers')
            stm.select()

            stm.setHeaderData(1, QtCore.Qt.Horizontal, 'Фамилия')
            stm.setHeaderData(2, QtCore.Qt.Horizontal, 'Услуга')
            stm.setHeaderData(4, QtCore.Qt.Horizontal, 'Дата')
            stm.setHeaderData(3, QtCore.Qt.Horizontal, 'Итог')

            self.ui.tableWidget.setModel(stm)

            self.ui.total_lbl.setText(f'Суммарная стоимость всех оказанных услуг: {DB_work.total_sum()}')
        except:
            self.warning = QMessageBox.warning(self, 'Ошибка', "Возникла ошибка. Возможно таблица базы данных пустая", QMessageBox.Ok)

    def draw_chart(self):
        res = DB_work.chart()
        x = []
        y = []
        for i in res:
            x.append(i[0])
            y.append(i[1])
        #print(x, y)
    
        fig = plt.figure()
        plt.barh(x, y, label = "Кол-во товара на складе")
        plt.tick_params(axis = 'y', labelsize = 5)
        plt.yticks(rotation=30)
        plt.xlabel("Наименование товара")
        plt.ylabel("Кол-во товара")
        plt.legend()
        #fig.show()

        self.canvas = MplCanvas(fig)
        self.ui.vbl.addWidget(self.canvas)

        self.toolbar = NavigToolBar(self.canvas, self)
        self.ui.vbl.addWidget(self.toolbar)




if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    myapp = MyWin()
    myapp.show()
    sys.exit(app.exec_())
