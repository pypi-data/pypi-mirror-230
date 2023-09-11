from ..readstat.conversion import convert_readstat,Path


def convert_spss(file_path,
    data_dictionary_props=None):

    ext = Path(file_path).suffix

    if ext == ".sav":
        return convert_readstat(file_path,data_dictionary_props)
    else:
        raise Exception("Currently, SPSS inputtypes only support SAV files")