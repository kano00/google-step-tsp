#!/usr/bin/env python3

import sys
import math
import random
import time
import numpy as np

#追加
import os
import concurrent.futures

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

    N=len(tour)

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
各頂点から未到達の中で近い頂点をgreedy_num個とってきて、
それぞれとつないで６手先までを貪欲法で探すとき最も短い経路を返す関数

→つまり、頂点から最も近い頂点を見るだけでなく、６手先まで貪欲にすすんだときに
最短経路となるようなルートを取ったほうがよいのでは？という考え。ただし、
すべての頂点にそれをやるのは非効率的なのでgreedy_num個を取ってきて調べてる

引数　dist:二次元配列,start_i:int型,greedy_num:int型
返り値　tour:配列
"""
def greedy(dist,start_i,greedy_num):
    current_city = start_i
    unvisited_cities = set(range(1,len(dist)))
    tour = [current_city]

    #ここは何手先まで見るかを決める
    dipth=6

    #未到達の頂点がある限りループさせる
    while unvisited_cities:
        results=[]


        #近い頂点からgreedy_num個取ってきたいので未到達都市をソートする
        sorted_unvisited_cities = sorted(unvisited_cities,
                                    key=lambda city: dist[current_city][city])
        
        #もしgreedy_num個も頂点がのこっていないなら普通に近い方からつなげていく
        if greedy_num > len(sorted_unvisited_cities):

            next_city=min(unvisited_cities,
                            key=lambda city: dist[current_city][city])
            unvisited_cities.remove(next_city)
            tour.append(next_city)
            current_city = next_city

        else:
            #greedy_num個の近い頂点についてdipth手先まで探索
            for target_city in sorted_unvisited_cities[:greedy_num]:

                #各target_cityからdipth手先まで探索する用の変数を宣言
                temp_distance=0
                #探索開始の頂点
                temp_current_city=current_city
                #次の探索頂点
                temp_next_city=target_city
                #仮の未到達頂点の配列
                temp_unvisited_cities=unvisited_cities.copy()
                #仮の経路用の配列
                temp_tour=tour.copy()

                #dipth手先まで行く過程で未到達頂点がなくなったとき用
                #つまりtemp_unvisited_citiesのサイズが０になったとき用
                flag=0

                for _ in range(dipth):

                    temp_distance+=dist[temp_current_city][temp_next_city]

                    temp_unvisited_cities.remove(temp_next_city)
                    temp_tour.append(temp_next_city)

                    temp_current_city=temp_next_city

                    #未到達頂点がなくなってなければ次の頂点に行く
                    if len(temp_unvisited_cities)>0:
                        temp_next_city=min(temp_unvisited_cities,
                            key=lambda city: dist[temp_current_city][city])
                    else:
                        flag=1
                        break

                #未到達頂点がなくなったならその経路ではもう最適経路はない
                if flag:
                    results.append([None,None,None])
                else:
                    results.append([temp_tour,temp_unvisited_cities,temp_distance])
            
            #すべてのtarget_cityについて処理が終わった
            #経路が一番短いものを採用する処理に入る。結果をまとめる
            results = np.array(results)
            distances = results[:,2]
            can_tour = results[:,0]
            can_unvisited_cities = results[:,1]

            #未到達頂点がなくなったときにNoneが出力される
            #つまり、 このときはもうdipth分の頂点がないので普通に最も近い頂点をつないでいく
            if None in distances:
                while unvisited_cities:
                    next_city = min(unvisited_cities,
                                    key=lambda city: dist[current_city][city])
                    unvisited_cities.remove(next_city)
                    tour.append(next_city)
                    current_city = next_city

            #まだまだ未到達頂点がたくさんあるなら、探索を続ける
            else:
                mi = np.argmin(distances)
                tour = can_tour[mi]
                unvisited_cities = can_unvisited_cities[mi]
                tour.append(next_city)
                current_city = next_city

    return tour



"""
メインの補助関数　start_i地点をスタートとしてcities内の要素をすべて通る時の経路をできるだけ最適化して返す
引数　cities:配列, start_i:int型,greedy_num:int型
（返り値はないが一応tours配列に入れたtour配列がこのスタート地点に対する最適経路である）
"""
def solve_helper(cities,start_i,tours,greedy_num):
    print("start : ",start_i)

    N = len(cities)

    dist = [[0] * N for i in range(N)]
    for i in range(N):
        for j in range(i, N):
            dist[i][j] = dist[j][i] = distance(cities[i], cities[j])
    

    #1.経路を求める手法
    #頂点から未到達の中で最も近い頂点を結ぶような経路を求める
    tour=greedy(dist,start_i,greedy_num)

    #2.経路をより短いものに改善する手法
    #2-optでランダムに2本の辺を選び入れ替えて短くなるなら入れ替える
    opt_2(tour,dist)

    print("finish : ", start_i)

    tours.append(tour)



"""
メインの関数　start_num個のスタート地点をランダムに選んできて探索する
greedy_numはgreedy_advanced関数にもちいる
（citiesのサイズが大きいときはstart_numを小さくしないと探索がおわらないことに注意）
引数　cities:配列, start_num:int型,greedy_num:int型
返り値　tour:配列
"""
def solve(cities,start_num,greedy_num):

    N = len(cities)

    #N>128ならランダムにstart_num個のスタート地点を選ぶ
    start_list = [i for i in range(N)]

    if N > 128:
        start_list = random.sample(start_list, start_num)


    #toursには並列処理で各threadの実行結果である経路tourが入る
    tours=[]
    
    #マルチスレッドで複数のスタート地点からの探索を並列処理する
    # （モジュールはthreadingよりconcurrent.futuresの方が処理の効率が良いようなので後者を利用）
    with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        #各スタート地点に着いてスレッドを立ち上げる
        for start_i in start_list:
            #引数は（各スレッドに対して実行する関数、その関数に対する引数１，引数２、‥）
            executor.submit(solve_helper,cities, start_i, tours,greedy_num)


    #ここまででstart_num個のスタート地点についてsolve_helper関数を実行した
    #ここから最も経路の短いものを選択すればよい

    ans_tour = None
    min_length = float('inf')
    for j in range(len(start_list)):
        tour = tours[j]
        try:
            #経路長を求めている
            path_l = sum(distance(cities[tour[i]], cities[tour[(i + 1) % N]]) for i in range(N))
            if path_l < min_length:
                min_length = path_l
                ans_tour = tour
        except:
            pass
    
    print("path_length : ", min_length)
    return ans_tour
    

if __name__ == '__main__':
    assert len(sys.argv) > 3

    start = time.time()

    #コマンドライン引数１には実行するChallengeの番号を、
    #コマンドライン引数２には調べてほしいスタート地点の個数を入れる
    #コマンドライン引数３には貪欲法で各頂点からいくつの経路を調べてほしいか入れる
    tour = solve(read_input('input_{}.csv'.format(sys.argv[1])),int(sys.argv[2]),int(sys.argv[3]))

    with open(f'output_{sys.argv[1]}.csv', 'w') as f:
                f.write(format_tour(tour) + '\n')
    
    #print_tour(tour)
    end = time.time()
    print('whole time', end-start)