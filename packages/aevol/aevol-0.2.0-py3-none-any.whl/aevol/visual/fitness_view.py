import matplotlib.pyplot as plt

from aevol.models.environment import Environment
from aevol.models.individual import Individual
from aevol.visual.utils import *

def draw(individual: Individual, environment: Environment, display_legend, outdir, title):
    """
    Create the visualization of the fitness subplot

    Args:
        individual: the individual whose phenotype to plot
        environment: the environment object with the phenotypic target
        display_legend: True if we want to add the legend and textual information
        outdir: where to save the figure
        title: title of the figure
    """
    fig, ax = create_figure()
    fig.subplots_adjust(bottom=0.3)

    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    # Compute the environment gaussian curve
    ax.plot(environment.target.points['x'], environment.target.points['y'],
            color="blue", alpha=0.75, label="Environmental target")

    # Plot the phenotype curve of the best individual on the subplot
    ax.plot(individual.phenotype.points['x'], individual.phenotype.points['y'],
            color="red", alpha=0.75, label="Phenotype of best individual")

    # Add a title
    plt.rcParams.update({'font.size': font_size_title})
    ax.set_title('Phenotype of best individual in the environment', y=1, pad=5)

    # Display the legend
    if (display_legend == True):
        plt.rcParams.update({'font.size': font_size_legend})
        ax.plot([], [], ' ', label="Number of proteins : " + str(len(individual.proteins)))
        ax.legend(loc=(0.35, -0.3))

    return save_figure(fig, outdir, title)
