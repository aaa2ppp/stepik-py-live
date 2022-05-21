import array
from functools import reduce
from operator import add
from typing import Optional, List

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


def _cell_will_be_live(previous_generation: 'CellGeneration', row: int, col: int) -> bool:
    number_of_neighbors = _count_neighbors(previous_generation, row, col)

    if previous_generation.is_live_cell(row, col):
        return number_of_neighbors in (2, 3)
    else:
        return number_of_neighbors == 3


def _count_neighbors(generation: 'CellGeneration', row: int, col: int) -> int:
    def is_live_neighbor(offset):
        return generation.is_live_cell(row + offset[0], col + offset[1])

    return reduce(add, map(is_live_neighbor, _neighbors_coords), 0)


class CellGeneration:
    def __init__(self, height: int, width: int, previous: Optional['CellGeneration'] = None, serial: int = 0, random: bool = False):
        self._width = width
        self._height = height
        self._previous = previous
        self._serial = serial
        self._world = makeBitArray(width * height, random=random)
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
        # TODO: Возможно это можно эффективно решить с помощью хешсуммы
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

    def is_live_cell(self, row: int, col: int) -> bool:
        return testBit(self._world, (row % self._height) * self._width + col % self._width)

    def create_next_generation(self) -> 'CellGeneration':
        width = self._width
        height = self._height
        next_generation = CellGeneration(width=width, height=height, previous=self, serial=self._serial + 1)
        next_world = next_generation._world

        i = 0
        for row in range(self._height):
            for col in range(self._width):
                if _cell_will_be_live(self, row, col):
                    setBit(next_world, i)
                i += 1

        return next_generation

    def forget_previous(self):
        self._previous = None


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
        self._generations: Optional[List[CellGeneration]] = None

    def create_new_random_life(self, height: int = 20, width: int = 20) -> None:
        self._generations = [CellGeneration(height, width, random=True)]

    def get_generation(self, serial: int) -> CellGeneration:
        if serial < 0:
            raise GameOfLifeError('Serial must be positive number')

        if self._generations is None:
            raise NoGenerationError('First need to call the create_new_life function')

        if serial < len(self._generations):
            return self._generations[serial]

        generation = self._generations[-1]
        while generation.serial < serial and not generation.is_over:
            generation = generation.create_next_generation()
            self._generations.append(generation)

        return generation
