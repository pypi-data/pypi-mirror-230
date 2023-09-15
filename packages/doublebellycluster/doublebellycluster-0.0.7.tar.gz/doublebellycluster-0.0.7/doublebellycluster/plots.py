
from matplotlib import cm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import plotly.graph_objects as go


def plot_color_map( df, name, show_save = True):
    fig, ax = plt.subplots()
    scatter_x = np.array(df.iloc[:,0])
    scatter_y = np.array(df.iloc[:,1])
    group = np.array(df.iloc[:,2])

    for g in np.unique(group):
        i = np.where(group == g)
        ax.scatter(scatter_x[i], scatter_y[i], label=g)
    ax.legend()
    
    if show_save:
        plt.show()
    else:
        fig.savefig(name+'.png')


def d3_color_map( fs, name):
    
    fs_table = pd.pivot_table(fs, index= fs[0], columns = fs[1], values = 'f').fillna(0)
    X = np.array(fs_table.index)
    Y = np.array(fs_table.columns)
    X, Y = np.meshgrid(X, Y)
    Z = np.array(fs_table.T)
    
    fs_table = pd.pivot_table(fs, index= fs[0], 
                        columns = fs[1], values = 'col').T
        
    fig = go.Figure(data=[go.Surface(x=X, y=Y, z=Z, surfacecolor=np.array(fs_table))])

    fig.write_html(name+'.html')

