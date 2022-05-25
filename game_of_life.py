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

            # We allocate 2 bits per cell and align the row to 32 bits to speed up the calculation of neighbors
            # (see _create_next_world)
            self._row_in_bits = ((self._width << 1) + 31) & 0xFFFFFFE0
            size_in_bits = self._row_in_bits * self._height
            empty_world = tuple(makeBitArray(size_in_bits, fill=0))

            self._prev_world = empty_world  # Now the world was empty, and the Spirit of God hovered over it...
            self._different_worlds = {empty_world}  # always includes an empty world

            if _world is not None:
                self._world = _world
            elif random:
                # Fill the bit array randomly and clear all odd bits.

                # NOTE: To right compare generation need clear unused tail of rows. But here this is not critical,
                # because it is very unlikely that the first random  generation will repeat.

                self._world = tuple(num & 0x55555555 for num in makeBitArray(size_in_bits, random=True))
            else:
                self._world = empty_world
        else:
            self._serial = previous._serial + 1
            self._width = previous._width
            self._row_in_bits = previous._row_in_bits
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
        i = row * self._row_in_bits + (col << 1)
        return CellState(testBit(self._world, i) + (testBit(self._prev_world, i) << 1))

    @staticmethod
    def _create_next_world(world, width, height):
        """
        1. Any live cell with two or three live neighbours survives.
        2. Any dead cell with three live neighbours becomes a live cell.
        3. All other live cells die in the next generation. Similarly, all other dead cells stay dead.

        https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life#Rules
        """

        # Index calculating.
        # rX - row offset
        # cX - position in row
        #
        #    |   c1  |   c0  |   c2  |
        # ---+-------+-------+-------+
        # r1 | r1+c1 | r1+c0 | r1+c2 |
        # ---+-------+-------+-------+
        # r0 | r0+c1 | r0+c0 | r0+c2 |
        # ---+-------+-------+-------+
        # r2 | r2+c1 | r2+c0 | r2+c2 |
        # ---+-------+-------+-------+

        row_used_bits = width << 1  # we use 2 bits per cell
        row_in_bits = (row_used_bits + 31) & 0xFFFFFFE0  # align row size to 32-bits
        size_in_bits = row_in_bits * height

        # Let's calculate the vertical neighbors for each 1x3 rectangle. To speed up, we sum numbers instead of bits
        # (each 32-bit integer number contains 16 2-bit cells).

        subtotals = makeBitArray(size_in_bits)
        row_in_int32 = row_in_bits >> 5
        size_in_int32 = size_in_bits >> 5

        for r0 in range(0, size_in_int32, row_in_int32):
            r1 = (r0 - row_in_int32) % size_in_int32
            r2 = (r0 + row_in_int32) % size_in_int32
            for c0 in range(row_in_int32):
                subtotals[r0 + c0] = world[r0 + c0] + world[r1 + c0] + world[r2 + c0]

        # Now let's sum horizontally and calculate all the neighbors in each 3x3 square. After that, we subtract one 
        # if the central cell is live.

        # NOTE: This can also be accelerated by using numbers instead of bits.
        #  But it will take 4 bits for each cell, and getting the index will become more complicated. 

        new_world = makeBitArray(size_in_bits)

        for r0 in range(0, size_in_bits, row_in_bits):
            for c0 in range(0, row_used_bits, 2):
                c1 = (c0 - 2) % row_used_bits
                c2 = (c0 + 2) % row_used_bits

                i = r0 + c0

                cell_is_live = testBit(world, i)
                neighbours = (getTwoBit(subtotals, i) +
                              getTwoBit(subtotals, r0 + c1) +
                              getTwoBit(subtotals, r0 + c2) - cell_is_live)

                if neighbours == 3 or neighbours == 2 and cell_is_live:
                    setBit(new_world, i)

                # i1 = r0 + c1
                # i2 = r0 + c2
                #
                # cell_is_live = (world[i >> 5] >> (i & 31)) & 1
                # neighbours = (((subtotals[i >> 5] >> (i & 31)) & 3) +
                #               ((subtotals[i1 >> 5] >> (i1 & 31)) & 3) +
                #               ((subtotals[i2 >> 5] >> (i2 & 31)) & 3) - cell_is_live)
                #
                # if neighbours == 3 or neighbours == 2 and cell_is_live:
                #     new_world[i >> 5] |= 1 << (i & 31)

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
