#!/usr/bin/env python3

import sys
import math
import random
import time

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


"""
経路内にある全ての２辺の組み合わせについて、入れ替えて経路が短くなるなら入れ替える
引数　tour：配列, dist:二次元配列
返り値　tour:配列
"""
def opt_2(tour,dist):

    #今の経路の経路長
    original_length=tour_length(tour,dist)
    #頂点の個数
    N_tour=len(tour)

    #全ての２辺について入れ替えたら短くなるなら入れ替える処理をする
    for length in range(N, 1, -1):
        for start in range(N - length + 1):
            reverse_segment(tour,start,start + length,dist)

    #入れ替えたの後経路長の方が短くなるなら、再帰的に繰り返す
    #これはtour_length(tour,dist)=original_lengthとなったら終了する
    if tour_length(tour,dist)<original_length:
        return opt_2(tour,dist)
    
    #もしもう入れ替えても短くならないなら終了
    return tour


"""
頂点から未到達の中で最も近い頂点を結ぶような経路を返す関数
引数　dist:二次元配列
返り値　tour:配列
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

    #1.経路を求める手法
    #頂点から未到達の中で最も近い頂点を結ぶような経路を求める
    tour=greedy(dist)

    print("finish greedy")

    #2.経路をより短いものに改善する手法
    #2-optでランダムに2本の辺を選び入れ替えて短くなるなら入れ替える
    print("start opt2")

    opt_2(tour,dist)

    return tour


if __name__ == '__main__':
    assert len(sys.argv) > 1

    start = time.time()
    tour = solve(read_input('input_{}.csv'.format(sys.argv[1])))
    with open(f'output_{sys.argv[1]}.csv', 'w') as f:
                f.write(format_tour(tour) + '\n')
    #print_tour(tour)
    end = time.time()
    print('whole time', end-start)