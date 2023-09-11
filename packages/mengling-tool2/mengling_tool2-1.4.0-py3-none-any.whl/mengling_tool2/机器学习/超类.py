import joblib
import numpy as np

'''
音频
图片
文字
'''


class Sklearn:
    def __init__(self):
        self.model = None

    def getModel(self):
        assert self.model is not None, '模型尚未初始化'
        return self.model

    # 训练
    def training(self, arr: np.ndarray, indexs, **kwargs):
        pass

    # 保存模型
    def saveModel(self, filepath, compress=5):
        assert self.model is not None
        joblib.dump(self.model, filepath, compress=compress)

    # 加载模型
    def loadModel(self, filepath):
        self.model = joblib.load(filepath)

    # 预测
    def predicts(self, arr, ifdetailed=False):
        assert len(arr.shape) == 2
        func = self.model.predict_proba if ifdetailed else self.model.predict
        return func(arr)

    # 综合预测
    def predict_all(self, arr: np.ndarray, indexs) -> float:
        assert arr.shape[0] == len(indexs), f'{arr.shape[0]} {len(indexs)}'
        p = self.model.score(arr, indexs)
        return p
