# -*- coding: UTF-8 -*-

from psycopg2 import connect as pgt_connect
from .__sqltool__ import TemplateSQLTool, decrypt


# postgresql执行类
class PostgresqlExecutor(TemplateSQLTool):
    def __init__(self, dbname: str, **connect):
        self.dbname = dbname
        self.connect = connect
        self.host = connect.get('host', '127.0.0.1')
        self.port = connect.get('port', 5432)
        self.user = connect.get('user', 'postgres')
        self.passwd = connect['password']
        self.charset = connect.get('charset', 'UTF8')
        ifassert = connect.pop('ifassert', True)
        iftz = connect.pop('iftz', False)
        self.ifencryption = connect.get('ifencryption', True)
        if self.ifencryption:
            self.passwd = decrypt(self.user, self.passwd)

        # 打开数据库连接
        def db_func():
            db = pgt_connect(host=self.host, port=self.port,
                             user=self.user, password=self.passwd,
                             database=self.dbname)
            db.set_client_encoding(self.charset)
            return db

        TemplateSQLTool.__init__(self, db_func, ifassert, iftz, **connect)

    def getTablestr(self, table, **kwargs):
        if '.' in table:
            t1, t2 = table.split('.')
            return f'"{t1}"."{t2}"'
        else:
            return f'"{table}"'

    def getLiestrs(self, lies, **kwargs):
        if type(lies) == str:
            if lies in {'*', '1', 'count(1)'}:
                return [lies]
            else:
                lies = [lies]
        lies = [f'"{lie}"' for lie in lies]
        return lies

    # 创建物化视图
    def createMaterializedView(self, view_name, run_sql):
        self.run(f'create materialized view "{view_name}" as {run_sql}')

    # 创建唯一约束
    pass

    # 刷新物化视图
    def refreshMaterializedView(self, view_name, if_lock=True):
        # 使用CONCURRENTLY的物化索引必须具有 unique 约束,否则会报错
        self.run(f'REFRESH MATERIALIZED VIEW {"" if if_lock else "CONCURRENTLY"} "{view_name}"')

    # 删除物化视图
    def deleteMaterializedView(self, view_name):
        self.run(f'drop materialized view if exists {view_name}')

    def createTable(self, table, lies: list = None, columnclassdict: dict = None, colmap: dict = None, key=None,
                    hz: str = None, parentable_valuetxt: tuple = None, **kwargs):
        if parentable_valuetxt:
            parent_table, valuetxt = parentable_valuetxt
            return self.createTable_child(table, parent_table, valuetxt, **kwargs)
        else:
            return TemplateSQLTool.createTable(self, table, lies, hz=hz,
                                               columnclassdict=columnclassdict, colmap=colmap, key=key, **kwargs)

    def createTable_copy(self, table, copy_table, **kwargs):
        # 子表与父表结构保持一致
        sql = f'CREATE TABLE If Not Exists {self.getTablestr(table)} (LIKE {self.getTablestr(copy_table)} including all)'
        return self.run(sql, **kwargs)

    def createTable_parent(self, table, lies: list, key_lie: str, columnclassdict: dict = None, colmap: dict = None,
                           key=None, map_class='list', **kwargs):  # range
        # 分区父表
        return TemplateSQLTool.createTable(self, table, lies, hz=f"PARTITION BY {map_class} (\"{key_lie}\")",
                                           columnclassdict=columnclassdict, colmap=colmap, key=key, **kwargs)

    def createTable_child(self, table, parent_table, valuetxt, **kwargs):
        # 分区子表
        sql = f'CREATE TABLE If Not Exists {self.getTablestr(table)} PARTITION of {self.getTablestr(parent_table)} FOR values {valuetxt}'  # in ('123') from ('123') to ('125')
        return self.run(sql, **kwargs)

    # 解除子表分区关系
    def detachPartition(self, parentable, childtable):
        sql = f"ALTER TABLE {self.getTablestr(parentable)} detach PARTITION {self.getTablestr(childtable)}"
        return self.run(sql)

    # 绑定子表分区关系
    def attachPartition(self, parentable, childtable, valuetxt):
        sql = f"ALTER TABLE {self.getTablestr(parentable)} attach PARTITION {self.getTablestr(childtable)} FOR VALUES {valuetxt}"
        return self.run(sql)

    # 判断表是否存在
    def ifExist(self, table):
        return TemplateSQLTool.ifExist(self, table, def_schema='public')