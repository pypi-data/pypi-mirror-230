import anndata
import matplotlib.pyplot as plt
import numpy as np

#细胞簇比例
def population_ratio(adata: anndata.AnnData,
                     x: str,
                     y: str,
                     *,
                     normalize=True,
                     path=None,
                     Legend=True,
                     figsize=(6, 3)
                     ):
    adata1 = adata.obs
    df = adata1[[x, y]]
    x_items = df[x].cat.categories.tolist()
    y_items = df[y].cat.categories.tolist()
    y_dict = df[y].value_counts().to_dict()

    heights = []
    for x_item in x_items:
        tmp_result = []
        x_item_counter = df[df[x] == x_item][y].value_counts().to_dict()
        for y_item in y_items:
            tmp_result.append(x_item_counter.get(y_item, 0))
        heights.append(tmp_result)
    heights = np.asarray(heights)
    if normalize:
        heights = heights / np.sum(heights, axis=0)
    heights = (heights.T / np.sum(heights, axis=1)).T
    plt.figure(figsize=figsize)
    _last = np.matrix([0.] * heights.shape[0])
    for i, y_item in enumerate(y_items):
        p = plt.bar(range(0, heights.shape[0]), heights[:, i],
                    bottom=np.asarray(_last)[0],
                    label=y_item
                    )
        _last = _last + np.matrix(heights[:, i])
    plt.xticks(range(0, len(x_items)), labels=x_items, rotation=70)
    plt.ylim((0, 1))
    if Legend:
        plt.legend()
        ax = plt.gca()
        ax.legend(bbox_to_anchor=(0.65, 0, 0.5, 1))
    if path is not None:
        plt.savefig(path, dpi=600)