"""Module contains objects for importing and exporting parts and sequences."""

from basicsynbio.decorators import add2docs
from basicsynbio.main import CommonArgDocs, IP_SEQREC, IS_SEQREC, seqrec2part
import basicsynbio as bsb
from Bio import SeqIO
from Bio.SeqRecord import SeqRecord
import io
import json
import os
import tempfile
from typing import Union, Iterable, Iterator, Generator
from sbol2 import Document


@add2docs(CommonArgDocs.HANDLE, CommonArgDocs.FORMAT, CommonArgDocs.ADD_I_SEQS)
def import_part(handle: str, format: str, add_i_seqs: bool =False) -> bsb.BasicPart:
    """Imports a Part object using Bio.SeqIO.read().

    Note:
        Refer to Biopython documentation for further information on Bio.SeqIO.read().

    Args:
        handle: handle of file to be parsed
        format: format of handle file could be 'fasta', 'genbank'...
        add_i_seqs (optional): if True adds flanking BASIC iP and iS sequences.
            Note, letter_annotations attribute is lost."

    Returns:
        BasicPart: a Part object using Bio.SeqIO.read()
    """
    seqrec = SeqIO.read(handle, format)
    return seqrec2part(seqrec, add_i_seqs)


@add2docs(CommonArgDocs.ADD_I_SEQS)
def import_sbol_parts(path: str, add_i_seqs=False) -> Generator[bsb.BasicPart, None, None]:
    """Imports a BasicPart object using sbol2.Document.exportToFormat.

    Note:
        Refer to Biopython documentation for further information on Bio.SeqIO.read().
        Refer to pysbol2 documentation for further information.

    Args:
        path: path to SBOL file.
        add_i_seqs (optional): if True adds flanking BASIC iP and iS sequences.
            Note, letter_annotations attribute is lost."

    Returns:
        BasicPart: a Part object using Bio.SeqIO.read()
    """
    doc = Document(path)
    fp = tempfile.NamedTemporaryFile(delete=False)
    doc.exportToFormat("GenBank", fp.name)
    seqrecs = SeqIO.parse(fp.name, "genbank")
    fp.close()
    os.unlink(fp.name)
    yield from (seqrec2part(seqrec, add_i_seqs) for seqrec in seqrecs)


@add2docs(CommonArgDocs.HANDLE, CommonArgDocs.FORMAT, CommonArgDocs.ADD_I_SEQS)
def import_parts(handle: str , format: str, add_i_seqs=False) -> Iterable[bsb.BasicPart]:
    """Imports a Generator of BasicPart objects using Bio.SeqIO.parse().

    Note:
        Refer to Biopython documentation for further information on Bio.SeqIO.parse().

    Args:
        handle: handle of file to be parsed
        format: format of handle file could be 'fasta', 'genbank'...
        add_i_seqs (optional): if True adds flanking BASIC iP and iS sequences.
            Note, letter_annotations attribute is lost."

    Yields:
        BasicPart: all BasicPart objects within the file.
    """
    seqrecs = SeqIO.parse(handle, format)
    yield from (seqrec2part(seqrec, add_i_seqs) for seqrec in seqrecs)


@add2docs(
    CommonArgDocs.HANDLE,
    CommonArgDocs.FORMAT,
)
def export_sequences_to_file(sequences: Iterable[Union[SeqRecord, bsb.BasicPart, bsb.BasicAssembly]], handle: str, format: str ="genbank", molecule_type: str ="DNA") -> None:
    """Exports sequences to file using Bio.SeqIO.write().

    Note:
        Refer to Biopython documentation for further information on Bio.SeqIO.write().

    Args:
        sequences: Sequences to export.
        handle: File name to write to.
        format (optional): Format of handle file could be 'fasta', 'genbank'.
            Defaults to 'genbank'.
        molecule_type (optional): Type of molecule within sequences.
            defaults to 'DNA'.

    Raises:
        ValueError: sequences was not of correct type.

    """
    if type(sequences) in [bsb.BasicPart, bsb.BasicAssembly, SeqRecord]:
        SeqIO.write(_process_basic_object(sequences, molecule_type), handle, format)
    elif hasattr(sequences, "__iter__"):
        sequences = (
            _process_basic_object(basic_object, molecule_type)
            for basic_object in sequences
        )
        SeqIO.write(sequences, handle, format)
    else:
        raise TypeError(
            "sequences was not iterable or of type BasicPart, BasicAssembly or SeqRecord"
        )


def _process_basic_object(basic_object, molecule_type):
    """Converts basic_object into an object that can be processed by Bio.SeqIO.

    """
    try:
        basic_object = basic_object.return_seqrec()
    except AttributeError:
        pass
    basic_object.annotations["molecule_type"] = molecule_type
    return basic_object
