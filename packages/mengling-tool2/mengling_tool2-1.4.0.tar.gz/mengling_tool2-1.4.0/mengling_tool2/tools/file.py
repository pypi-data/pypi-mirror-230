import os
import os.path as op
import traceback
from datetime import datetime
import easygui
import uuid
import shutil
import xlsxwriter
from PIL import Image
from pandas import DataFrame
import win32com.client as win32
import winreg
import hashlib


# 获取路径大小
def getSize(fpath, unit='kb'):
    if op.isfile(fpath):
        size = op.getsize(fpath)
    else:
        size = 0
        for root, dirs, files in os.walk(fpath):
            size += sum([op.getsize(op.join(root, name)) for name in files])
    if unit == 'kb':
        size /= 1024
    elif unit == 'mb':
        size /= 1024 * 1024
    elif unit == 'b':
        size = size
    else:
        assert False, '单位应为b或kb或mb'
    return round(size, 2)  # 四舍五入取小数点位后2位


# 获取路径时间信息字典
def getTimeDict(fpath):
    # ("文件名", "创建时间", "修改时间", "访问时间")
    ctime = op.getctime(fpath)
    xtime = op.getmtime(fpath)
    atime = op.getatime(fpath)
    time_dict = {"创建时间": datetime.fromtimestamp(ctime).strftime("%Y/%m/%d_%H:%M:%S"),
                 "修改时间": datetime.fromtimestamp(xtime).strftime("%Y/%m/%d_%H:%M:%S"),
                 "访问时间": datetime.fromtimestamp(atime).strftime("%Y/%m/%d_%H:%M:%S")}
    return time_dict


# 获取当前目录下完整的子类信息
def getDirChilds(path, ifmerge=True) -> (list, list):
    try:
        root, dirps, files = next(os.walk(path))
        # 是否将路径及文件名称合并
        if ifmerge:
            fulldirs = [f'{root}\\{dirp}' for dirp in dirps]
            fullfiles = [f'{root}\\{file}' for file in files]
        else:
            fulldirs = [(root, dirp) for dirp in dirps]
            fullfiles = [(root, file) for file in files]
    except:
        traceback.print_exc()  # 直接打印出来
        print('[路径遍历出错]', path)
        fulldirs, fullfiles = [], []
    return fulldirs, fullfiles


# 获取目录下完整的子类信息
def getAllFiles(path, ifmerge=True) -> list:
    all_files = list()
    for root, dirps, files in os.walk(path):
        for file in files:
            # 是否将路径及文件名称合并
            if ifmerge:
                all_files.append(f'{root}\\{file}')
            else:
                all_files.append((root, file))
    return all_files


# 对目录下的全部文件进行时间排序
def sortTimeDatas(path, timeclass='修改时间', **kwargs):
    reverse = kwargs.get('reverse', False)
    # None为全部格式文件
    fileclass = kwargs.get('fileclass', None)
    if fileclass is not None and type(fileclass) == str: fileclass = [fileclass]
    print('[排序文件类型]', '全部文件' if fileclass is None else fileclass)
    assert timeclass in ['创建时间', '修改时间', '访问时间'], 'timeclass应为 创建时间、修改时间、访问时间'
    fulldirs, fullfiles = getAllFiles(path)
    # 广度优先遍历全部子目录
    while len(fulldirs) > 0:
        tempdirs = fulldirs
        fulldirs = []
        for dir in tempdirs:
            dirs, files = getAllFiles(dir)
            fullfiles.extend(files)
            fulldirs.extend(dirs)
    timedts, times = list(), list()
    for file in fullfiles:
        # 过滤不满足文件类型的文件
        if fileclass is not None and file.split('.')[-1] not in fileclass:
            continue
        else:
            tdt = getTimeDict(file)
            tdt['文件'] = file
            timedts.append(tdt)
            times.append(tdt[timeclass])
    # 根据所算时间类型进行排序
    times.sort(reverse=reverse)
    length = len(times)
    ttable = dict()
    for i in range(length):
        ttable[times[i]] = ttable.get(times[i], [])
        ttable[times[i]].append(i)
    results = [None for i in range(length)]
    # 排序位置
    for i in range(length):
        value = timedts.pop(0)
        index = ttable[value[timeclass]].pop(0)
        results[index] = value
    print('[数据量]', len(results))
    [print(result) for result in results]


# 获取选择的路径
def getSelectPath(default=None):
    path = easygui.diropenbox(default=default)
    return path


# 获取选择的文件
def getSelectFile(default=None, filetypes: list = None):
    filepath = easygui.fileopenbox(default=default, filetypes=filetypes)
    return filepath


def timeRAR(targetpath, path, filename=''):
    assert '\\' in path, '路径中需要使用\\!'
    assert ' ' not in targetpath and ' ' not in path and ' ' not in filename, '不能有空格!'

    def ifhaveHZ(str):
        for ch in str:
            if '\u4e00' <= ch <= '\u9fff': return True
        return False

    assert not ifhaveHZ(targetpath + path + filename), '不能有中文!'

    name = filename.split('.')[0] if filename != '' else path.split('\\')[-1]
    # 增加时间后缀
    name += '_' + datetime.today().strftime("%Y%m%d")
    ml = f'"\"C:\\WinRAR\\WinRAR.exe\" a -r -ep1 -or \"{targetpath}\\{name}.rar\" \"{path}\\{filename}\""'.encode(
        'utf-8').decode('ASCII')
    # tzs.emailSend('test', ml)
    os.system(ml)


# 具体文件全名进行uuid的计算
def getUUID(filepath):
    return uuid.uuid3(uuid.NAMESPACE_DNS, filepath).hex


def copy(fillepath, targetpath):
    return shutil.copyfile(fillepath, targetpath)


def move(fillepath, targetpath):
    return shutil.move(fillepath, targetpath)


def rename(filepath, newname):
    path, filename = os.path.split(filepath)
    name, extension = os.path.splitext(filename)
    return shutil.move(filepath, f'{path}\\{newname}{extension}')


def remove(filepath):
    return shutil.rmtree(filepath)  # 删除文件夹下所有文件,优先选用


def getFileSplitName(filepath) -> (str, str, str):
    path, filename = os.path.split(filepath)
    name, extension = os.path.splitext(filename)
    return path, name, extension


def ifExist(path, ifcreate=False):
    ife = os.path.exists(path)
    if not ife and ifcreate: os.makedirs(path)  # 新建文件目录
    return ife


def get_desktop():
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
    return winreg.QueryValueEx(key, "Desktop")[0]


# 读取加密的excel文件
def getPasswordExcel(filename, password, sheetname, gl_excel_com="Excel.Application") -> DataFrame:
    #    文件路径中不能使用中文
    """
    gl_excel_com：不同配置的Excel-COM 参数，WPS excel用'KET.Application',
            MS office Excel文件用'Excel.Application'
    """
    psw_xlsx = win32.DispatchEx(gl_excel_com)  # 这个功能创建新进程，不会打扰用户手动进程
    psw_xlsx.DisplayAlerts = 0  # 不显示警告,SaveAS的弹框就不出来了。
    wb = psw_xlsx.Workbooks.Open(filename, UpdateLinks=False, ReadOnly=False, Format=None, Password=password,
                                 WriteResPassword=password)
    # 获取工作表具体情况
    data_lst = list(wb.Worksheets(sheetname).UsedRange())  # 数据存入,"原始数据"，2-"借贷求和计数"...数字与表名可以互换
    # 去除全为None的行
    for index in range(len(data_lst)):
        if all(data is None for data in data_lst[index]):
            break
    df = DataFrame(data_lst[1:index], columns=data_lst[0])
    wb.Close()
    psw_xlsx.DisplayAlerts = 1
    psw_xlsx.Application.Quit()  # 只清掉我自己开启的进程
    return df  # 返回的excel表数据形成的df.


# 获取文件md5值,更改文件名及扩展名不影响
def getFileMd5(filename, ceil_size: int = 1024 * 500) -> str:
    d5 = hashlib.md5()
    with open(filename, 'rb') as file:
        data = file.read(ceil_size)
        while data:
            d5.update(data)
            data = file.read(ceil_size)
    return d5.hexdigest()


def createXlsx(datadts: list, markfile_path: str, pic_lies: list = None, sheet_name: str = None, h=50, w=13,iftz=True):
    # 取第一行数据作为列顺序
    lies = list(datadts[0].keys())
    book = xlsxwriter.Workbook(markfile_path)
    sheet = book.add_worksheet(sheet_name)
    str_format = book.add_format({
        # 'bold': True,  # 字体加粗
        # 'align': 'center',  # 水平位置设置：居中
        'valign': 'vcenter',  # 垂直位置设置，居中
        # 'font_size': 14,  # '字体大小设置'
    })
    lie_format = book.add_format({
        'bold': True,  # 字体加粗
        'align': 'center',  # 水平位置设置：居中
        'valign': 'vcenter',  # 垂直位置设置，居中
        # 'font_size': 14,  # '字体大小设置'
    })
    row = 0
    # 构建列
    [sheet.write_string(row, i, lies[i], lie_format) for i in range(len(lies))]
    row += 1
    temp_pics = list()
    for dt in datadts:
        sheet.set_row(row, h)
        for col in range(len(lies)):
            lie = lies[col]
            value = dt.get(lie, '')
            if len(value) > 0 and pic_lies and lie in pic_lies:
                try:
                    img = Image.open(value)
                    x, y = img.size
                    if x > 256:
                        y *= 256 / x
                        x = 256
                    if y > 256:
                        x *= 256 / y
                        y = 256
                    img = img.resize((int(x),int(y)), Image.ANTIALIAS)
                    path, filename = os.path.split(value)
                    name, extension = os.path.splitext(filename)
                    temp_path = f'{path}/{name}_temp{extension}'
                    img.save(temp_path)
                    sheet.insert_image(row, col, temp_path)
                    # 设置表格尺寸
                    sheet.set_row(row, 200)
                    sheet.set_column(col, col, 35.5)
                    temp_pics.append(temp_path)
                except:
                    if iftz: traceback.print_exc()
                    # print('图片数据应为图片路径', row, col, dt[lie])
            else:
                sheet.set_column(col, col, w)
                sheet.write(row, col, value, str_format)
        row += 1
    book.close()
    # 删除临时文件
    [os.remove(pic) for pic in temp_pics]


def createXlsx_df(df: DataFrame, markfile_path: str, pic_lies: list = None, sheet_name: str = None, h=50, w=13):
    dts = list()
    for index, row in df.iterrows():
        dts.append(row.to_dict())
    return createXlsx(dts, markfile_path, pic_lies, sheet_name, h=h, w=w)


if __name__ == '__main__':
    dir = r'D:'
    # print(isfile(dir))  # 只判断文件 返回bool类型
    # print(getSize(dir))
    # print(getTimeDict(dir))
    sortTimeDatas(dir, '修改时间')
