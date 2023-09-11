import pandas as pd
from healdata_utils.utils import to_int_if_base10,stringify_keys
from healdata_utils.io import read_pyreadstat
from healdata_utils.types import typesets
from ..jsontemplate.conversion import convert_templatejson
from datetime import datetime
from pathlib import Path

def convert_readstat(file_path,
    data_dictionary_props=None,
    sas_catalog_filepath=None,):
    """
    Converts a "metadata-rich" (ie statistical software file) 
    into a HEAL-specified data dictionary in both csv format and json format.

    This function relies on [readstat](https://github.com/Roche/pyreadstat) which supports SPSS (sav), 
    SAS (sas7bdat), and Stata (dta). 

    > Currently, this function uses both data and metadata to generate 
    a HEAL specified data dictionary. That is, types are inferred from the 
    data (so at least test or synthetic data needed) while everything else is taken 
    from the metadata (eg missing values, variable labels, variable value labels etc)

    Parameters
    ----------
    file_path : str or path-like or any object
        Data or path to data with the data being a tabular HEAL-specified data dictionary.
        This input can be any data object or path-like string excepted by a frictionless Resource object.
    data_dictionary_props : dict
        The HEAL-specified data dictionary properties.
    
    sas_catalog_filepath : str or path-like
        Path to a sas catalog file (sas7bcat). Needed for value formats if a sas (sas7bdat) input file

    Returns
    -------
    dict
        A dictionary with two keys:
            - 'templatejson': the HEAL-specified JSON object.
            - 'templatecsv': the HEAL-specified tabular template.

    Notes
    -----
    ## Missing values (from pyreadstat docs)

    SPSS only supports 3 discrete missing in addition to ranges.
    For POC, only using discrete. TODO: use range(lo,hi+1) to do ranges; JCOIN Core Measures, for example, will need this
    
    From module documentation on missing values:

    - SPSS
        missing_ranges: a dict with keys being variable names. 
        Values are a list of dicts. 
        Each dict contains two keys, 'lo' and 'hi' being the lower boundary and higher boundary for the missing range. 
        Even if the value in both lo and hi are the same, the two elements will always be present. 
        This appears for SPSS (sav) files when using the option user_missing=True: user defined missing values appear not as nan but as their true value and this dictionary stores the information about which values are to be considered missing.
    
    - Stata/SAS
        missing_user_values: a dict with keys being variable names. 
        Values are a list of character values (A to Z and _ for SAS, a to z for SATA) 
        representing user defined missing values in SAS and STATA. 
        This appears when using user_missing=True in read_sas7bdat or read_dta 
        if user defined missing values are present.

    """
    metaparams = dict(file_path=file_path,user_missing=True)
    if sas_catalog_filepath:
        metaparams["catalog_file"] = sas_catalog_filepath
    _,meta = read_pyreadstat(**metaparams) # get user missing values (for stata/sas will make string so need sep call to infer types)
    df,_ = read_pyreadstat(file_path) # dont fill user defined missing vals (to get correct types)
    
    if not data_dictionary_props:
        data_dictionary_props = {}

    # NOTE: not inferring categoricals as this is inferred from value labels
    fields = typesets.infer_frictionless_fields(df,typesets=[typesets.typeset_original])

    for field in fields:
        field.pop('extDtype',None)
        fieldname = field['name']

        variable_label = meta.column_names_to_labels.get(fieldname)
        if variable_label:
            field['description'] = variable_label

        missing_values = meta.missing_user_values.get(fieldname,[])
        missing_ranges = meta.missing_ranges.get(fieldname,[])
        #see NOTE in docstring (on missing values): 
        # below maps SPSS missing values
        for items in missing_ranges:
            values = list(set(items.values()))
            if len(values)==1:
                if isinstance(values[0],datetime):
                    missing_values.append(str(values[0]))
                else:
                    missing_values.append(values[0])
            else:
                raise Exception("Currently, only discrete values are supported")

        # NOTE: stringify to conform to frictionless pattern
        value_labels = meta.variable_value_labels.get(fieldname)

        if value_labels:
            # NOTE: collect enums before stringfying - frictionless spec evaluates on logical representation
            enums = [
                val for val in list(value_labels.keys()) 
                if not val in missing_values
            ]
            stringify_keys(value_labels)
            field['encodings'] = value_labels

            if enums:
                constraints_enums = {'constraints':{'enum':enums}}
                field.update(constraints_enums)
        
        if missing_values:
            # NOTE: stringify to conform to frictionless standards (missing values evaluated on physical representation)
            missing_values_str = [str(val) for val in missing_values]
            field['missingValues'] = missing_values_str

    data_dictionary = data_dictionary_props.copy()
    data_dictionary['data_dictionary'] = fields 

    package = convert_templatejson(data_dictionary)
    return package
