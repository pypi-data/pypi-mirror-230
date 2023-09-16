# ************************************************************************
#                          population  -  realization
# ************************************************************************

# Create a population object

# ---------------------------------------------------------------- INCLUDE
import json
import pandas as pd

# ---------------------------------------------------------------- POPULATION


class Population:
    """
    Attributes
    ----------
    grid_width : int
        the width of the population grid
    grid_height : int
        the height of the population grid
    fitness_array : List(float)
        an array containing the fitness of each individual in the population
    """

    def __init__(self, grid_width, grid_height, fitness_array):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.fitness_array = fitness_array

    @classmethod
    def from_json_file(cls, filename):
        file = open(filename)
        population = json.load(file)
        file.close()

        grid_width = population["grid_data"]["grid_width"]
        grid_height = population["grid_data"]["grid_height"]
        fitness_array = population["grid_data"]["fitness_grid"]

        return cls(grid_width, grid_height, fitness_array)

    # From 1D to 2D array, depending on grid-width and grid_height
    def compute_fitness_grid(self):
        # create a series
        array = pd.Series(self.fitness_array)

        # reshaping series into 2D
        fitness_grid = array.values.reshape((self.grid_height, self.grid_width))

        return fitness_grid
