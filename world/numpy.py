from array import array
import numpy as np

from world import AbstractWorldFactory


class WorldFactory(AbstractWorldFactory):

    def __init__(self, width, height):
        super(WorldFactory, self).__init__(width, height)

        # To improve the performance of the world calculation, we store the world in an array of 64-bit integers,
        # allocate 4 bits per cell, and align size the row to the size of the array elements.
        self._row_size = row_size = ((width << 2) + 63) >> 6

        # FIXME: adjusting the width of world (to align the data row with the array elements)
        self._width = row_size << 4

    def is_live_cell(self, world, row, col):
        offset = (col << 2) & 63
        return int(world[row, col >> 4] >> np.uint(offset)) & 1

    def revive_cell(self, world, row: int, col: int):
        offset = (col << 2) & 63
        world[row, col >> 4] |= np.uint64(1 << offset)

    def kill_cell(self, world, row: int, col: int):
        offset = (col << 2) & 63
        world[row, col >> 4] &= ~np.uint64(1 << offset)

    def create_empty_world(self):
        return np.zeros((self._height, self._row_size), dtype='uint64')

    def create_random_world(self):
        return np.random.randint(0x1_0000_0000_0000_0000, size=(self._height, self._row_size),
                                 dtype='uint64') & 0x1111_1111_1111_1111

    def create_next_world(self, world):
        """
        1. Any live cell with two or three live neighbours survives.
        2. Any dead cell with three live neighbours becomes a live cell.
        3. All other live cells die in the next generation. Similarly, all other dead cells stay dead.

        https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life#Rules
        """

        # Let's calculate the vertical neighbors for each 1x3 rectangle. To speed up, we sum 64-bit integer numbers
        # instead of bits.

        subtotals = world + np.roll(world, 1, axis=0) + np.roll(world, -1, axis=0)

        # Now let's sum horizontally to calculate all the neighbors in each 3x3 square (x0)...

        x0 = (subtotals +
              (subtotals << 4) + (np.roll(subtotals, 1, axis=1) >> 60) +
              (subtotals >> 4) + (np.roll(subtotals, -1, axis=1) << 60))

        # ... and add bit magic to get new cell states

        x2 = x0 >> 2
        x1 = x0 >> 1
        return (world & x2 & ~x1 & ~x0 | ~x2 & x1 & x0) & 0x1111_1111_1111_1111

    def pack_two_worlds_into_array(self, prev_world, cur_world):
        """Pack two worlds (previous and current) into an uint32 array (2 bit per cell)"""

        pack = cur_world | (prev_world << 1)

        pack |= pack >> 2
        pack = (pack & 0x000F_000F_000F_000F) | ((pack >> 4) & 0x00F0_00F0_00F0_00F0)
        pack = (pack & 0x0000_00FF_0000_00FF) | ((pack >> 8) & 0x0000_FF00_0000_FF00)
        pack = (pack & 0x0000_0000_0000_FFFF) | (pack >> 16)

        return array('L', pack.flat)
