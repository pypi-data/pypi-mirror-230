from numpy import array
from PIL import Image
import numpy as np


# 获取图像对象
def getImg(filepath: str, ifl=True, height=None, width=None, ifauto=False) -> Image:
    img = Image.open(filepath)
    if height is not None or width is not None:
        if ifauto:
            img.thumbnail((img.shape[0] if height is None else height, img.shape[1] if width is None else width),
                          Image.ANTIALIAS)
        else:
            img = img.resize((img.shape[0] if height is None else height, img.shape[1] if width is None else width),
                             Image.ANTIALIAS)
    if ifl: img = img.convert('L')
    return img


# 图像转矩阵数组
def imgToArr(img: Image) -> array:
    return np.asarray(img)


# 矩阵数组转图像
def arrToImg(arr: array) -> Image:
    return Image.fromarray(arr)


# 获取子区域矩阵数组
def getChildArrs(arr: array, cellsize, xn, yn) -> list:
    charrs = list()
    for x in range(0, arr.shape[0] - cellsize + 1, xn):
        templs = []
        for y in range(0, arr.shape[1] - cellsize + 1, yn):
            templs.append(arr[x:x + cellsize, y:y + cellsize])
        charrs.append(templs)
    return charrs
