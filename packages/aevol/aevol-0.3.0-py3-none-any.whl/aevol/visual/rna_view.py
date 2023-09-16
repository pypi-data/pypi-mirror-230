import matplotlib.pyplot as plt
from matplotlib.patches import Arc

from aevol.visual.genome_view import *
from aevol.visual.utils import *


class RnaView(GenomeView):
    def __init__(self, nb_layers=max_layers):
        GenomeView.__init__(self, nb_layers)

    def draw(self, individual, display_legend):
        """
        Create the visualization of the rna subplot

        Args:
            individual: the individual object with all the information to plot the graph
            display_legend: True if we want to add the legend and textual information
        """
        number_is_coding = 0  # number of rna strand that contains at least a protein
        number_is_not_coding = 0  # number of rna strand that does not contain proteins

        # for each rna
        for rna in individual.rnas:
            # Calculate the number of coding and not coding rna
            if rna.is_coding == True:
                number_is_coding += 1
            else:
                number_is_not_coding += 1

            self.draw_rna(rna, individual.genome_length)

        del self.occupied_sectors

        # add the subplot title
        plt.rcParams.update({"font.size": font_size_title})
        self.ax.set_title("Genome and RNAS", y=1.0, pad=5)

        # add legend for coding and not coding arn
        plt.rcParams.update({"font.size": font_size_legend})
        self.ax.plot(
            "grey", color="black", label="Coding RNA : " + str(number_is_coding)
        )
        self.ax.plot(
            "black",
            color="lightgrey",
            label="Non coding RNA : " + str(number_is_not_coding),
        )

        # Display the legend
        if display_legend == True:
            self.ax.legend(
                title="Genome length : " + str(individual.genome_length) + " bp",
                loc=(0.85, 0),
            )

    def draw_rna(self, rna, genome_length):
        """
        Draw the provided RNA on the figure.

        Args:
            rna: the RNA to be drawn
            genome_length:
        """
        diameter = 2 * radius

        # Compute the angles of the ROI on the genome circle
        begin_angle, end_angle, term_angle = rna.compute_angles(genome_length)

        # Compute the layer of the ROI (the distance from the genome circle)
        layer = self.compute_layer(rna.strand, begin_angle, end_angle)
        offset = layer * delta

        # Compute the display color of the ROI
        color = "black" if rna.is_coding else "grey"

        # Actually draw a representation of the RNA
        if rna.strand == "LEADING":
            # Draw main arc
            self.ax.add_patch(
                Arc(
                    center,
                    diameter + offset,
                    diameter + offset,
                    angle=90,
                    theta1=-end_angle,
                    theta2=-begin_angle,
                    linewidth=3,
                    color=color,
                )
            )
            # Draw decorator
            self.ax.add_patch(
                Arc(
                    center,
                    diameter + offset,
                    diameter + offset,
                    angle=90,
                    theta1=-end_angle,
                    theta2=-term_angle + 1,
                    linewidth=5,
                    color=color,
                )
            )
        else:
            # Draw main arc
            self.ax.add_patch(
                Arc(
                    center,
                    diameter + offset,
                    diameter + offset,
                    angle=90,
                    theta1=-begin_angle,
                    theta2=-end_angle,
                    linewidth=3,
                    color=color,
                )
            )
            # Draw decorator
            self.ax.add_patch(
                Arc(
                    center,
                    diameter + offset,
                    diameter + offset,
                    angle=90,
                    theta1=-term_angle - 1,
                    theta2=-end_angle,
                    linewidth=5,
                    color=color,
                )
            )

    def save(self, out: Path, verbose=True):
        self.fig.savefig(out)
        if verbose:
            print("RNA view written to " + str(out))
