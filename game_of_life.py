import array
from functools import reduce
from operator import add
from typing import Optional

from util.bitarray import makeBitArray, setBit, testBit
from util.session import SessionContext

_duplicate_search_depth = 4

"""
1. Any live cell with two or three live neighbours survives.
2. Any dead cell with three live neighbours becomes a live cell.
3. All other live cells die in the next generation. Similarly, all other dead cells stay dead.

https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life#Rules
"""

_neighbors_coords = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))


def _is_live_cell(previous_generation: 'CellGeneration', row: int, col: int) -> bool:
    number_of_neighbors = _count_neighbors(previous_generation, row, col)

    if previous_generation.is_live_cell(row, col):
        return number_of_neighbors in (2, 3)
    else:
        return number_of_neighbors == 3


def _count_neighbors(generation: 'CellGeneration', row: int, col: int) -> int:
    height = generation.height
    width = generation.width

    def is_live_neighbor(offset):
        return generation.is_live_cell(
            (row + offset[0]) % height,
            (col + offset[1]) % width)

    return reduce(add, map(is_live_neighbor, _neighbors_coords), 0)


class CellGeneration:
    def __init__(self, height: int, width: int, previous: Optional['CellGeneration'] = None, serial: int = 0):
        self._width = width
        self._height = height
        self._previous = previous
        self._serial = serial
        self._world = self._create_world(height, width)
        self._is_empty = None
        self._is_over = None

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

    @property
    def world(self) -> array:
        return self._world

    @property
    def is_empty(self):
        if self._is_empty is not None:
            return self._is_empty

        for x in self._world:
            if x != 0:
                return False
        return True

    @property
    def is_over(self):
        if self._is_over is not None:
            return self._is_over

        # NONE: Disable check for empty to avoid redundant calculations.
        #  In this case, the game will be over on the next generation.
        #  Because if a generation is empty, then the next generation will also be empty.

        # if self.is_empty:
        #     self._is_over = True
        #     return True

        # NOTE: To avoid redundant calculations, we limit the search depth.
        last = self
        prev = last
        for _ in range(_duplicate_search_depth):
            prev = prev.previous
            if prev is None:
                return False

            if prev._world == last._world:
                self._is_over = True
                return True

        self._is_over = False
        return False

    def _create_world(self, height, width):
        """
        Descendants must override this method
        """
        return makeBitArray(height * width)

    def is_live_cell(self, row: int, col: int) -> bool:
        return testBit(self._world, row * self._width + col) != 0

    def forget_previous(self):
        self._previous = None


class RandomCellGeneration(CellGeneration):
    def _create_world(self, height, width):
        return makeBitArray(height * width, random=True)


class NextCellGeneration(CellGeneration):
    def __init__(self, previous: CellGeneration):
        super().__init__(previous.height, previous.width, previous=previous, serial=previous.serial + 1)

    def _create_world(self, height, width):
        prev = self.previous
        world = makeBitArray(height * width)

        i = 0
        for row in range(height):
            for col in range(width):
                if _is_live_cell(prev, row, col):
                    setBit(world, i)
                i += 1
        return world


class GameOfLifeError(Exception):
    pass


class NoGenerationError(GameOfLifeError):
    pass


class GameOfLifeMeta(type):
    def __call__(cls, context: SessionContext):
        instance = context.data.get(cls)
        if instance is None:
            context.data[cls] = instance = super(GameOfLifeMeta, cls).__call__()
        return instance


class GameOfLife(metaclass=GameOfLifeMeta):
    max_history_length = 10

    def __init__(self):
        self._last_generation = None
        self._is_new_life = False
        self._is_over = True
        self._empty_world = None
        self._items = []

    def create_new_life(self, height: int = 20, width: int = 20) -> None:
        self._empty_world = makeBitArray(height * width)
        self._last_generation: CellGeneration = RandomCellGeneration(height, width)
        self._is_new_life = True
        self._is_over = False
        self._items = [self._last_generation]

    def get_next_generation(self) -> CellGeneration:
        if self._last_generation is None:
            raise NoGenerationError('First need to call the create_new_life function')

        if self._is_new_life:
            self._is_new_life = False
        elif not self.is_over():
            self._last_generation = NextCellGeneration(self._last_generation)
            self._items.append(self._last_generation)

        return self._last_generation

    def get_generation(self, serial: int) -> CellGeneration:
        if self._last_generation is None:
            raise NoGenerationError('First need to call the create_new_life function')

        if serial < 0:
            raise GameOfLifeError('Serial must be positive number')

        if serial < len(self._items):
            return self._items[serial]

        generation = self._last_generation
        while generation.serial < serial and not self.is_over():
            generation = self.get_next_generation()

        return generation

    def is_over(self):
        return self._last_generation.is_over
