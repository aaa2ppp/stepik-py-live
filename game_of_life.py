from enum import IntEnum
from typing import Optional, List

from util.session import SessionContext
import world


class CellState(IntEnum):
    empty = 0
    living = 1
    dead = 2
    surviving = 3


class CellGeneration:

    def __init__(self, *,
                 width: Optional[int] = None,
                 height: Optional[int] = None,
                 random: bool = False,
                 previous: Optional['CellGeneration'] = None,
                 ):

        if previous is None:
            self._serial = 0

            if width is None:
                raise AttributeError("Required `previous` or `width` and `height`")
            elif width < 1:
                raise ValueError(f"`width` must be natural number, got {width}")

            if height is None:
                raise AttributeError("Required `previous` or `width` and `height`")
            elif height < 1:
                raise ValueError(f"`height` must be natural number, got {height}")

            self._world_factory = world.factory(width, height)

            empty_world = tuple(self._world_factory.create_empty_world())
            self._prev_world = empty_world  # Now the world was empty, and the Spirit of God hovered over it...
            self._different_worlds = {empty_world}  # always includes an empty world

            if random:
                self._world = tuple(self._world_factory.create_random_world())
            else:
                self._world = empty_world
        else:
            self._previous = previous
            self._serial = previous._serial + 1
            self._world_factory = previous._world_factory
            self._prev_world = previous._world
            self._different_worlds = previous._different_worlds
            self._world = tuple(self._world_factory.create_next_world(self._prev_world))

        self._different_worlds.add(self._world)
        self._is_over = self._serial >= len(self._different_worlds) - 1

    @property
    def serial(self) -> int:
        return self._serial

    @property
    def width(self) -> int:
        return self._world_factory.width

    @property
    def height(self) -> int:
        return self._world_factory.height

    @property
    def is_over(self):
        return self._is_over

    def cell_state(self, row: int, col: int) -> CellState:
        s = self._world_factory
        return CellState(s.is_live_cell(self._world, row, col) + (s.is_live_cell(self._prev_world, row, col) << 1))


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
