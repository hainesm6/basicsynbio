"""Main module for basicsynbio."""

from basicsynbio.utils import _easy_seqrec
from basicsynbio.decorators import add2docs
from Bio import SeqUtils, SeqIO
from Bio.Restriction.Restriction import BsaI
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.SeqFeature import SeqFeature, FeatureLocation
from Bio.SeqUtils.CheckSum import seguid
from collections import Counter
import datetime
import hashlib

DATE = datetime.datetime.now()
DEFAULT_ANNOTATIONS = {
    "source": "synthetic construct",
    "organism": "synthetic construct",
    "taxonomy": ["other sequences", "artificial sequences"],
    "date": DATE.strftime("%d-") + DATE.strftime("%b").upper() + DATE.strftime("-%Y"),
    "accessions": [],
    "sequence_version": 1,
    "topology": "circular",
    "molecule_type": "DNA",
}
IP_STR = "TCTGGTGGGTCTCTGTCC"
IS_STR = "GGCTCGGGAGACCTATCG"
IP_SEQREC = _easy_seqrec(IP_STR, "iP", note=["BASIC integrated prefix"])
IS_SEQREC = _easy_seqrec(IS_STR, "iS", note=["BASIC integrated suffix"])


class CommonArgDocs:
    ADD_I_SEQS = ":param bool add_i_seqs: if True adds flanking BASIC iP and iS sequences. Note, letter_annotations attribute is lost."
    HANDLE = ":param handle: handle to file."
    FORMAT = ":param string format: file format."
    SEQREC_KWARGS = ":param \**kwargs: assigns alternative SeqRecord attributes."
    PARTS_LINKERS_ARGS = ":param \*parts_linkers: :py:class:`BasicPart` and :py:class:`BasicLinker` objects."


class BasicPart(SeqRecord):
    """Class for BASIC DNA assembly parts.

    A DNA sequence joined with other BasicParts via :py:class:`BasicLinker`
    instances when initialising :py:class:`BasicAssembly` objects. All 
    sequences must contain intergated prefix and suffix sequences.

    Attributes:
        _ip_loc (int): The index/location of `IP_STR` within sequence.
        _is_loc (int): The index/location of `IS_STR` within sequence.
    """

    def __init__(self, seq, id: str, **kwargs):
        """Class for BASIC DNA assembly parts.

        Args:
            seq (seq): Refer to Bio.SeqRecord.SeqRecord documentation.
            id (string): Refer to Bio.SeqRecord.SeqRecord documentation.
            **kwargs: assigns alternative SeqRecord attributes.
        """
        super().__init__(seq=seq, id=id, **kwargs)
        self._ip_loc = self._find_iseq(IP_STR, "iP sequence")
        self._is_loc = self._find_iseq(IS_STR, "iS sequence")
        self._check_bsai()

    def basic_slice(self) -> SeqRecord:
        """The Function to obtain region flanked by BASIC iP & iS sequences

        Returns:
            SeqRecord: The region flanked by BASIC iP & iS sequences as a SeqRecord object.

        Raises:
            ValueError: If iP and iS sequences not correctly identified.

        """
        returned_seqrec = SeqRecord(seq=self.seq, id=self.id)
        for key in returned_seqrec.__dict__.keys():
            setattr(returned_seqrec, key, self.__dict__[key])
        if self._ip_loc < self._is_loc:
            return returned_seqrec[self._ip_loc + len(IP_STR) : self._is_loc]
        elif self._ip_loc > self._is_loc:
            return (
                returned_seqrec[self._ip_loc + len(IP_STR) :]
                + returned_seqrec[: self._is_loc]
            )
        else:
            raise ValueError("incorrect sequence used.")

    def _find_iseq(self, iseq_str: str, iseq_id: str = "integrated sequence") -> int:
        """The Function to find index/location of iseq_str within the sequence.

        Args:
            iseq_str (str): The subsequence you are searching for.
            iseq_id (str, optional): The id/name of the subsequence 
                (iseq_str), Defaults to "integrated sequence".

        Returns:
            int: The index/location of iseq within sequence.

        Raises:
            PartException: If iseq_str can not be found within the sequence,
                if multiple iseq_str exist within the sequence.
        """
        search_out = SeqUtils.nt_search(str(self.seq), iseq_str)
        if len(search_out) < 2:
            raise PartException(f"{self.id} lacks {iseq_id}")
        elif len(search_out) > 2:
            raise PartException(f"{self.id} contains multiple {iseq_id}")
        return search_out[1]

    def _check_bsai(self):
        """The function to check if sliced BasicPart contains a BsaI site.
        
        Raises:
            PartException: If the BasicPart sequence contains more than two
                BsaI sites.
        """
        if len(BsaI.search(self.seq)) > 2:
            raise PartException(f"{self.id} contains more than two BsaI sites.")

    def __eq__(self, other) -> bool:
        """The function test if an object `other` is equal to this BasicPart.
        
        Args:
            other (BasicPart): The object to be compared for similarity with 
                this BasicPart.

        Returns:
            bool: True if `other` is equal to self, false otherwise.

        Raises:
            TypeError: If the `other` arg is not of type BasicPart.
        """
        if not isinstance(other, BasicPart):
            raise TypeError(f"{other} is not a BasicPart instance.")
        return self.id == other.id and str(self.seq) == str(other.seq)


BasicPart.__doc__ += CommonArgDocs.SEQREC_KWARGS


class BasicLinker(SeqRecord):
    """Class for BASIC DNA assembly linkers.

    A DNA sequence joined with other BasicLinkers via :py:class:`BasicPart`
    instances when initialising :py:class:`BasicAssembly` objects.

    Attributes:
        prefix_id (str): The prefix half linker id.
        suffix_id (str): The suffix half linker id.
        seq: Refer to Bio.SeqRecord.SeqRecord documentation.
        id: Refer to Bio.SeqRecord.SeqRecord documentation.
        features (array[seqFeature]): array of features and their details,
            with the BasicLinker object.

    """

    def __init__(self, seq, id, prefix_id=None, suffix_id=None, **kwargs):
        """Class for BASIC DNA assembly parts.

        Args:
            seq (seq): Refer to Bio.SeqRecord.SeqRecord documentation.
            id (string): Refer to Bio.SeqRecord.SeqRecord documentation.
            prefix_id (str, optional): prefix id if known and not needing 
                generation, defaults to None.
            suffix_id (str, optional): suffix id if known and not needing 
                generation, defaults to None.
            **kwargs: assigns alternative SeqRecord attributes.
        """
        super().__init__(seq=seq, id=id, **kwargs)
        self.prefix_id = self._assign_linker_half_id("prefix", prefix_id)
        self.suffix_id = self._assign_linker_half_id("suffix", suffix_id)
        self._linker_feature()

    def basic_slice(self):
        """The function to obtain the basic slice of `BasicLinker` objects.

        Returns:
            BasicLinker: returns self, the basic slice of `BasicLinker` objects.
        """
        return self

    def _linker_feature(self):
        """The function to populate `features` attribute of `BasicLinker` Object.
        """
        self.features.append(
            SeqFeature(
                type="misc_feature",
                location=FeatureLocation(2, len(self.seq), strand=+1),
                qualifiers={"label": [str(self.id)]},
            )
        )

    def _assign_linker_half_id(self, linker_half: str, id) -> str:
        """The function to assign half linker id attributes.

        Args:
            linker_half (str): A variable to determine whether linker half
                is being assigned for a 'prefix' or a 'suffix'.
            id: if present linker half id is determined and returned, if half
                linker id needs generating, pass (None).

        Returns:
            NoneType: the assigned half linker id.
        """
        if not id and linker_half == "prefix":
            return f"{self.id}-P"
        elif not id and linker_half == "suffix":
            return f"{self.id}-S"
        return id

    def __eq__(self, other) -> bool:
        """The function test if an object `other` is equal to this BasicLinker.
        
        Args:
            other (BasicLinker): The object to be compared for similarity with 
                this BasicLinker.

        Returns:
            bool: True if `other` is equal to self, false otherwise.

        Raises:
            TypeError: If the `other` arg is not of type BasicLinker.
        """
        if not isinstance(other, BasicLinker):
            raise TypeError(f"{other} is not a BasicLinker instance.")
        return self.id == other.id and str(self.seq) == str(other.seq)


BasicLinker.__doc__ += CommonArgDocs.SEQREC_KWARGS


class BasicUTRRBSLinker(BasicLinker):
    """Sub-class of :py:class:`BasicLinker` for UTR-RBS linkers.
    
    Attributes:
        prefix_id (str): The prefix half linker id.
        suffix_id (str): The suffix half linker id.
        seq: Refer to Bio.SeqRecord.SeqRecord documentation.
        id: Refer to Bio.SeqRecord.SeqRecord documentation.
        features (array[seqFeature]): array of features and their details,
            with the BasicLinker object.
    """

    def __init__(self, seq, id, prefix_id=None, suffix_id=None, **kwargs):
        """The function to initial the basic slice of `BasicLinker` objects.
        
        Args:
            seq (seq): Refer to Bio.SeqRecord.SeqRecord documentation.
            id (string): Refer to Bio.SeqRecord.SeqRecord documentation.
            prefix_id (str, optional): prefix id if known and not needing 
                generation, defaults to None.
            suffix_id (str, optional): suffix id if known and not needing 
                generation, defaults to None.
            **kwargs: assigns alternative SeqRecord attributes.
        """
        super().__init__(seq, id, prefix_id, suffix_id, **kwargs)
        self.prefix_id = super()._assign_linker_half_id("prefix", prefix_id)
        self.suffix_id = f"UTR{self.id[3]}-S"


class BasicAssembly:
    """Class for BASIC DNA assemblies.

    Note:
        BasicAssembly class requires alternating :py:class:`BasicPart` and
        :py:class:`BasicLinker` instances in any order.

    Attributes:
        id(str): Identifier for BasicAssemby object. Must be unique
            amongst BasicAssembly instances used to initiate a BasicBuild
            object.
        parts_linkers(tuple): tuple of BasicPart and BasicLinker objects used to
            create this assembly.
        clip_reactions(tuple): The :py:class:`ClipReaction` instances required
            for BASIC assembly.
    """

    def __init__(self, id: str, *parts_linkers):
        """Class for BASIC DNA assemblies.

        Args:
            id (string): Identifier for BasicAssemby object. Must be unique
                amongst BasicAssembly instances used to initiate a BasicBuild
                object.
            *parts_linkers(tuple): tuple of BasicPart and BasicLinker
                objects used to create this assembly.

        Raises:
            TypeError: If the id parsed to BasicAssembly constructor was not of
                type str.
        """
        if isinstance(id, str) == False:
            raise TypeError(
                f"id parsed to BasicAssembly constructor was not of type str."
            )
        self.id = id
        self.parts_linkers = parts_linkers
        self.clip_reactions = self.return_clip_reactions()

    @add2docs(CommonArgDocs.SEQREC_KWARGS, indentation=8)
    def return_part(self, **kwargs) -> BasicPart:
        """A function to return the assembled construct as a new part.

        Args:
            **kwargs: assigns alternative SeqRecord attributes.

        Returns:
            BasicPart: assembled construct as a new part.
        """
        return seqrec2part(self.return_seqrec(**kwargs))


    def return_seqrec(self, **kwargs) -> SeqRecord:
        """A function to return the assembled construct as a seqrecord.

        Args:
            **kwargs: assigns alternative SeqRecord attributes.

        Returns:
            SeqRecord: assembled construct as a new seqrecord.
        """
        seqrec = SeqRecord(Seq(str()))
        for part_linker in self.parts_linkers:
            seqrec += part_linker.basic_slice()
        seqrec.id = self.id
        seqrec.name = "BASIC_construct_" + self.id
        seqrec.description = f"BASIC DNA Assembly of {[part_linker.id for part_linker in self.parts_linkers]}"
        seqrec.annotations = DEFAULT_ANNOTATIONS
        if kwargs:
            for key, value in kwargs.items():
                setattr(seqrec, key, value)
        return seqrec

    def return_clip_reactions(self) -> tuple:
        """A function to return the :py:class:`ClipReaction` instances required for BASIC assembly.

        Returns:
            tuple(ClipReaction): A collection of `ClipReaction` instances 
            required for BASIC assembly.
        """
        clip_reactions = []
        for ind, part_linker in enumerate(self.parts_linkers):
            if issubclass(type(part_linker), BasicLinker):
                pass
            else:
                if ind == len(self.parts_linkers) - 1:
                    suffix = self.parts_linkers[0]
                else:
                    suffix = self.parts_linkers[ind + 1]
                clip_reactions.append(
                    ClipReaction(
                        prefix=self.parts_linkers[ind - 1],
                        part=part_linker,
                        suffix=suffix,
                    )
                )
        self._check_clip_reactions(clip_reactions)
        return tuple(clip_reactions)

    def _check_clip_reactions(self, clip_reactions):
        """Checks `ClipReactions` are compatible e.g. same half linker not used
        multiple times.
        
        Args:
            clip_reactions (list(ClipReaction)): the list of `ClipReaction`
                objects to be analysed for compatability.
        """

        def _check_linker_halves(linker_halves):
            """Check linker_halves are compatible.

            Note:
                UTR linker-halves must be compatible.

            Args:
                linker_halves (list(half_linker_id)): the list of 
                    half_linker_ids to be analysed for compatability.

            Raises:
                AssemblyException: If non unique half linker ids present.
            """
            if len(linker_halves) > len(set(linker_halves)):
                top_linker_half = Counter(linker_halves).most_common(1)[0]
                raise AssemblyException(
                    f"BasicAssembly initiated with {top_linker_half[0]} used {top_linker_half[1]} times."
                )

        prefix_linkers = [
            clip_reaction.linker_half_ids()[0] for clip_reaction in clip_reactions
        ]
        _check_linker_halves(prefix_linkers)
        suffix_linkers = [
            clip_reaction.linker_half_ids()[1] for clip_reaction in clip_reactions
        ]
        _check_linker_halves(suffix_linkers)

    @property
    def parts_linkers(self):
        """tuple(BasicPart & BasicLinker): Returns tuple of BasicParts and 
            BasicLinkers in the assembly"""
        return self._parts_linkers

    @parts_linkers.setter
    def parts_linkers(self, values):
        if not all(
            issubclass(type(value), BasicPart) or issubclass(type(value), BasicLinker)
            for value in values
        ):
            raise TypeError(
                "Not all *parts_linkers are BasicParts or BasicLinkers instances."
            )
        for ind, value in enumerate(values):
            if ind != 0:
                if type(values[ind - 1]) == type(value):
                    raise AssemblyException(
                        f"Alternating BasicPart, BasicLinker instances required: {value.id} is preceeded by {type(values[ind - 1])} and is of type {type(value)}."
                    )
        if len(values) % 2 != 0:
            raise AssemblyException(
                f"BasicAssembly instance with id:{self.id}, initiated with an odd number of BasicPart/BasicLinker objects. An even number is a requirement."
            )
        self._parts_linkers = values


BasicAssembly.__doc__ += CommonArgDocs.PARTS_LINKERS_ARGS


class ClipReaction:
    """Class for describing clip reactions. 
    
    Note: 
        ClipReaction is hashable.

    Attributes:
        prefix(BasicLinker): The BasicLinker used as a prefix in this clip
        part(BasicPart): The central BasicPart within this clip
        suffix(BasicLinker): The BasicLinker used as a suffix in this clip
    """

    def __init__(self, prefix, part, suffix):
        """Class for describing clip reactions.

        Args:
            prefix(BasicLinker): The BasicLinker used as a prefix in this clip
            part(BasicPart): The central BasicPart within this clip
            suffix(BasicLinker): The BasicLinker used as a suffix in this clip

        """
        self._prefix = prefix
        self._suffix = suffix
        self._part = part

    def linker_half_ids(self) -> tuple:
        """A function to return ids for prefix and suffix linkers in the form (prefix_id, suffix_id).

        Returns:
            tuple(string, string): returns ids for prefix and suffix linkers in
            the form (prefix_id, suffix_id).
        """
        return self._prefix.prefix_id, self._suffix.suffix_id

    def clip_items(self) -> tuple:
        """A function to returns a tuple describing each of the items within each clip.

        Returns:
            tuple(BasicLinker, BasicPart, BasicLinker): items within each clip
        """
        return self._prefix, self._part, self._suffix

    def _hexdigest(self, length=16, byteorder="big", signed=True):
        """The function to create the hexadecimal digest
        
        the hexadecimal digest of the Clip Reaction md5 hash by
        converting it to a byte array

        Note:
            See docs for information on built-in function: int.to_bytes().

        Args:
            length(int, optional): bit length.
            byteorder(string, optional): determines where most signaficat byte is 
                locatated, see Note.
            signed(bool, optional): see Note.

        Returns:
            string: hexadecimal digest of the Clip Reaction md5 hash by
            converting it to a byte array

        """
        return hashlib.md5(
            self.__hash__().to_bytes(length, byteorder=byteorder, signed=signed)
        ).hexdigest()

    def __hash__(self):
        """The function to create the object hash

        Returns:
            string: hash of tuple containing, prefix_id, part_id and suffix_id
        """
        return hash((self._prefix.id, self._part.id, self._suffix.id))

    def __eq__(self, other) -> bool:
        """The function test if an object `other` is equal to this `ClipReaction`.
        
        Args:
            other (ClipReaction): The object to be compared for similarity with 
                this ClipReaction.

        Returns:
            bool: True if `other` is equal to self, false otherwise.

        Raises:
            TypeError: If the `other` arg is not of type ClipReaction.
        """
        if not isinstance(other, ClipReaction):
            raise TypeError(f"{other} is not a ClipReaction instance.")
        return (
            self._prefix == other._prefix
            and self._part == other._part
            and self._suffix == other._suffix
        )


class PartException(Exception):
    pass


class LinkerException(Exception):
    pass


class AssemblyException(Exception):
    pass


@add2docs(CommonArgDocs.ADD_I_SEQS, indentation=4)
def seqrec2part(seqrec: SeqRecord, add_i_seqs=False) -> BasicPart:
    """A function to Convert SeqRecord to :py:class:`BasicPart`.
    
    Note:
        Relevant attributes are maintained.

    Args:
        seqrec(Bio.SeqRecord.SeqRecord): SeqRecord to be converted to
            :py:class:`BasicPart` subclass.
        add_i_seqs(bool, optional): if True adds flanking BASIC iP and iS 
            sequences. Note, letter_annotations attribute is lost.

    Returns:
        BasicPart: the BasicPart created from Args
    """
    if add_i_seqs:
        new_seqrec = IP_SEQREC + seqrec + IS_SEQREC
        part = BasicPart(new_seqrec.seq, seqrec.id, features=new_seqrec.features)
        for key, value in seqrec.__dict__.items():
            if key not in ("_seq", "_per_letter_annotations", "features"):
                setattr(part, key, value)
    else:
        part = BasicPart(seqrec.seq, seqrec.id)
        for key, value in seqrec.__dict__.items():
            setattr(part, key, value)
    return part
