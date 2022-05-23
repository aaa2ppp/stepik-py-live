from enum import IntEnum
from typing import Optional, List, Tuple

from util.bitarray import makeBitArray, setBit, testBit
from util.session import SessionContext


class CellState(IntEnum):
    empty = 0
    living = 1
    dead = 2
    surviving = 3


class CellGeneration:
    _serial = 0
    _width = 20
    _height = 20

    def __init__(self, *,
                 width: Optional[int] = None,
                 height: Optional[int] = None,
                 random: bool = False,
                 previous: Optional['CellGeneration'] = None,
                 _world: Tuple[int] = None
                 ):

        if previous is None:
            if width is not None:
                if width < 1:
                    raise ValueError(f"`width` must be natural number, got {width}")
                self._width = width

            if height is not None:
                if height < 1:
                    raise ValueError(f"`height` must be natural number, got {height}")
                self._height = height

            array_size = self._width * self._height
            empty_world = tuple(makeBitArray(array_size, fill=0))

            self._prev_world = empty_world  # Now the world was empty, and the Spirit of God hovered over it...
            self._different_worlds = {empty_world}  # always includes an empty world

            if _world is not None:
                self._world = _world
            else:
                self._world = tuple(makeBitArray(array_size, random=True)) if random else empty_world
        else:
            self._serial = previous._serial + 1
            self._width = previous._width
            self._height = previous._height
            self._prev_world = previous._world
            self._different_worlds = previous._different_worlds

            if _world is not None:
                self._world = _world
            else:
                self._world = self.__class__._create_next_world(previous._world, previous._width, previous._height)

        self._different_worlds.add(self._world)
        self._is_over = self._serial >= len(self._different_worlds) - 1

    @property
    def serial(self) -> int:
        return self._serial

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @property
    def is_over(self):
        return self._is_over

    def cell_state(self, row: int, col: int) -> CellState:
        i = row * self._width + col
        return CellState(testBit(self._world, i) + (testBit(self._prev_world, i) << 1))

    @staticmethod
    def _create_next_world(world, width, height):
        """
        1. Any live cell with two or three live neighbours survives.
        2. Any dead cell with three live neighbours becomes a live cell.
        3. All other live cells die in the next generation. Similarly, all other dead cells stay dead.

        https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life#Rules
        """

        new_world = makeBitArray(width * height)

        i = 0
        for row in range(height):
            for col in range(width):

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

        return tuple(new_world)


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

    def __init__(self):
        self._generations: Optional[List[CellGeneration]] = None

    def create_new_random_life(self, width: int = 20, height: int = 20) -> None:
        self._generations = [CellGeneration(width=width, height=height, random=True)]

    def get_generation(self, serial: int) -> CellGeneration:
        if serial < 0:
            raise ValueError(f"`serial` must be positive number, get {serial}")

        if self._generations is None:
            raise NoGenerationError("First need to call the `create_new_life` function")

        if serial < len(self._generations):
            return self._generations[serial]

        generation = self._generations[-1]
        while generation.serial < serial and not generation.is_over:
            generation = CellGeneration(previous=generation)
            self._generations.append(generation)

        return generation
