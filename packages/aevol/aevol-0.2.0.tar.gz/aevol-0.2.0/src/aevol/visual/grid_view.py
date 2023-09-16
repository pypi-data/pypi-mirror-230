import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import numpy as np

from aevol.models.population import Population
from aevol.visual.utils import *

def draw(json_population, display_legend, outdir, title):
    """
    Create a grid view of the population

    Args:
        json_population: the population object with all the informations to plot the population repartition visualization
        display_legend: True if we want to add the legend and textual informations
        outdir:  where to save the figure
        title: title of the figure
    """
    fig, ax = create_figure()
    ax.axis('off')
    fig.subplots_adjust(bottom=0.3)

    # deserialize population json
    population = Population.from_json_file(json_population)

    # Computes the fitness grid (1D to 2D array)
    fitness_grid = population.compute_fitness_grid()

    # Get max and min values
    max_value = np.max(fitness_grid)
    min_value = np.min(fitness_grid)

    # Build the heatmap with logarithmic scale
    extent = (0, population.grid_height, population.grid_width, 0)
    im = ax.imshow(fitness_grid, norm=LogNorm(), aspect='equal', extent=extent)
    im.set_clim(vmin=min_value, vmax=max_value)

    ax.grid(color='black', linewidth=2)
    ax.set_frame_on(False)

    # Add a colorbar
    fig.colorbar(im, ax=ax)

    # Add a title
    plt.rcParams.update({'font.size': font_size_title})
    ax.set_title('Population repartition', y=1, pad=5)

    # Display the legend
    if (display_legend == True):
        plt.rcParams.update({'font.size': font_size_legend})
        max = "{:.2e}".format(np.max(fitness_grid))
        median = "{:.2e}".format(np.median(fitness_grid))

        ax.plot([], [], ' ', label="Number of individuals : " + str(len(population.fitness_array)))
        ax.plot([], [], ' ', label="Fitness of best individual : " + str(max))
        ax.plot([], [], ' ', label="Median fitness : " + str(median))
        ax.legend(loc=(0.1, -0.3))

    return save_figure(fig, outdir, title)
