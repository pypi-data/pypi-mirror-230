import numpy as np
from matplotlib import pyplot as plt
from matplotlib import colors
from mersenne import MersenneRng
from funcs import *
from dataclasses import dataclass
from copy import deepcopy


@dataclass
class Point:
    type_id: int
    type: str
    colour: str
    temp: float | int
    hum: float | int
    dew: float | int


class MapBuild2D:
    def __init__(self, generator=None, seed: int = 1, **kwargs):
        self.points = []
        self.generator = generator or MersenneRng(seed)
        self.CONFIG = {'TYPES': ['LAND', 'OCEAN'],
                       'TYPE_PROB': [1/10, 9/10],
                       'TYPE_COLOUR': ['green', 'blue'],
                       'DEFAULT_TEMP': 20,
                       'EXTENT': [-128, 128, -128, 128],
                       'DEFAULT_DEW_POINT': 10}
        self.CONFIG.update(kwargs)

    def init(self, size: tuple[int, int]):
        island_layer = []
        probs = [sum(self.CONFIG['TYPE_PROB'][:i+1]) for i in range(len(self.CONFIG['TYPE_PROB']))]
        for i in range(size[0]):
            row = []
            for j in range(size[1]):
                num = self.generator.get_random_number()
                for type, prob, colour in zip(self.CONFIG['TYPES'], probs, self.CONFIG['TYPE_COLOUR']):
                    if num <= 2 ** 32 * prob:
                        row.append(Point(self.CONFIG['TYPES'].index(type),
                                         type,
                                         colour,
                                         self.CONFIG['DEFAULT_TEMP'],
                                         calc_hum(self.CONFIG['DEFAULT_TEMP'], self.CONFIG['DEFAULT_DEW_POINT']),
                                         self.CONFIG['DEFAULT_DEW_POINT']))
                        break

            island_layer.append(row)
        self.points = island_layer

    def zoom(self):
        zoom_layer = []
        for row in self.points:
            new_row = []
            for point in row:
                new_row.append(point)
                new_row.append(deepcopy(point))
            zoom_layer.append(new_row[:])
            zoom_layer.append(deepcopy(new_row[:]))
        self.points = zoom_layer

    def detail_types(self, type_probs: dict[str, int | float]):
        """
        Add detail to the given types.

        :param type_probs: Dictionary containing the types as keys and probabilities as values, probability is the
        chance that if a given point is not that type then it has that probability to become that type.
        """
        for row in self.points:
            for point in row:
                for type, prob in type_probs.items():
                    num = self.generator.get_random_number()
                    if point.type != type and num < 2 ** 32 * prob:
                        point.type_id = self.CONFIG['TYPES'].index(type)
                        point.type = type
                        point.colour = self.CONFIG['TYPE_COLOUR'][self.CONFIG['TYPES'].index(type)]
                        break

    def add_temps(self, temps: dict[int | float, int | float]):
        probs = [sum(list(temps.values())[:i+1]) for i in range(len(temps.values()))]
        for row in self.points:
            for point in row:
                num = self.generator.get_random_number()
                for temp, prob in zip(temps.keys(), probs):
                    if num <= 2 ** 32 * prob:
                        point.temp = temp
                        point.hum = calc_hum(point.temp, point.dew)
                        break

    def blend_temps(self):
        for row in range(len(self.points)):
            for point in range(len(self.points[0])):
                points = self.get_adjacent_points(row, point)
                temps = [point.temp for point in points]
                self.points[row][point].temp = np.average(temps)
                self.points[row][point].hum = calc_hum(self.points[row][point].temp, self.points[row][point].dew)

    def add_dew_point(self, dews: dict[int | float, int | float]):
        probs = [sum(list(dews.values())[:i + 1]) for i in range(len(dews.values()))]
        for row in self.points:
            for point in row:
                num = self.generator.get_random_number()
                for dew, prob in zip(dews.keys(), probs):
                    if num <= 2 ** 32 * prob:
                        point.dew = dew
                        point.hum = calc_hum(point.temp, point.dew)
                        break

    def blend_dews(self):
        for row in range(len(self.points)):
            for point in range(len(self.points[0])):
                points = self.get_adjacent_points(row, point)
                dews = [point.dew for point in points]
                self.points[row][point].dew = np.average(dews)
                self.points[row][point].hum = calc_hum(self.points[row][point].temp, self.points[row][point].dew)

    def get_adjacent_points(self, row_idx, col_idx):
        points = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            r, c = row_idx + dr, col_idx + dc
            if is_valid_coord(r, c, len(self.points), len(self.points[0])):
                points.append(self.points[r][c])
        return points

    def show(self):
        fig, ax = plt.subplots()
        points = [[i.type_id for i in self.points[j]] for j in range(len(self.points))]
        print(np.array(self.points))
        print(np.array(points))
        print(f'Shape: {np.array(points).shape}')
        cmap = colors.ListedColormap(self.CONFIG['TYPE_COLOUR']) if 'CMAP' not in self.CONFIG.keys() else self.CONFIG['CMAP']
        ax.imshow(np.array(points), extent=self.CONFIG['EXTENT'], cmap=cmap)
        plt.show()

    def __repr__(self):
        return f"2D Map, Shape: {np.array(self.points).shape[:2]}, Types: {self.CONFIG['TYPES']}"