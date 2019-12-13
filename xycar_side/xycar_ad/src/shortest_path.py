# -*- coding: utf-8 -*-
# -*- coding: euc-kr -*-

import Queue

class SPF(object):

    def __init__(self, W, H):
        # 가로가 W이고 높이가 H인 빈 지도 생성

        self.W = W
        self.H = H

        self.Map = [[False for x in range(self.W)] for y in range(self.H)]

    def set_obs(self, x, y):
        # (x, y)에 장애물 표시
        self.Map[y][x] = True


    def get_path(self, sx, sy, dx, dy):
        #(x, y)에서 출발 했을 때 경로 좌표들의 리스트 반환

        q = Queue.Queue()
        q.put([sx, sy, 1])


        dir = [[-1, 0], [1, 0], [0, -1], [0, 1]]

        visit = [[False for x in range(self.W)] for y in range(self.H)]
        preP = [[[0, 0] for x in range(self.W)] for y in range(self.H)]

	visit[sy][sx] = True

        while not q.empty():
            t = q.get()

            if t[0] == dx and t[1] == dy:
                break

            for d in dir:
                variable_x = t[0] + d[0]
                variable_y = t[1] + d[1]
                if variable_x < 0 or variable_y < 0 or variable_x >= self.W or variable_y >= self.H:
                     continue
                if visit[variable_y][variable_x]:
                    continue
                if self.Map[variable_y][variable_x]:
                    continue

                visit[variable_y][variable_x] = True
                preP[variable_y][variable_x] = [t[0], t[1]]
                q.put([variable_x, variable_y, t[2] + 1])

	'''
	0: empty grid
	1: path
	2: current grid
	3: target grid
	-1: obstacle
	'''
	drawMap = [[0 for x in range(self.W)] for y in range(self.H)]
	drawMap[dy][dx] = 1 #'@'
	
        variable_x, variable_y = dx, dy

        path_list = [[dx, dy]]

        while not (variable_x == sx and variable_y == sy):
            path_list.append(preP[variable_y][variable_x])
            variable_x, variable_y = preP[variable_y][variable_x]
	    drawMap[variable_y][variable_x] = 1 #'@'
	drawMap[sy][sx] = 2 #'&'
	drawMap[dy][dx] = 3
        path_list.reverse()

	currentMap = [self.W, self.H]
	
	for y in range(self.H):
		r = []
		for x in range(self.W):
			if self.Map[y][x]:
				#r += 'X'
				r.append(-1)
			else:
				#r += drawMap[y][x]
				r.append(drawMap[y][x])
		#currentMap += r + '\n'
		#currentMap.append(r)
		currentMap += r
		#print(r)
	#print()

        return (path_list[1:], currentMap)
