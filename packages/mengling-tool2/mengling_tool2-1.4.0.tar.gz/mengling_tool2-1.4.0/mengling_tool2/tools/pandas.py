import pandas as pd


# 重写用于进行常用设置的配置
class DataFrameTool:
    def __init__(self, poly_data: pd.DataFrame or str or list, sheet_name=0, if_strip=True):
        # 参数多态化
        tpd = type(poly_data)
        if tpd == pd.DataFrame:
            df = poly_data
        elif tpd == str:
            df = pd.read_excel(poly_data, sheet_name=sheet_name)
        elif tpd == list:
            df = pd.DataFrame(data=poly_data)
        else:
            raise ValueError(f'多态参数:poly_data 类型不正确!{tpd}')
        df.fillna('', inplace=True)
        # 字段清洗
        if if_strip:
            self.df = df.applymap(lambda x: str(x).strip())
        else:
            self.df = df
        self.lies = self.df.columns.values.tolist()
        self.sheet_name = sheet_name

    def to_dict(self, orient="records"):
        return self.df.to_dict(orient=orient)

    def to_excel(self, filename, index=False):
        return self.df.to_excel(filename, index=index)

    def getAllSheet(self):
        return self.df.keys()


def merge_df_to_excel(filename: str, *dfs, sheets: list = None, index=False):
    if sheets is None: sheets = []
    # 名称补齐
    [sheets.append(f'Sheet{i}') for i in range(len(sheets) + 1, len(dfs) + 1)]

    writer = pd.ExcelWriter(filename)
    for df, sheet in zip(dfs, sheets):
        df.to_excel(writer, sheet_name=sheet, index=index)
    # writer.save()
    writer.close()


def merge_dts_to_excel(filename: str, *dtss, sheets: list = None, index=False):
    return merge_df_to_excel(filename, *[pd.DataFrame(data=dts).fillna('') for dts in dtss], sheets=sheets, index=index)
