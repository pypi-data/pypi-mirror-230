import matplotlib.pyplot as plt
from matplotlib.patches import Circle

from aevol.visual.utils import *

center = (0.5, 0.5)  # center of the genome circle
radius = 0.35  # radius of the genome circle
delta = 0.045  # distance between the arn/protein layers

max_layers = 10
last_layer = 0  # the furthest layer of the genome occupied by a strand


class GenomeView:
    def __init__(self, nb_layers=max_layers):
        self.fig, self.ax = create_figure()

        self.ax.get_xaxis().set_visible(False)
        self.ax.get_yaxis().set_visible(False)
        self.ax.axis("off")

        self.ax.set_aspect(1)
        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(0, 1)

        # add the unmoving genome circle
        self.ax.add_patch(
            Circle(center, radius, angle=90, fill=False, lw=1, color="black")
        )

        # matrix that represents the occupied angles of the circle for each layer
        self.nb_layers = nb_layers
        self.occupied_sectors = [[0] * 360 for i in range(nb_layers)]

    def compute_layer(self, strand, begin_angle, end_angle):
        """
        Computes the display layer on which the ROI can be drawn without overlapping already processed elements.

        Args:
            strand: strand of the ROI
            begin_angle: angle (in degrees) of the beginning of the ROI
            end_angle: angle (in degrees) of the end of the ROI

        Returns:
            the layer on which the ROI can be drawn
        """
        # Carole code implementation (cf. Individual_X11.cpp l. 553 (function display rna))
        # The algorithm use an array of 360 cells * maximum number of layers.
        # It computes the angles of each arcs and check if there is enough place on the circle
        # at this angle location. If not, it adds a layer and check again.
        strand_direction = 1 if (strand == "LEADING") else -1

        nb_sectors = round((strand_direction * (end_angle - begin_angle) + 1) % 360)
        layer = 1
        sector_free = (
            False  # false while we do not find an empty sector to draw the strand
        )
        global last_layer

        # We check for each layer if there is no other strand at the same position on the genome
        while not sector_free:
            sector_free = True
            rho = 0
            for rho in range(nb_sectors):
                # For each angle on the genome circle
                sector = round((begin_angle + (rho * strand_direction)) % 360)
                if sector == 360:
                    sector = 0
                if self.occupied_sectors[layer * strand_direction][sector] != 0:
                    # There is another strand on the same layer and the same angle
                    sector_free = False
                    break
            if sector_free:
                # There is no overlapping strand
                break
            else:
                layer += 1
                if layer > last_layer:
                    # If this is the first time this layer is used, we are sure it has enough place
                    last_layer += 1
                    break
        for rho in range(nb_sectors):
            # We update occupied_sectors with the added strand.
            sector = round((begin_angle + (rho * strand_direction)) % 360)
            if sector == 360:
                sector = 0
            self.occupied_sectors[layer * strand_direction][sector] = -1

        return (layer) * strand_direction
