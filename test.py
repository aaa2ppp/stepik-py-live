import time

from game_of_life import CellGeneration
from util.bitarray import makeBitArray, setBit

count = 100
width = 200
height = 100
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
# for _ in range(count):
#     s = hash(tuple(cells))
# end_time = time.time()
# print("calc hash sum:", end_time - start_time)
