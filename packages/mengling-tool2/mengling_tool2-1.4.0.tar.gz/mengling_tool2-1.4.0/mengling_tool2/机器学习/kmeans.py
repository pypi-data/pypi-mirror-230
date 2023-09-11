import numpy as np
from sklearn.cluster import KMeans
from .超类 import Sklearn


class Kmeans(Sklearn):
    def __init__(self):
        Sklearn.__init__(self)

    # 设置参数计算相关模型
    def training(self, arr: np.ndarray, center_num, random_state=None, **kwargs):
        self.model = KMeans(n_clusters=center_num, random_state=random_state, **kwargs)
        # 执行聚类
        self.model.fit(arr)

    # 获取分类后的中心点
    def getAllCenters(self):
        return self.model.cluster_centers_

    # 获取分类后的类型标签
    def getAllLabels(self):
        return self.model.labels_

    # 预测
    def predicts(self, arr: np.ndarray, ifit=False):
        assert len(arr.shape) == 2
        if ifit:
            # 聚类影响源模型
            results = self.model.fit_predict(arr)
        else:
            # 不影响原模型预测
            results = self.model.predict(arr)
        return results


if __name__ == '__main__':
    from mengling_tool.机器学习.数组处理工具 import getRandomBlobs
    import mengling_tool.view_tool as viewtool

    km = Kmeans()
    allarr, indexs = getRandomBlobs(200, 2, random_state=1, center_num=5)

    km.training(allarr, 5)
    arrdt = dict()
    i = 0
    print(km.getAllLabels())
    for index in km.getAllLabels():
        if arrdt.get(index) is None: arrdt[index] = list()
        arrdt[index].append(allarr[i, :])
        i += 1
    arrs = [np.stack(arrs) for arrs in arrdt.values()]
    print('集群数:', len(arrs))
    viewtool.graphicalN(*[viewtool.getLoadt(arr[:, 1], xs=arr[:, 0]) for arr in arrs])
    # print(ms.predicts(np.array([[5, 10]])))
