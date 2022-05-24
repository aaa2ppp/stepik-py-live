from enum import IntEnum
from typing import Optional, List, Tuple

from util.bitarray import makeBitArray, setBit, testBit, getTwoBit
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

            # We allocate 2 bits per cell and align the row with a 32-bit word to speed up
            # the calculation of neighbors (see _create_next_world)
            self._width2 = ((self._width + 15 << 1) & 0xFFFFFFE0)
            array_size = self._width2 * self._height
            empty_world = tuple(makeBitArray(array_size, fill=0))

            self._prev_world = empty_world  # Now the world was empty, and the Spirit of God hovered over it...
            self._different_worlds = {empty_world}  # always includes an empty world

            if _world is not None:
                self._world = _world
            elif random:
                # fill random and clear all odd bits
                # TODO: clear unused tail of rows
                self._world = tuple(n & 0x55555555 for n in makeBitArray(array_size, random=True))
            else:
                self._world = empty_world
        else:
            self._serial = previous._serial + 1
            self._width = previous._width
            self._width2 = previous._width2
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
        i = row * self._width2 + (col << 1)
        return CellState(testBit(self._world, i) + (testBit(self._prev_world, i) << 1))

    @staticmethod
    def _create_next_world(world, width, height):
        """
        1. Any live cell with two or three live neighbours survives.
        2. Any dead cell with three live neighbours becomes a live cell.
        3. All other live cells die in the next generation. Similarly, all other dead cells stay dead.

        https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life#Rules
        """

        # Index calculating
        #    |   c1  |   c0  |   c2  |
        # ---+-------+-------+-------+
        # r1 | r1+c1 | r1+c0 | r1+c2 |
        # ---+-------+-------+-------+
        # r0 | r0+c1 | r0+c0 | r0+c2 |
        # ---+-------+-------+-------+
        # r2 | r2+c1 | r2+c0 | r2+c2 |
        # ---+-------+-------+-------+

        width2 = (width + 15 << 1) & 0xFFFFFFE0
        size = width2 * height

        # Let's calculate the vertical neighbors for each 1x3 rectangle. To speed up, we sum numbers instead of bits
        # (each 32-bit integer number contains 16 2-bit cells).

        subtotals = makeBitArray(size)
        n_width2 = width2 >> 5
        n_size = size >> 5

        for r0 in range(0, n_size, n_width2):
            r1 = (r0 - n_width2) % n_size
            r2 = (r0 + n_width2) % n_size
            for c0 in range(n_width2):
                subtotals[r0 + c0] = world[r0 + c0] + world[r1 + c0] + world[r2 + c0]

        # Now let's sum horizontally and calculate all the neighbors in each 3x3 square. After that, we subtract one 
        # if the central cell is live.

        # NOTE: This can also be accelerated by working with numbers instead of bits. 
        #  But it will take 4 bits for each cell, and getting the index will become more complicated. 

        new_world = makeBitArray(size)

        for r0 in range(0, size, width2):
            for c0 in range(0, width << 1, 2):
                c1 = (c0 - 2) % width
                c2 = (c0 + 2) % width

                i = r0 + c0
                cell_is_live = testBit(world, i)
                neighbours = (getTwoBit(subtotals, i) +
                              getTwoBit(subtotals, r0 + c1) +
                              getTwoBit(subtotals, r0 + c2) - cell_is_live)

                if neighbours == 3 or cell_is_live and neighbours == 2:
                    setBit(new_world, i)

                # if cell_is_live:
                #     if neighbours in (2, 3):
                #         setBit(new_world, i)
                # else:
                #     if neighbours == 3:
                #         setBit(new_world, i)

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
            raise ValueError(f"`serial` must be positive number, got {serial}")

        if self._generations is None:
            raise NoGenerationError("First need to call the `create_new_life` function")

        if serial < len(self._generations):
            return self._generations[serial]

        generation = self._generations[-1]
        while generation.serial < serial and not generation.is_over:
            generation = CellGeneration(previous=generation)
            self._generations.append(generation)

        return generation
