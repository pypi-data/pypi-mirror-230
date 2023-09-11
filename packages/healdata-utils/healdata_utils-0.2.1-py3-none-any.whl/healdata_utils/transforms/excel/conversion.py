from healdata_utils.io import read_excel,pd
from healdata_utils.types import typesets
from healdata_utils.transforms.jsontemplate.conversion import convert_templatejson
def convert_dataexcel(file_path,sheet_name=None,multiple_data_dicts=True,**kwargs):
    """ 
    converts a file or file like object (eg pandas.ExcelFile) into a data dictionary
    package or a dict of data_dictionary packages

    file_path: str - path to xlsx file
    sheet_names: Union[str,list,None]. By default (None), all sheets are read and a dict
        of data frame is returned. If a list of sheets is provided, also returns a dict of packages. Else, returns 
    multiple_data_dicts, boolean: if each sheet represents one data resource 
        (ie if False, all sheets will be concatenated before inference)
    
    """ 

    dfs = read_excel(file_path,sheet_name)

    if isinstance(dfs,pd.DataFrame):
        dfs_to_infer = {"_onlyone":dfs}
        onlyone = True
    else:
        if multiple_data_dicts:
            dfs_to_infer = dfs
            onlyone = False
        else:
            dfs_to_infer = {"_onlyone":pd.concat(dfs.values())}
            onlyone = True
    
    packages = {}

    for name,df in dfs_to_infer.items():
        data_dictionary = {}
        fields = typesets.infer_frictionless_fields(df)

        data_dictionary['data_dictionary'] = fields

        package = convert_templatejson(data_dictionary)

    
        packages[name] = package

    if onlyone:
        return packages["_onlyone"]
    else:
        return packages
     


