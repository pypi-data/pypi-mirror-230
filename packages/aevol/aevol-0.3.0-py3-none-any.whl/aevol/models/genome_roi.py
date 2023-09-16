class GenomeROI:
    """
    Region Of Interest on a genome

    Attributes
    ----------
        -begin: the beginning position of the rna on the genome
        -end: the ending position of the rna on the genome
        -strand: the direction of the strand
            - "LEADING" if it is outside of the genome circle
            - "LAGGING" if it is inside of the genome circle
    """

    # init a strand with the beginning position, ending position, and direction
    def __init__(self, begin, end, strand):
        self.begin = begin
        self.end = end
        self.strand = strand

    def compute_angles(self, genome_length):
        """
        Compute the characteristic angles of the ROI on a genome of length 'genome_length'

        Args:
            genome_length: the length of the genome

        Returns:
            begin_angle: the angle (in degrees) of 'begin'
            end_angle: the angle (in degrees) of 'end'
        """
        begin_angle = (self.begin / genome_length) * 360
        end_angle = (self.end / genome_length) * 360

        if self.begin == self.end:
            # If the strand has the same beginning and ending position on the genome
            end_angle -= 0.0001

        return begin_angle, end_angle
