# https://www.youtube.com/watch?v=7r93l-sRmwI&ab_channel=CodingShiksha
# https://www.youtube.com/watch?v=Zcg71lxW-Yo&list=WL&index=34&t=167s&ab_channel=CodeJava
# https://www.youtube.com/watch?v=16OIg7cyLw4&ab_channel=kurkurzz
# https://www.youtube.com/watch?v=EyEn5gREn_U&ab_channel=DoableDanny
# https://stackoverflow.com/questions/54566480/how-to-read-a-file-in-python-flask

from datetime import datetime, timedelta
from flask import Flask, render_template, request
from flask_mysqldb import MySQL
import traceback
import sys
import os
import background_op
from flask import Flask, render_template, request
from flask_mysqldb import MySQL
# from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField
from wtforms.validators import DataRequired
from dateutil.relativedelta import *
import numpy as np
from configparser import ConfigParser
from mysqlquerys import connect
from mysqlquerys.config import config



class CheltPlanificate:
    def __init__(self, ini_file, data_base_name):
        try:
            self.dataBase = connect.DataBase(ini_file, data_base_name)
        # except FileNotFoundError as err:
        #     iniFile, a = QFileDialog.getOpenFileName(None, 'Open data base configuration file', os.getcwd(), "data base config files (*.ini)")
        #     if os.path.exists(iniFile):
        #         self.dataBase = connect.DataBase(iniFile, data_base_name)
        #     # ctypes.windll.user32.MessageBoxW(0, "Your text", "Your title", 1)
        except Exception as err:
            print(traceback.format_exc())

    def get_all_sql_vals(self, tableHead):
        # print(sys._getframe().f_code.co_name, tableHead)
        all_chelt = []
        for table in self.dataBase.tables:
            self.dataBase.active_table = table
            check = all(item in list(self.dataBase.active_table.columnsProperties.keys()) for item in tableHead)
            if check:
                vals = self.dataBase.active_table.returnColumns(tableHead)
                for row in vals:
                    row = list(row)
                    row.insert(0, table)
                    all_chelt.append(row)

        newTableHead = ['table']
        for col in tableHead:
            newTableHead.append(col)

        return newTableHead, all_chelt

    def filter_dates_old(self, tableHead, table, selectedStartDate, selectedEndDate):
        print(sys._getframe().f_code.co_name, tableHead)

        tableHead.append('payDay')
        validFromIndx = tableHead.index('valid_from')
        validToIndx = tableHead.index('valid_to')
        freqIndx = tableHead.index('freq')
        payDayIndx = tableHead.index('pay_day')
        postPayIndx = tableHead.index('post_pay')
        autoExtIndx = tableHead.index('auto_ext')
        nameIndx = tableHead.index('name')

        payments4Interval = []
        for val in table:
            # print(val)
            validfrom, validTo, freq, payDatum, postPay, autoExt = val[validFromIndx], \
                                                              val[validToIndx], \
                                                              val[freqIndx], \
                                                              val[payDayIndx], \
                                                              val[postPayIndx], \
                                                              val[autoExtIndx]

            if autoExt is None or autoExt == 0:
                autoExt = False
            else:
                autoExt = True
            if postPay is None or postPay == 0:
                postPay = False
            else:
                postPay = True

            #daca data expirarii este mai mica decat data de start selectata continua
            if validTo:
                if validTo < selectedStartDate and not autoExt:
                    if not postPay:
                        continue
            if not freq:
                continue

            if postPay:
                if not validTo:
                    paymentDate = datetime(validfrom.year, validfrom.month, payDatum).date() + relativedelta(months=freq)
                else:
                    paymentDate = validTo
            else:
                paymentDate = validfrom

            try:
                payDay = datetime(paymentDate.year, paymentDate.month, payDatum).date()
                if payDay < paymentDate:
                    payDay = datetime(paymentDate.year, paymentDate.month, payDatum).date() + relativedelta(months=1)
            except ValueError:
                payDay = datetime(paymentDate.year, paymentDate.month+1, 1).date() - relativedelta(days=1)
            except TypeError:
                payDay = paymentDate
            except Exception:
                print('OOOO')
                print(traceback.format_exc())
                sys.exit()

            toBePayed = False
            # cat timp data de end selectata este mai mare decat data platii...
            while selectedEndDate >= payDay:
                if selectedStartDate <= payDay <= selectedEndDate:
                    if not validTo:
                        tup = [x for x in val]
                        tup.append(payDay)
                        payments4Interval.append(tup)
                        toBePayed = True
                    elif payDay <= validTo:
                        tup = [x for x in val]
                        tup.append(payDay)
                        payments4Interval.append(tup)
                        toBePayed = True
                    elif payDay >= validTo and autoExt:
                        tup = [x for x in val]
                        tup.append(payDay)
                        payments4Interval.append(tup)
                        toBePayed = True
                    elif payDay >= validTo and postPay and selectedStartDate <= payDay <= selectedEndDate:
                        tup = [x for x in val]
                        tup.append(payDay)
                        payments4Interval.append(tup)
                        toBePayed = True

                payDay = payDay + relativedelta(months=+freq)
                try:
                    payDay = datetime(payDay.year, payDay.month, payDatum).date()
                except ValueError:
                    payDay = datetime(payDay.year, payDay.month + 1, 1).date() - relativedelta(days=1)
                except TypeError:
                    payDay = payDay
                except Exception:
                    print('OOOO')
                    print(traceback.format_exc())
                    sys.exit()
                # print(payDay, type(payDay), freq, type(freq), payDay.month+freq)
            if not toBePayed:
                continue
        payments4Interval = np.atleast_2d(payments4Interval)
        return tableHead, payments4Interval

    def filter_dates(self, tableHead, table, selectedStartDate, selectedEndDate):
        print(sys._getframe().f_code.co_name, tableHead)
        # print(sys._getframe().f_code.co_name, selectedStartDate, selectedEndDate)

        def get_next_pay_datum(validfrom, payDatum, freq, autoExt, validTo):
            # print('++++', validfrom, type(validfrom))
            dates2pay = []
            try:
                if postPay:
                    date_of_payment = datetime(validfrom.year, validfrom.month, payDatum).date() + relativedelta(months=freq)
                else:
                    date_of_payment = datetime(validfrom.year, validfrom.month, payDatum).date()
            except ValueError:
                if postPay:
                    date_of_payment = datetime(validfrom.year, validfrom.month + 1, 1).date() + relativedelta(months=freq) - timedelta(days=1)
                else:
                    date_of_payment = datetime(validfrom.year, validfrom.month + 1, 1).date() - timedelta(days=1)

            # print(date_of_payment, selectedStartDate <= date_of_payment <= selectedEndDate)
            if selectedStartDate <= date_of_payment < selectedEndDate:
                dates2pay.append(date_of_payment)

            if autoExt:
                while date_of_payment < selectedEndDate:
                    date_of_payment = date_of_payment + relativedelta(months=freq)
                    if date_of_payment.month == 3 and date_of_payment.day != payDatum:
                        date_of_payment = datetime(date_of_payment.year, date_of_payment.month, payDatum).date()
                    # print(date_of_payment, selectedStartDate <= date_of_payment <= selectedEndDate)
                    if selectedStartDate <= date_of_payment < selectedEndDate:
                        dates2pay.append(date_of_payment)
            elif validTo:
                if not autoExt and validTo > selectedEndDate:
                    while date_of_payment < selectedEndDate:
                        date_of_payment = date_of_payment + relativedelta(months=freq)
                        if date_of_payment.month == 3 and date_of_payment.day != payDatum:
                            date_of_payment = datetime(date_of_payment.year, date_of_payment.month, payDatum).date()
                        # print(date_of_payment, selectedStartDate <= date_of_payment <= selectedEndDate)
                        if selectedStartDate <= date_of_payment < selectedEndDate:
                            dates2pay.append(date_of_payment)

            return dates2pay

        tableHead.append('payDay')
        validFromIndx = tableHead.index('valid_from')
        validToIndx = tableHead.index('valid_to')
        freqIndx = tableHead.index('freq')
        payDayIndx = tableHead.index('pay_day')
        postPayIndx = tableHead.index('post_pay')
        autoExtIndx = tableHead.index('auto_ext')
        nameIndx = tableHead.index('name')

        payments4Interval = []
        for val in table[1:]:
            # print('µµµµµµ', val)
            validfrom, validTo, freq, payDatum, postPay, autoExt = val[validFromIndx], \
                                                              val[validToIndx], \
                                                              val[freqIndx], \
                                                              val[payDayIndx], \
                                                              val[postPayIndx], \
                                                              val[autoExtIndx]
            if autoExt is None or autoExt == 0:
                autoExt = False
            else:
                autoExt = True
            if postPay is None or postPay == 0:
                postPay = False
            else:
                postPay = True

            if not payDatum:
                continue
            dates_of_payment = get_next_pay_datum(validfrom, payDatum, freq, autoExt, validTo)
            if dates_of_payment:
                for date in dates_of_payment:
                    # print(str(date))
                    tup = []
                    for v in val:
                        tup.append(v)
                    tup.append(date)
                    payments4Interval.append(tuple(tup))

        payments4Interval = np.atleast_2d(payments4Interval)

        return tableHead, payments4Interval

    def filter_conto(self, tableHead, table, currentConto):
        print(sys._getframe().f_code.co_name, tableHead, currentConto)
        if table.shape[1] > 0:
            if currentConto == 'all':
                indxConto = np.where(table[:, tableHead.index('table')] != 'intercontotrans')
            else:
                indxConto = np.where(table[:, tableHead.index('myconto')] == currentConto)
            return tableHead, table[indxConto]
        else:
            return tableHead, np.empty((0, len(tableHead)))

    def split_expenses_income(self, tableHead, table):
        # print(sys._getframe().f_code.co_name)
        indxValue = tableHead.index('value')
        payments = []
        income = []
        for row in table:
            if row[indxValue] > 0:
                income.append(row)
            if row[indxValue] < 0:
                payments.append(row)
        payments = np.atleast_2d(payments)
        income = np.atleast_2d(income)

        return payments, income


app = Flask(__name__)
# app.config['MYSQL_USER'] = 'newuser_radu'
# app.config['MYSQL_PASSWORD'] = 'Paroladetest_1234'
# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_DB'] = 'radu_test_db'

app.config['MYSQL_USER'] = 'b378aa5bf705d4'
app.config['MYSQL_PASSWORD'] = 'a6e05cf3'
app.config['MYSQL_HOST'] = 'eu-cdbr-west-03.cleardb.net'
app.config['MYSQL_DB'] = 'heroku_6ed6d828b97b626'
app.config['SECRET_KEY'] = 'prima mea incercare'

mysql = MySQL(app)

# class iniFileCls(FlaskForm):
#     # iniFile = StringField("Please select the iniFile", validators=[DataRequired()])
#     iniFile = FileField("Please select the iniFile", validators=[DataRequired()])
#     submit = SubmitField("Submit")
#

@app.route('/', methods=['GET', 'POST'])
def index():
    # print(sys._getframe().f_code.co_name, request.method)
    print('++++', request.method)
    # iniFile = None
    # form = iniFileCls()
    # if form.validate_on_submit():
    #     iniFile = form.iniFile.data
    #     # ttt = UPLOAD_PATH
    #     # print(iniFile)
    #     # print(UPLOAD_PATH)
    #     form.iniFile.data = ''
    # if request.method == 'POST':
    #     username = request.form['username']
    #     email = request.form['email']
    #     cur = mysql.connection.cursor()
    #     cur.execute('INSERT INTO users (name, email) VALUES (%s, %s)', (username, email))
    #     mysql.connection.commit()
    #     cur.close()
    # cur = mysql.connection.cursor()
    # users = cur.execute('SELECT * FROM aeroclub')
    # ini_file = r"D:\Python\MySQL\web_db.ini"
    # data_base_name = 'heroku_6ed6d828b97b626'
    # app = QApplication([])
    # iniFile, a = QFileDialog.getOpenFileName(None, 'Open data base configuration file', '',
    #                                          "data base config files (*.ini)")
    # dataBase = connect.DataBase(ini_file, data_base_name)
    # tableHead = ['name', 'value', 'myconto', 'freq', 'pay_day', 'valid_from', 'valid_to', 'auto_ext', 'post_pay']
    # all_chelt = []
    # for table in dataBase.tables:
    #     dataBase.active_table = table
    #     check = all(item in list(dataBase.active_table.columnsProperties.keys()) for item in tableHead)
    #     if check:
    #         vals = dataBase.active_table.returnColumns(tableHead)
    #         for row in vals:
    #             row = list(row)
    #             row.insert(0, table)
    #             all_chelt.append(row)
    #
    # newTableHead = ['table']
    # for col in tableHead:
    #     newTableHead.append(col)
    # params = config(iniFile)
    # print(params)
    # if users > 0:
    #     userDetails = cur.fetchall()
    # userDetails = {'ddd': 'ggg'}
    return render_template('index.html', iniFile='iniFile', form='form')#, userDetails='all_chelt', database_name='heroku_6ed6d828b97b626'


@app.route('/users', methods=['GET', 'POST'])
def users():
    if request.method == 'POST':
        dataFrom = request.form['dataFrom']
        dataBis = request.form['dataBis']
        try:
            dataFrom = datetime.strptime(dataFrom, "%Y-%m-%d").date()
        except:
            dataFrom = datetime(2023, 1, 1).date()

        try:
            dataBis = datetime.strptime(dataBis, "%Y-%m-%d").date()
        except:
            dataBis = datetime(2023, 1, 1).date()
        conto = request.form['conto']
    else:
        dataFrom = datetime(2023, 1, 1).date()
        dataBis = datetime(2023, 1, 31).date()
        conto = 'all'

    if dataFrom == '':
        dataFrom = datetime(2023, 1, 1).date()
    if dataBis == '':
        dataBis = datetime(2023, 1, 1).date()

    # ini_file = r"D:\Python\MySQL\web_db.ini"
    # ini_file = r"D:\Python\MySQL\web_db.ini"
    # ini_file = os.path.abspath(ini_file)#todo
    payments4Interval = None
    income = None
    totalExpenses = None
    totalIncomes = None

    try:
        data_base_name = 'heroku_6ed6d828b97b626'
        connexion = CheltPlanificate('static/web_db.ini', data_base_name)
        tableHead = ['name', 'value', 'myconto', 'freq', 'pay_day', 'valid_from', 'valid_to', 'auto_ext', 'post_pay']
        newTableHead, table = connexion.get_all_sql_vals(tableHead)
        tableHead, payments4Interval = connexion.filter_dates(newTableHead, table, dataFrom, dataBis)
        tableHead, payments4Interval = connexion.filter_conto(tableHead, payments4Interval, conto)
        payments4Interval, income = connexion.split_expenses_income(tableHead, payments4Interval)
        table_payments = np.atleast_2d(payments4Interval)
        table_income = np.atleast_2d(income)
        allpayments = table_payments[:, tableHead.index('value')]
        if None in allpayments:
            allpayments = allpayments[allpayments != np.array(None)]
        totalExpenses = round(sum(allpayments.astype(float)), 2)
        allIncomes = table_income[:, tableHead.index('value')]
        if None in allIncomes:
            allIncomes = allIncomes[allIncomes != np.array(None)]
        totalIncomes = round(sum(allIncomes.astype(float)), 2)
    except:
        income = traceback.format_exc()
    return render_template('users.html',
                           payments4Interval=payments4Interval,
                           income=income,
                           totalExpenses=totalExpenses,
                           totalIncomes=totalIncomes,
                           dataFrom=dataFrom,
                           dataBis=dataBis,
                           )


@app.route('/add_Alimentari', methods=['GET', 'POST'])
def add_Alimentari():
    print(sys._getframe().f_code.co_name, request.method)
    if request.method == 'POST':
        date = request.form['data']
        type = request.form['type']
        brutto = request.form['brutto']
        amount = request.form['amount']
        km = request.form['km']

        ppu = round(float(brutto)/float(amount), 3)

        cur = mysql.connection.cursor()
        if date != '':
            cur.execute('INSERT INTO alimentari (data, type, brutto, amount, ppu, km) VALUES (%s, %s, %s, %s, %s, %s)', (date, type, brutto, amount, ppu, km))
        else:
            cur.execute('INSERT INTO alimentari (type, brutto, amount, ppu, km) VALUES (%s, %s, %s, %s, %s)', (type, brutto, amount, ppu, km))
        mysql.connection.commit()
        cur.close()
    cur = mysql.connection.cursor()
    alimentari = cur.execute('SELECT * FROM alimentari ORDER BY data DESC')
    if alimentari > 0:
        alimentariTable = cur.fetchall()
        total, tot_benzina, tot_electric, tot_lm, lm_benz, lm_elec, date_from = background_op.get_total(alimentariTable)

    return render_template('add_Alimentari.html', total=total, tot_el=tot_electric, tot_benz=tot_benzina,
                           tot_lm=tot_lm, lm_benz=lm_benz, lm_elec=lm_elec, userDetails=alimentariTable,
                           date_from=date_from.date())


if __name__ == "__main__":
    app.run(debug=True)
