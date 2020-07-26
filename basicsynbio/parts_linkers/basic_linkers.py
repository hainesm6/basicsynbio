"""Module contains objects to access BASIC DNA assembly parts from within the pacakge."""

import basicsynbio as bsb
from Bio.Seq import Seq
from .main import PartLinkerCollection

standard_linkers = {
    "L1": "CTCGTTACTTACGACACTCCGAGACAGTCAGAGGGTATTTATTGAACTAGTCC",
    "L2": "CTCGATCGGTGTGAAAAGTCAGTATCCAGTCGTGTAGTTCTTATTACCTGTCC",
    "L3": "CTCGATCACGGCACTACACTCGTTGCTTTATCGGTATTGTTATTACAGAGTCC",
    "L4": "CTCGAGAAGTAGTGCCACAGACAGTATTGCTTACGAGTTGATTTATCCTGTCC",
    "L5": "CTCGGTATTGTAAAGCACGAAACCTACGATAAGAGTGTCAGTTCTCCTTGTCC",
    "L6": "CTCGAACTTTTACGGGTGCCGACTCACTATTACAGACTTACTACAATCTGTCC",
    "LMP": "CTCGGGTAAGAACTCGCACTTCGTGGAAACACTATTATCTGGTGGGTCTCTGTCC",
    "LMS": "CTCGGGAGACCTATCGGTAATAACAGTCCAATCTGGTGTAACTTCGGAATCGTCC",
    "LF1": "CTCGGGCTCGGGCTCCGAAAACTTGTACTTCCAGGGATCGGGCTCCGGGTCC",
    "LF2": "CTCGGGCTCGGGCTCCCTGGAAGTTCTGTTTCAAGGTCCATCGGGCTCCGGGTCC",
    "LF3": "CTCGGGCTCGGGCTCCGGATCTGGTTCAGGTTCAGGATCGGGCTCCGGGTCC",
    "LF4": "CTCGGGCTCGGGCTCCGGATCAGGATCTGGTTCAGGTTCAGGATCGGGCTCCGGGTCC",
    "LF5": "CTCGGGCTCGGGCTCCGGATCAGGATCTGGTTCAGGTTCAGGATCAGGATCGGGCTCCGGGTCC",
    "LF6": "CTCGGCCGAAGCGGCTGCTAAAGAAGCAGCTGCTAAAGAGGCGGCCGCCAAGGCAGGGTCC"}

utr_rbs_linkers = {
    "UTR1-RBS1": "CTCGTTGAACACCGTCTCAGGTAAGTATCAGTTGTAAATCACACAGGACTAGTCC",
    "UTR1-RBS2": "CTCGTTGAACACCGTCTCAGGTAAGTATCAGTTGTAAAAAGAGGGGAAATAGTCC",
    "UTR1-RBS3": "CTCGTTGAACACCGTCTCAGGTAAGTATCAGTTGTAAAAAGAGGAGAAATAGTCC",
    "UTR1-RBS-A01": "CTCGTTGAACACCGTCTCAGGTAAGTATCAGTTGTAAATCTGGGGAGGTAGTCC",
    "UTR1-RBS-A02": "CTCGTTGAACACCGTCTCAGGTAAGTATCAGTTGTAAATCCGGGGAGGTAGTCC",
    "UTR1-RBS-A03": "CTCGTTGAACACCGTCTCAGGTAAGTATCAGTTGTAAATCTGAGGAGGTAGTCC",
    "UTR1-RBS-A04": "CTCGTTGAACACCGTCTCAGGTAAGTATCAGTTGTAAATCCAGGGAGGTAGTCC",
    "UTR1-RBS-A05": "CTCGTTGAACACCGTCTCAGGTAAGTATCAGTTGTAAATCCCGGGAGGTAGTCC",
    "UTR1-RBS-A06": "CTCGTTGAACACCGTCTCAGGTAAGTATCAGTTGTAAATCCGAGGAGGTAGTCC",
    "UTR1-RBS-A07": "CTCGTTGAACACCGTCTCAGGTAAGTATCAGTTGTAAATCTCAGGAGGTAGTCC",
    "UTR1-RBS-A08": "CTCGTTGAACACCGTCTCAGGTAAGTATCAGTTGTAAATCCAAGGAGGTAGTCC",
    "UTR1-RBS-A09": "CTCGTTGAACACCGTCTCAGGTAAGTATCAGTTGTAAATCTAGGGAGGTAGTCC",
    "UTR1-RBS-A10": "CTCGTTGAACACCGTCTCAGGTAAGTATCAGTTGTAAATCCCAGGAGGTAGTCC",
    "UTR1-RBS-A11": "CTCGTTGAACACCGTCTCAGGTAAGTATCAGTTGTAAATCTCGGGAGGTAGTCC",
    "UTR1-RBS-A12": "CTCGTTGAACACCGTCTCAGGTAAGTATCAGTTGTAAATCTAAGGAGGTAGTCC",
    "UTR2-RBS1": "CTCGTGTTACTATTGGCTGAGATAAGGGTAGCAGAAAATCACACAGGACTAGTCC",
    "UTR2-RBS2": "CTCGTGTTACTATTGGCTGAGATAAGGGTAGCAGAAAAAAGAGGGGAAATAGTCC",
    "UTR2-RBS3": "CTCGTGTTACTATTGGCTGAGATAAGGGTAGCAGAAAAAAGAGGAGAAATAGTCC",
    "UTR2-RBS-A01": "CTCGTGTTACTATTGGCTGAGATAAGGGTAGCAGAAAATCTGGGGAGGTAGTCC",
    "UTR2-RBS-A02": "CTCGTGTTACTATTGGCTGAGATAAGGGTAGCAGAAAATCCGGGGAGGTAGTCC",
    "UTR2-RBS-A03": "CTCGTGTTACTATTGGCTGAGATAAGGGTAGCAGAAAATCTGAGGAGGTAGTCC",
    "UTR2-RBS-A04": "CTCGTGTTACTATTGGCTGAGATAAGGGTAGCAGAAAATCCAGGGAGGTAGTCC",
    "UTR2-RBS-A05": "CTCGTGTTACTATTGGCTGAGATAAGGGTAGCAGAAAATCCCGGGAGGTAGTCC",
    "UTR2-RBS-A06": "CTCGTGTTACTATTGGCTGAGATAAGGGTAGCAGAAAATCCGAGGAGGTAGTCC",
    "UTR2-RBS-A07": "CTCGTGTTACTATTGGCTGAGATAAGGGTAGCAGAAAATCTCAGGAGGTAGTCC",
    "UTR2-RBS-A08": "CTCGTGTTACTATTGGCTGAGATAAGGGTAGCAGAAAATCCAAGGAGGTAGTCC",
    "UTR2-RBS-A09": "CTCGTGTTACTATTGGCTGAGATAAGGGTAGCAGAAAATCTAGGGAGGTAGTCC",
    "UTR2-RBS-A10": "CTCGTGTTACTATTGGCTGAGATAAGGGTAGCAGAAAATCCCAGGAGGTAGTCC",
    "UTR2-RBS-A11": "CTCGTGTTACTATTGGCTGAGATAAGGGTAGCAGAAAATCTCGGGAGGTAGTCC",
    "UTR2-RBS-A12": "CTCGTGTTACTATTGGCTGAGATAAGGGTAGCAGAAAATCTAAGGAGGTAGTCC",
    "UTR3-RBS1": "CTCGGTATCTCGTGGTCTGACGGTAAAATCTATTGTAATCACACAGGACTAGTCC",
    "UTR3-RBS2": "CTCGGTATCTCGTGGTCTGACGGTAAAATCTATTGTAAAAGAGGGGAAATAGTCC",
    "UTR3-RBS3": "CTCGGTATCTCGTGGTCTGACGGTAAAATCTATTGTAAAAGAGGAGAAATAGTCC",
    "UTR3-RBS-A01": "CTCGGTATCTCGTGGTCTGACGGTAAAATCTATTGTAATCTGGGGAGGTAGTCC",
    "UTR3-RBS-A02": "CTCGGTATCTCGTGGTCTGACGGTAAAATCTATTGTAATCCGGGGAGGTAGTCC",
    "UTR3-RBS-A03": "CTCGGTATCTCGTGGTCTGACGGTAAAATCTATTGTAATCTGAGGAGGTAGTCC",
    "UTR3-RBS-A04": "CTCGGTATCTCGTGGTCTGACGGTAAAATCTATTGTAATCCAGGGAGGTAGTCC",
    "UTR3-RBS-A05": "CTCGGTATCTCGTGGTCTGACGGTAAAATCTATTGTAATCCCGGGAGGTAGTCC",
    "UTR3-RBS-A06": "CTCGGTATCTCGTGGTCTGACGGTAAAATCTATTGTAATCCGAGGAGGTAGTCC",
    "UTR3-RBS-A07": "CTCGGTATCTCGTGGTCTGACGGTAAAATCTATTGTAATCTCAGGAGGTAGTCC",
    "UTR3-RBS-A08": "CTCGGTATCTCGTGGTCTGACGGTAAAATCTATTGTAATCCAAGGAGGTAGTCC",
    "UTR3-RBS-A09": "CTCGGTATCTCGTGGTCTGACGGTAAAATCTATTGTAATCTAGGGAGGTAGTCC",
    "UTR3-RBS-A10": "CTCGGTATCTCGTGGTCTGACGGTAAAATCTATTGTAATCCCAGGAGGTAGTCC",
    "UTR3-RBS-A11": "CTCGGTATCTCGTGGTCTGACGGTAAAATCTATTGTAATCTCGGGAGGTAGTCC",
    "UTR3-RBS-A12": "CTCGGTATCTCGTGGTCTGACGGTAAAATCTATTGTAATCTAAGGAGGTAGTCC",
    "UTR1-RBS-AM12": "CTCGTTGAACACCGTCTCAGGTAAGTATCAGTTGTAAATCYVRGGAGGTAGTCC",
    "UTR1-RBS-AM24": "CTCGTTGAACACCGTCTCAGGTAAGTATCAGTTGTAAATCYVRGGRGGTAGTCC",
    "UTR2-RBS-AM12": "CTCGTGTTACTATTGGCTGAGATAAGGGTAGCAGAAAATCYVRGGAGGTAGTCC",
    "UTR2-RBS-AM24": "CTCGTGTTACTATTGGCTGAGATAAGGGTAGCAGAAAATCYVRGGRGGTAGTCC",
    "UTR3-RBS-AM12": "CTCGGTATCTCGTGGTCTGACGGTAAAATCTATTGTAATCYVRGGAGGTAGTCC",
    "UTR3-RBS-AM24": "CTCGGTATCTCGTGGTCTGACGGTAAAATCTATTGTAATCYVRGGRGGTAGTCC",
}


def _make_linker(linker_class, str_seq, id, description="visit https://www.biolegio.com/products-services/basic/ for further information."):
    seq = Seq("GG" + str_seq)
    return linker_class(
        seq,
        id,
        description=description
    )


BIOLEGIO_LINKERS = {
    key: _make_linker(bsb.BasicLinker, value, key) for key, value in standard_linkers.items()
}
BIOLEGIO_LINKERS.update(
    **{key: _make_linker(bsb.BasicUTRRBSLinker, value, key) for key, value in utr_rbs_linkers.items()}
)
BIOLEGIO_LINKERS = PartLinkerCollection(BIOLEGIO_LINKERS.items())
