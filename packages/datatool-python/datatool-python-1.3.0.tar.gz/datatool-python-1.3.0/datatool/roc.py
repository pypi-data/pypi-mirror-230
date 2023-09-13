"""
There is a was to work with ROC-curves: creation, plotting,
searching for the coordinates of the points.
"""

from operator import itemgetter

import numpy as np
import matplotlib.pyplot as plt


class ROC:
    """
    A class for working with a ROC-curve.

    Example:

        ...
        proba = clf.predict_proba(X)

        roc = ROC()
        roc.build(proba, y)
        print(roc.auc())
        print(roc.gini())
        roc.plot()
    """

    def __init__(self):
        self._indexes = None
        self._roc_x = None
        self._roc_y = None

    def auc(self):
        """
        Calculates AUC of the curve.
        """
        return self._roc_y[1:].dot(self._roc_x[1:] - self._roc_x[:-1])

    def gini(self):
        """
        Calculates GINI value of the curve.
        """
        return 2.0 * self.auc() - 1.0

    def indexes(self):
        """
        Returns indices that corresponds to sorted rows by given 'proba'
        in 'build' method.
        """
        return self._indexes

    def build(self, proba, target):
        """
        Creates a ROC-curve by given proba sequence (for example,
        returned from a classifier model) and actual target sequence.
        """
        assert len(proba) == len(target)

        size = len(target)
        items = list(zip(proba, target, range(size)))
        items.sort(key=itemgetter(0), reverse=True)

        self._indexes = np.array(map(itemgetter(2), items))

        x = [0]
        y = [0]
        for _, t, _ in items:
            x.append(x[-1] + 1 - t)
            y.append(y[-1] + t)

        self._roc_x = np.array(x) / x[-1]
        self._roc_y = np.array(y) / y[-1]

    def plot(self, save_path=None):
        """
        Plots the curve.
        """
        plt.figure(figsize=(8, 8))
        plt.plot([0, 1], [0, 1], 'r--', linewidth=2)
        plt.plot(self._roc_x, self._roc_y, linewidth=2)
        plt.grid(True)
        plt.xlabel("FPR")
        plt.ylabel("TPR")
        plt.title(f"AUC = {round(self.auc(), 2)}, "
                  f"GINI = {round(self.gini(), 2)}")
        if save_path:
            plt.savefig(save_path)
        plt.show()
