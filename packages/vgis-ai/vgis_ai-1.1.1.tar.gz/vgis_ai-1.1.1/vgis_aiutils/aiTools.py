"""
#!/usr/bin/python3.9
# -*- coding: utf-8 -*-
@Project :pythonCodeSnippet
@File    :aiTools.py
@IDE     :PyCharm
@Author  :chenxw
@Date    :2023/9/13 11:53
@Descr:
"""
import numpy as np


class AIHelper:
    def __init__(self):
        pass

    @staticmethod
    # 计算一个 ground truth 边界盒和 k 个先验框(Anchor)的交并比(IOU)值。
    def __iou(box, clusters):
        """
        计算一个 ground truth 边界盒和 k 个先验框(Anchor)的交并比(IOU)值。
        参数box: 元组或者数据，代表 ground truth 的长宽。
        参数clusters: 形如(k,2)的numpy数组，其中k是聚类Anchor框的个数
        返回：ground truth和每个Anchor框的交并比。
        """
        x = np.minimum(clusters[:, 0], box[0])
        y = np.minimum(clusters[:, 1], box[1])
        if np.count_nonzero(x == 0) > 0 or np.count_nonzero(y == 0) > 0:
            raise ValueError("Box has no area")
        intersection = x * y
        box_area = box[0] * box[1]
        cluster_area = clusters[:, 0] * clusters[:, 1]
        iou_ = intersection / (box_area + cluster_area - intersection)
        return iou_

        # 计算一个ground truth和k个Anchor的交并比的均值。

    @staticmethod
    def avg_iou(boxes, clusters):
        """
        计算一个ground truth和k个Anchor的交并比的均值。
        """
        return np.mean([np.max(AIHelper.__iou(boxes[i], clusters)) for i in range(boxes.shape[0])])

        # 利用IOU值进行K-means聚类

    @staticmethod
    def kmeans(boxes, k, dist=np.median):
        """
        利用IOU值进行K-means聚类
        参数boxes: 形状为(r, 2)的ground truth框，其中r是ground truth的个数
        参数k: Anchor的个数
        参数dist: 距离函数
        返回值：形状为(k, 2)的k个Anchor框
        """
        # 即是上面提到的r
        rows = boxes.shape[0]
        # 距离数组，计算每个ground truth和k个Anchor的距离
        distances = np.empty((rows, k))
        # 上一次每个ground truth"距离"最近的Anchor索引
        last_clusters = np.zeros((rows,))
        # 设置随机数种子
        np.random.seed()

        # 初始化聚类中心，k个簇，从r个ground truth随机选k个
        clusters = boxes[np.random.choice(rows, k, replace=False)]
        # 开始聚类
        while True:
            # 计算每个ground truth和k个Anchor的距离，用1-IOU(box,anchor)来计算
            for row in range(rows):
                distances[row] = 1 - AIHelper.__iou(boxes[row], clusters)
            # 对每个ground truth，选取距离最小的那个Anchor，并存下索引
            nearest_clusters = np.argmin(distances, axis=1)
            # 如果当前每个ground truth"距离"最近的Anchor索引和上一次一样，聚类结束
            if (last_clusters == nearest_clusters).all():
                break
            # 更新簇中心为簇里面所有的ground truth框的均值
            for cluster in range(k):
                clusters[cluster] = dist(boxes[nearest_clusters == cluster], axis=0)
            # 更新每个ground truth"距离"最近的Anchor索引
            last_clusters = nearest_clusters

        return clusters