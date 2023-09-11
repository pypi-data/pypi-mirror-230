from ..readstat.conversion import convert_readstat,Path


def convert_stata(file_path,
    data_dictionary_props=None):

    ext = Path(file_path).suffix

    if ext == ".dta":
        return convert_readstat(file_path,data_dictionary_props)
    else:
        raise Exception("Currently, Stata inputtypes only support DTA files")