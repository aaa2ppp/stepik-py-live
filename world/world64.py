from array import array
from random import randint

from util.bitarray import getBit
from world import AbstractWorldFactory


class WorldFactory(AbstractWorldFactory):

    def __init__(self, width, height):
        super(WorldFactory, self).__init__(width, height)

        # To improve the performance of the world calculation, we store the world in an array of 64-bit integers,
        # allocate 4 bits per cell, and size the strings to the size of the array elements.
        self._row_size = row_size = ((width << 2) + 63) >> 6
        self._size = size = row_size * height
        self._subtotals = array('Q', (0,) * size)

        # FIXME: adjusting the width of world (to align the data row with the array elements)
        self._width = row_size << 4

    def is_live_cell(self, world, row, col):
        record = row * self._row_size + (col >> 4)
        offset = (col << 2) & 63
        return (world[record] >> offset) & 1

    def revive_cell(self, world, row: int, col: int):
        record = row * self._row_size + (col >> 4)
        offset = (col << 2) & 63
        world[record] |= (1 << offset)

    def kill_cell(self, world, row: int, col: int):
        record = row * self._row_size + (col >> 4)
        offset = (col << 2) & 63
        world[record] &= ~(1 << offset)

    def create_empty_world(self):
        return array('Q', (0,) * self._size)

    def create_random_world(self):
        return array('Q', (randint(0, 0xFFFF_FFFF_FFFF_FFFF) & 0x1111_1111_1111_1111 for _ in range(self._size)))

    def create_next_world(self, world):
        """
        1. Any live cell with two or three live neighbours survives.
        2. Any dead cell with three live neighbours becomes a live cell.
        3. All other live cells die in the next generation. Similarly, all other dead cells stay dead.

        https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life#Rules
        """

        # Index calculating.
        # rX - row offset
        # cX - position in row
        #
        #    |   c1  |   c0  |   c2  |
        # ---+-------+-------+-------+
        # r1 | r1+c1 | r1+c0 | r1+c2 |
        # ---+-------+-------+-------+
        # r0 | r0+c1 | r0+c0 | r0+c2 |
        # ---+-------+-------+-------+
        # r2 | r2+c1 | r2+c0 | r2+c2 |
        # ---+-------+-------+-------+

        row_size, size, subtotals = self._row_size, self._size, self._subtotals
        new_world = array('Q', (0,) * size)

        # Let's calculate the vertical neighbors for each 1x3 rectangle. To speed up, we sum 64-bit integer numbers
        # instead of bits.

        for r0 in range(0, size, row_size):
            r1 = (r0 - row_size) % size
            r2 = (r0 + row_size) % size
            for c0 in range(row_size):
                i = r0 + c0
                subtotals[i] = world[i] + world[r1 + c0] + world[r2 + c0]

        # Now let's sum horizontally to calculate all the neighbors in each 3x3 square...

        for r0 in range(0, size, row_size):
            for c0 in range(row_size):
                i = r0 + c0
                i1 = r0 + (c0 - 1) % row_size
                i2 = r0 + (c0 + 1) % row_size

                neighbors = (subtotals[i] +
                             ((subtotals[i] & 0x0FFF_FFFF_FFFF_FFFF) << 4) + (subtotals[i1] >> 60) +
                             (subtotals[i] >> 4) + ((subtotals[i2] & 0xF) << 60))

                # Bit magic to get new cell state
                x1 = (neighbors >> 2) & 0x1111_1111_1111_1111
                x2 = (neighbors >> 1) & 0x1111_1111_1111_1111
                x3 = neighbors & 0x1111_1111_1111_1111
                new_world[i] = world[i] & x1 & ~x2 & ~x3 | ~x1 & x2 & x3

        return new_world

    def create_world_from_array(self, array_):
        size = self._size
        new_world = array('Q', (0,) * size)

        i = 0
        for record in range(size):
            num = 0
            for offset in range(0, 64, 4):
                num |= (getBit(array_, i) << offset)
                i += 1
            new_world[record] = num

        return new_world

    def pack_two_worlds_into_array(self, prev_world, cur_world):
        result = array('L')

        for num0, num1 in zip(cur_world, prev_world):
            even = num0 | (num1 << 1)  # ~24% of the time it's 0
            if even:
                # Next is bit magic. I don't understand how it works. I took it from
                # https://www.cyberforum.ru/post13690948.html
                even |= (even >> 2) & 0x0C0C_0C0C_0C0C_0C0C
                even = (even & 0x000F_000F_000F_000F) | ((even >> 4) & 0x00F0_00F0_00F0_00F0)
                even = (even & 0x0000_00FF_0000_00FF) | ((even >> 8) & 0x0000_FF00_0000_FF00)
                even = (even & 0x0000_0000_0000_FFFF) | ((even >> 16) & 0x0000_0000_FFFF_0000)
            result.append(even)

        return result