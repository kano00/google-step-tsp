#!/usr/bin/env python3

import sys
import math
import random
import time
import itertools
from collections import deque

from common import print_tour, read_input,format_tour


def distance(city1, city2):
    return math.sqrt((city1[0] - city2[0]) ** 2 + (city1[1] - city2[1]) ** 2)


"""
tour内の頂点を結んだ全長を返す関数
引数　tour：配列,　dist:二次元配列
返り値　length:int型
"""
def tour_length(tour, dist):
    # 経路長を計算
    length = 0
    for i in range(len(tour)+1):
        length += dist[tour[i-1]][tour[i % len(tour)]]
    return length


#全探索
def search_all_path(dist,N):
    min_tour=[]
    min_length = 1e100
    
    #スタート地点の頂点０以外の頂点の順列を列挙してそれらの経路の距離を比較する
    for path in itertools.permutations(range(1,N)):
        new_path=list(path)
        new_path.insert(0,0)
        new_len=tour_length(new_path,dist)

        if new_len<min_length:
            min_tour=new_path[:]
            min_length=new_len

    return min_tour,min_length



#深さ優先探索１
#参考サイト
#http://www.nct9.ne.jp/m_hiroi/light/pyalgo62.html
def dfs(dist,N):

    def dfs_sub(tour_size,new_tour):
        global min_tour,min_length

        if N==tour_size:
            new_len=tour_length(new_tour,dist)

            if new_len<min_length:
                min_length=new_len
                min_tour=new_tour[:]

        else :
            #すべての子ノードについて探索
            for i in range(1,N):
                #i番目の街に到達済ならループを抜ける
                if i in new_tour:
                    continue
            
                #このif文で計算量を２分の１に減らせる
                if tour_size != 2 or new_tour[0]>i:
                    new_tour.append(i)
                    dfs_sub(tour_size+1,new_tour)
                    new_tour.pop()

    global min_tour,min_length

    #tourは後で経路を返す配列
    min_tour=[]
    min_length=1e100

    for x in range(1,N):
        dfs_sub(2,[x,0])

    return min_tour


#深さ優先探索２
#深さ優先探索１より２倍位時間がかかる
#参考サイトのp７の疑似コードを参考にした
#http://www.cas.mcmaster.ca/~nedialk/COURSES/4f03/tsp/tsp.pdf
def recursive_dfs(dist,N):

    def recursive_dfs_sub(tour_size,new_tour):
        global min_tour,min_length
        new_len=tour_length(new_tour,dist)

        if N==tour_size:
            
            if new_len<min_length:
                #すべての頂点を訪れたときのみmin_lengthを更新できる
                min_length=new_len
                min_tour=new_tour[:]

        else :
            for i in range(1,N):

                #i番目の街に到達済ならループを抜ける
                if i in new_tour:
                    continue

                #まだすべての頂点を訪れていない時点で、
                #すでに経路長がmin_lengthより長いならそれ以上深くに行かない
                if new_len<min_length:
                    new_tour.append(i)
                    recursive_dfs_sub(tour_size+1,new_tour)
                    new_tour.pop()

    global min_tour,min_length

    #tourは後で経路を返す配列
    min_tour=[]
    min_length=1e100

    recursive_dfs_sub(1,[0])

    return min_tour,min_length


#反復深化深さ優先探索
#擬似コード通りだとうまく行かない（？）
#参考サイトのp9の疑似コードを参考にした
#http://www.cas.mcmaster.ca/~nedialk/COURSES/4f03/tsp/tsp.pdf
def iterative_dfs(dist,N):

    min_tour=[]
    min_length=1e100

    stack=[]
    new_tour=[]

    for city in range(N-1,-1,-1):
        stack.append(city)
    
    while stack!=[]:

        city=stack.pop()
        
        if city==-1:
            new_tour.pop()
        else:
            new_tour.append(city)

            if N==len(new_tour):
                new_len=tour_length(new_tour,dist)
                if new_len<min_length:
                    min_length=new_len
                    min_tour=new_tour[:]
                    new_tour.pop()
            else:
                stack.append(-1)
                for j in range(N-1,0,-1):
                    if j in new_tour:
                        continue

                    new_len=tour_length(new_tour,dist)
                    if new_len<min_length:
                        stack.append(j)

        #print("city=",city)
        #print("tour=",new_tour)
        #print("stack=",stack)
        #print("min_tour=",min_tour)

    return min_tour,min_length



"""
メインの関数　cities内の要素をすべて通る時の経路をできるだけ最適化して返す
引数　cities:配列
返り値　tour:配列
"""
def solve(cities):
    N = len(cities)

    dist = [[0] * N for i in range(N)]
    for i in range(N):
        for j in range(i, N):
            dist[i][j] = dist[j][i] = distance(cities[i], cities[j])


    start = time.time()
    
    #全探索
    #tour,length=search_all_path(dist,N)
    ##深さ優先探索１
    tour,length=recursive_dfs(dist,N)
    ##深さ優先探索２
    #tour,length=iterative_dfs(dist,N)

    

    end = time.time()

    print(tour)
    print('whole time: ', end-start)
    print('tour_length: ', tour_length(tour,dist))
    
    return tour

"""
やること

全探索、
深さ優先２、
反復深化優先探索、
貪欲法＋2_opt

上４つで時間と経路長比較
"""

if __name__ == '__main__':
    assert len(sys.argv) > 1

    tour = solve(read_input('input_{}.csv'.format(sys.argv[1])))
    with open(f'output_{sys.argv[1]}.csv', 'w') as f:
                f.write(format_tour(tour) + '\n')
