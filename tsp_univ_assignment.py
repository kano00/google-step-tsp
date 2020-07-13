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


"""
2辺を入れ替える関数
（頂点i-1とiを結んだ辺と頂点j-1とjを結んだ辺を入れ替える）
引数　tour：配列,　i,j:int型, dist:二次元配列
"""
def reverse_segment(tour, i, j, dist):
    # 交換した方が短くなるなら交換する
    A, B, C, D = tour[i-1], tour[i], tour[j-1], tour[j % len(tour)]

    #辺AB＋辺CD＞辺AC＋辺BD（入れ替えた方）ならば入れ替える
    if dist[A][B] + dist[C][D] > dist[A][C] + dist[B][D]:
        tour[i:j] = reversed(tour[i:j])



##
##ここから下は各探索手法の関数
##

"""
全探索

可能な経路を順列を用いて全探索し、最短経路を返す関数
引数　dist:二次元配列,N：int型
返り値：min_tour：配列,min_length：int型
"""
def search_all_path(dist,N):
    min_tour=[]
    min_length = 1e100
    
    #スタート地点の頂点０以外の頂点の順列を列挙してそれらの経路の距離を比較する
    for path in itertools.permutations(range(1,N)):
        new_path=list(path)
        #出発地点に0を入れる
        new_path.insert(0,0)
        new_len=tour_length(new_path,dist)

        if new_len<min_length:
            min_tour=new_path[:]
            min_length=new_len

    return min_tour,min_length



"""
再帰関数を用いた深さ優先探索

深さ優先探索で経路を探索し、最短経路を返す関数
引数　dist:二次元配列,N：int型
返り値：min_tour：配列,min_length：int型

参考サイトのp７の疑似コードを参考にした
http://www.cas.mcmaster.ca/~nedialk/COURSES/4f03/tsp/tsp.pdf
"""
def recursive_dfs(dist,N):

    def recursive_dfs_sub(tour_size,new_tour):
        global min_tour,min_length
        new_len=tour_length(new_tour,dist)

        #すべての頂点を通ったあと、その経路長が最短経路か調べる
        if N==tour_size:
            new_len+=dist[0][new_tour[tour_size-1]]
            
            if new_len<min_length:
                #すべての頂点を訪れたときのみmin_lengthを更新できる
                min_length=new_len
                min_tour=new_tour[:]

        else :
            #すべての子ノードに対して以下の処理
            for i in range(1,N):

                #i番目の頂点に到達済ならループを抜ける
                if i in new_tour:
                    continue

                #まだすべての頂点を訪れていない時点で、すでに経路長がmin_lengthより
                # 長いならそれ以上深くに行かない。min_lengthより短いなら再帰呼び出しでさらに深くまで行く
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



"""
貪欲法

ある頂点から未到達の頂点の中で最も近い頂点をぶのを繰り返し、求めた経路を返す関数
引数　dist:二次元配列
返り値：tour：配列

参考　同じリポジトリ内のsolver_greedy.py
"""
def greedy(dist):
    current_city = 0
    unvisited_cities = set(range(1,len(dist)))
    tour = [current_city]

    #未到達の頂点がある限りループさせる
    while unvisited_cities:
        next_city = min(unvisited_cities,
                        key=lambda city: dist[current_city][city])
        unvisited_cities.remove(next_city)
        tour.append(next_city)
        current_city = next_city
    return tour


"""
2_opt

経路内にある全ての２辺の組み合わせについて、入れ替えて経路が短くなるなら入れ替える
引数　tour：配列, dist:二次元配列
返り値　tour:配列
"""
def two_opt(tour,dist):

    #今の経路の経路長
    original_length=tour_length(tour,dist)
    #頂点の個数
    N=len(tour)

    #全ての２辺について入れ替えたら短くなるなら入れ替える処理をする
    for length in range(N, 1, -1):
        for start in range(N - length + 1):
            reverse_segment(tour,start,start + length,dist)

    #入れ替えたの後経路長の方が短くなるなら、再帰的に繰り返す
    #これはtour_length(tour,dist)=original_lengthとなったら終了する
    if tour_length(tour,dist)<original_length:
        return two_opt(tour,dist)
    
    #もしもう入れ替えても短くならないなら終了
    return tour



"""
2-opt+焼きなまし法

経路内にある全ての２辺の組み合わせについて、入れ替えて経路が短くなるなら入れ替えるが、
短くならなくても確率的に入れ替える関数
引数　tour：配列, dist:二次元配列
返り値　tour:配列
"""
def two_opt_with_SA(tour,dist):
    #温度の減少割合
    alpha = 0.999
    #最初の温度
    initial_t = 1.3
    #最後の温度
    final_t = 1.0

    #確率を求める際に温度に乗算するパラメータ
    para_for_t=10

    #いままでで最も短い経路を入れる
    best_tour=tour[:]
    best_length=tour_length(tour,dist)

    N=len(tour)

    #更新する温度
    current_t=initial_t

    #2-optをcurrent_t > final_tである限り繰り返す

    while current_t > final_t:
        #print("T=",current_t)
        #print("tour=",best_length)

        #2-optのアルゴリズム
        for length in range(N, 1, -1):
            for start in range(N - length + 1):
                i=start
                j=start+length

                A, B, C, D = tour[i-1], tour[i], tour[j-1], tour[j% len(tour)]
                #diff_len=入れ替え前ー入れ替え後の経路長差
                diff_len=(dist[A][B] + dist[C][D])-(dist[A][C] + dist[B][D])
                
                #current_tが大きいほど（後になるほど）確率possibは小さくなる、
                #よくオーバーフローするので値para_for_tを微調整
                possib=math.exp(diff_len/(para_for_t*current_t))

                #辺AB＋辺CD＞辺AC＋辺BD（入れ替えた方）ならば入れ替える
                if diff_len>0:
                    tour[i:j] = reversed(tour[i:j])

                #辺AB＋辺CD<=辺AC＋辺BD（入れ替えた方）でも確率的に入れ替える   
                #入れ替える確率のしきい値はランダムだが、possibの方の値は経路の変化量と現在の温度に依存
                elif possib>=random.uniform(0,1):
                    tour[i:j] = reversed(tour[i:j])

        #current_tは徐々に小さくする
        current_t*= alpha
        current_length=tour_length(tour,dist)

        if  current_length<best_length:
            best_tour=tour[:]
            best_length=current_length

    return best_tour



"""
メインの関数　cities内の要素をすべて通る時の経路をできるだけ最適化して返す
引数　cities:配列
返り値　tour:配列
"""
def solve(cities,algorithm_num):
    N = len(cities)

    dist = [[0] * N for i in range(N)]
    for i in range(N):
        for j in range(i, N):
            dist[i][j] = dist[j][i] = distance(cities[i], cities[j])


    #コマンドライン引数(algorithm_num)でアルゴリズムを指定する
    if algorithm_num==1:
        #全探索
        print("全探索")
        start = time.time()
        tour,length=search_all_path(dist,N)

        end = time.time()
        search_time=end-start
        tour_len=tour_length(tour,dist)

        print('whole time: ', search_time)
        print('tour_length: ', tour_len)

    elif algorithm_num==2:
        #深さ優先探索
        print("深さ優先探索")
        start = time.time()

        tour,length=recursive_dfs(dist,N)

        end = time.time()
        search_time=end-start
        tour_len=tour_length(tour,dist)

        print('whole time: ', search_time)
        print('tour_length: ', tour_len)
    
    elif algorithm_num==3:
        #貪欲法のみ
        print("貪欲法のみ")
        start = time.time()

        tour=greedy(dist)

        end = time.time()
        search_time=end-start
        tour_len=tour_length(tour,dist)

        print('whole time: ', search_time)
        print('tour_length: ', tour_len)

    elif algorithm_num==4:
        #貪欲法＋2_opt
        print("貪欲法＋2_opt")
        start = time.time()

        tour=greedy(dist)
        tour=two_opt(tour,dist)

        end = time.time()
        search_time=end-start
        tour_len=tour_length(tour,dist)

        print('whole time: ', search_time)
        print('tour_length: ', tour_len)
    
    elif algorithm_num==5:
        #貪欲法＋2_opt+焼きなまし法(Simulated Annealing)
        print("貪欲法＋2_opt+焼きなまし法")
        start = time.time()

        tour=greedy(dist)
        tour=two_opt_with_SA(tour,dist)

        end = time.time()

        search_time=end-start
        tour_len=tour_length(tour,dist)

        print('whole time: ', search_time)
        print('tour_length: ', tour_len)
    else:
        print("error in algorithm_num")

    #実験用
    return tour,search_time,tour_len
    #return tour


"""
比較するアルゴリズム

全探索、
深さ優先
貪欲法のみ
貪欲法＋2_opt
貪欲法＋2_opt(with焼きなまし)

時間と経路長比較
"""

if __name__ == '__main__':
    assert len(sys.argv) > 2

    tour = solve(read_input('input_{}.csv'.format(sys.argv[1])),int(sys.argv[2]))
    #実験用
    times=[]
    tour_lengths=[]
    for i in range(10):
        tour,search_time,tour_len=solve(read_input('input_{}.csv'.format(sys.argv[1])),int(sys.argv[2]))
        times.append(search_time)
        tour_lengths.append(tour_len)

    print(sum(times)/10)
    print(sum(tour_lengths)/10)

    #with open(f'output_{sys.argv[1]}.csv', 'w') as f:
    #            f.write(format_tour(tour) + '\n')
