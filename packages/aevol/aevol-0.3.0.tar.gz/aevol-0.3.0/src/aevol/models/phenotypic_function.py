import pandas as pd


class PhenotypicFunction:
    """
    A phenotypic function a.k.a. a "fuzzy set"

    E.g. an individual's phenotype or the phenotypic target defined in the environmental

    Attributes
    ----------
    points : pd.DataFrame
        (x, y) coordinates of the constituting points
        columns=['x', 'y']
    """

    def __init__(self, pts=[[0.0, 0.0], [1.0, 0.0]]):
        self.points = pd.DataFrame(data=pts, columns=["x", "y"])
