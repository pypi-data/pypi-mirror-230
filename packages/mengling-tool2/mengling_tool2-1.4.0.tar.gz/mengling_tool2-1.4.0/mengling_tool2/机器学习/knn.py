from sklearn.neighbors import KNeighborsClassifier
import numpy as np
from .超类 import Sklearn


class KNN(Sklearn):
    def __init__(self):
        Sklearn.__init__(self)

    # 训练模型,数组为一行二维数组
    def training(self, arr: np.ndarray, indexs, n_neighbors=5, algorithm='auto', **kwargs):
        assert arr.shape[0] == len(indexs)
        self.model = KNeighborsClassifier(n_neighbors=n_neighbors, algorithm=algorithm, **kwargs)
        self.model.fit(arr, indexs)


if __name__ == '__main__':
    from os import listdir
    import traceback
    from mengling_tool.机器学习.数组处理工具 import img_arr, load_train_images, load_train_labels, load_test_images, \
        load_test_labels

    knn = KNN()
    num, testnum = 50000, 10
    train_arr = load_train_images(num=num)
    train_arr = train_arr.reshape(train_arr.shape[0], 28 * 28)
    knn.training(train_arr, load_train_labels(num), n_neighbors=3)
    # knn.saveModel(r'F:\temp\model.knn', compress=5)
    test_arr = load_test_images(testnum).reshape(testnum, 28 * 28)
    print(knn.predict_all(test_arr, load_test_labels(testnum)))
