import os
from array import array

from util.bitarray import makeBitArray, setBit, testBit


class WorldFactory:

    def __init__(self, width: int, height: int):
        self._width = width
        self._height = height

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    def is_live_cell(self, world, row: int, col: int) -> bool:
        raise Exception("Abstract method")

    def revive_cell(self, world, row: int, col: int):
        raise Exception("Abstract method")

    def kill_cell(self, world, row: int, col: int):
        raise Exception("Abstract method")

    def create_empty_world(self):
        raise Exception("Abstract method")

    def create_random_world(self):
        raise Exception("Abstract method")

    def create_next_world(self, world):
        raise Exception("Abstract method")

    def create_world_from_bitarray(self, array_):
        width, height = self._width, self._height
        new_world = self.create_empty_world()

        for row in range(height):
            offset = row * width
            for col in range(width):
                if testBit(array_, offset + col):
                    self.revive_cell(new_world, row, col)

        return new_world

    def convert_world_to_bitarray(self, world):
        width, height = self._width, self._height
        array_ = makeBitArray(width * height)

        i = 0
        for row in range(height):
            for col in range(width):
                if self.is_live_cell(world, row, col):
                    setBit(array_, i)
                i += 1

        return array_

    def pack(self, old_world, new_world):
        width, height = self._width, self._height
        size = width * height
        result = array('L', (0,) * ((size + 15) >> 4))
        i = 0
        for row in range(height):
            for col in range(width):
                record = i >> 5
                offset = i & 31
                result[record] |= (self.is_live_cell(new_world, row, col) | (
                            self.is_live_cell(old_world, row, col) << 1)) << offset
                i += 2
        return result


from .naive import BitArrayWorldFactory, OriginalWorldFactory
from .world64 import World64Factory

factory = BitArrayWorldFactory if int(os.environ.get('NAIVE_ALGO', 0)) else World64Factory
