import struct
import numpy as np
from PIL import Image
from sklearn.datasets import make_blobs, make_regression


# 图像转数组
def img_arr(filepath, resize: tuple = None):
    # 打开文件
    image = Image.open(filepath)
    # 压缩
    if resize is not None: image = image.resize(resize, Image.ANTIALIAS)
    img_arr = np.array(image)
    return img_arr


# 数组转图片
def arr_img(arr, filepath, ifsave=True):
    img = Image.fromarray(arr)  # numpy 转 image类
    if img.mode != 'RGB': img = img.convert('RGB')
    if ifsave: img.save(filepath)
    return img


# 获取随机分布数据集样本
# https://scikit-learn.org.cn/view/556.html
# n_samples:行数   n_features:特征数(列数) centers:集块数量(标签种类)
def getRandomBlobs(n_samples, n_features, random_state: int = None, center_num=2, **kwargs):
    arr, indexs = make_blobs(n_samples=n_samples, centers=center_num, n_features=n_features,
                             random_state=random_state, **kwargs)
    return arr, indexs


# 获取随机回归数据集样本
# n_informative:信息特征的数量，即用于构建用于生成输出的线性模型的特征的数量  noise:噪音,数据集混乱程度,默认为0不混乱
def getRandomRegression(n_samples, n_features=1, random_state: int = None, n_informative=10, noise=50, **kwargs) \
        -> (np.ndarray, list):
    xarr, indexs = make_regression(n_samples=n_samples, n_features=n_features, noise=noise,
                                   random_state=random_state, n_informative=n_informative, **kwargs)
    return xarr, indexs


# 按标签拆分数组
def getIndexPartArrs(allarr, indexs) -> list:
    arrdt = dict()
    i = 0
    for index in indexs:
        if arrdt.get(index) is None: arrdt[index] = list()
        arrdt[index].append(allarr[i, :])
        i += 1
    arrs = [np.stack(arrs) for arrs in arrdt.values()]
    return arrs


# 训练集文件
__trainpath0__ = r'D:\python39\训练集'
__train_images_idx3_ubyte_file__ = f'{__trainpath0__}/train-images.idx3-ubyte'
# 训练集标签文件
__train_labels_idx1_ubyte_file__ = f'{__trainpath0__}/train-labels.idx1-ubyte'
# 测试集文件
__test_images_idx3_ubyte_file__ = f'{__trainpath0__}/test-images.idx3-ubyte'
# 测试集标签文件
__test_labels_idx1_ubyte_file__ = f'{__trainpath0__}/test-labels.idx1-ubyte'


def __decode_idx3_ubyte(idx3_ubyte_file, num: int = None):
    # 读取二进制数据
    bin_data = open(idx3_ubyte_file, 'rb').read()
    # 解析文件头信息，依次为魔数、图片数量、每张图片高、每张图片宽
    offset = 0
    fmt_header = '>iiii'  # 因为数据结构中前4行的数据类型都是32位整型，所以采用i格式，但我们需要读取前4行数据，所以需要4个i。我们后面会看到标签集中，只使用2个ii。
    magic_number, images_num, num_rows, num_cols = struct.unpack_from(fmt_header, bin_data, offset)

    # 解析数据集
    image_size = num_rows * num_cols
    offset += struct.calcsize(fmt_header)  # 获得数据在缓存中的指针位置，从前面介绍的数据结构可以看出，读取了前4行之后，指针位置（即偏移位置offset）指向0016。
    fmt_image = '>' + str(
        image_size) + 'B'  # 图像数据像素值的类型为unsigned char型，对应的format格式为B。这里还有加上图像大小784，是为了读取784个B格式数据，如果没有则只会读取一个值（即一副图像中的一个像素值）
    num = num if num is not None and num < images_num else images_num
    images = np.empty((num, num_rows, num_cols))
    for i in range(num):
        images[i] = np.array(struct.unpack_from(fmt_image, bin_data, offset)).reshape((num_rows, num_cols))
        offset += struct.calcsize(fmt_image)
    return images


def __decode_idx1_ubyte(idx1_ubyte_file, num: int = None):
    # 读取二进制数据
    bin_data = open(idx1_ubyte_file, 'rb').read()
    # 解析文件头信息，依次为魔数和标签数
    offset = 0
    fmt_header = '>ii'
    magic_number, images_num = struct.unpack_from(fmt_header, bin_data, offset)

    # 解析数据集
    offset += struct.calcsize(fmt_header)
    fmt_image = '>B'
    num = num if num is not None and num < images_num else images_num
    labels = np.empty(num)
    for i in range(num):
        labels[i] = struct.unpack_from(fmt_image, bin_data, offset)[0]
        offset += struct.calcsize(fmt_image)
    return labels


# 返回三维图像训练数组,num*28*28
def load_train_images(num: int = None, idx_ubyte_file=__train_images_idx3_ubyte_file__):
    return __decode_idx3_ubyte(idx_ubyte_file, num=num)


# 返回图像训练标签组,num
def load_train_labels(num: int = None, idx_ubyte_file=__train_labels_idx1_ubyte_file__):
    return __decode_idx1_ubyte(idx_ubyte_file, num=num)


# 返回三维图像训练数组,num*28*28
def load_test_images(num: int = None, idx_ubyte_file=__test_images_idx3_ubyte_file__):
    return __decode_idx3_ubyte(idx_ubyte_file, num=num)


# 返回图像测试标签组,num
def load_test_labels(num: int = None, idx_ubyte_file=__test_labels_idx1_ubyte_file__):
    return __decode_idx1_ubyte(idx_ubyte_file, num=num)


# 多项式拟合
def polyFitting(xs, indexs, n=2, ifprint=False) -> (np.ndarray, np.poly1d):
    argarr = np.polyfit(xs, indexs, n)
    gs_func = np.poly1d(argarr)
    if ifprint:
        print(gs_func)
    return argarr, gs_func


if __name__ == '__main__':
    x_arr, ys = getRandomRegression(200, random_state=1)
    a, b = polyFitting(x_arr[:, 0], ys, n=1)
    print(a, b(x_arr))
