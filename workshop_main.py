import sys
from workshop_interface import *
from PyQt5 import QtCore, QtGui, QtWidgets, QtSql
from PyQt5.QtWidgets import QSizePolicy, QMessageBox, QTableWidgetItem
from PyQt5.QtGui import QIcon, QPixmap, QRegExpValidator
from PyQt5.QtCore import QSize, QDate, QRegExp
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

        self.setStyleSheet("""
                QTableWidget{
                    color:#FF9200;
                    gridline-color: #25567B;
                    border: transparent;
                    font: 8pt \"Segoe Print\";
                }
        """)

        #self.ui.order_table.setFrameStyle(0)
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

        self.ui.btn_title.clicked.connect(lambda: self.ui.stackedWidget_main.setCurrentIndex(0))
        self.ui.pushButton_shop.clicked.connect(lambda: self.ui.stackedWidget_main.setCurrentIndex(1))
        self.ui.pushButton_profile.clicked.connect(self.profile_button)
        
        # Подключение функций к пунктам меню
        self.ui.action_4.triggered.connect(lambda:self.close())
        self.ui.action_2.triggered.connect(self.open)
        self.ui.action.triggered.connect(self.draw_chart)

        # Установка иконок к кнопкам навигации
        self.ui.pushButton.setIcon(QIcon('Icons\\home2.png'))
        self.ui.pushButton.setIconSize(QSize(35, 35))
        self.ui.pushButton_2.setIcon(QIcon('Icons\\database.png'))
        self.ui.pushButton_2.setIconSize(QSize(35, 35))
        self.ui.pushButton_3.setIcon(QIcon('Icons\\pie_chart.png'))
        self.ui.pushButton_3.setIconSize(QSize(35, 35))
        self.ui.pushButton_shop.setIcon(QIcon('Icons\\shopping_cart.png'))
        self.ui.pushButton_shop.setIconSize(QSize(20, 20))
        self.ui.pushButton_profile.setIcon(QIcon('Icons\\profile.png'))
        self.ui.pushButton_profile.setIconSize(QSize(20, 20))

        pixmap = QPixmap('Icons\\technology.png')
        p = pixmap.scaled(80, 80, QtCore.Qt.KeepAspectRatio)
        self.ui.label.setPixmap(p)

        # Установка минимальной даты для выбора (устанавливает текущую дату)
        self.ui.dateEdit.setMinimumDate(QDate(date.today()))
        # Подключение функции к combobox'у
        self.ui.comboBox.currentIndexChanged.connect(self.cbb_changed)
        # Подключение функции к кнопке оформления заказа
        self.ui.pushButton_4.clicked.connect(self.add_good)

        self.row_count = 0
        self.total = 0

        self.isregistration = False

        self.ui.ent_button.clicked.connect(lambda: self.ui.enter_stack.setCurrentIndex(0))
        self.ui.reg_button.clicked.connect(lambda: self.ui.enter_stack.setCurrentIndex(1))

        self.ui.conf_reg_button.clicked.connect(self.add_new_user)
        self.ui.conf_ent_button.clicked.connect(self.enter)

        self.service_name = ''
        self.service_price = ''
        self.detail = ''
        self.detail_price = ''

        self.ui.place_order_btn.clicked.connect(self.place_order)

        self.ui.name_reg_lineEdit.textChanged.connect(lambda:self.ui.name_reg_lineEdit.setStyleSheet("background-color: rgb(255, 255, 255);"))
        self.ui.email_reg_lineEdit.textChanged.connect(lambda:self.ui.email_reg_lineEdit.setStyleSheet("background-color: rgb(255, 255, 255);"))
        self.ui.password_reg_lineEdit.textChanged.connect(lambda:self.ui.password_reg_lineEdit.setStyleSheet("background-color: rgb(255, 255, 255);"))

        pixmap = QPixmap("Icons\\my_profile.png")
        p = pixmap.scaled(60, 60, QtCore.Qt.KeepAspectRatio)
        self.ui.profile_photo.setPixmap(p)


    def profile_button(self):
        email = self.ui.user_email.text()

        self.ui.stackedWidget_main.setCurrentIndex(2)
        if self.isregistration:
            con = QtSql.QSqlDatabase.addDatabase('QSQLITE')
            con.setDatabaseName('workshop.db')
            con.open()

            stm = QtSql.QSqlTableModel()
            stm.setTable('orders')
            stm.setFilter(f"consumer_email='{email}'")
            stm.select()

            self.ui.tableview.setModel(stm)


    # Функция, срабатывающая при изменении значения в combobox'е
    def cbb_changed(self):
        self.ui.amount_lbl.setText('')
        # Выборка из базы данных
        db_select = DB_work.select_name_n_price(self.ui.comboBox.itemText(self.ui.comboBox.currentIndex()))
        nes_detail = db_select[0][2]
        detail_amount = DB_work.select_detail_count_from_warehouse(nes_detail)
        detail_amount_from_service = DB_work.select_detail_count_from_services(db_select[0][0])

        if detail_amount_from_service == 0 and detail_amount != 0:
           self.ui.amount_lbl.setText("Количество товара в магазине: 0\n"
                                      "Товар будет заказан со склада")

        if detail_amount_from_service == 0 and detail_amount == 0:
            self.ui.amount_lbl.setText("В данный момент товар недоступен")

            
        # Установка текста(название услуги + цена)
        self.ui.service_lbl.setText(f'{db_select[0][0]}         {db_select[0][1]}')
        # Установка текста(название детали + цена)
        self.ui.good_lbl.setText(f'{db_select[0][2]}            {db_select[0][3]}')
        # Установка текста итоговой цены
        self.ui.label_6.setText(f'{db_select[0][1] + db_select[0][3]}')

    def add_good(self):
        try:

            self.row_count += 1

            db_select = DB_work.select_name_n_price(self.ui.comboBox.itemText(self.ui.comboBox.currentIndex()))
            nes_detail = db_select[0][2]
            detail_amount = DB_work.select_detail_count_from_warehouse(nes_detail)
            detail_amount_from_service = DB_work.select_detail_count_from_services(db_select[0][0])
            if detail_amount_from_service == 0 and detail_amount == 0:
                self.ui.statusbar.setStyleSheet("color: red")
                self.ui.statusbar.showMessage("В данный момент данная услуга недоступна")
                return

            self.ui.order_table.setRowCount(self.row_count + 1)

            db_select = DB_work.select_name_n_price(self.ui.comboBox.itemText(self.ui.comboBox.currentIndex()))
            self.ui.order_table.setItem(self.row_count - 1, 0, QTableWidgetItem(db_select[0][0]))
            self.ui.order_table.setItem(self.row_count - 1, 1, QTableWidgetItem(str(db_select[0][1])))
            self.ui.order_table.setItem(self.row_count - 1, 2, QTableWidgetItem(db_select[0][2]))
            self.ui.order_table.setItem(self.row_count - 1, 3, QTableWidgetItem(str(db_select[0][3])))
            self.total += db_select[0][1] + db_select[0][3]
            self.ui.order_table.setItem(self.row_count, 0, QTableWidgetItem("Итог"))
            self.ui.order_table.setItem(self.row_count, 3, QTableWidgetItem(str(self.total)))

            self.service_name = self.service_name + str(db_select[0][0]) + ', '
            self.service_price = self.service_price + str(db_select[0][1]) + ', '
            self.detail = self.detail + str(db_select[0][2]) + ', '
            self.detail_price = self.detail_price + str(db_select[0][3]) + ', '
        
        except:
            self.warning = QMessageBox.warning(self, 'Ошибка', "Возникла непредвиденная ошибка", QMessageBox.Ok)

    # def closeEvent(self, event):
    #     if self.warning == QMessageBox.Ok:
    #         event.accept()
        
        

    def open(self):
        try:
            con = QtSql.QSqlDatabase.addDatabase('QSQLITE')
            con.setDatabaseName('workshop.db')
            con.open()

            stm = QtSql.QSqlTableModel()
            stm.setTable('orders')
            stm.select()

            # stm.setHeaderData(1, QtCore.Qt.Horizontal, 'Фамилия')
            # stm.setHeaderData(2, QtCore.Qt.Horizontal, 'Услуга')
            # stm.setHeaderData(4, QtCore.Qt.Horizontal, 'Дата')
            # stm.setHeaderData(3, QtCore.Qt.Horizontal, 'Итог')

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


    def add_new_user(self):
        name = self.ui.name_reg_lineEdit.text()
        email = self.ui.email_reg_lineEdit.text()
        password = self.ui.password_reg_lineEdit.text()

        if name != "" and email != "" and password != "":
            self.ui.profile_stack.setCurrentIndex(1)
            user_info = DB_work.check_user_info(email)
            self.ui.user_name.setText(user_info[0][0])
            self.ui.user_surname.setText(user_info[0][1])
            self.ui.user_email.setText(user_info[0][2])
            DB_work.add_user(name, email, password)
            self.isregistration = True
        else:
            self.ui.statusbar.setStyleSheet("color: red")
            self.ui.statusbar.showMessage("Все поля должны быть заполнены")
            if name == "":
                self.ui.name_reg_lineEdit.setStyleSheet("border-color:red; border-width:2px; "
                                                        "background-color: rgb(255, 255, 255);")
            if email == "":
                self.ui.email_reg_lineEdit.setStyleSheet("border-color:red; border-width:2px; "
                                                        "background-color: rgb(255, 255, 255);")
            if password == "":
                self.ui.password_reg_lineEdit.setStyleSheet("border-color:red; border-width:2px; "
                                                        "background-color: rgb(255, 255, 255);")
            return



    def enter(self):
        email = self.ui.email_lineEdit.text()
        password = self.ui.password_lineEdit.text()
        try:
            ent = DB_work.check_enter(email)
            if password == ent[0][1]:
                self.ui.profile_stack.setCurrentIndex(1)
                user_info = DB_work.check_user_info(email)

                self.ui.user_name.setText(user_info[0][0])
                self.ui.user_surname.setText(user_info[0][1])
                self.ui.user_email.setText(user_info[0][2])
                self.isregistration = True
            else:
                self.warning = QMessageBox.warning(self, 'Ошибка',
                                                   "Возникла ошибка. Неправильный Email или пароль",
                                                   QMessageBox.Ok)
        except:
            self.warning = QMessageBox.warning(self, 'Ошибка', "Неправильный Email или пароль", QMessageBox.Ok)




    def place_order(self):
        date_my = self.ui.dateEdit.date()
        email = self.ui.email_lineEdit.text()
        user_info = DB_work.check_user_info(email)
        consumer_name = user_info[0][0]

        # print(self.service_name, self.service_price, self.detail, self.detail_price, self.total, consumer_name, email, date_my.toPyDate())

        service_list = self.service_name.split(',')[:-1]
        detail_list = self.detail.split(',')[:-1]

        print(service_list, detail_list)

        for i in range(len(service_list)):
            if DB_work.select_detail_count_from_services(service_list[i].strip()) > 0:
                DB_work.update_data_in_services(service_list[i].strip())
            else:
                if DB_work.select_detail_count_from_warehouse(detail_list[i].strip()) > 0:
                    DB_work.update_data_in_warehouse(detail_list[i].strip())
                else:
                    return

        DB_work.place_new_order(self.service_name, self.service_price, self.detail, self.detail_price,
                                self.total, consumer_name, email, date_my.toPyDate())



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    myapp = MyWin()
    myapp.show()
    sys.exit(app.exec_())
