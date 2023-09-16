import matplotlib.pyplot as plt
from pathlib import Path

# ------------------------------------------------------- Global variables
font_size_title = 11# size of the font for the title
font_size_legend = 9# size of the font for the legend


def create_figure():
    """
    Initialize a figure with a single subplot

    Returns:
        fig (Figure)
        ax (Axes)
    """
    fig, ax = plt.subplots(figsize=(7.3 ,5))
    fig.subplots_adjust(left=0.03, bottom=0.1, right=0.95, top=0.95, wspace=0.15, hspace=0.15)

    return fig, ax

def save_figure(fig, outdir, title):
    """
    Save the figure in .svg

    Args:
        fig: the figure to save
        outdir: the path where we want the figure to be saved
        title: the title of the saved figure

    Returns:
        output_path (str): path to the file the figure was written to
    """
    output_path = Path(outdir)
    output_path.mkdir(parents=True, exist_ok=True)
    filename = title + '.svg'
    output_path = output_path / filename
    fig.savefig(output_path, format='svg')

    return str(output_path)
