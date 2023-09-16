from aevol.models.genome_roi import GenomeROI


class Rna(GenomeROI):
    """
    An RNA

    Attributes
    ----------
    is_coding : bool
        whether the RNA is coding i.e. contains at least 1 gene
    """

    def __init__(self, begin, end, strand, is_coding):
        GenomeROI.__init__(self, begin, end, strand)
        self.is_coding = is_coding

    @classmethod
    def from_json_obj(cls, json_obj):
        return cls(
            json_obj["begin"],
            json_obj["end"],
            json_obj["strand"],
            json_obj["is_coding"],
        )

    def compute_angles(self, genome_length):
        """
        Compute the characteristic angles of the RNA on a genome of length 'genome_length'

        Args:
            genome_length: the length of the genome

        Returns:
            begin_angle: the angle (in degrees) of 'begin'
            end_angle: the angle (in degrees) of 'end'
            term_angle: the angle (in degrees) corresponding to the position of the terminator
        """
        if self.strand == "LEADING":
            term_angle = ((self.end - 11) / genome_length) * 360
        else:
            term_angle = ((self.end + 11) / genome_length) * 360

        return *GenomeROI.compute_angles(self, genome_length), term_angle
