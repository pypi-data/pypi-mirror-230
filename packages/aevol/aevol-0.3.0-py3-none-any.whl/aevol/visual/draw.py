from pathlib import Path

from aevol.models.environment import Environment
from aevol.models.individual import Individual
from aevol.visual.grid_view import GridView
from aevol.visual.fitness_view import FitnessView
from aevol.visual.rna_view import RnaView
from aevol.visual.protein_view import ProteinView

default_fnames = {
    "rnas": "RNAs.svg",
    "proteins": "Proteins.svg",
    "fitness": "Fitness.svg",
    "grid": "Grid.svg",
}


def draw_all(
    indivfile,
    envfile,
    gridfile,
    outdir: Path,
    display_legend=True,
    fnames=default_fnames,
    verbose=True,
):
    """
    Draw and save to file those views whose required data have been provided

    Args:
        indivfile: individual json file
        envfile: environment json file
        gridfile: grid json file
        outdir (Path): output directory
        display_legend (bool): whether to display legends on the figures
        fnames (dict): output filenames. keys: {"rnas", "proteins", "fitness", "grid"}
        verbose (bool): whether to be verbose
    """
    individual = Individual.from_json_file(indivfile) if indivfile else None
    environment = Environment.from_json_file(envfile) if envfile else None

    # build those views whose required data have been provided
    if individual:
        rna_view = RnaView()
        rna_view.draw(individual, display_legend)
        rna_view.save(outdir / fnames["rnas"], verbose=verbose)

        protein_view = ProteinView()
        protein_view.draw(individual, display_legend)
        protein_view.save(outdir / fnames["proteins"], verbose=verbose)

    if individual and environment:
        fitness_view = FitnessView()
        fitness_view.draw(individual, environment, display_legend)
        fitness_view.save(outdir / fnames["fitness"], verbose=verbose)

    if gridfile:
        grid_view = GridView()
        grid_view.draw(gridfile, display_legend)
        grid_view.save(outdir / fnames["grid"], verbose=verbose)
