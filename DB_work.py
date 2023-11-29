import sqlite3 as sq
import json


def select_all(database, table):
    '''
    Функция для выборки всех полей из указанной таблицы
    '''
    
    con = sq.connect(database)
    cursor = con.cursor()
    cursor.execute(f"SELECT * FROM {table}")
    return cursor.fetchall()


def add_data(surname, service, date, total, database='workshop.db', table='consumers'):
    '''
    Функция для добавления данных о покупателях в базу данных.
    Принимает следующие параметры:
    surname - фамилия клиента,
    service - услуга, оказываемая клиенту,
    total - итоговая сумма
    '''
    
    con = sq.connect(database)
    cursor = con.cursor()
    cursor.execute(f"INSERT INTO {table} (surname, services, total, date) VALUES ('{surname}', '{service}', {total}, '{date}')")
    con.commit()


def select_name_n_price(name_of_service, database='workshop.db'):
    con = sq.connect(database)
    cursor = con.cursor()
    cursor.execute(
        f'''SELECT "name of services", "service price", name_of_good, price FROM services, warehouse
    WHERE services.detail = warehouse.id
    AND
    services.detail
    IN(SELECT detail FROM services
    WHERE "name of services" = '{name_of_service}');''')
    return cursor.fetchall()


def select_detail_count(detail, table = "warehouse", database = "workshop.db"):
    con = sq.connect(database)
    cursor = con.cursor()
    cursor.execute(f"SELECT amount FROM {table} WHERE name_of_good = '{detail}'")
    return int(cursor.fetchall()[0][0])


def records(table, database = "workshop.db"):
    con = sq.connect(database)
    cursor = con.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    return int(cursor.fetchall()[0][0])


def total_sum():
    con = sq.connect('workshop.db')
    cursor = con.cursor()
    cursor.execute(f"SELECT SUM(total) FROM consumers")
    return int(cursor.fetchall()[0][0])


def chart():
    con = sq.connect('workshop.db')
    cursor = con.cursor()
    cursor.execute(f"SELECT name_of_good, amount FROM warehouse")
    return cursor.fetchall()


def update_data(detail, table="services"):
    field = ''
    if table == "warehouse":
        field = 'amount'
    if table == "services":
        field = "detail_amount"
    con = sq.connect('workshop.db')
    cursor = con.cursor()
    cursor.execute(f"UPDATE {table} SET '{field}' = '{field}' - 1 WHERE name_of_good = '{detail}'")
    con.commit()


def add_user(name, email, password):
    con = sq.connect('workshop.db')
    cursor = con.cursor()
    cursor.execute(
        f"INSERT INTO consumers (name, email, password) VALUES ('{name}', '{email}', '{password}')")
    con.commit()


def check_enter(email):
    con = sq.connect('workshop.db')
    cursor = con.cursor()
    cursor.execute(f"SELECT email, password FROM consumers WHERE email = '{email}'")
    return cursor.fetchall()

def check_user_info(email):
    con = sq.connect('workshop.db')
    cursor = con.cursor()
    cursor.execute(f"SELECT name, surname, email, password FROM consumers WHERE email = '{email}'")
    return cursor.fetchall()


def place_new_order(service_name, service_price, detail, detail_price, total, consumer_name, consumer_email, date):
    # service_name = json.dumps(service_name)
    # service_price = json.dumps(service_price)
    # detail = json.dumps(detail)
    # detail_price = json.dumps(detail_price)
    con = sq.connect('workshop.db')
    cursor = con.cursor()
    cursor.execute(
        f"INSERT INTO orders (service_name, service_price, detail, detail_price, total, "
        f"consumer_name, consumer_email, date) VALUES ('{service_name}', '{service_price}', '{detail}', '{detail_price}',"
        f"'{total}', '{consumer_name}', '{consumer_email}', '{date}')")
    con.commit()

##con = sq.connect('workshop.db')
##cursor = con.cursor()
##cursor.execute(f"DELETE FROM consumers")
##con.commit()


#print(select_all('workshop.db', 'warehouse'))
# ass = str(['dssdf'])
# place_new_order(ass, 321, 'sdsdc', 113,1323, 'ssc',
#                 'sdds', 'dsdfed')


# con = sq.connect('workshop.db')
# cursor = con.cursor()
# cursor.execute(f"SELECT service_name FROM orders")
# print(cursor.fetchall())