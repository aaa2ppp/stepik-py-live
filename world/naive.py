from array import array
from random import randint

from util.bitarray import getBit, makeBitArray, setBit, clearBit
from world import WorldFactory


class OrigWorldFactory(WorldFactory):

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

    def __init__(self, width, height):
        super(BitArrayWorldFactory, self).__init__(width, height)

        # To performance pack old and new worlds, we allocate 2 bit per cell
        self._row_size = row_size = width << 1
        self._size = row_size * height

    def is_live_cell(self, world, row: int, col: int):
        return getBit(world, row * self._row_size + (col << 1))

    def revive_cell(self, world, row: int, col: int):
        setBit(world, row * self._row_size + (col << 1))

    def kill_cell(self, world, row: int, col: int):
        clearBit(world, row * self._row_size + (col << 1))

    def create_empty_world(self):
        return makeBitArray(self._size, fill=0)

    def create_random_world(self):
        new_world = makeBitArray(self._size, random=True)
        for record in range(len(new_world)):
            new_world[record] &= 0x5555_5555
        return new_world

    def create_next_world(self, world):
        """
        1. Any live cell with two or three live neighbours survives.
        2. Any dead cell with three live neighbours becomes a live cell.
        3. All other live cells die in the next generation. Similarly, all other dead cells stay dead.

        https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life#Rules
        """

        size, row_size, height = self._size, self._row_size, self._height
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

        for r0 in range(0, size, row_size):
            r1 = (r0 - row_size) % size
            r2 = (r0 + row_size) % size

            for c0 in range(0, row_size, 2):
                c1 = (c0 - 2) % row_size
                c2 = (c0 + 2) % row_size

                neighbours = (getBit(world, r0 + c1) + getBit(world, r0 + c2) +
                              getBit(world, r1 + c1) + getBit(world, r1 + c2) + getBit(world, r1 + c0) +
                              getBit(world, r2 + c1) + getBit(world, r2 + c2) + getBit(world, r2 + c0))

                i = r0 + c0
                if neighbours == 3 or neighbours == 2 and getBit(world, i):
                    setBit(new_world, i)

        return new_world

    def pack_two_worlds_to_array(self, old_world, new_world):
        result = array('L')
        for num0, num1 in zip(new_world, old_world):
            result.append(num0 | (num1 << 1))
        return result
