import os
from array import array
from abc import ABCMeta, abstractmethod

from util.bitarray import makeBitArray, setBit, testBit


class AbstractWorldFactory:
    __metaclass__ = ABCMeta

    def __init__(self, width: int, height: int):
        self._width = width
        self._height = height

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @abstractmethod
    def is_live_cell(self, world, row: int, col: int) -> bool:
        """Returns true if cell of world is live or false otherwise"""

    @abstractmethod
    def revive_cell(self, world, row: int, col: int):
        """Revive cell of world"""

    @abstractmethod
    def kill_cell(self, world, row: int, col: int):
        """Kill cell of world"""

    @abstractmethod
    def create_empty_world(self):
        """Create new world that all cell is dead"""

    @abstractmethod
    def create_random_world(self):
        """Create new world with random state of cells"""

    @abstractmethod
    def create_next_world(self, world):
        """Create new world based on the existing world"""

    def create_world_from_array(self, array_):
        """Create new world from the bitarray"""

        new_world = self.create_empty_world()

        i = 0
        for row in range(self._height):
            for col in range(self._width):
                if testBit(array_, i):
                    self.revive_cell(new_world, row, col)
                i += 1

        return new_world

    def pack_world_into_array(self, world):
        """Pack the world into a bitarray"""

        array_ = makeBitArray(self._width * self._height, fill=0)

        i = 0
        for row in range(self._height):
            for col in range(self._width):
                if self.is_live_cell(world, row, col):
                    setBit(array_, i)
                i += 1

        return array_

    def pack_two_worlds_into_array(self, prev_world, cur_world):
        """Pack two worlds (previous and current) into an uint32 array (2 bit per cell)"""

        size = self._width * self._height * 2
        array_ = array('L', (0,) * ((size + 31) >> 5))

        i = 0
        for row in range(self._height):
            for col in range(self._width):
                value = self.is_live_cell(cur_world, row, col) | (self.is_live_cell(prev_world, row, col) << 1)
                record = i >> 5
                offset = i & 31
                array_[record] |= value << offset
                i += 2

        return array_


if int(os.environ.get('NAIVE_ALGO', 0)):
    from .bitarray import WorldFactory
else:
    from .world64 import WorldFactory
