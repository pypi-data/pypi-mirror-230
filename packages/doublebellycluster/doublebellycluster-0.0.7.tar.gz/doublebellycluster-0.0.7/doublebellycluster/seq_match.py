import numpy as np
import copy
from sklearn.metrics.pairwise import pairwise_distances
import pandas as pd
import itertools

def flat(ll):
    return list(itertools.chain(*ll))


def seq_match(a, b):
    ka = range(len(a))
    kb = range(len(b))
    d1 = []
    num = 2
    for num in range(2, len(a)+1):
        a1 = []
        print(ka)
        for i in ka:
            if i + num <= len(a):
                a1 += [[i, a[i:i + num]]]
        b1 = []
        print(kb)
        for i in kb:
            if i + num <= len(b):
                b1 += [[i, b[i:i + num]]]
        c1 = []
        for n, k in a1:
            for nm, m in b1:
                if k == m:
                    c1 += [[n, nm, k]]
                    d1 = [i for i in d1 if str(i[2])[1:-1] not in str(k)[1:-1]]
        d1 += c1
        ka = list(np.unique([i[0] for i in d1]))[::-1]
        kb = list(np.unique([i[1] for i in d1]))[::-1]
        print(d1)
        if len(c1) == 0:
            break
    return d1

def agglom_clustering(pair_mat_0, cut_edge_disjoint):
    
        alles_index = list(pair_mat_0.index)
        pair_mat_wize = pairwise_distances(pair_mat_0)
        pair_mat_wize = pd.DataFrame(pair_mat_wize,index = list(pair_mat_0.index),columns = list(pair_mat_0.index))
        print(pair_mat_wize)
        pair_mat_wize = pair_mat_wize.unstack()
        pair_mat_wize = pair_mat_wize[(pair_mat_wize>0)&(pair_mat_wize<cut_edge_disjoint)].reset_index()
        pair_mat_wize = pair_mat_wize.apply(lambda x: sorted(x[:2]),axis=1).drop_duplicates()
        
        pair_mat_wize = pair_mat_wize.to_list()
        
        print(pair_mat_wize)

        m=0
        a=0
        while True:
            a = len(pair_mat_wize)
            
            g = []
            dd=[]
            for n, io in enumerate(pair_mat_wize):
                for k, i in enumerate(pair_mat_wize):
                    if k > n and k not in g and n not in g:
                        if len(set(i)&set(io)):
                            dd+=[list(set(i+io))]
                            g+=[n,k]
                if n not in g:
                    dd+=[io]
                
            pair_mat_wize = copy.deepcopy(dd)   
            print(dd)

            m = len(dd)

            if a==m:
                break

                     
        
        for i in alles_index:
            if i not in flat(dd):
                dd+=[[i]]

        print(dd)
        return dd

if __name__ == '__main__':
    
    print('\n\n\n\n', seq_match([0,2,3,4,5,6], [0,3,4,0,2,3,4,12,3]))


