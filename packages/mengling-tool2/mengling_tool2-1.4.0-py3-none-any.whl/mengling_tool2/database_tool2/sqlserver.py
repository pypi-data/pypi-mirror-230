from pymssql import connect as sst_connect
from .__sqltool__ import TemplateSQLTool, decrypt
import traceback
import pyodbc


# postgresql执行类
class SqlserverExecutor(TemplateSQLTool):
    def __init__(self, dbname: str, default_lie_class='nvarchar(255)', **connect):
        self.dbname = dbname
        self.connect = connect
        self.host = connect.get('host', '127.0.0.1')
        self.port = connect.get('port', 1433)
        self.user = connect.get('user', 'root')
        self.passwd = connect['password']
        self.charset = connect.get('charset', 'UTF8')  # cp936
        ifassert = connect.pop('ifassert', True)
        iftz = connect.pop('iftz', True)
        self.ifencryption = connect.get('ifencryption', True)
        if self.ifencryption:
            self.passwd = decrypt(self.user, self.passwd)

        # 打开数据库连接
        def db_func():
            db = pyodbc.connect(
                f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.host};DATABASE={self.dbname};UID={self.user};PWD={self.passwd}')  # DRIVER={SQL Server};
            # db = sst_connect(host=self.host, port=self.port,
            #                      user=self.user, password=self.passwd,
            #                      database=self.dbname, charset=self.charset)
            return db

        TemplateSQLTool.__init__(self, db_func, ifassert, iftz, default_lie_class, "1=1", **connect)

    def in_run(self, sql, *datas, if_error_one=True, **kwargs):
        sql = sql.replace('%s', '?')
        try:
            self.cursor.executemany(sql, datas)
            return True
        except Exception as e:
            self.rollback()
            if if_error_one:
                print("\033[0;31m", '批量插入出错,执行单条插入', "\033[0m")
                for i, data in enumerate(datas):
                    try:
                        self.cursor.executemany(sql, [data])
                    except:
                        print("\033[0;32m", sql, "\033[0m")
                        print(f'具体数据出错-index{i}:\n', data)
                        self.rollback()
                        break
            if self.ifassert:
                raise e
            else:
                traceback.print_exc()
            return False

    # 使用sql操作
    def run(self, sql, **kwargs):
        # print(sql)
        sql = sql.replace('%s', '?')
        try:
            self.cursor.execute(sql)
            return True
        except Exception as e:
            print("\033[0;32m", sql, "\033[0m")
            if self.ifassert:
                raise e
            else:
                traceback.print_exc()
            return False

    def getTablestr(self, table, **kwargs):
        if '.' in table:
            t1, t2 = table.split('.')
            return f'[{t1}].[{t2}]'
        else:
            return f'[{table}]'

    def getLiestrs(self, lies, **kwargs):
        if type(lies) == str:
            if lies in {'*', '1', 'count(1)', 'top 1 1'}:
                return [lies]
            else:
                lies = [lies]
        lies = [f"[{lie}]" for lie in lies]
        return lies

    # 判断是否可以查询到
    def ifGet(self, table, where=None, if_error=True, **kwargs):
        try:
            if len(self.select('top 1 1', table, where=where if where else self.default_where,
                               data_class='ls', iftz=False, **kwargs)) > 0:
                return True
            else:
                return False
        except:
            if if_error: traceback.print_exc()
            return False

    def createTable(self, table, lies: list, columnclassdict: dict = None, key=None, **kwargs):
        # CREATE TABLE table_name (column_name column_type);  Create Table If Not Exists
        if columnclassdict is None:
            columnclassdict = {}
        assert len(lies) > 0, "数量有误！"
        # 列类型进行默认赋值
        for lie in lies:
            # 参数自动匹配
            temp = columnclassdict.get(lie, self.default_lie_class)
            if temp.startswith('varchar'):
                temp = temp.replace('varchar', 'nvarchar')
            elif temp == 'text':
                temp = 'ntext'
            columnclassdict[lie] = temp
        # Create Table If Not Exists
        if key is not None:
            if type(key) == str: key = [key]
            if key != '*': key = " ,PRIMARY KEY(%s)" % ','.join(self.getLiestrs(key, **kwargs))
        else:
            key = ''
        # 不再使用null，默认为空字符
        liestr = ",".join([("%s %s " % (self.getLiestrs([lie], **kwargs)[0], columnclassdict[lie]) +
                            ("NOT NULL DEFAULT ''" if 'varchar' in columnclassdict[lie] else ''))
                           for lie in lies])
        sql = '''
            If Not Exists (select * from sysobjects where id = object_id('{table}') and OBJECTPROPERTY(id, 'IsUserTable') = 1)
               Create Table {table}
               ({lies} {key})
           '''.format(table=self.getTablestr(table, **kwargs), lies=liestr, key=key)
        return self.run(sql, **kwargs)

    def deleteTable(self, table, **kwargs):
        # DROP TABLE table_name
        sql = '''
            If Exists (select * from sysobjects where id = object_id('{table}') and OBJECTPROPERTY(id, 'IsUserTable') = 1)
                DROP TABLE {table} 
        '''.format(table=self.getTablestr(table, **kwargs))
        return self.run(sql, **kwargs)

    # 判断表是否存在
    def ifExist(self, table):
        return TemplateSQLTool.ifExist(self, table, def_schema='dbo')
