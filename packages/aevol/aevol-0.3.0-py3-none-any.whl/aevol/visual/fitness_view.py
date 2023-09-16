import matplotlib.pyplot as plt

from aevol.models.environment import Environment
from aevol.models.individual import Individual
from aevol.visual.utils import *


class FitnessView:
    def draw(
        self,
        individual: Individual,
        environment: Environment,
        display_legend,
    ):
        """
        Create the visualization of the fitness subplot

        Args:
            individual: the individual whose phenotype to plot
            environment: the environment object with the phenotypic target
            display_legend: True if we want to add the legend and textual information
        """
        self.fig, self.ax = create_figure()
        self.fig.subplots_adjust(bottom=0.3)

        self.ax.spines["right"].set_visible(False)
        self.ax.spines["top"].set_visible(False)

        # Compute the environment gaussian curve
        self.ax.plot(
            environment.target.points["x"],
            environment.target.points["y"],
            color="blue",
            alpha=0.75,
            label="Environmental target",
        )

        # Plot the phenotype curve of the best individual on the subplot
        self.ax.plot(
            individual.phenotype.points["x"],
            individual.phenotype.points["y"],
            color="red",
            alpha=0.75,
            label="Phenotype of best individual",
        )

        # Add a title
        plt.rcParams.update({"font.size": font_size_title})
        self.ax.set_title("Phenotype of best individual in the environment", y=1, pad=5)

        # Display the legend
        if display_legend == True:
            plt.rcParams.update({"font.size": font_size_legend})
            self.ax.plot(
                [],
                [],
                " ",
                label="Number of proteins : " + str(len(individual.proteins)),
            )
            self.ax.legend(loc=(0.35, -0.3))

    def save(self, out: Path, verbose=True):
        self.fig.savefig(out)
        if verbose:
            print("Fitness view written to " + str(out))
