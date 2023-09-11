import numpy as np
from sklearn.naive_bayes import GaussianNB
from .超类 import Sklearn


# 高斯朴素贝叶斯
# 适合变量参数较少的分类情况
class Conditional(Sklearn):
    def __init__(self):
        Sklearn.__init__(self)

    def training(self, arr: np.ndarray, indexs, var_smoothing=1e-09):
        self.model = GaussianNB(var_smoothing=var_smoothing)
        self.model.fit(arr, indexs)


if __name__ == '__main__':
    from mengling_tool.机器学习.数组处理工具 import load_train_images, load_train_labels, \
        load_test_images, \
        load_test_labels

    gs = Conditional()
    num, testnum = 50000, 1000
    train_arr = load_train_images(num=num)
    train_arr = train_arr.reshape(train_arr.shape[0], 28 * 28)
    gs.training(train_arr, load_train_labels(num))
    test_arr = load_test_images(testnum).reshape(testnum, 28 * 28)
    print(gs.predict_all(test_arr, load_test_labels(testnum)))
