from aevol.models.environment import Environment
from aevol.models.individual import Individual
from aevol.visual import fitness_view, grid_view
from aevol.visual.rna_view import RnaView
from aevol.visual.protein_view import ProteinView


def draw_all(indivfile, envfile, gridfile, display_legend, outdir):
    individual = Individual.from_json_file(indivfile) if indivfile else None
    environment = Environment.from_json_file(envfile) if envfile else None

    # build those views whose required data have been provided
    if individual:
        rna_view = RnaView()
        out = rna_view.draw(individual, display_legend, outdir, 'RNAS')
        print('RNA view written to ' + out)

        protein_view = ProteinView()
        out = protein_view.draw(individual, display_legend, outdir, 'Proteins')
        print('Protein view written to ' + out)

    if individual and environment:
        out = fitness_view.draw(individual, environment, display_legend, outdir, 'Fitness')
        print('Fitness view written to ' + out)

    if gridfile:
        out = grid_view.draw(gridfile, display_legend, outdir, 'Grid')
        print('Grid view written to ' + out)
