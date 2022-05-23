import time

from game_of_life import CellGeneration
from util.bitarray import makeBitArray, setBit

count = 1000
size = 100

start_time = time.time()

cells = makeBitArray(100 * 100)
for _ in range(count):
    for i in range(size * size):
        setBit(cells, i)
end_time = time.time()
print("fill bit array:", end_time - start_time)

cells = CellGeneration(size, size, random=True)
start_time = time.time()
for _ in range(count):
    cells.create_next_generation()
end_time = time.time()
print("create next generation:", end_time - start_time)

cells = makeBitArray(size * size, random=True)
start_time = time.time()
for _ in range(count):
    s = hash(tuple(cells))
end_time = time.time()
print("calc hash sum:", end_time - start_time)
