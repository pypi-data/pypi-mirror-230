import mysql.connector
import traceback
import sys
import csv
from datetime import datetime
import json
from mysqlquerys import config

from flask import Flask, render_template, request
from flask_mysqldb import MySQL


class DBonline:
    def __init__(self):
        app = Flask(__name__)
        self.app = app

        @self.app.route("/")
        def hello_world():
            app.config['MYSQL_USER'] = 'b378aa5bf705d4'
            app.config['MYSQL_PASSWORD'] = 'a6e05cf3' #a6e05cf3
            app.config['MYSQL_HOST'] = 'eu-cdbr-west-03.cleardb.net'
            app.config['MYSQL_DB'] = 'heroku_6ed6d828b97b626'
            # dic = {'mysql_host': 'eu-cdbr-west-03.cleardb.net', 'mysql_user': 'b378aa5bf705d4', 'mysql_password': 'a6e05cf3'}
            # app.config = dic
            mysql = MySQL(app)
            return "<p>{}</p>".format('++++')

        @self.app.route("/con")
        def bbb():
            # cur = mysql.connection.cursor()
            # cur.execute('SELECT * FROM aeroclub')
            # userDetails = cur.fetchall()
            return "<p>{}</p>".format(print(mysql))

    def start_app(self):
        self.app.run()

    # @property
    # def configuration_parameters(self):
    #     try:
    #         params = config(r"D:\Python\MySQL\db.ini")
    #     except Exception as err:
    #         print('ERROR: ',traceback.format_exc())
    #         sys.exit()
    #     return params


class DBmySQL:
    def __init__(self, ini_file):
        self.ini_file = ini_file
        self.connection = self.connect_to_database()
        self.cursor = self.connection.cursor()

    @property
    def configuration_parameters(self):
        try:
            params = config(self.ini_file)
        except Exception as err:
            print('ERROR: !!!{}'.format(sys._getframe().f_code.co_name), traceback.format_exc())
            sys.exit()
        return params

    @property
    def version(self):
        # cursor = self.connection.cursor()
        self.cursor.execute('SELECT version()')
        db_version = self.cursor.fetchone()
        # self.cursor.close()
        return db_version

    @property
    def schemas(self):
        # cursor = self.connection.cursor()
        self.cursor.execute('SHOW DATABASES')
        dbase = self.cursor.fetchall()
        dataBases = []
        for i in dbase:
            if i[0] == 'information_schema' or i[0] == 'performance_schema' or i[0] == 'mysql' or i[0] == 'sys':
                continue
            dataBases.append(i[0])
        # self.cursor.close()
        return dataBases

    def connect_to_database(self):
        try:
            connection = mysql.connector.connect(**self.configuration_parameters)
        except Exception as err:
            print('ERROR: ',traceback.format_exc())
            sys.exit()
        return connection

    def set_active_schema(self, schema_name):
        self.connection.database = schema_name


class DbConnection:
    def __init__(self, ini_file, sec_name):
        print('Module: {}, Class: {}, Def: {}'.format(__name__, __class__, sys._getframe().f_code.co_name))
        self.iniFile = ini_file
        self.sec_name = sec_name
        try:
            self.connection = mysql.connector.connect(**self.params)
        except Exception as err:
            print(err)
            print(traceback.print_exc())

    @property
    def params(self):
        params = config.config(self.iniFile, self.sec_name)
        return params

    @property
    def version(self):
        cursor = self.connection.cursor()
        cursor.execute('SELECT version()')
        db_version = cursor.fetchone()
        cursor.close()
        return db_version

    @property
    def databases(self):
        print('Module: {}, Class: {}, Def: {}'.format(__name__, __class__, sys._getframe().f_code.co_name))
        # cursor = self.connection.cursor()
        # cursor.execute('SHOW DATABASES')
        # dbase = cursor.fetchall()
        # dataBases = []
        # for i in dbase:
        #     if i[0] == 'information_schema' or i[0] == 'performance_schema' or i[0] == 'mysql' or i[0] == 'sys':
        #         continue
        #     dataBases.append(i[0])
        # cursor.close()
        dataBases = config.get_available_databases(self.iniFile)
        return dataBases
    
    @property
    def active_data_base(self):
        return self.dataBase

    @active_data_base.setter
    def active_data_base(self, data_base_name):
        self.dataBase = DataBase(self.iniFile, data_base_name)

    def drop_data_base(self, schema_name):
        cursor = self.connection.cursor()
        query = 'DROP SCHEMA {}'.format(schema_name)
        cursor.execute(query)
        cursor.close()

    def create_data_base(self, schema_name):
        try:
            cursor = self.connection.cursor()
            query = 'CREATE SCHEMA {}'.format(schema_name)
            cursor.execute(query)
            cursor.close()
        except mysql.connector.Error as err:
            print('mysql.Error', err.msg)
        except Exception:
            print(traceback.format_exc())
        else:
            print('successfully executed query: ', query)


class DataBase(DbConnection):
    def __init__(self, iniFile, data_base_name):
        super().__init__(iniFile, data_base_name)
        # print('aaaaaa', self.params, type(self.params))
        # print('aaaaaa', self.params['database'])
        # self.connection.database = self.params['database']
        self.data_base_name = self.params['database']

    @property
    def tables(self):
        cursor = self.connection.cursor()
        cursor.execute('SHOW tables')
        tabs = cursor.fetchall()
        tables = []
        for i in tabs:
            tables.append(i[0])
        cursor.close()
        return tables

    @property
    def active_table(self):
        print('Module: {}, Class: {}, Def: {}'.format(__name__, __class__, sys._getframe().f_code.co_name,
                                                      self.data_base_name))
        return self.table

    @active_table.setter
    def active_table(self, table_name):
        print('Module***: {}, Class: {}, Def: {}'.format(__name__, __class__, sys._getframe().f_code.co_name, self.data_base_name))
        self.table = Table(self.iniFile, self.data_base_name, table_name)

    def drop_table(self, tableName):
        cursor = self.connection.cursor()
        query = 'DROP TABLE {}'.format(tableName)
        cursor.execute(query)
        cursor.close

    def createTableFromFile(self, file):
        print(sys._getframe().f_code.co_name)
        # print(file)
        cursor = self.connection.cursor()
        if isinstance(file, str):
            commands = file.split(';')
        for command in commands:
            print('executing command: ', command)
            cursor.execute(command)

    def renameTable(self, oldTableName, newTableName):
        query = "RENAME TABLE {} TO {}".format(oldTableName, newTableName)
        cursor = self.connection.cursor()
        cursor.execute(query)
        cursor.close()

    def deleteAllRows(self, table_name):
        query = 'DELETE FROM {}'.format(table_name)
        cursor = self.connection.cursor()
        cursor.execute(query)
        self.connection.commit()
        cursor.close()


class Table(DataBase):
    def __init__(self, iniFile, data_base_name, table_name):
        super().__init__(iniFile, data_base_name)
        self.table_name = table_name

    @property
    def tableProperties(self):
        query = 'SHOW CREATE TABLE {}'.format(self.table_name)
        cursor = self.connection.cursor()
        cursor.execute(query)
        res = cursor.fetchone()
        cursor.close()
        return res[1]

    @property
    def columnsNames(self):
        query = 'DESC {}'.format(self.table_name)
        cursor = self.connection.cursor()
        cursor.execute(query)
        res = cursor.fetchall()
        cols = []
        for col in res:
            cols.append(col[0])
        cursor.close()
        return cols

    @property
    def columnsProperties(self):
        query = 'DESC {}'.format(self.table_name)
        colNames = ['Field', 'Type', 'Null', 'Key', 'Default', 'Extra']
        cursor = self.connection.cursor()
        cursor.execute(query)
        res = cursor.fetchall()
        cols = {}
        for col in res:
            colName, colType, null, key, default, extra = col
            if isinstance(colType, bytes):
                colType = str(colType.decode("utf-8"))
            cols[colName] = [colType, null, key, default, extra]
        cursor.close()
        return cols

    @property
    def noOfRows(self):
        query = 'SELECT * FROM {}'.format(self.table_name)
        cursor = self.connection.cursor()
        cursor.execute(query)
        cursor.fetchall()
        rowNo = cursor.rowcount
        cursor.close()
        return rowNo

    @property
    def data(self):
        query = 'SELECT * FROM {}'.format(self.table_name)
        cursor = self.connection.cursor()
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()
        return records

    def get_column_type(self, column):
        colProps = self.columnsProperties[column]
        colType = colProps[0]
        return colType

    def add_row(self, columns, values):
        print(len(columns), len(values))
        strCols = (('{}, ' * len(columns)).format(*columns))
        strCols = '({})'.format(strCols[:-2])
        strVals = ('%s,'*len(columns))
        strVals = '({})'.format(strVals[:-1])

        query = "INSERT INTO {} {} VALUES {}".format(self.table_name, strCols, strVals)
        #######
        print(query)
        for i in range(len(columns)):
            print(columns[i], values[i])
        #######
        if isinstance(values, int):
            values = (values, )
        elif isinstance(values, str):
            values = (values,)

        cursor = self.connection.cursor()
        cursor.execute(query, values)
        self.connection.commit()
        cursor.close()

        return cursor.lastrowid

    def modify2AutoIncrement(self, column, colType):
        query = 'ALTER TABLE {} MODIFY {} {} AUTO_INCREMENT;'.format(self.table_name, column, colType)
        print(query)
        cursor = self.connection.cursor()
        cursor.execute(query)
        self.connection.commit()
        cursor.close()

    def modifyType(self, column, colType):
        query = 'ALTER TABLE {} MODIFY {} {};'.format(self.table_name, column, colType)
        cursor = self.connection.cursor()
        cursor.execute(query)
        self.connection.commit()
        cursor.close()

    def deleteRow(self, condition):
        colName, value = condition
        query = 'DELETE FROM {} WHERE {} = {} '.format(self.table_name, colName, value)
        print(query)
        cursor = self.connection.cursor()
        cursor.execute(query, value)
        self.connection.commit()
        cursor.close()

    def changeCellContent(self, column2Modify, val2Moify, refColumn, refValue):
        query = "UPDATE {} SET {} = %s WHERE {} = %s".format(self.table_name, column2Modify, refColumn)
        # print(query)
        cursor = self.connection.cursor()
        vals = (val2Moify, refValue)
        # print(vals)
        cursor.execute(query, vals)
        self.connection.commit()
        cursor.close()

    def dropColumn(self, column2Del):
        query = "ALTER TABLE {} DROP COLUMN %s;".format(self.table_name)
        query = "ALTER TABLE {} DROP COLUMN {};".format(self.table_name, column2Del)
        print(query)
        cursor = self.connection.cursor()
        # vals = (column2Del, )
        cursor.execute(query)
        self.connection.commit()
        cursor.close()

    def executeQuery(self, query):
        print(sys._getframe().f_code.co_name)
        # print(file)
        cursor = self.connection.cursor()
        if isinstance(query, str):
            commands = query.split(';')
        for command in commands:
            print('executing command: ', command)
            cursor.execute(command)

    def filterRows(self, matches):
        filterText = ''
        for match in matches:
            search_col, search_key = match
            if isinstance(search_key, tuple):
                min, max = search_key
                new = "{} > '{}' AND {} < '{}' AND ".format(search_col, min, search_col, max)
                filterText += new
            elif isinstance(search_key, list):
                new = "{} IN {} AND ".format(search_col, tuple(search_key))
                filterText += new
            else:
                new = "{} = '{}' AND ".format(search_col, search_key)
                filterText += new

        query = "SELECT * FROM {} WHERE ".format(self.table_name) + filterText[:-4]
        cursor = self.connection.cursor()
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()
        return records

    def importCSV(self, inpFile):
        with open(inpFile, 'r', encoding='unicode_escape', newline='') as csvfile:
            linereader = csv.reader(csvfile, delimiter=';', quotechar='|')
            for i, row in enumerate(linereader):
                if i == 0:
                    tableHead = row
                    continue
                if '' in row or 'None' in row:
                    new_strings = []
                    for string in row:
                        if string == '' or string == 'None':
                            new_strings.append(None)
                        else:
                            new_strings.append(string)
                    row = new_strings
                self.add_row(tableHead, row)

    def importSparkasseCSV(self, inpFile):
        with open(inpFile, 'r', encoding='unicode_escape', newline='') as csvfile:
            linereader = csv.reader(csvfile, delimiter=';', quotechar='"')
            indxBuchungstag = self.columnsNames.index('Buchungstag')
            indxValutDatum = self.columnsNames.index('Valutadatum')
            indxBetrag = self.columnsNames.index('Betrag')
            for i, row in enumerate(linereader):
                # print(row)
                row.insert(0, i)
                if i == 0:
                    tableHead = row
                    continue
                if '' in row or 'None' in row:
                    new_strings = []
                    for string in row:
                        if string == '' or string == 'None':
                            new_strings.append(None)
                        else:
                            new_strings.append(string)
                    row = new_strings
                buchungstag = row[indxBuchungstag]
                valutDatum = row[indxValutDatum]
                betrag = row[indxBetrag]
                betrag = float(betrag.replace(',', '.'))
                buchungstag = self.convertDatumFormat4SQL(buchungstag)
                valutDatum = self.convertDatumFormat4SQL(valutDatum)

                row[indxBuchungstag] = buchungstag
                row[indxValutDatum] = valutDatum
                row[indxBetrag] = betrag
                self.add_row(self.columnsNames, row)

    def convertDatumFormat4SQL(self, datum):
        # print(sys._getframe().f_code.co_name)
        # newDate = datetime.strptime(datum, '%d.%m.%y')
        for fmt in ('%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y', '%m/%d/%Y', '%d.%m.%y'):
            try:
                newDate = datetime.strptime(datum, fmt)
                return newDate.date()
            except ValueError:
                pass
        raise ValueError('no valid date format found')

    def convertTimeFormat4SQL(self, time):
        # print(sys._getframe().f_code.co_name)
        # newDate = datetime.strptime(datum, '%d.%m.%y')
        for fmt in ('%H:%M', '%H:%M:%S'):
            try:
                newDate = datetime.strptime(time, fmt)
                return newDate.time()
            except ValueError:
                pass
        raise ValueError('no valid date format found')

    def returnColumn(self, col):
        query = 'SELECT {} FROM {}'.format(col, self.table_name)
        cursor = self.connection.cursor()
        # vals = (column2Del, )
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()
        values = []
        for i in records:
            values.append(i[0])
        return values

    def returnColumns(self, cols):
        strTableHead = ''
        for col in cols:
            strTableHead += '{}, '.format(col)
        strTableHead = strTableHead[:-2]

        query = 'SELECT {} FROM {}'.format(strTableHead, self.table_name)
        cursor = self.connection.cursor()
        # vals = (column2Del, )
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()
        values = []
        for i in records:
            values.append(i)
        return values

    def returnCellsWhere(self, col, matches):
        if isinstance(matches, tuple):
            searchCol, searchKey = matches
            if isinstance(searchKey, str) or isinstance(searchKey, int):
                query = "SELECT {} FROM {} WHERE {} = '{}'".format(col, self.table_name, searchCol, searchKey)
            if isinstance(searchKey, tuple):
                query = "SELECT {} FROM {} WHERE {} IN {}".format(col, self.table_name, searchCol, searchKey)
        elif isinstance(matches, list):
            text = ''
            for i in matches:
                searchCol, searchKey = i
                new = '{} = "{}" AND '.format(searchCol, searchKey)
                text += new
            query = "SELECT {} FROM {} WHERE ".format(col, self.table_name) + text[:-4]
        else:
            raise TypeError('{} must be tuple or list of tuples'.format(matches))

        cursor = self.connection.cursor()
        # print('query', query)
        cursor.execute(query)
        records = cursor.fetchall()
        # print(records)
        cursor.close()
        values = []
        colType = self.get_column_type(col)
        for i in records:
            if colType == 'json':
                values.append(json.loads(i[0]))
            else:
                values.append(i[0])
        return values

    def returnColsWhere(self, cols, matches):
        relCols = ''
        for col in cols:
            relCols += '{}, '.format(col)
        relCols = relCols[:-2]

        if isinstance(matches, tuple):
            searchCol, searchKey = matches
            if isinstance(searchKey, str) or isinstance(searchKey, int):
                query = "SELECT {} FROM {} WHERE {} = '{}'".format(relCols, self.table_name, searchCol, searchKey)
            if isinstance(searchKey, tuple):
                query = "SELECT {} FROM {} WHERE {} IN '{}'".format(relCols, self.table_name, searchCol, searchKey)
            if searchKey is None:
                query = "SELECT {} FROM {} WHERE {} IS NULL".format(relCols, self.table_name, searchCol)
        elif isinstance(matches, list):
            text = ''
            for i in matches:
                searchCol, searchKey = i
                if searchKey is None:
                    new = '{} IS NULL AND '.format(searchCol)
                else:
                    new = '{} = "{}" AND '.format(searchCol, searchKey)
                text += new
            query = "SELECT {} FROM {} WHERE ".format(relCols, self.table_name) + text[:-4]
        else:
            raise TypeError('{} must be tuple or list of tuples'.format(matches))

        cursor = self.connection.cursor()
        # print('query', query)
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()
        values = []
        for i in records:
            values.append(i)
        return values

    def returnRowsWhere(self, matches):
        if isinstance(matches, tuple):
            searchCol, searchKey = matches
            if isinstance(searchKey, str) or isinstance(searchKey, int):
                query = "SELECT * FROM {} WHERE {} = '{}'".format(self.table_name, searchCol, searchKey)
            if isinstance(searchKey, tuple):
                query = "SELECT * FROM {} WHERE {} IN '{}'".format(self.table_name, searchCol, searchKey)
            if searchKey is None:
                query = "SELECT * FROM {} WHERE {} IS NULL".format(self.table_name, searchCol)
        elif isinstance(matches, list):
            text = ''
            for i in matches:
                searchCol, searchKey = i
                if searchKey is None:
                    new = '{} IS NULL AND '.format(searchCol)
                else:
                    new = '{} = "{}" AND '.format(searchCol, searchKey)
                text += new
            query = "SELECT * FROM {} WHERE ".format(self.table_name) + text[:-4]
        else:
            raise TypeError('{} must be tuple or list of tuples'.format(matches))

        cursor = self.connection.cursor()
        # print('query', query)
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()
        values = []
        for i in records:
            values.append(i)
        return values


if __name__ == '__main__':

    # iniFile = r"D:\Python\MySQL\database.ini"
    iniFile = r"D:\Python\MySQL\web_db.ini"

    print('#####')
    db = DBmySQL(iniFile)
    print('db.configuration_parameters', db.configuration_parameters)
    print(db.connection.is_connected())
    print(db.version)
    print(db.schemas)
    # db.connect_db()
    # print('****', db.connection)
    # test = DBonline()
    # test.start_app()

    # db.set_active_schema('cheltuieli')
    # # cursor = db.connection.cursor()
    # db.cursor.execute('SHOW tables')
    # tabs = db.cursor.fetchall()
    # for i in tabs:
    #     print(i)

    # dbase = cursor.fetchall()
    # # print(dbase)
    # # iniFile = r"D:\Python\MySQL\web_db.ini"
    # # db = DbConnection(iniFile)
    # # print(db.version)
    # # db = DataBase(iniFile, 'heroku_6ed6d828b97b626')
    # # print(db.tables)
    # # table = Table(iniFile, 'heroku_6ed6d828b97b626', 'apartament')
    # # table = Table(iniFile, 'cheltuieli', 'apartament')
    # # print(table.columnsProperties)
    # #
    # # try:
    # #     iniFile = r"D:\Python\MySQL\database.ini"
    # #     iniFile = r"D:\Python\MySQL\web_db.ini"
    # #     db = DbConnection(iniFile)
    # #     print(db.version)
    # #     db = DataBase(iniFile, 'heroku_6ed6d828b97b626')
    # #     print(db.tables)
    # #     table = Table(iniFile, 'heroku_6ed6d828b97b626', 'apartament')
    # #     print(table.columnsProperties)
    # # except Exception as error:
    # #     print(error)
    # # print('aaaaa')
