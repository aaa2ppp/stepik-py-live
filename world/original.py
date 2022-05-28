from array import array
from random import randint

from util.bitarray import getBit, makeBitArray, setBit, clearBit
from world import WorldFactory


class OrigGame:

    def __init__(self, width, height):
        self._width = width
        self._height = height
        self._prev_world = self._create_empty_world()
        self._world = self._create_random_world()

    def is_live_cell(self, row: int, col: int) -> bool:
        return self._world[row][col]

    def revive_cell(self, row: int, col: int):
        self._world[row][col] = 1

    def kill_cell(self, row: int, col: int):
        self._world[row][col] = 0

    def _create_empty_world(self):
        return [[0] * self._width for _ in range(self._height)]

    def _create_random_world(self):
        return [[randint(0, 1) for _ in range(self._width)] for _ in range(self._height)]

    def _create_next_world(self, world):
        universe = world
        new_world = [[0 for _ in range(self._width)] for _ in range(self._height)]

        for i in range(len(universe)):
            for j in range(len(universe[0])):

                if universe[i][j]:
                    if self.__get_near(universe, [i, j]) not in (2, 3):
                        new_world[i][j] = 0
                        continue
                    new_world[i][j] = 1
                    continue

                if self.__get_near(universe, [i, j]) == 3:
                    new_world[i][j] = 1
                    continue
                new_world[i][j] = 0
        return new_world

    @staticmethod
    def __get_near(universe, pos, system=None):
        if system is None:
            system = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))

        count = 0
        for i in system:
            if universe[(pos[0] + i[0]) % len(universe)][(pos[1] + i[1]) % len(universe[0])]:
                count += 1
        return count

    def get_world_as_array(self):
        size = self._width * self._height
        result = array('L', (0,) * ((size + 15) >> 4))
        return self._fill_array(result)

    def _fill_array(self, array_):
        prev_world, world = self._prev_world, self._world
        i = 0
        for row in range(self._height):
            for col in range(self._width):
                record = i >> 5
                offset = i & 31
                array_[record] |= (world[row][col] | prev_world[row][col] << 1) << offset
                i += 2
        return array_

    def set_world_from_array(self, array_):
        prev_world, world = self._prev_world, self._world
        i = 0
        for row in range(self._height):
            for col in range(self._width):
                record = i >> 5
                offset = i & 31
                state = array_[record] >> offset
                world[row][col] = state & 1
                prev_world[row][col] = (state >> 1) & 1
                i += 2
        return array_
