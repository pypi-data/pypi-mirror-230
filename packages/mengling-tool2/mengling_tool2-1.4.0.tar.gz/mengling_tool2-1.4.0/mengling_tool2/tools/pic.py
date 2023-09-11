import base64
import re
import xml.etree.ElementTree as ET
import zipfile
import cv2
import pytesseract
from PIL import Image, ImageEnhance
import numpy as np


def pic_to_str(filepath, resize_num=1, b=1.0,
               config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwsyz#$%'):
    """
    :param filepath: 文件路径
    :param filename:图片名
    :param resize_num:缩放倍数
    :param b:对比度
    :return:返回图片识别文字
    """
    im = Image.open(filepath)
    # 图像放大
    im = im.resize((im.width * int(resize_num), im.height * int(resize_num)))
    # 图像二值化
    imgry = im.convert('L')
    # 对比度增强
    sharpness = ImageEnhance.Contrast(imgry)
    sharp_img = sharpness.enhance(b)
    # sharp_img.save('test.png')
    content = pytesseract.image_to_string(sharp_img, lang='eng', config=config)

    return content.replace(' ', '').strip()


def getImgArr(filepath, ifgry=True, reshape: tuple = None):
    img = Image.open(filepath)
    # 灰度处理
    if ifgry: img = img.convert('L')
    if reshape: img.resize((reshape[1], reshape[0]), Image.ANTIALIAS)
    return np.asarray(img)


def arr_to_img(arr):
    return Image.fromarray(np.uint8(arr))


def img_base64(imgpath):
    with open(imgpath, "rb") as f:  # 转为二进制格式
        base64_data = base64.b64encode(f.read())  # 使用base64进行加密
        bstr = base64_data
    return bstr.decode()


def base64_img(base64_str, path, name):
    try:
        ##前缀可能需要先删除
        hz = re.findall('^data:image/(.+?);base64,', base64_str)[0]
    except:
        # 默认jpg
        hz = 'jpg'
    imgpath = '{}/{}.{}'.format(path, name, hz)
    with open(imgpath, "wb+") as f:
        imgdata = base64.b64decode(base64_str)
        f.write(imgdata)


# 获取图片分辨率
def getShape(filepath) -> tuple:
    img = Image.open(filepath)
    return img.size


# 改变图片分辨率
def picResize(picpath: str, width: int, height: int, newpath: str = None):
    image = Image.open(picpath)
    # 压缩,高质量
    image = image.resize((width, height), Image.ANTIALIAS)
    image.save(picpath if newpath is None else newpath)


# 图片混合(权重)
def imgAdd(picpath1, picpath2, mark_picpath, weight1: float = 0.5, weight2: float = 0.5):
    img1 = cv2.imread(picpath1)
    img2 = cv2.imread(picpath2)
    img3 = cv2.addWeighted(img1, weight1, img2, weight2, 0)
    cv2.imwrite(mark_picpath, img3)


# 提取excel中图片,索引坐标为键
def getExcelPicdt(file_path: str) -> dict:
    xml_name = 'xl/drawings/drawing1.xml'
    pic0 = 'xl/media/image%s.png'
    ns = {'i': 'http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing',
          'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
          'r': 'http://schemas.openxmlformats.org/drawingml/2006/relationships'}
    with zipfile.ZipFile(file_path, 'r') as fz:
        xml_string = fz.read(xml_name).decode()
        xml = ET.fromstring(xml_string)
        nodes = xml.findall('.//i:twoCellAnchor', ns)  # 找到⽗节点，再遍历⼦节点
        redt = dict()
        for node in nodes:
            # 以第一行数据索引计为0,与loc同步
            hang = int(node.find('.//i:from/i:row', ns).text) - 1  # 获取⾏索引
            lie = int(node.find('.//i:from/i:col', ns).text)  # 获取列索引
            rid = node.find('.//i:blipFill/a:blip', ns).attrib[
                '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed'] \
                .replace('rId', '')  # 获取图⽚资源序号
            redt[(hang, lie)] = redt.get((hang, lie), [])
            # 保存图片为base64格式
            redt[(hang, lie)].append(base64.b64encode(fz.read(pic0 % rid)).decode())
        return redt


if __name__ == '__main__':
    filepath = r'C:\Users\Administrator\Desktop\test.jpg'
    # image = Image.open(filepath)
    # code = pytesseract.image_to_string(image)
    # print(code.replace('\n', '').replace('\f', ''))

    content = pic_to_str(filepath)
    print(content)
