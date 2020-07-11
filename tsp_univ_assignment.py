#!/usr/bin/env python3

import sys
import math
import random
import time
from collections import deque

from common import print_tour, read_input,format_tour


def distance(city1, city2):
    return math.sqrt((city1[0] - city2[0]) ** 2 + (city1[1] - city2[1]) ** 2)


"""
反復深化優先探索＋A*探索＋勾配効果＋焼きなまし
で時間を測定してみる

深さ優先　幅優先

ヒューリスティック関数の比較
"""


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


"""
start_idから他のidまでの距離を深さ優先探索で調べて返す関数
引数：int型
返り値：list型　中身はstart_idからの距離、index=idという対応
"""
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

    min_tour=[]
    min_length=1e100

    for x in range(1,N):
        dfs_sub(2,[x,0])

    return min_tour



"""
    #まず起点のidから繋がるノードをキューに入れる
    queue=deque([start_id])
    
    #start_idからの距離を保持する配列(-1ならまだ訪れてないidであることを表す)
    dist_from_start=[-1]*N
    
    #自分との距離は０
    dist_from_start[start_id]=0
    
    #幅優先探索を始める
    while queue:

        #idをqueueから取り出す
        search_id=queue.popleft()

        for i in range(N):

            #まだ訪れていないなら距離を更新
            if dist_from_start[i] ==-1:
                dist_from_start[i]=dist_from_start[search_id]+dist[i][j]
                #新たにidをキューに追加して今度これと繋がるidを探索する
                queue.append(i)
"""
    



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

    #import itertools

    #0番を除いて順列を列挙
    #cities_list=[i for i in range(1,N)]
    #cities_permut=itertools.permutations(cities_list,len(cities_list))

    start = time.time()
    
    tour=dfs(dist,N)

    end = time.time()

    print('whole time: ', end-start)
    print('tour_length: ', tour_length(tour,dist))
    print(tour)

    return tour


if __name__ == '__main__':
    assert len(sys.argv) > 1

    tour = solve(read_input('input_{}.csv'.format(sys.argv[1])))
    with open(f'output_{sys.argv[1]}.csv', 'w') as f:
                f.write(format_tour(tour) + '\n')
