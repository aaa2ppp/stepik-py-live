from random import randint
from functools import reduce
from operator import add
from typing import Optional

from bitarray import makeBitArray, setBit, testBit
from session import SessionContext


class GameOfLiveRules:
    """
    1. Any live cell with two or three live neighbours survives.
    2. Any dead cell with three live neighbours becomes a live cell.
    3. All other live cells die in the next generation. Similarly, all other dead cells stay dead.

    https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life#Rules}
    """

    _neighbors_coords = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))

    @classmethod
    def is_live_cell(cls, previous_generation: 'CellGeneration', row: int, col: int) -> bool:
        number_of_neighbors = cls.count_neighbors(previous_generation, row, col)

        if previous_generation.is_live_cell(row, col):
            return number_of_neighbors in (2, 3)
        else:
            return number_of_neighbors == 3

    @classmethod
    def count_neighbors(cls, generation: 'CellGeneration', row: int, col: int) -> int:
        height = generation.height
        width = generation.width

        def is_live_neighbor(offset):
            return generation.is_live_cell(
                (row + offset[0]) % height,
                (col + offset[1]) % width)

        return reduce(add, map(is_live_neighbor, cls._neighbors_coords), 0)


class CellGeneration:
    def __init__(self, height: int, width: int, previous: Optional['CellGeneration'] = None, serial: int = 0):
        self._width = width
        self._height = height
        self._previous = previous
        self._serial = serial
        self._world = self._create_world(height, width)

    @property
    def height(self) -> int:
        return self._height

    @property
    def width(self) -> int:
        return self._width

    @property
    def previous(self) -> 'CellGeneration':
        return self._previous

    @property
    def serial(self) -> int:
        return self._serial

    def _calc_cell_state(self, row, col) -> bool:
        """
        Descendants must override this method
        """
        return False

    # TODO: `BitArray` is in place here
    # def _create_world(self, height, width):
    #     return tuple(tuple(self._calc_cell_state(row, col) for col in range(width)) for row in range(height))
    #
    # def is_live_cell(self, row: int, col: int) -> bool:
    #     return self._world[row][col]

    def _create_world(self, height, width):
        world = makeBitArray(height * width)
        i = 0
        for row in range(height):
            for col in range(width):
                if self._calc_cell_state(row, col):
                    setBit(world, i)
                i += 1
        return world

    def is_live_cell(self, row: int, col: int) -> bool:
        return testBit(self._world, row * self._width + col) != 0

    def is_dead_cell(self, row: int, col: int) -> bool:
        if self._previous:
            return not self.is_live_cell(row, col) and self._previous.is_live_cell(row, col)
        else:
            return False

    def forget_previous(self):
        self._previous = None


class RandomCellGeneration(CellGeneration):
    def _calc_cell_state(self, row, col):
        return randint(0, 1)


class NextCellGeneration(CellGeneration):
    def __init__(self, previous: CellGeneration):
        super().__init__(previous.height, previous.width, previous=previous, serial=previous.serial + 1)

    def _calc_cell_state(self, row, col):
        return GameOfLiveRules.is_live_cell(self._previous, row, col)


class NoCellGenerationError(Exception):
    pass


class GameOfLifeMeta(type):
    def __call__(cls, context: SessionContext):
        instance = context.data.get(cls)
        if instance is None:
            context.data[cls] = instance = super(GameOfLifeMeta, cls).__call__()
        return instance


class GameOfLife(metaclass=GameOfLifeMeta):
    def __init__(self):
        self._cell_generation = None
        self._is_new_life = False

    def create_new_life(self, height: int, width: int) -> None:
        self._cell_generation = RandomCellGeneration(height, width)
        self._is_new_life = True

    def get_next_generation(self) -> CellGeneration:
        if self._cell_generation is None:
            raise NoCellGenerationError("Maybe you forgot to call 'create_new_life' before")

        if self._is_new_life:
            self._is_new_life = False
        else:
            self._cell_generation.forget_previous()
            self._cell_generation = NextCellGeneration(self._cell_generation)

        return self._cell_generation
