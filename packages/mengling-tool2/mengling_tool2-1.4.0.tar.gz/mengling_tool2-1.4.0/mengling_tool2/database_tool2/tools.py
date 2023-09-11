from .__sqltool__ import TemplateSQLTool
import json


# 数据保存工具
class DataUpdateSave:
    def __init__(self, sqlt: TemplateSQLTool, main_keys: list, iftz=True):
        self.sqlt = sqlt
        self.main_keys = main_keys
        self.iftz = iftz

    def getWhere(self, datadts):
        assert datadts
        wheres = []
        for dt in datadts:
            txt = "','".join([str(dt[k]) for k in self.main_keys])
            wheres.append("('" + txt + "')")
        # 删除主表主键数据
        where = f"({','.join(self.sqlt.getLiestrs(self.main_keys))}) in ({','.join(wheres)})"
        return where

    def getChildDts(self, datadts, chlie, if_pop=True) -> list:
        all_chls = []
        for dt in datadts:
            if if_pop:
                chls = dt.pop(chlie, [])
            else:
                chls = dt.get(chlie, [])
            # 自动转换
            if type(chls) == str: chls = json.loads(chls)
            for key in self.main_keys:
                for chdt in chls:
                    chdt[key] = dt[key]
            all_chls.extend(chls)
        return all_chls

    def updateMain(self, datadts, table, json_lies: list = (), colmap: dict = {}):
        if not datadts:
            if self.iftz: print('没有主数据')
            return False
        where = self.getWhere(datadts)
        if self.sqlt.ifExist(table):
            if self.iftz: print('删除主表主键')
            self.sqlt.delete(table, where)
        else:
            if self.iftz: print('暂无主表:', table)
        for lie in json_lies:
            colmap[lie] = 'text'
            for dt in datadts:
                dt[lie] = json.dumps(dt.get(lie, ''), ensure_ascii=False)
        # 插入数据
        self.sqlt.insert_create_dt(table, *datadts, colmap=colmap, key=self.main_keys)
        if self.iftz: print(table, '主表数据量:', len(datadts))

    def updateChild(self, datadts, child_table, chlie, if_pop=True, colmap=None):
        chdts = self.getChildDts(datadts, chlie, if_pop=if_pop)
        if chdts:
            where = self.getWhere(datadts)
            if self.sqlt.ifExist(child_table):
                if self.iftz: print('删除子表主键')
                self.sqlt.delete(child_table, where)
            else:
                if self.iftz: print('暂无子表:', child_table)
            # 插入数据
            self.sqlt.insert_create_dt(child_table, *chdts, colmap=colmap)
            if self.iftz: print(child_table, '子表数据量:', len(chdts))
        else:
            if self.iftz: print('没有子表数据!')

    def commit(self):
        self.sqlt.commit()
        if self.iftz: print('提交成功!')
