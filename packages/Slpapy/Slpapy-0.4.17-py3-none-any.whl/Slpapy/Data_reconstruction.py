import csv
import os
import anndata as ad
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from typing import Optional

def resave(input_file, head):
    # 指定输入和输出文件路径
    input_file = str(input_file)
    output_file = f'{input_file}' + "-1.csv"

    # 增加字段大小限制
    csv.field_size_limit(104857600)  # 100MB

    # 打开输入和输出文件
    with open(input_file, 'r', encoding='utf-8') as input_csv_file, open(output_file, 'w', newline='',
                                                                         encoding='utf-8') as output_csv_file:
        # 创建CSV读取器和写入器对象
        input_csv_reader = csv.reader(input_csv_file, delimiter=';')
        output_csv_writer = csv.writer(output_csv_file)

        # 跳过前6行
        for _ in range(int(head)):
            next(input_csv_reader)

        # 逐行读取并写入新的CSV文件
        for row in input_csv_reader:
            output_csv_writer.writerow(row)



def Data_reconstruction(
    name: str,            # TIC和XY文件路径
    annotation: str,  # 注释文件路径
    *,
    mask: str = None,   # mask文件路径
    mm: int = 5,        # 每个像素点的面积
    raw: str = None,    # 原始数据文件路径
) -> Optional[ad.AnnData]:

    TIC = f'{str(name)}-Root Mean Square.csv'
    XY = f'{str(name)}.csv'
    # 文件修整重排
    resave(TIC, 10)
    resave(XY, 8)
    # 重新读取并转换保存为AnnData对象
    df = pd.read_csv(f'{TIC}' + "-1.csv", header=0, index_col='m/z', low_memory=False)
    df1 = pd.read_csv(f'{XY}' + "-1.csv", header=0, index_col='Spot index', low_memory=False)
    os.remove(f'{TIC}' + "-1.csv")
    os.remove(f'{XY}' + "-1.csv")
    # 建一个基本的 AnnData 对象
    counts = csr_matrix(df.T, dtype=np.float32)
    adata = ad.AnnData(counts)
    # 添加raw数据
    if raw is not None:
        raw = str(raw)
        resave(raw, 10)
        df2 = pd.read_csv(f'{raw}' + "-1.csv", header=0, index_col='m/z', low_memory=False)
        os.remove(f'{raw}' + "-1.csv")
        adata.layers["raw"] = csr_matrix(df2.T, dtype=np.float32)

    # 为x和y轴提供索引
    adata.obs_names = df.columns
    adata.var['m/z'] = df.index
    adata.var_names = ['lips' + str(x) for x in range(adata.n_vars)]
    print(adata.obs_names[:])
    print(adata.var_names[:])

    # 标注坐标位置
    adata.obs["X_org"] = df1.x.values
    adata.obs["Y_org"] = df1.y.values

    adata.obs["X"] = (df1.x.values-df1.x.values.min())//mm
    adata.obs["Y"] = (df1.y.values-df1.y.values.min())//mm

    # 标注mask
    if mask is not None:
        mask = str(mask)
        resave(mask, 10)
        df2 = pd.read_csv(f'{mask}' + "-1.csv", usecols=['m/z'], low_memory=False)
        os.remove(f'{mask}' + "-1.csv")
        for i in df2['m/z']:
            t = round(i, 2)
            for j in adata.var_names:
                tt = adata.var.loc[j, 'm/z']
                if round(tt, 2) == t:
                    adata.var.loc[j, 'mask'] = True
                    break
        adata = adata[:, adata.var['mask'] != True]
        del adata.var['mask']
    # 标注注释
    annotation = str(annotation)
    liball = pd.read_csv(f'{annotation}.csv',header=0)
    #填充liball中的空值为unknow
    #liball = liball.fillna('unknow')
    adata.var_names = liball['Name']
    if 'HMDB' in liball.columns:
        liball.index = liball['Name']
        for i in liball['Name']:
            adata.var.loc[i, 'HMDB'] = liball.loc[i, 'HMDB']  # HMDB
    # 保存adata
    adata.write(f'{XY}' + ".h5ad")
    return adata
