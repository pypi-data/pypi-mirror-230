from aevol.models.genome_roi import GenomeROI


class Protein(GenomeROI):
    """
    A Protein (with info on the corresponding gene)

    Attributes
    ----------
    m : float
        the position (center) of the protein triangle
    w : float
        the width of the protein triangle
    h : float
        the height of the protein triangle
    expression_level : float
        the expression level of the gene
    """

    def __init__(self, begin, end, strand, m, w, h, expression_level):
        GenomeROI.__init__(self, begin, end, strand)
        self.m = m
        self.w = w
        self.h = h
        self.expression_level = expression_level

    @classmethod
    def from_json_obj(cls, json_obj):
        return cls(
            json_obj["begin"],
            json_obj["end"],
            json_obj["strand"],
            json_obj["m"],
            json_obj["w"],
            json_obj["h"],
            json_obj["expression_level"],
        )
