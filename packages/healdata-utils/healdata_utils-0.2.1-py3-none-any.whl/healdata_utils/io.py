""" 
functions to read and write files in a "smart" way
"""
import pyreadstat
import pandas as pd 
from pathlib import Path
import json
import charset_normalizer
import re

from healdata_utils import schemas
# read pyreadstat files

def read_pyreadstat(file_path,**kwargs):
    ''' 
    reads in a "metadata rich file"
    (dta, sav,b7bdat). Note, xport format not supported
    as it doesnt supply value labels.

    '''
    file_path = Path(file_path)
    ext = file_path.suffix 
    if ext=='.sav':
        read = pyreadstat.read_sav
    elif ext=='.sas7bdat':
        read = pyreadstat.read_sas7bdat
    elif ext=='.dta':
        read = pyreadstat.read_dta
    elif ext=='.por':
        read = pyreadstat.read_por

    return read(file_path,**kwargs)



def detect_file_encoding(file_path):
    """ 
    detects file encoding using charset_normalizer package
    """ 
    with open(file_path,'rb') as f:
        data = f.read()
        encoding_for_input = charset_normalizer.detect(data)

    is_confident = encoding_for_input["confidence"]==1
    if not is_confident:
        print("Be careful, the detected file encoding for:")
        print(f"{file_path}")
        print(r"has less than 100% confidence")
    #chardet_normalizer.detect returns confidence,encoding (as a string), and language (eg English)
    return encoding_for_input["encoding"]


def read_delim(file_path,castdtype = "string"):
    """ 
    reads in a tabular file (ie spreadsheet) after detecting
    encoding and file extension without any type casting.

    currently supports csv and tsv

    defaults to not casting values (ie all columns are string dtypes)
    and not parsing strings into NA values (eg "" is kept as "")
    """ 
    ext = Path(file_path).suffix
    if ext==".csv":
        sep = ","
    elif ext==".tsv":
        sep = "\t"
        
    encoding = detect_file_encoding(file_path)
    file_encoding = pd.read_csv(
        file_path,sep=sep,encoding=encoding,dtype=castdtype,
        keep_default_na=False)

    return file_encoding

def read_excel(filepath,sheet_names=None,castdtype="string"):
    """ 
    reads in an excel file that outputs
    a dict of dataframes with each sheet name being
    the dict key and the dict value being the pandas 
    dataframe of the corresponding sheet. 
    
    This is akin to pandas.read_excel when all sheet_names (or sheet_name=None)
    is specified EXCEPT that the default is each value is the string representation.

    See the dtype arg in pandas read_excel docs for more info.


    file_path: str - path to xlsx file
    sheet_names: Union[str,list,None]. By default (None), all sheets are read and a dict
        of data frame is returned. If a list of sheets is provided, also returns a dict of packages. Else, returns 
    """ 

    book = pd.ExcelFile(filepath)
    
    if isinstance(sheet_names,list):
        selected_sheet_names = [sheet for sheet in book.sheet_names 
            if sheet in sheet_names]
    elif isinstance(sheet_names,str):
        selected_sheet_names = [sheet_names]
    else:
        selected_sheet_names = book.sheet_names


    if len(selected_sheet_names) == 1:
        df = pd.read_excel(book,sheet_name=sheet,dtype=castdtype).fillna("")
        return df
    else:
        dfs = {}
        for sheet in selected_sheet_names:
            dfs[sheet] = pd.read_excel(book,sheet_name=sheet,dtype=castdtype).fillna("")
        
        return dfs


def read_zip():
    pass 


def read_archive():
    pass 

def _generate_jsontemplate(schema):

    if schema.get('type','') == 'object':
        val = {}
        if 'properties' in schema:
            for prop, prop_schema in schema['properties'].items():
                val[prop] = _generate_jsontemplate(prop_schema)
    elif schema.get('type','') == 'array':
        val = []
        if schema.get("items"):
            val.append(_generate_jsontemplate(schema['items']))
    # elif schema.get("enum"):
    #     val = f"Pick one of: {str(schema['enum'])}"
    else:
        val = None
   
    return val

    
def write_vlmd_template(outputfile,output_overwrite=False,numfields=1):

    """ 
    Writes a  json or csv template:
    If writing a json template, will iniiate null vals for all fields
    If writing a csv template (ie csv tabular template), will copy the recommendation level across num fields specified.
    

    NOTE
    -----
    - Recommendation level is in description property with expression [<recommendation level>]. The 
    "required" property takes precdence over rec level.

    - csv is a frictionless table schema and json is a jsonschema
    """  
    

    ext = Path(outputfile).suffix 

    # if file exists and overwrite option is false, raise error
    if Path(outputfile).exists() and not output_overwrite:
        raise FileExistsError(f"{outputfile} exists")


    if ext == ".json":
        schema = schemas.healjsonschema
        fields_propname = "data_dictionary"
        template = _generate_jsontemplate(schema)
        template[fields_propname] = numfields *  template[fields_propname]
        Path(outputfile).write_text(json.dumps(template,indent=2))
    
    elif ext == ".csv":
        schema = schemas.healcsvschema
        fields_propname = "fields"
        cols = []
        vals = {}

        for field in schema["fields"]:
            cols.append(field["name"])
            if field.get("constraints",{}).get("required"):
                val = "[Required]"
            elif re.search("\[Highly Recommended\]",field.get("description",""),
                flags=re.IGNORECASE):
                val = "[Highly Recommended]"
            else:
                val = ""
                
            vals[field["name"]] = numfields * [val]

        template = pd.DataFrame(vals)
        template.to_csv(outputfile,index=False)


