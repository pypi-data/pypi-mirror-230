import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import numpy as np

from aevol.models.population import Population
from aevol.visual.utils import *


class GridView:
    def draw(self, json_population, display_legend):
        """
        Create a grid view of the population

        Args:
            json_population: the population object with all the informations to plot the population repartition visualization
            display_legend: True if we want to add the legend and textual informations
        """
        self.fig, self.ax = create_figure()
        self.ax.axis("off")
        self.fig.subplots_adjust(bottom=0.3)

        # deserialize population json
        population = Population.from_json_file(json_population)

        # Computes the fitness grid (1D to 2D array)
        fitness_grid = population.compute_fitness_grid()

        # Get max and min values
        max_value = np.max(fitness_grid)
        min_value = np.min(fitness_grid)

        # Build the heatmap with logarithmic scale
        extent = (0, population.grid_height, population.grid_width, 0)
        im = self.ax.imshow(fitness_grid, norm=LogNorm(), aspect="equal", extent=extent)
        im.set_clim(vmin=min_value, vmax=max_value)

        self.ax.grid(color="black", linewidth=2)
        self.ax.set_frame_on(False)

        # Add a colorbar
        self.fig.colorbar(im, ax=self.ax)

        # Add a title
        plt.rcParams.update({"font.size": font_size_title})
        self.ax.set_title("Population repartition", y=1, pad=5)

        # Display the legend
        if display_legend == True:
            plt.rcParams.update({"font.size": font_size_legend})
            max = "{:.2e}".format(np.max(fitness_grid))
            median = "{:.2e}".format(np.median(fitness_grid))

            self.ax.plot(
                [],
                [],
                " ",
                label="Number of individuals : " + str(len(population.fitness_array)),
            )
            self.ax.plot([], [], " ", label="Fitness of best individual : " + str(max))
            self.ax.plot([], [], " ", label="Median fitness : " + str(median))
            self.ax.legend(loc=(0.1, -0.3))

    def save(self, out: Path, verbose=True):
        self.fig.savefig(out)
        if verbose:
            print("Grid view written to " + str(out))
