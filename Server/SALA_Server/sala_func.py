#-*- coding:utf-8 -*-
import salabase as sl
from operator import attrgetter
import math
from math import sqrt
import scipy.stats
from operator import itemgetter

def rssiCentroidEstimation(device, reports):
    # RSSI Centroid의 결과(임시)
    pos_star = sl.Pos(0, 0)

    # processing
    
    # sorted_reports는 rssi 의 값이 큰 것부터의 순서대로 정렬된 리스트
    sorted_reports = sorted(reports, key=lambda Report: Report.rssi)
    sorted_reports.reverse()
    
    # sorted_reports에서 앞 부분 m 개를 추출하기 위해 필요한 변수
    sl.m = 10
    
    # m개의 추출된 report들의 x, y 좌표들의 합을 위한 변수들
    sum_x = 0
    sum_y = 0
    # 좌표들을 합한다
    for i in range(0, sl.m):
        sum_x += sorted_reports[i].position.x
        sum_y += sorted_reports[i].position.y
    # 평균을 내준다
    pos_star.x = sum_x / sl.m
    pos_star.y = sum_y / sl.m

    # result
    # print('\n=======================================')
    # print('=== RSSI Centroid Estimation Result ===')
    # print('=======================================')
    # print('IoT Device: ' + str(device))
    # print('report list length: ' + str(len(reports)))
    # for n in range(0, len(reports)):
    #     print('\t' + str(reports[n]))

    # print('RSSI centroid (p*): ' + str(pos_star))
    return device, reports, pos_star


def powerDistanceTableConstruct(device, reports, pos_star):
    # power-distance table 생성 결과(임시)
    table = sl.PowerDistanceTable()
    # processing
    # ...
    # 변수 초기화
    point = sl.Pos(0, 0)
    power = 0
    distance = 0
    avg_dist = 0
    std_dev = 0
    N = sl.m   # 점 개수 기준

    # table 구성요소

    # for 문을 통해 table 구성요소중 point, power, distance 부분부터 add(avg_dist, std_dev 는 0으로 일단 add)
    for i in range(0, len(reports)):
        # point
        point = reports[i].position

        # power
        power = reports[i].rssi

        # distance
        distance = sl.find_distance(point, pos_star)
        table.add(point, power, distance, avg_dist, std_dev)

    # for 문을 통해 table 구성요소중 avg_dist, std_dev 값을 계산해서 수정, 계산은 기준 점, 좌측 점, 우측 점으로 나눠서 계산
    for i in range(0, len(reports)):
        # avg_dist
        left_points = []
        right_points = []
        for k in range(0, len(reports)):
            tmp_point = reports[k].position # 현재 p 점과의 거리를 구하기 위한 임시 점 저장
            if i == k:
                continue
            # 좌측 점 분류
            if tmp_point.x < reports[i].position.x:
                # 정렬하기 위해 point 와 distance 를 가지고 있는 tuple 을 append 함
                left_points.append((sl.find_distance(reports[i].position, tmp_point), k))
            # 우측 점 분류
            elif tmp_point.x >= reports[i].position.x:
                # 정렬하기 위해 point 와 distance 를 가지고 있는 tuple 을 append 함
                right_points.append((sl.find_distance(reports[i].position, tmp_point), k))
        # 좌측
        left_sum = 0    # p 점 좌측에 있는 점들의 table 에 저장된 distance 값의 합
        left_count = 0  # left_sum 에 더해질 점의 수를 정해주는 변수
        left_points.sort(key=itemgetter(0))     # 좌측 distance 값으로 정렬
        if len(left_points) >= int((N-1)/2):
            left_count = int((N - 1) / 2)
            for k in range(0, left_count):
                # p 점에 가까운 순서대로 left_count 만큼 'distance'값 더해줌
                left_sum += table[left_points[k][1]]["distance"]
        else:
            left_count = len(left_points)
            for k in range(0, left_count):
                left_sum += table[left_points[k][1]]["distance"]
        # 우측
        right_sum = 0   # p 점 우측에 있는 점들의 table 에 저장된 distance 값의 합
        right_count = 0     # right_sum 에 더해질 점의 수를 정해주는 변수
        right_points.sort(key=itemgetter(0))    # 우측 distance 값으로 정렬
        if len(right_points) >= int(N / 2):
            right_count = int(N / 2)
            for k in range(0, right_count):
                right_sum += table[right_points[k][1]]["distance"]   # p 점에 가까운 순서대로 right_count 만큼 'distance'값 더해줌
        else:
            right_count = len(right_points)
            for k in range(0, right_count):
                right_sum += table[right_points[k][1]]["distance"]
        count_sum = left_count + right_count + 1
        avg_dist = round((left_sum + right_sum + table[i]["distance"]) / count_sum, 1)

        # std_dev
        sum_of_sub_s = 0    # 편차 제곱들의 합
        # left_points 의 편차, right_points 의 편차를 sub 에 저장
        for k in range(0, left_count):
            sub = table[left_points[k][1]]["distance"] - avg_dist
            sub_s = sub * sub
            sum_of_sub_s += sub_s
        for k in range(0, right_count):
            sub = table[right_points[k][1]]["distance"] - avg_dist
            sub_s = sub * sub
            sum_of_sub_s += sub_s

        sum_of_sub_s += (table[i]["distance"] - avg_dist) * (table[i]["distance"] - avg_dist)
        std_dev = round(sqrt(sum_of_sub_s / count_sum), 1)
        table[i]["avg_dist"] = avg_dist
        table[i]["std_dev"] = std_dev
    # ...
    # result
    # print('\n=============================================')
    # print('=== Power Distance Table Construct Result ===')
    # print('=============================================')
    # print('IoT Device: ' + str(device))
    # print('report list length: ' + str(len(reports)))
    # print('RSSI centroid (p*): ' + str(pos_star))
    # print('power distance table length: ' + str(len(table)))
    # for n in range(0, len(table)):
    #     print('\t' + str(table[n]))

    return device, reports, table


def gridWeightMapContruct(device, reports, table):
    
    # 0. 필요한 변수들 사전 정의
    grid_length = 20   # 단위 grid의 길이, cm단위
    room_width = 20    # 방의 가로길이, grid의 갯수로 정의됨
    room_length = 20   # 방의 세로길이, grid의 갯수로 정의됨
    room = []          # grid 단위로 방이 구현 될 리스트, 각 grid에는 grid의 center 좌표가 저장됨, 이 좌표를 바탕으로 모든 거리계산이 이루어 짐
    max_prob = 0       # 가장 큰 확률을 저장할 변수 
    max_prob_xy = sl.Pos(0,0)   # 가장 큰 확률을 가지는 grid의 x,y 좌표를 저장할 변수
    max_xy_list = []   # max_prob이 여러 개라면, 해당 x,y 좌표들을 저장할 리스트
    location = []      # 가장 큰 확률을 가지는 grid의 x,y 좌표를 return하기 위한 변수
    device = device    # return에 포함 될 device를 미리 저장
    """
   1)  -----------
       |         |   = grid 1개
       ----------- 
    
   2)  ( x, y )      = 각 grid의 center x,y 좌표
   
   3) 실제 방의 위치 정보를 나타내는 2차원 리스트 [10 grid x 10 grid] size의 room을 시각화 한 것
    ---------------------------------------------------
    | (10,10) | (10,30) | (10,50) |........| (10,190) |
    ---------------------------------------------------
    | (30,10) | (30,30) | (30,50) |........| (30,190) |
    ---------------------------------------------------
    .........(중간 생략)...............................
    ---------------------------------------------------
    | (190,10)| (190,30)| (190,50)|........| (190,190)|
    --------------------------------------------------
    """
    matrix_p = []      # 각 grid의 확률 값을 담을 리스트

    # 1. Grid 초기화
    for i in range(room_width):                # room의 각 grid마다 grid의 center 좌표를 저장
        temp = []
        for j in range(room_length):
            temp.append([i*20+10, j*20+10])   
        room.append(temp)
    
    for i in range(room_width):                # 확률이 저장될 matrix_p를 0으로 초기화
        temp = []
        for j in range(room_length):
            temp.append(0)
        matrix_p.append(temp)

    # Gradient Descent는 Centroid point + 그 근처 몇 개 점에서 뿌려 볼 것
    # 2. matrix_p에 확률값을 더하기

    # PowerDistanceTable에서 point 순차 선택
    for k in range(len(table)):
        # 각각의 grid에 접근, point의 avg_dist와 std_dev를 바탕으로 표준정규분포를 구함, 계산하여 나온 확률값을 grid에 누적하여 더함
        for i in range(room_width):
            for j in range(room_length):
                matrix_p[i][j] += scipy.stats.norm(0, table[k]["std_dev"]).pdf(
                    sl.distance2(
                        table[k]["point"].x, room[i][j][0], table[k]["point"].y, room[i][j][1]) - table[k]["avg_dist"])
                # room[i][j][0] = grid.x, room[i][j][1] = grid.y

    # 3. 3중 for loop을 통해 모든 grid의 확률 값을 구했으면, matrix prob에서 가장 큰 값이 들어있는 grid를 찾아내어 좌표를 return
    # 같은 값을 가진 cell이 여러개라면 그 cell들의 중간 좌표를 return
    for i in range(room_width):
        for j in range(room_length):
            if matrix_p[i][j] > max_prob:
                max_prob = matrix_p[i][j]
                max_prob_xy = [room[i][j][0], room[i][j][1]]  # max_prob을 가지고 있는 grid의 x,y좌표를 저장
                max_xy_list.clear()            # 기존 max_prob보다 더 큰 값을 가진 grid를 찾았으면, 기존의 max_xy_list를 비우고 새로 시작
                max_xy_list.append(max_prob_xy)
            elif matrix_p[i][j] == max_prob:
                max_prob_xy = [room[i][j][0], room[i][j][1]] 
                max_xy_list.append(max_prob_xy)     # 기존 max_prob와 같은 값을 가진 grid를 찾았으면, 기존의 max_xy_list에 해당 x,y좌표를 추가
                
    if len(max_xy_list) == 1:      # 가장 큰 확률값을 가진 grid가 1개일 때
        location = max_xy_list
    elif len(max_xy_list) >= 2:     # 가장 큰 확률값을 가진 grid가 1개 이상일 때, 해당 grid들의 중간 좌표를 return
        sum_x = 0
        sum_y = 0
        for i in max_xy_list:
            sum_x += i[0]
            sum_y += i[1]
        final_x = sum_x/len(max_xy_list)
        final_y = sum_y/len(max_xy_list)
        location = [final_x, final_y]
    else:
        location = [[0,0]]
        # print("debug ELSE", len(max_xy_list))

    # print('\n========================================')
    # print('=== Grid Weight Map Construct Result ===')
    # print('========================================')
    # print('IoT Device: ' + str(device))
    # print('IoT Device location: ' + str(location))

    return device, location

def wallCornorHandling(device, reports, pos_star, wall_Info):

    m = 10      # number of test points (base: 2m)
    prodistance = 100   # distance between wall and centroid which is condition of wall-corner handling (base: 2m)

    properDistance = sl.prodistance    # distance between wall and centroid which is condition of wallcorner handling
    numofPoint = sl.m  # number of points for test
    limitofWallhandling = math.ceil(numofPoint / 2)     # number of points to test when wall handling
    limitofCornorhandling = math.ceil(numofPoint / 4)    # number of points to test when corner handling
    numofadjWall = 0    # The number of walls adjacent to pos_star
    adjReports = []  # set of points which are adjacent to the wall or corner
    adjWall = Wall()    # set of wall adjacent to pos_star

    # 1. find adjacent wall to the pos_star(centroid point)
    for j in wall_Info:
        # when wall is vertical to x-axis
        if j["startpoint"].x == j["endpoint"].x:
            # 설정한 거리 안인지 확인
            if j["startpoint"].x - properDistance <= pos_star.x <= j["startpoint"].x + properDistance:
                # 설정한 거리 안인데 벽의 y축 범위 안에 있는 경우
                if j["startpoint"].y <= pos_star.y <= j["endpoint"].y:
                    # 인접한 벽 저장
                    adjWall.add_wall(j["startpoint"].x, j["startpoint"].y, j["endpoint"].x, j["endpoint"].y)
                    numofadjWall = numofadjWall + 1
        # 벽이 y축에 수직인 경우
        elif j["startpoint"].y == j["endpoint"].y:
            # 설정한 거리 안인지 확인
            if j["startpoint"].y - properDistance <= pos_star.y <= j["startpoint"].y + properDistance:
                # 설정한 거리 안인데 벽의 x축 범위 안에 있는 경우
                if j["startpoint"].x <= pos_star.x <= j["endpoint"].x:
                    # 인접한 벽 저장
                    adjWall.add_wall(j["startpoint"].x, j["startpoint"].y, j["endpoint"].x, j["endpoint"].y)
                    numofadjWall = numofadjWall + 1
    # adjWall.print_wall()      # print 인접 벽
    # print("len of adjWall:", numofadjWall)

    # rssi를 기준으로 sorting 한 reports
    sorted_reports = sorted(reports, key=attrgetter('rssi'), reverse=True)

    # 2.1 case of Wall handling (한개의 벽에서 설정한 거리 안에 있는 경우)
    if numofadjWall == 1:
        case = "Case of Wall handling"
        # 벽이 x축에 수직인 경우
        if adjWall[0]["startpoint"].x == adjWall[0]["endpoint"].x:
            #  rssi 가 쌘점 m/2개 선택 (in adjReports)
            n = 0
            i = 0
            lengthofReports = len(reports)
            while n < limitofWallhandling and i < lengthofReports:
                if (adjWall[0]["startpoint"].y <= sorted_reports[i].position.y <= adjWall[0]["endpoint"].y) \
                        and (adjWall[0]["startpoint"].x - properDistance <= sorted_reports[i].position.x <= adjWall[0]["startpoint"].x + properDistance):
                    adjReports.append(sl.Report(sorted_reports[i].timestamp, sorted_reports[i].position.x,
                                                sorted_reports[i].position.y, sorted_reports[i].rssi))
                    n = n + 1
                i = i + 1
            # centroid
            if len(adjReports) != 0:
                sum_y = 0
                for i in adjReports:
                    sum_y = sum_y + i.position.y
                pos_star = sl.Pos(adjWall[0]["startpoint"].x, sum_y / len(adjReports))
                # reports에 대칭한 값들 포함
                for i in adjReports:
                    reports.append(
                        sl.Report(len(reports) + 1, 2 * adjWall[0]["startpoint"].x - i.position.x, i.position.y, i.rssi))

        # 벽이 y축에 수직인 경우
        elif adjWall[0]["startpoint"].y == adjWall[0]["endpoint"].y:
            #  rssi 가 쌘점 m/2개 선택 (in adjReports)
            n = 0
            i = 0
            lengthofReports = len(reports)
            while n < limitofWallhandling and i < lengthofReports:
                if (adjWall[0]["startpoint"].x <= sorted_reports[i].position.x <= adjWall[0]["endpoint"].x) \
                        and (adjWall[0]["startpoint"].y - properDistance
                             <= sorted_reports[i].position.y <= adjWall[0]["startpoint"].y + properDistance):
                    adjReports.append(sl.Report(sorted_reports[i].timestamp, sorted_reports[i].position.x,
                                                sorted_reports[i].position.y, sorted_reports[i].rssi))
                    n = n + 1
                i = i + 1
            # centroid
            if len(adjReports) != 0:
                sum_x = 0
                for i in adjReports:
                    sum_x = sum_x + i.position.x
                pos_star = sl.Pos(sum_x / len(adjReports), adjWall[0]["startpoint"].y)
                # reports에 대칭한 값들 포함
                for i in adjReports:
                    reports.append(
                        sl.Report(len(reports) + 1, i.position.x, 2 * adjWall[0]["startpoint"].y - i.position.y, i.rssi))

    # 2.2 case of corner handling 두개의 벽에서 설정한 거리 안에 있는 경우
    elif numofadjWall == 2:
        case = "case of corner handling"
        # 첫번째 벽이 x축에 수직인 경우 (두번째 벽은 y축에 수직)
        if adjWall[0]["startpoint"].x == adjWall[0]["endpoint"].x:
            # 두 벽의 교점 좌표
            inter_x = adjWall[0]["startpoint"].x
            inter_y = adjWall[1]["startpoint"].y

            maxX = 0
            minX = 0
            maxY = 0
            minY = 0
            # 1. corner가 ㄴ모양인 경우
            if pos_star.x > inter_x and pos_star.y > inter_y:
                # x 값 범위
                if inter_x + properDistance > adjWall[1]["endpoint"].x:
                    maxX = adjWall[1]["endpoint"].x
                    minX = inter_x
                else:
                    maxX = inter_x + properDistance
                    minX = inter_x
                # y값 범위
                if inter_y + properDistance > adjWall[0]["endpoint"].y:
                    maxY = adjWall[0]["endpoint"].y
                    minY = inter_y
                else:
                    maxY = inter_y + properDistance
                    minY = inter_y

            # 2. corner가 ㄴ 상하반전한 모양인 경우
            elif pos_star.x > inter_x and pos_star.y < inter_y:
                # x 값 범위
                if inter_x + properDistance > adjWall[1]["endpoint"].x:
                    maxX = adjWall[1]["endpoint"].x
                    minX = inter_x
                else:
                    maxX = inter_x + properDistance
                    minX = inter_x
                # y값 범위
                if inter_y - properDistance > adjWall[0]["startpoint"].y:
                    maxY = inter_y
                    minY = inter_y - properDistance
                else:
                    maxY = inter_y
                    minY = adjWall[0]["startpoint"].y

            # 3. 두벽이 ㄱ 모양인 경우
            elif pos_star.x < inter_x and pos_star.y < inter_y:
                # x 값 범위
                if inter_x - properDistance > adjWall[1]["startpoint"].x:
                    maxX = inter_x
                    minX = inter_x - properDistance
                else:
                    maxX = inter_x
                    minX = adjWall[1]["startpoint"].x
                # y값 범위
                if inter_y - properDistance > adjWall[0]["startpoint"].y:
                    maxY = inter_y
                    minY = inter_y - properDistance
                else:
                    maxY = inter_y
                    minY = adjWall[0]["startpoint"].y

            # 4. 두벽이  ㄱ 상하반전한 모양인 경우
            elif pos_star.x < inter_x and pos_star.y > inter_y:
                # x 값 범위
                if inter_x - properDistance > adjWall[1]["startpoint"].x:
                    maxX = inter_x
                    minX = inter_x - properDistance
                else:
                    maxX = inter_x
                    minX = adjWall[1]["startpoint"].x
                # y값 범위
                if inter_y + properDistance > adjWall[0]["endpoint"].y:
                    maxY = adjWall[0]["endpoint"].y
                    minY = inter_y
                else:
                    maxY = inter_y + properDistance
                    minY = inter_y

            # m/4개의 점 선택
            n = 0
            i = 0
            lengthofReports = len(reports)
            while (n < limitofCornorhandling) & (i < lengthofReports):
                if (minX < sorted_reports[i].position.x < maxX) and (minY < sorted_reports[i].position.y < maxY):
                    adjReports.append(sl.Report(sorted_reports[i].timestamp, sorted_reports[i].position.x,
                                                sorted_reports[i].position.y, sorted_reports[i].rssi))
                    n = n + 1
                i = i + 1

            if len(adjReports) != 0:
                # 두벽의 교점을 pos_star로 지정
                pos_star = sl.Pos(inter_x, inter_y)
                # reports에 대칭한 점 추가
                for i in adjReports:
                    # x축 대칭
                    reports.append(
                        sl.Report(len(reports) + 1, 2 * inter_x - i.position.x, i.position.y, i.rssi))
                    # y축 대칭
                    reports.append(sl.Report(len(reports) + 1, i.position.x, 2 * inter_y - i.position.y, i.rssi))
                    # 점 대칭
                    reports.append(sl.Report(len(reports) + 1, 2 * inter_x - i.position.x,
                                             2 * inter_y - i.position.y, i.rssi))

        # 첫번째 벽이 y축에 수직인 경우 (두번째 벽은 x축에 수직)
        elif adjWall[0]["startpoint"].y == adjWall[0]["endpoint"].y:

            # 두 벽의 교점 좌표
            inter_x = adjWall[1]["startpoint"].x
            inter_y = adjWall[0]["startpoint"].y

            # 두벽의 교점을 왼쪽 아래로 하는 설정한 거리를 변의 길이로 가지는 정사각형 안에 있는 m/4개의 점 선택

            maxX = 0
            minX = 0
            maxY = 0
            minY = 0
            # 1. corner가 ㄴ모양인 경우
            if pos_star.x > inter_x and pos_star.y > inter_y:
                # x 값 범위
                if inter_x + properDistance > adjWall[0]["endpoint"].x:
                    maxX = adjWall[0]["endpoint"].x
                    minX = inter_x
                else:
                    maxX = inter_x + properDistance
                    minX = inter_x
                # y값 범위
                if inter_y + properDistance > adjWall[1]["endpoint"].y:
                    maxY = adjWall[1]["endpoint"].y
                    minY = inter_y
                else:
                    maxY = inter_y + properDistance
                    minY = inter_y

            # 2. corner가 ㄴ 상하반전한 모양인 경우
            elif pos_star.x > inter_x and pos_star.y < inter_y:
                # x 값 범위
                if inter_x + properDistance > adjWall[0]["endpoint"].x:
                    maxX = adjWall[0]["endpoint"].x
                    minX = inter_x
                else:
                    maxX = inter_x + properDistance
                    minX = inter_x
                # y값 범위
                if inter_y - properDistance > adjWall[1]["startpoint"].y:
                    maxY = inter_y
                    minY = inter_y - properDistance
                else:
                    maxY = inter_y
                    minY = adjWall[1]["startpoint"].y

            # 3. 두벽이 ㄱ 모양인 경우
            elif pos_star.x < inter_x and pos_star.y < inter_y:
                # x 값 범위
                if inter_x - properDistance > adjWall[0]["startpoint"].x:
                    maxX = inter_x
                    minX = inter_x - properDistance
                else:
                    maxX = inter_x
                    minX = adjWall[0]["startpoint"].x
                # y값 범위
                if inter_y - properDistance > adjWall[1]["startpoint"].y:
                    maxY = inter_y
                    minY = inter_y - properDistance
                else:
                    maxY = inter_y
                    minY = adjWall[1]["startpoint"].y

            # 4. 두벽이  ㄱ 상하반전한 모양인 경우
            elif pos_star.x < inter_x and pos_star.y > inter_y:
                # x 값 범위
                if inter_x - properDistance > adjWall[0]["startpoint"].x:
                    maxX = inter_x
                    minX = inter_x - properDistance
                else:
                    maxX = inter_x
                    minX = adjWall[0]["startpoint"].x
                # y값 범위
                if inter_y + properDistance > adjWall[1]["endpoint"].y:
                    maxY = adjWall[1]["endpoint"].y
                    minY = inter_y
                else:
                    maxY = inter_y + properDistance
                    minY = inter_y
            # m/4개의 점 선택 (in adjReports)
            n = 0
            i = 0
            lengthofReports = len(reports)
            while n < limitofCornorhandling and i < lengthofReports:
                if (minX < sorted_reports[i].position.x < maxX) and (minY < sorted_reports[i].position.y < maxY):
                    adjReports.append(sl.Report(sorted_reports[i].timestamp, sorted_reports[i].position.x,
                                                sorted_reports[i].position.y, sorted_reports[i].rssi))
                    n = n + 1
                i = i + 1
            if len(adjReports) != 0:
                # 두벽의 교점으로 pos_star 지정
                pos_star = sl.Pos(adjWall[1]["startpoint"].x, inter_y)
                # reports에 대칭한 점 추가
                for i in adjReports:
                    # x축 대칭
                    reports.append(
                        sl.Report(len(reports) + 1, 2 * inter_x - i.position.x, i.position.y, i.rssi))
                    # y축 대칭
                    reports.append(
                        sl.Report(len(reports) + 1, i.position.x, 2 * inter_y - i.position.y, i.rssi))
                    # 점 대칭
                    reports.append(sl.Report(len(reports) + 1, 2 * inter_x - i.position.x,
                                             2 * inter_y - i.position.y, i.rssi))
    else:
        case = "Not the case of wall-corner handling"
    # 세개의 벽은 핸들링의 대상에서 제외 (해당 기기가 벽에 치우쳐서 쓰는 용도로 보기가 힘듦)

    # 3. result
    # print('\n===================================')
    # print('=== Wall Cornor Handling Result ===')
    # print('===================================')
    # print(case)
    # print('IoT Device: '+str(device))
    # print('report list length: ' + str(len(reports)))
    # print('RSSI centroid (p*): '+str(pos_star))

    return device, reports, pos_star


class Wall(list):

    def print_wall(self):
        for k in self:
            print("startpoint (", k["startpoint"].x, ",", k["startpoint"].y, "), endpoint ("
                  , k["endpoint"].x, ",", k["endpoint"].y, ")")

    # Condition: startpoint must be smaller than endpoint
    def add_wall(self, x1, y1, x2, y2):
        line = dict()
        line["startpoint"] = sl.Pos(x1, y1)
        line["endpoint"] = sl.Pos(x2, y2)
        self.append(line)
