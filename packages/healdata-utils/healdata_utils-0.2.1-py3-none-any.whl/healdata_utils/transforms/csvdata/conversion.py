""" 
 
CSV data to HEAL VLMD conversion


""" 
from healdata_utils.io import read_delim 
from healdata_utils.transforms.jsontemplate.conversion import convert_templatejson
from healdata_utils.types import typesets
import pandas as pd
def convert_datacsv(file_path,data_dictionary_props={}):
    """ 
    Takes a CSV file containing data (not metadata) and 
    infers each of it's variables data types and names.
    These inferred properties are then outputted as partially-completed HEAL variable level metadata
    files. That is, it outputs the `name` and `type` property. 

    NOTE: this will be an invalid file as `description` is required
    for each variable. However, this serves as a great way to start
    the basis of a VLMD submission.
    """  
    df = read_delim(file_path)
    data_dictionary = data_dictionary_props.copy()
    fields = typesets.infer_frictionless_fields(df)
    data_dictionary['data_dictionary'] = fields 

    package = convert_templatejson(data_dictionary)
    return package
