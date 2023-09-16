import json

from aevol.models.phenotypic_function import PhenotypicFunction


class Environment:
    """
    The environment in which a population of individuals may evolve

    Attributes
    ----------
    target : PhenotypicFunction
        the phenotypic target of the environment
    """

    def __init__(self, target: PhenotypicFunction):
        self.target = target

    @classmethod
    def from_json_file(cls, filename):
        file = open(filename)
        env = json.load(file)
        file.close()
        return cls(PhenotypicFunction(env["environment"]["target"]["points"]))
