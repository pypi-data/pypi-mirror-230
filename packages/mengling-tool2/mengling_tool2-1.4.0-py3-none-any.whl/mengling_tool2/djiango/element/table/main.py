import os, json
from django.core.handlers.asgi import ASGIRequest
from django.http import HttpResponse, Http404, FileResponse
from math import ceil
from pandas import DataFrame, ExcelWriter
from io import BytesIO


class Tabler:
    def __init__(self, request: ASGIRequest, sqlt, identifier='`%s`',
                 cookie_name0='table', table_width='', table_height='',
                 helpdt: dict = None):
        self.req = request
        self.sqlt = sqlt
        self.identifier = identifier
        self.cookie_name0 = cookie_name0
        self.table_width = table_width
        self.table_height = table_height
        # self.title = title
        self.helpdt = helpdt if helpdt else dict()
        self.kwdt = {}

    def getWhere(self):
        wheres = [(1, '=', 1)]
        for i in range(self.kwdt.get('find_num', 10)):
            key, value = self.req.GET.get(f'fkey{i}', ''), self.req.GET.get(f'fvalue{i}', '')
            if len(key) > 0 and len(value) > 0:
                value = value.replace("'", "\\'")
                if self.req.GET.get(f'mh{i}', '0') == '1':
                    wheres.append((self.identifier % key, 'like', f'%{value.strip()}%'))
                else:
                    wheres.append((self.identifier % key, '=', value.strip()))
        return ' and '.join(f"{a} {b} '{c}'" for a, b, c in wheres)

    def getOther(self, cellnum: int = None, def_key='', def_down=True):
        page = max(int(self.req.GET.get('page', 1)), 0)
        order_name, order = self.req.GET.get('okey', def_key), self.req.GET.get('ovalue', 'down' if def_down else 'up')
        if len(order_name) > 0:
            other = f'order by {self.identifier % order_name} {"desc" if order == "down" else "asc"} '
        else:
            other = ''
        if cellnum:
            other += f'limit {cellnum} offset {page * cellnum - cellnum}'
        return other

    def getDownload(self, file_path):
        with open(file_path, 'rb') as f:
            try:
                response = HttpResponse(f)
                response['content_type'] = "application/octet-stream"
                response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
                return response
            except Exception:
                raise Http404

    def getDownload_xlsx(self, filename, df: DataFrame):
        try:
            bio = BytesIO()
            writer = ExcelWriter(bio, engine='xlsxwriter')  # 注意安装这个包 pip install xlsxwriter
            df.to_excel(writer)
            writer.save()
            bio.seek(0)
            # bio.read() 不要read出来，否则seek就到文件最后了，导致下载的是空文件
            # 至此，数据已写入bio中
            response = FileResponse(bio)
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = f'attachment;filename="{filename}.xlsx"'
            return response
        except Exception:
            raise Http404

    # 用于合并主数据生成表格
    def _parentRows(self, parent_lies, dts):
        # 同类列数据合并
        key_rows = dict()
        for dt in dts:
            key = tuple(dt.pop(lie, '') for lie in parent_lies)
            if key_rows.get(key) is None: key_rows[key] = list()
            key_rows[key].append(dt)
        # 表格字段生成
        rows = list()
        for key, ch_dts in key_rows.items():
            first = True
            for ch_dt in ch_dts:
                if first:
                    row = dict((lie, {'text': k, 'rowspan': len(ch_dts)}) for k, lie in zip(key, parent_lies))
                    first = False
                else:
                    row = dict((lie, dict()) for lie in parent_lies)
                row.update(ch_dt)
                rows.append(row)
        return rows

    def getData(self, table, lies='*', cellnum=None, data_class='ls', def_key='', def_down=True):
        return self.sqlt.select(lies, table, where=self.getWhere(),
                                other=self.getOther(cellnum, def_key=def_key, def_down=def_down), data_class=data_class)

    def getMaxnum(self, table):
        return self.sqlt.getNum(table, self.getWhere())

    # 新增、修改或删除操作
    def adu_action(self, table, and_where='1=1', sqlt=None):
        if sqlt is None: sqlt = self.sqlt
        print(self.req.body)
        datadt = json.loads(self.req.body)
        # where
        vr = lambda v: v.replace("'", "\\'")
        where = ' and '.join(
            [f"{self.identifier % k}='{vr(v)}'" for k, v in datadt.get('old', dict()).items()] + [and_where])
        if datadt.get('new') is None:
            # 删除操作
            print('删除表数据', table)
            sqlt.delete(table, where=where)
        elif datadt.get('old') is None:
            # 新增操作
            print('新增表数据', table)
            sqlt.insert_create_dt(table, datadt['new'], ifcreate=False)
        else:
            # 修改操作
            print('修改表数据', table)
            sqlt.update_dt(table, datadt['new'], where=where)
        sqlt.commit()

    # 设置增、删、改
    def setADU(self, url, if_add=False, if_update=False, if_del=False, addup_lies=None, select_liedt=None):
        self.kwdt['adu_url'] = url
        self.kwdt['if_add'] = if_add
        self.kwdt['if_update'] = if_update
        self.kwdt['if_del'] = if_del
        self.kwdt['addup_lies'] = addup_lies
        self.kwdt['select_liedt'] = select_liedt

    # 设置下载
    def setDownload(self, url):
        self.kwdt['downloadurl'] = url

    # 设置查找
    def setFinds(self, find_num: int, find_lies: list = None):
        self.kwdt['find_num'] = find_num
        self.kwdt['find_lies'] = find_lies

    # 设置可选项
    def setView(self, if_view, def_view_lies=None):
        self.kwdt['if_view'] = if_view
        self.kwdt['def_view_lies'] = def_view_lies

    # 设置行合并
    def setTableParent(self, parent_lies):
        self.kwdt['parent_lies'] = parent_lies

    def getTable(self, table, cellnum: int, lies='*', rowdts: list = None, maxnum: int = 0,
                 def_key='', def_down=True) -> dict:
        if rowdts is None:
            df = self.getData(table, lies=lies, cellnum=cellnum, data_class='df', def_key=def_key, def_down=def_down)
        else:
            df = DataFrame(data=rowdts)
        df.fillna('', inplace=True)
        rowdts = df.to_dict(orient='records')
        if type(lies) == str:
            lies = list(rowdts[0].keys()) if rowdts else []
        if self.kwdt.get('parent_lies'):
            rowdts = self._parentRows(self.kwdt['parent_lies'], rowdts)
            # 开启合并表格功能后不再允许编辑操作
            self.kwdt['if_add'], self.kwdt['if_update'] = False, False
        page = max(int(self.req.GET.get('page', 1)), 0)

        return {'rowdts': rowdts, 'lies': lies, 'page': page, 'maxpage': ceil(maxnum / cellnum), 'helpdt': self.helpdt,
                'cookie_name0': self.cookie_name0,
                'table_width': self.table_width if self.table_width else '',
                'table_height': self.table_height if self.table_height else '',

                'range_finds': list(range(self.kwdt.get('find_num', 0))),
                'find_lies': self.kwdt['find_lies'] if self.kwdt.get('find_lies') else lies,

                'adu_url': self.kwdt.get('adu_url', ''),
                'if_add': 'true' if self.kwdt.get('if_add') else 'false',
                'if_del': 'true' if self.kwdt.get('if_del') else 'false',
                'if_update': 'true' if self.kwdt.get('if_update') else 'false',
                'addup_lies': self.kwdt['addup_lies'] if self.kwdt.get('addup_lies') else [],
                'select_liedt': self.kwdt['select_liedt'] if self.kwdt.get('select_liedt') else {},

                'downloadurl': self.kwdt['downloadurl'] if self.kwdt.get('downloadurl') else '',

                'if_view': 'true' if self.kwdt.get('if_view') else 'false',
                'def_view_lies': self.kwdt['def_view_lies'] if self.kwdt.get('def_view_lies') else [],
                }
