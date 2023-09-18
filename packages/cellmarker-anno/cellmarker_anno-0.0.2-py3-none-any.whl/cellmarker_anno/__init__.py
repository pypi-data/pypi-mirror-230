# -*- coding: utf-8 -*-
"""
Created on Fri Sep 15  2023

@author: Administrator
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os,sys
os.getcwd()
# help(os.chdir)
#os.chdir(r"D:\AAAA_learning\Python_advanced_Learning")
os.getcwd()

data_dir="cellmarker_dataset"
if not os.path.isdir(data_dir):
    os.mkdir(data_dir)
else:
    print(data_dir,'directory already exists.')
    
import urllib.request
data_url="https://raw.githubusercontent.com/wangzichenbioinformatics/cellmarker_anno/main/Mouse_cell_markers.txt"
data_file_path="cellmarker_dataset/Mouse_cell_markers.txt"
if not os.path.isfile(data_file_path):
    result = urllib.request.urlretrieve(data_url,data_file_path)
else:
    print(data_file_path,'data file already exists.')    

"""
cell_marker = pd.read_table("https://raw.githubusercontent.com/wangzichenbioinformatics/cellmarker_anno/main/Mouse_cell_markers.txt",index_col=0)
cell_marker
"""

def get_mat(gene_name):
    cell_marker = pd.read_table("cellmarker_dataset/Mouse_cell_markers.txt",index_col=0)
    cell_marker.head()
    cell_marker['geneSymbol']
    cell_marker[['tissueType','cellName','geneSymbol']]
    cell_marker['cancerType']
    """
    #计算Normal的个数
    cell_marker[['cancerType']]
    j = 0
    for i in cell_marker['cancerType'].tolist():
        if i =='Normal':
            j=j+1
            print(j)
            #print("true")
    """

    #批量处理成功
    import re
    f = open("cellmarker_dataset/Mouse_cell_markers.txt", "r", encoding='utf-8')     #打开test.txt文件，以只读得方式，注意编码格式，含中文
    data = f.readlines()                            #循环文本中得每一行，得到得是一个列表的格式<class 'list'>
    f.close() 
    i=-2
    lst=[] 
    cluster=[]  
    for line in data:
            i=i+1
            for gene in gene_name:
                #print(gene)
                #print(type(gene)) 
                if re.search(gene,line):
                    lst.append(i)
                    cellname=cell_marker.iloc[i,:]['cellName']
                    #print(cellname)
                    #print(type(cellname))
                    cluster.append(cellname)

    #print("总的celltype:{}".format(cluster))

    #统计字符串个数
    resoult={}
    for i in cluster:
        #print(i)    
        resoult[i]=cluster.count(i)
    #print(resoult)

    cluster_count = pd.Series(resoult).sort_values(ascending=False)
    #print(cluster_count)
    return cluster_count
#cluster_count=get_mat(gene_name)


def plot_celltype_percent(mat,figsize):
    #可视化1
    from matplotlib import font_manager as fm
    import matplotlib as mpl
    labels = mat.index
    sizes = mat.values
    explode=tuple(np.zeros(len(mat),dtype=int))
    #explode = (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)
    fig1, ax1 = plt.subplots(figsize=figsize)
    patches, texts, autotexts = ax1.pie(sizes, explode=explode, labels=labels,
    autopct='%1.0f%%',
    shadow=False, startangle=170)
    ax1.axis('equal')
    #plt.savefig('test26_cluster15.jpg')
    plt.show()
    
    
#plot_celltype_percent(cluster_count)


def get_plot_celltype_percent(gene_name,figsize=(12,8)):
	cluster_count=get_mat(gene_name)
	return plot_celltype_percent(cluster_count,figsize)
	
#gene_name=['Esam','Vwf','Pcam1']
#get_plot_celltype_percent(gene_name,figsize=(20,12))
#get_plot_celltype_percent(gene_name)
"""
import pandas as pd
squirrel = pd.read_csv("https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2019/2019-10-29/nyc_squirrels.csv")
squirrel



https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2019/2019-10-29/nyc_squirrels.csv
https://github.com/rfordatascience/tidytuesday/blob/master/data/2019/2019-10-29/nyc_squirrels.csv
"""