import array
from functools import reduce
from operator import add
from typing import Optional

from util.bitarray import makeBitArray, setBit, testBit
from util.session import SessionContext


class GameOfLiveRules:
    """
    1. Any live cell with two or three live neighbours survives.
    2. Any dead cell with three live neighbours becomes a live cell.
    3. All other live cells die in the next generation. Similarly, all other dead cells stay dead.

    https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life#Rules
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

    @property
    def world(self) -> array:
        return self._world

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
        is_live = GameOfLiveRules.is_live_cell
        world = makeBitArray(height * width)

        i = 0
        for row in range(height):
            for col in range(width):
                if is_live(prev, row, col):
                    setBit(world, i)
                i += 1
        return world


class NoCellGenerationError(Exception):
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
        self._cell_generation = None
        self._is_new_life = False
        self._is_over = True
        self._empty_world = None

    def create_new_life(self, height: int = 25, width: int = 25) -> None:
        self._empty_world = makeBitArray(height * width)
        self._cell_generation = RandomCellGeneration(height, width)
        self._is_new_life = True
        self._is_over = False

    def get_next_generation(self) -> CellGeneration:
        if self._cell_generation is None:
            raise NoCellGenerationError("Maybe you forgot to call 'create_new_life' before")

        if self._is_new_life:
            self._is_new_life = False
        elif not self.is_over():
            self._cell_generation = NextCellGeneration(self._cell_generation)

        return self._cell_generation

    def is_over(self):
        if self._is_over:
            return True

        last = self._cell_generation
        if last.world == self._empty_world:
            self._is_over = True
            return True

        # NOTE: To avoid excessive load, we limit the history of generations.
        prev = last
        for _ in range(self.max_history_length):
            prev = prev.previous
            if prev is None:
                return False

            if prev.world == last.world:
                self._is_over = True
                return True

        prev.forget_previous()
        return False
