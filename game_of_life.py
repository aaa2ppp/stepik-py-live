import random
import uuid
from functools import reduce
from operator import add
from threading import Lock

import flask


class RulesOfLife:
    _neighbors_coords = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))

    @classmethod
    def cell_will_live(cls, life, row: int, col: int) -> bool:
        count = cls.count_neighbors(life, row, col)

        if life.cell_is_alive(row, col):
            return count in (2, 3)
        else:
            return count == 3

    @classmethod
    def count_neighbors(cls, life, row: int, col: int) -> int:
        vertical = 0
        horizontal = 1
        height = life.height
        width = life.width

        def neighbor_is_alive(offset):
            return life.cell_is_alive((row + offset[vertical]) % height, (col + offset[horizontal]) % width)

        return reduce(add, map(neighbor_is_alive, cls._neighbors_coords), 0)


class LifeGeneration:

    def __init__(self, parent=None, height: int = 20, width: int = 20):
        self._parent = parent

        if parent is None:
            self._serial = 0
            self._width = width
            self._height = height
            self._world = tuple(
                tuple(bool(random.randint(0, 1)) for _ in range(self._width)) for _ in range(self._height)
            )
        else:
            parent._parent = None
            self._serial = parent._serial + 1
            self._height = parent._height
            self._width = parent._width
            self._world = tuple(
                tuple(RulesOfLife.cell_will_live(parent, row, col) for col in range(self._width))
                for row in range(self._height)
            )

    # TODO: I don't like the name generation and I don't like the name serial!
    #  serial_number, ordinal_number, sequence_number? hmm?.. two word - imho too long...
    @property
    def generation(self) -> int:
        return self._serial

    @property
    def parent(self):
        return self._parent

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    def cell_is_alive(self, row: int, col: int) -> bool:
        return self._world[row][col]

    def cell_was_alive(self, row: int, col: int) -> bool:
        parent = self._parent
        return parent and parent.cell_is_alive(row, col)


# class SingletonMeta(type):
#     _instances = {}
#     _lock: Lock = Lock()
#
#     def _call_(cls, *args, **kwargs):
#         with cls._lock:
#             # XXX: It's not a Singleton!!! Adding `or args or kwargs' breaks the whole idea!
#             if cls not in cls._instances or args or kwargs:
#                 instance = super()._call_(*args, **kwargs)
#                 cls._instances[cls] = instance
#         return cls._instances[cls]


# Another question: "Why is the singleton here?!"
# The instance of GameOfLife must be stored in the session and die with it!

# TODO:
#  I haven't thought it through yet. The game must be linked to the session. The game must be in one copy per session.
#  There must be a mechanism that removes all data associated with a user-terminated or outdated session from memory.
#  We need a separate class for this task. Or find a ready-made solution. But the bicycle  is more interesting.

class _DummyMeta(type):
    _instances = {}
    _lock: Lock = Lock()
    _uuid = '87fcf5d2-5391-467b-81c1-22e7989d5a35'

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            session_id = flask.session.get(cls._uuid)
            if session_id is None:
                session_id = uuid.uuid4()
                flask.session[cls._uuid] = session_id

            instance = cls._instances.get(session_id)
            if instance is None or args or kwargs:
                instance = super().__call__(*args, **kwargs)
                cls._instances[session_id] = instance

        return instance


class GameOfLife(metaclass=_DummyMeta):

    def __init__(self, width=20, height=20):
        self._is_new_life = True
        self._generation = LifeGeneration(width=width, height=height)

    def create_next_generation(self):
        if self._is_new_life:
            self._is_new_life = False
        else:
            self._generation = LifeGeneration(parent=self._generation)

        return self._generation
