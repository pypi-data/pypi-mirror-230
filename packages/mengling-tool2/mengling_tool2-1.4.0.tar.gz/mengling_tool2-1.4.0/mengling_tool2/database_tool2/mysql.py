from pymysql import connect as myt_connect
from .__sqltool__ import TemplateSQLTool, decrypt


# mysql执行类
class MysqlExecutor(TemplateSQLTool):
    def __init__(self, dbname: str, **connect):
        self.dbname = dbname
        self.connect = connect
        self.host = connect.get('host', '127.0.0.1')
        self.port = connect.get('port', 3306)
        self.user = connect.get('user', 'root')
        self.passwd = connect['password']
        self.charset = connect.get('charset', 'utf8mb4')
        ifassert = connect.pop('ifassert', True)
        iftz = connect.pop('iftz', True)
        self.ifencryption = connect.get('ifencryption', True)
        if self.ifencryption: self.passwd = decrypt(self.user, self.passwd)
        # 打开数据库连接
        db_func = lambda: myt_connect(host=self.host, port=self.port,
                                          user=self.user, passwd=self.passwd,
                                          db=self.dbname, charset=self.charset)
        TemplateSQLTool.__init__(self, db_func, ifassert, iftz,**connect)

    def run(self, sql, **kwargs):
        # 设置重连
        self.db.ping(reconnect=True)
        return TemplateSQLTool.run(self, sql, **kwargs)

    def in_run(self, sql, *datas, if_error_one=True, **kwargs):
        # 设置重连
        self.db.ping(reconnect=True)
        return TemplateSQLTool.in_run(self, sql, *datas, if_error_one=if_error_one, **kwargs)

    def commit(self):
        # 设置重连
        self.db.ping(reconnect=True)
        return TemplateSQLTool.commit(self)

    def getTablestr(self, table, **kwargs):
        return '`%s`' % table

    def getLiestrs(self, lies, **kwargs):
        if type(lies) == str:
            if lies in {'*', '1', 'count(1)'}:
                return [lies]
            else:
                lies = [lies]
        lies = [f"`{lie.replace('%', '%%')}`" for lie in lies]
        return lies

    def createTable(self, table, lies: list, colmap: dict = None, key=None, ifmyisam=False, **kwargs):
        b = TemplateSQLTool.createTable(self, table, lies, colmap=colmap, key=key, **kwargs)
        # 使用MyISAM引擎具有更强的读写速度,但是不支持事物
        if ifmyisam: self.run(f'ALTER TABLE {self.getTablestr(table)} ENGINE = MyISAM')
        return b

    def ifExist(self, table):
        b = self.run(f'show tables like "{table}"')
        return b and len(self.cursor.fetchall()) > 0

# 测试
if __name__ == "__main__":
    pass
