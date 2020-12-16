from basicsynbio.decorators import add2docs
from basicsynbio.main import CommonArgDocs
from basicsynbio.main import BasicPart, BasicLinker
from basicsynbio.cam import _seqrecord_hexdigest
from typing import Union


class PartLinkerCollection(dict):
    def __str__(self):
        string = ""
        for item in self.items():
            string += f"{item[0]} id: {item[1].id}\n"
            string += f"{item[0]} name: {item[1].name}\n"
            string += f"{item[0]} description: {item[1].description}\n\n"
        return string


@add2docs(CommonArgDocs.PARTS_LINKERS_ARGS)
def make_collection(*parts_linkers: Union[BasicPart, BasicLinker], keys=None, id_function: callable =None) -> dict:
    """Generates a PartLinkerCollection object using parts_linkers.
    Args:
        keys -- if None, uses name attribute, otherwise user supplies iterable of keys corresponding to each part/linker.
        id_function: function to define id of objects. If none uses set_part_linker_id function.
    """
    parts_linkers_w_id = map(set_part_linker_id, parts_linkers)
    if not keys:
        collection = {part_linker.name: part_linker for part_linker in parts_linkers_w_id}
    else:
        collection = {key: value for key, value in zip(keys, parts_linkers_w_id)}
    return PartLinkerCollection(collection.items())


def set_part_linker_id(part_linker):
    """Sets the id attribute of a part_linker using the output of _seqrecord_hexdigest."""
    part_linker.id = _seqrecord_hexdigest(part_linker)
    return part_linker
