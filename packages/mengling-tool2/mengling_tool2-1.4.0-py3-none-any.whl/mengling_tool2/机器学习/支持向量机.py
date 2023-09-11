import numpy as np
import sklearn.svm as svm
from .超类 import Sklearn


class SVC(Sklearn):
    def __init__(self):
        Sklearn.__init__(self)

    def training(self, arr: np.ndarray, indexs, kernel='linear', c=1.0, **kwargs):
        self.model = svm.SVC(kernel=kernel, C=c, probability=True, **kwargs)
        self.model.fit(arr, indexs)

    # 获取支持向量
    def getSupportps(self):
        return self.model.support_vectors_

    # 获取每个类别的支持向量数量
    def getSupportpnum(self):
        return self.model.n_support_


if __name__ == '__main__':
    from mengling_tool.机器学习.数组处理工具 import load_train_images, load_train_labels, \
        load_test_images, \
        load_test_labels

    svc = SVC()
    # allarr, indexs = getRandomBlobs(200, 2, random_state=1, centers=5)
    #
    # svc.training(allarr, indexs, kernel=svc.kernels[0], c=1)
    #
    # arrs = getIndexPartArrs(allarr, svc.predicts(allarr))
    # print('集群数:', len(arrs))
    #
    # viewtool.graphicalN(*[viewtool.getLoadt(arr[:, 1], xs=arr[:, 0]) for arr in arrs])

    num, testnum = 5000, 100
    train_arr = load_train_images(num=num)
    train_arr = train_arr.reshape(train_arr.shape[0], 28 * 28)
    svc.training(train_arr, load_train_labels(num))
    test_arr = load_test_images(testnum).reshape(testnum, 28 * 28)
    print(svc.predict_all(test_arr, load_test_labels(testnum)))
