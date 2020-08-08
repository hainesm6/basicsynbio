# json representation of BASIC DNA assembly builds

This document tries to come with a json representation of BASIC DNA assembly builds.

## Requirements for json representation

1. Object easily converted into build instructions for liquid-handling robotics.
2. Object facilitates validation of constructs.
3. Capable of decoding object back into a BasicBuild object.

## Draft data structure

```json
build = {
    "unique_parts": {
        "hash((part_1.id, part_1.seq))": {
            "seqrecord": {},
            "clips_indexes": []
        }, ...
    },
    "unique_linkers": {
        "hash((linker_1.id, linker_1.seq))": {
            "seqrecord": {},
            "prefix_id": "linker_1 prefix",
            "suffix_id": "linker_1 suffix",
            "clips_indexes": []
        }, ...
    },
    "clips_data": [
        {
            "prefix_linker_key": "hash of corresponding linker from unique linkers",
            "part_key": "hash of correspond part from unique parts",
            "suffix_linker_key": "hash of corresponding linker from unique linkers",
            "basic_assemblies": [
                "hash of corresponding 1st basic assembly", ...
            ]
        }, ...
    ],
    "basic_assemblies": {
        "hash((basic_assembly_1.id, basic_assembly_1.seq))": {
            "seqrecord": {},
            "clips_indexes": []
        }, ...
    },
}
```

## How build json object facilitates instructions for building assemblies

Specific build instructions would centre around setting up clip reactions and completing assemblies. Arguments for purification and transformation steps are easily inferred from arguments used to setup these two critical processes. 

To setup clip reactions:
- `"clips_data"` contains information on what prefix, suffix and part to transfer. This information could be used to query databases describing collections of parts/linkers in lab freezers, enabling substrates to be parsed into liquid-handling robotic jobs.
- To calculate the number of times a specific clip reaction must be repeated in a build, it provides the `"basic_assemblies"` array which lists which assemblies use this specific clip reaction. The number of times the `i<sup>th</sup>` clip reaction must be repeated is calculated by:

```python
number = len(build.clips_data[i].basic_assemblies)/assemblies_per_clip
```

where `assemblies_per_clip` can vary between different implementations of BASIC assembly e.g. DNA-BOT vs manual.

To complete assemblies:
- Each object in `build.basic_assemblies` contains the indexes of required clip reactions as an array (`clips_indexes`). These can be used to identify which specific clip reactions to transfer when assembling the construct.

## How build json object facilitates validation of constructs

Each object in the `build.basic_assemblies` dictionary contains a `seqrecord` key-value pair which contains the `Bio.SeqRecord.SeqRecord` of the given BasicAssembly as a value. This can be converted into an annotated genbank file. *Can then mention the two common approaches for validating constructs. Specifically using sequencing primers that anneal to the T0 & T1 for validating inserts and diagnostic digests for validating insert/backbone*.

## How the build json object can be decoded

Using the corresponding json.load/loads command and passing the `decode_build` to the `object_hook` argument, e.g.

```python
decoded_build = json.loads(serialised_build, object_hook=bsb.decode_build)
```

This internally generates all unique bsb.BasicPart and bsb.BasicLinker objects in separate dictionaries, assigning each to a kye corresponding to their unique hash value. These dictionaries and the data in the build json object are used to generate each `BasicAssembly` object by identifying corresponding `id` and `*parts_linkers` arguments for each. The resulting BasicAssembly objects can then be parsed into the `BasicBuild` constructor to generate the BasicBuild object.