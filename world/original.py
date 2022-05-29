from random import randint

from world import AbstractWorldFactory


class WorldFactory(AbstractWorldFactory):

    def is_live_cell(self, world, row: int, col: int) -> bool:
        return world[row][col]

    def revive_cell(self, world, row: int, col: int):
        world[row][col] = 1

    def kill_cell(self, world, row: int, col: int):
        world[row][col] = 0

    def create_empty_world(self):
        return [[0 for _ in range(self._width)] for _ in range(self._height)]

    def create_random_world(self):
        return [[randint(0, 1) for _ in range(self._width)] for _ in range(self._height)]

    def create_next_world(self, world):
        universe = world
        new_world = [[0 for _ in range(self._width)] for _ in range(self._height)]

        for i in range(len(universe)):
            for j in range(len(universe[0])):

                if universe[i][j]:
                    if self.__get_near(universe, [i, j]) not in (2, 3):
                        new_world[i][j] = 0
                        continue
                    new_world[i][j] = 1
                    continue

                if self.__get_near(universe, [i, j]) == 3:
                    new_world[i][j] = 1
                    continue
                new_world[i][j] = 0
        return new_world

    @staticmethod
    def __get_near(universe, pos, system=None):
        if system is None:
            system = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))

        count = 0
        for i in system:
            if universe[(pos[0] + i[0]) % len(universe)][(pos[1] + i[1]) % len(universe[0])]:
                count += 1
        return count
