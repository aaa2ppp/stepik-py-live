import random
from functools import reduce
from operator import add
from threading import Lock
from typing import Optional


class GameOfLiveRules:
    # [https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life#Rules}
    # 1. Any live cell with two or three live neighbours survives.
    # 2. Any dead cell with three live neighbours becomes a live cell.
    # 3. All other live cells die in the next generation. Similarly, all other dead cells stay dead.

    _neighbors_coords = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))

    @classmethod
    def is_live_cell(cls, previous: 'CellGeneration', row: int, col: int) -> bool:
        number_of_neighbors = cls.count_neighbors(previous, row, col)

        if previous.is_live_cell(row, col):
            return number_of_neighbors in (2, 3)
        else:
            return number_of_neighbors == 3

    @classmethod
    def count_neighbors(cls, previous: 'CellGeneration', row: int, col: int) -> int:
        vertical = 0
        horizontal = 1
        height = previous.height
        width = previous.width

        def is_live_neighbor(offset):
            return previous.is_live_cell((row + offset[vertical]) % height, (col + offset[horizontal]) % width)

        return reduce(add, map(is_live_neighbor, cls._neighbors_coords), 0)


class CellGeneration:
    def __init__(self, height: int, width: int, serial: int = 0):
        self._serial = serial
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

    # TODO: I don't like the name 'serial' here!
    #  serial_number, ordinal_number, sequence_number... hmm?.. too ugly and too long...
    @property
    def serial(self) -> int:
        return self._serial

    @property
    def previous(self) -> Optional['CellGeneration']:
        return None

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    def is_live_cell(self, row: int, col: int) -> bool:
        return self._world[row][col]

    def is_dead_cell(self, row: int, col: int) -> bool:
        previous = self.previous
        return previous and previous.is_live_cell(row, col)

    def forget_previous(self) -> None:
        pass


class RandomCellGeneration(CellGeneration):
    def _get_new_cell_state(self, row: int, col: int) -> bool:
        return bool(random.randint(0, 1))


class NextCellGeneration(CellGeneration):
    def __init__(self, previous: CellGeneration):
        # The important thing here is to call the superclass initialization after assigning the value to `previous'
        self._previous = previous
        super().__init__(previous.height, previous.width, serial=previous.serial + 1)

    @property
    def previous(self) -> CellGeneration:
        return self._previous

    def _get_new_cell_state(self, row: int, col: int) -> bool:
        return GameOfLiveRules.is_live_cell(self._previous, row, col)

    def forget_previous(self) -> None:
        self._previous = None


# TODO:
#  Another question: "Why is the singleton here?!"
#  The 'GameOfLife' instance should be unique for the session, not for the application as a whole.
#  I haven't thought it through yet...
#    The game must be associated with a user session.
#    The game must be in one copy per session.
#    The game should be removed from memory when the session ends.
#    The session is terminated by the user or by the user's client activity timeout.
#  We need a new separate class for this task or a ready-made third-party solution.
#  But the bicycle is more interesting ;)

class SingletonMeta(type):

    def __init__(cls, *args, **kwargs):
        super(SingletonMeta, cls).__init__(*args, **kwargs)
        cls._instance = None
        cls._lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            instance = cls._instance
            if instance is None:
                instance = super(SingletonMeta, cls).__call__(*args, **kwargs)
                cls._instance = instance
        return instance


class NoCellGeneration(Exception):
    pass


class GameOfLife(metaclass=SingletonMeta):
    def __init__(self):
        self._cell_generation = None
        self._is_new_life = False

    def __enter__(self):
        self._lock.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._lock.release()

    def create_new_life(self, width=20, height=20) -> None:
        self._cell_generation = RandomCellGeneration(width, height)
        self._is_new_life = True

    def get_next_generation(self) -> CellGeneration:
        if self._cell_generation is None:
            raise NoCellGeneration("Maybe you forgot to call 'create_new_life' before")

        if self._is_new_life:
            self._is_new_life = False
        else:
            self._cell_generation.forget_previous()
            self._cell_generation = NextCellGeneration(self._cell_generation)

        return self._cell_generation
