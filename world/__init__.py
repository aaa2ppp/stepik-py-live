import os
from array import array
from abc import ABCMeta, abstractmethod, abstractproperty

from util.bitarray import makeBitArray, setBit, testBit


class WorldFactory:

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

    def create_world_from_pack(self, array_):
        width, height = self._width, self._height
        new_world = self.create_empty_world()

        i = 0
        for row in range(height):
            for col in range(width):
                record = i >> 5
                offset = i & 31
                if array_[record] & (1 << offset):
                    self.revive_cell(new_world, row, col)
                i += 1

        return new_world

    def pack_world_to_array(self, world):
        """Pack the world into an uint32 array (1 bit per cell)"""

        width, height = self._width, self._height
        size = width * height
        result = array('L', (0,) * ((size + 31) >> 5))

        i = 0
        for row in range(height):
            for col in range(width):
                record = i >> 5
                offset = i & 31
                result[record] |= self.is_live_cell(world, row, col) << offset
                i += 1

        return result

    def pack_two_worlds_to_array(self, old_world, new_world):
        """Pack two worlds (old and new) into an uint32 array (2 bit per cell)"""

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


from .naive import BitArrayWorldFactory, OrigWorldFactory
from .world64 import World64Factory

factory = BitArrayWorldFactory if int(os.environ.get('NAIVE_ALGO', 0)) else World64Factory
