import time

from test64.game_of_life64 import CellGeneration
from util.bitarray import makeBitArray, setBit

count = 100
width = 2000
height = 200
size = width * height

start_time = time.time()

cells = makeBitArray(size)
for _ in range(count):
    for i in range(size):
        setBit(cells, i)
end_time = time.time()
print("fill bit array:", end_time - start_time)

cells = CellGeneration(width=width, height=height, random=True)
start_time = time.time()
for _ in range(count):
    cells = CellGeneration(previous=cells)
end_time = time.time()
print("create next generation:", end_time - start_time)

# cells = makeBitArray(size * size, random=True)
# start_time = time.time()
# s = []
# for i in range(count):
#     setBit(cells, i*7)
#     setBit(cells, i*29)
#     s.append(hash(tuple(cells)))
# end_time = time.time()
# print(s)
# print("calc hash sum:", end_time - start_time)
