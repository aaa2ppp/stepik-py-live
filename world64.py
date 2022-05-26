from array import array
from random import randint

from util.bitarray64 import getFourBits, getOneBit, setBit


class WorldFactory:

    def __init__(self, width, height):
        self._row_size = row_size = self.calc_row_size(width)
        self._size = size = row_size * height
        self._width = row_size << 4  # FIXME: adjustment of width for 32 bit data alignment
        self._height = height
        self._subtotals = array('Q', (0,) * size)

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @staticmethod
    def calc_row_size(width):
        # To performance, we allocate 4 bits per cell and align the row size by 64 bits.
        return ((width << 2) + 63) >> 6

    def cell_is_live(self, world, row, col):
        record = row * self._row_size + (col >> 4)
        offset = (col << 2) & 63
        return (world[record] >> offset) & 1

    def create_empty_world(self):
        return array('Q', (0,) * self._size)

    def create_random_world(self):
        return array('Q', (randint(0, 0xFFFF_FFFF_FFFF_FFFFF) & 0x1111_1111_1111_1111 for _ in range(self._size)))

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

        row_size = self._row_size
        size = self._size

        # Let's calculate the vertical neighbors for each 1x3 rectangle. To speed up, we sum numbers instead of bits

        subtotals = self._subtotals
        for r0 in range(0, size, row_size):
            r1 = (r0 - row_size) % size
            r2 = (r0 + row_size) % size
            for c0 in range(row_size):
                i = r0 + c0
                subtotals[i] = world[i] + world[r1 + c0] + world[r2 + c0]

        # Now let's sum horizontally to calculate all the neighbors in each 3x3 square...

        new_world = array('Q', (0,) * size)
        for r0 in range(0, size, row_size):
            for c0 in range(row_size):
                i = r0 + c0
                i1 = r0 + (c0 - 1) % row_size
                i2 = r0 + (c0 + 1) % row_size

                x = (subtotals[i] +
                     ((subtotals[i] & 0x0FFF_FFFF_FFFF_FFFF) << 4) + (subtotals[i1] >> 60) +
                     (subtotals[i] >> 4) + ((subtotals[i2] & 0xF) << 60))

                # Bit magic
                # (X₀ & X₁ & ̅X₂ & ̅X₃) V (̅X₁ & X₂ & X₃)
                # TODO: проверить что не "навалял"

                x0 = world[i] & 0x1111_1111_1111_1111
                x1 = (x >> 2) & 0x1111_1111_1111_1111
                x2 = (x >> 1) & 0x1111_1111_1111_1111
                x3 = x & 0x1111_1111_1111_1111
                new_world[i] = x0 & x1 & ~x2 & ~x3 | ~x1 & x2 & x3

        return new_world
