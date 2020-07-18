from peewee import *
import schedule
import time

mysql_db = MySQLDatabase('mamta', user='root', password='pass',
                         host='127.0.0.1', port=3306)
tables = mysql_db.get_tables()
e_list = []
for a in mysql_db.get_columns('mamtaApp_staffuser'):
    e_list.append(a.name)

def disableCollectMoney():
    Employee = Table('mamtaApp_staffuser', tuple(e_list))  # creating a dummy table with the columns
    Employee = Employee.bind(mysql_db)
    for obj in Employee.select():
        nrows = (Employee
                 .update(canTakePayment=False).execute())

def enableCollectMoney():
    Employee = Table('mamtaApp_staffuser', tuple(e_list))  # creating a dummy table with the columns
    Employee = Employee.bind(mysql_db)
    for obj in Employee.select():
        nrows = (Employee
                 .update(canTakePayment=True).execute())
disableCollectMoney()


schedule.every().day.at("13:30").do(disableCollectMoney)
schedule.every().day.at("03:30").do(enableCollectMoney)

while True:
    # Checks whether a scheduled task
    # is pending to run or not
    schedule.run_pending()
    time.sleep(1)