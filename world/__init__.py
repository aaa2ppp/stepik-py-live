import os
from array import array
from abc import ABCMeta, abstractmethod


class WorldFactory:

    __metaclass__ = ABCMeta

    def __init__(self, width: int, height: int):
        self._width = width
        self._height = height
        self._prev_world = None
        self._world = self._create_empty_world()

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @abstractmethod
    def is_live_cell(self, row: int, col: int) -> bool:
        """Returns true if cell of current world is live or false otherwise"""

    @abstractmethod
    def revive_cell(self, row: int, col: int) -> None:
        """Revive cell of current world"""

    @abstractmethod
    def kill_cell(self, row: int, col: int) -> None:
        """Kill cell of current world"""

    def next_empty(self):
        self._prev_world = self._world
        self._world = self._create_empty_world()

    def next_random(self):
        self._prev_world = self._world
        self._world = self._create_random_world()

    def next(self):
        self._prev_world = self._world
        self._world = self._create_next_world()

    def next_from_array(self, array_) -> None:
        width, height = self._width, self._height
        new_world = self._create_empty_world()

        i = 0
        for row in range(height):
            for col in range(width):
                record = i >> 5
                offset = i & 31
                if array_[record] & (1 << offset):
                    self.revive_cell(row, col)
                i += 1

        self._prev_world = self._world
        self._world = new_world

    @abstractmethod
    def _create_empty_world(self) -> object:
        """Create new world that all cell is dead"""

    @abstractmethod
    def _create_random_world(self) -> object:
        """Create new world with random state of cells"""

    @abstractmethod
    def _create_next_world(self, world) -> object:
        """Create new world based on the exists world"""

    def pack_world_to_array(self):
        """Pack the current world into an uint32 array (1 bit per cell)"""

        width, height = self._width, self._height
        size = width * height
        result = array('L', (0,) * ((size + 31) >> 5))

        i = 0
        for row in range(height):
            for col in range(width):
                record = i >> 5
                offset = i & 31
                result[record] |= self.is_live_cell(row, col) << offset
                i += 1

        return result

    def get_as_array(self):
        """Pack two worlds (old and new) into an uint32 array (2 bit per cell)"""

        old_world, new_world = self._prev_world, self._world
        width, height = self._width, self._height
        size = width * height
        result = array('L', (0,) * ((size + 15) >> 4))

        i = 0
        for row in range(height):
            for col in range(width):
                record = i >> 5
                offset = i & 31
                result[record] |= (self.is_live_cell(row, col) | (
                            self.is_live_cell(row, col) << 1)) << offset
                i += 2

        return result


from .naive import BitArrayWorldFactory, OrigWorldFactory
from .world64 import World64Factory

factory = BitArrayWorldFactory if int(os.environ.get('NAIVE_ALGO', 0)) else World64Factory
