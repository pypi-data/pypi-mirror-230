from configparser import ConfigParser
import os


def config_old(ini_file):
    if not os.path.exists(ini_file):
        raise FileNotFoundError('{}'.format(ini_file))
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(ini_file)
    # print(len(parser.sections()))
    # get section, default to postgresql
    db = {}
    if parser.has_section(parser.sections()[0]):
        params = parser.items(parser.sections()[0])
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(parser.sections()[0], ini_file))
    return db

def config(ini_file, db):
    if not os.path.exists(ini_file):
        raise FileNotFoundError('{}'.format(ini_file))
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(ini_file)
    # print(parser.sections())
    # get section, default to postgresql
    parameter = {}
    if parser.has_section(db):
        # print(db)
        params = parser.items(db)
        # print(params)
        for param in params:
            parameter[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(parser.sections()[0], ini_file))
    return parameter

def get_available_databases(file):
    parser = ConfigParser(empty_lines_in_values=False)
    parser.read(file)
    # print(parser.sections())
    # if parser.has_section(name):
    #     key, val = parser.items(name)[0]
    av_db = []
    for i in parser.sections():
        # print(i)
        # dict = parser.items(i)
        # print(dict)
        db = parser[i]['database']
        # print(db)
        av_db.append(db)
    return av_db


if __name__ == '__main__':
    # params = config_old(r"D:\Python\MySQL\database.ini")
    # print(params)
    # params = config(r"D:\Python\MySQL\web_db.ini")
    # params = config(r"D:\Python\MySQL\db.ini")
    # avb_db = get_available_databases(r"D:\Python\MySQL\config.ini")
    avb_db = config(r"D:\Python\MySQL\config.ini", 'heroku')
    print(avb_db)