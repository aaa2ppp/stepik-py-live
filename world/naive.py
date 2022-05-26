from array import array
from random import randint

from util.bitarray import getBit, makeBitArray, setBit, clearBit
from world import WorldFactory


class OriginalWorldFactory(WorldFactory):

    def is_live_cell(self, world, row: int, col: int) -> bool:
        return world[row][col]

    def revive_cell(self, world, row: int, col: int):
        world[row][col] = 1

    def kill_cell(self, world, row: int, col: int):
        world[row][col] = 0

    def create_empty_world(self):
        return [[0 for _ in range(self._width)] for _ in range(self._height)]

    def create_random_world(self):
        return [[randint(0, 1) for _ in range(self._width)] for _ in range(self._height)]

    def create_next_world(self, world):
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


class BitArrayWorldFactory(WorldFactory):

    def __init__(self, width: int, height: int):
        super().__init__(width, height)

    def is_live_cell(self, world, row: int, col: int):
        return getBit(world, row * self._width + col)

    def revive_cell(self, world, row: int, col: int):
        setBit(world, row * self._width + col)

    def kill_cell(self, world, row: int, col: int):
        clearBit(world, row * self._width + col)

    def create_empty_world(self):
        return makeBitArray(self._width * self._height, fill=0)

    def create_random_world(self):
        return makeBitArray(self._width * self._height, random=True)

    def create_next_world(self, world):
        """
        1. Any live cell with two or three live neighbours survives.
        2. Any dead cell with three live neighbours becomes a live cell.
        3. All other live cells die in the next generation. Similarly, all other dead cells stay dead.

        https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life#Rules
        """

        width, height = self._width, self._height
        size = width * height
        new_world = makeBitArray(size)

        # Calculate indexes
        #  rX - row offset
        #  cX - position in row
        #
        #    |   c1  |   c0  |   c2  |
        # ---+-------+-------+-------+
        # r1 | r1+c1 | r1+c0 | r1+c2 |
        # ---+-------+-------+-------+
        # r0 | r0+c1 |   i   | r0+c2 |
        # ---+-------+-------+-------+
        # r2 | r2+c1 | r2+c0 | r2+c2 |
        # ---+-------+-------+-------+

        for r0 in range(0, size, width):
            r1 = (r0 - width) % size
            r2 = (r0 + width) % size

            for c0 in range(width):
                c1 = (c0 - 1) % width
                c2 = (c0 + 1) % width

                neighbours = (getBit(world, r0 + c1) + getBit(world, r0 + c2) +
                              getBit(world, r1 + c1) + getBit(world, r1 + c2) + getBit(world, r1 + c0) +
                              getBit(world, r2 + c1) + getBit(world, r2 + c2) + getBit(world, r2 + c0))

                i = r0 + c0
                if neighbours == 3 or neighbours == 2 and getBit(world, i):
                    setBit(new_world, i)

        return new_world
