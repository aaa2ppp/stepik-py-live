from random import randint
from functools import reduce
from operator import add
from typing import Optional


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
    def count_neighbors(cls, previous_generation: 'CellGeneration', row: int, col: int) -> int:
        vertical = 0
        horizontal = 1
        height = previous_generation.world_height
        width = previous_generation.world_width

        def is_live_neighbor(offset):
            return previous_generation.is_live_cell(
                (row + offset[vertical]) % height,
                (col + offset[horizontal]) % width)

        return reduce(add, map(is_live_neighbor, cls._neighbors_coords), 0)


class CellGeneration:
    def __init__(self, height: int, width: int, ordinal: int = 0):
        self._ordinal = ordinal
        self._width = width
        self._height = height
        self._world = self._create_new_word()

    def _create_new_word(self):
        return tuple(
            tuple(self._get_new_cell_state(row, col) for col in range(self._width))
            for row in range(self._height)
        )

    def _get_new_cell_state(self, row: int, col: int) -> bool:
        return False

    @property
    def ordinal(self) -> int:
        return self._ordinal

    @property
    def previous_generation(self) -> Optional['CellGeneration']:
        return None

    @property
    def world_height(self) -> int:
        return self._height

    @property
    def world_width(self) -> int:
        return self._width

    def is_live_cell(self, row: int, col: int) -> bool:
        return self._world[row][col]

    def is_dead_cell(self, row: int, col: int) -> bool:
        previous = self.previous_generation
        return previous and previous.is_live_cell(row, col)

    def forget_previous_generations(self) -> None:
        pass


class RandomCellGeneration(CellGeneration):
    def _get_new_cell_state(self, row: int, col: int) -> bool:
        return bool(randint(0, 1))


class NextCellGeneration(CellGeneration):
    def __init__(self, previous: CellGeneration):

        # NOTE: The important thing here is to call the superclass initialization after
        # assigning the value to `previous'
        self._previous = previous
        super().__init__(previous.world_height, previous.world_width, ordinal=previous.ordinal + 1)

    @property
    def previous_generation(self) -> CellGeneration:
        return self._previous

    def _get_new_cell_state(self, row: int, col: int) -> bool:
        return GameOfLiveRules.is_live_cell(self._previous, row, col)

    def forget_previous_generations(self) -> None:
        self._previous = None


class GameOfLifMeta(type):

    def __call__(cls, context: dict):
        instance = context.get(cls)
        if instance is None:
            instance = super(GameOfLifMeta, cls).__call__()
            context[cls] = instance
        return instance


class ErrorNoCellGeneration(Exception):
    pass


class GameOfLife(metaclass=GameOfLifMeta):

    def __init__(self):
        self._cell_generation = None
        self._is_new_life = False

    def create_new_life(self, width=20, height=20) -> None:
        self._cell_generation = RandomCellGeneration(width, height)
        self._is_new_life = True

    def get_next_generation(self) -> CellGeneration:
        if self._cell_generation is None:
            raise ErrorNoCellGeneration("Maybe you forgot to call 'create_new_life' before")

        if self._is_new_life:
            self._is_new_life = False
        else:
            self._cell_generation.forget_previous_generations()
            self._cell_generation = NextCellGeneration(self._cell_generation)

        return self._cell_generation
