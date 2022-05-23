import array
from enum import Enum, IntEnum
from typing import Optional, List

from util.bitarray import makeBitArray, setBit, testBit
from util.session import SessionContext

_DUPLICATE_SEARCH_DEPTH = 4


class CellState(IntEnum):
    empty = 0
    living = 1
    dead = 2
    surviving = 3


class CellGeneration:
    def __init__(self,
                 width: Optional[int] = None,
                 height: Optional[int] = None,
                 previous: Optional['CellGeneration'] = None,
                 serial: Optional[int] = None,
                 random: bool = False,
                 _world=None
                 ):

        if width is not None:
            self._width = width
        else:
            self._width = width = previous.width

        if height is not None:
            self._height = height
        else:
            self._height = height = previous.height

        array_size = width * height

        self._previous = previous

        if serial is not None:
            self._serial = serial
        elif previous is not None:
            self._serial = previous._serial + 1
        else:
            self._serial = 0

        if _world is not None:
            self._world = tuple(_world)
        else:
            self._world = tuple(makeBitArray(array_size, random=random))

        # check game over
        if previous is not None:
            self._worlds = _worlds = previous._worlds
            self._is_over = self._world in _worlds
            _worlds.add(self._world)
        else:
            self._worlds = {tuple(makeBitArray(array_size)), self._world}
            self._is_over = False

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @property
    def serial(self) -> int:
        return self._serial

    @property
    def previous(self) -> 'CellGeneration':
        return self._previous

    @property
    def is_over(self):
        return self._is_over

    def cell_state(self, row: int, col: int) -> CellState:
        i = row * self._width + col
        prev = self._previous

        if prev is None:
            return CellState(testBit(self._world, i))
        else:
            return CellState(testBit(self._world, i) + (testBit(prev._world, i) << 1))

    def create_next_generation(self) -> 'CellGeneration':
        """
        1. Any live cell with two or three live neighbours survives.
        2. Any dead cell with three live neighbours becomes a live cell.
        3. All other live cells die in the next generation. Similarly, all other dead cells stay dead.

        https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life#Rules
        """

        width = self._width
        height = self._height
        world = self._world

        new_world = makeBitArray(width * height)

        i = 0
        for row in range(self._height):
            for col in range(self._width):

                #    |   c1  |   c0  |   c2  |
                # ---+-------+-------+-------+
                # r1 | r1+c1 | r1+c0 | r1+c2 |
                # ---+-------+-------+-------+
                # r0 | r0+c1 |   i   | r0+c2 |
                # ---+-------+-------+-------+
                # r2 | r2+c1 | r2+c0 | r2+c2 |
                # ---+-------+-------+-------+

                r0 = row * width
                r1 = ((row - 1) % height) * width
                r2 = ((row + 1) % height) * width
                c0 = col
                c1 = (col - 1) % width
                c2 = (col + 1) % width

                neighbours = (testBit(world, r0 + c1) + testBit(world, r0 + c2) +
                              testBit(world, r1 + c1) + testBit(world, r1 + c2) + testBit(world, r1 + c0) +
                              testBit(world, r2 + c1) + testBit(world, r2 + c2) + testBit(world, r2 + c0))

                if testBit(world, i):
                    if neighbours in (2, 3):
                        setBit(new_world, i)
                else:
                    if neighbours == 3:
                        setBit(new_world, i)
                i += 1

        return CellGeneration(previous=self, _world=new_world)

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
