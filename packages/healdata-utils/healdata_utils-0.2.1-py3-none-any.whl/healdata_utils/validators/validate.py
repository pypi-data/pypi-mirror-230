""" utilities to validate data and metadata """ 
import jsonschema
import os
from pathlib import Path
import pandas as pd
import json

from healdata_utils.schemas import healjsonschema,healcsvschema
from healdata_utils.io import read_delim
from healdata_utils.transforms.frictionless.conversion import convert_frictionless_to_jsonschema
from .jsonschema import validate_against_jsonschema
from healdata_utils import utils

class Validator:
    """ 
    input a data object or pointer/path
    to data object with a given schema
    and corresponding type of schema. 
    validate against the said schema of a certain type.
    if the validation schema type is different than the 
    input schema type, will convert to that type (eg jsonschema to
    frictionless.)
    """ 
    @classmethod
    def from_csv_file(cls,path,schema,schema_type):
        data = read_delim(path).to_dict(orient="records")
        return cls(data,schema,schema_type)

    @classmethod
    def from_pandas(cls,data,schema,schema_type):
        data = data.to_dict(orient="records")
        return cls(data,schema,schema_type)
    
    @classmethod 
    def from_jsonarray(cls,data,schema,schema_type):
        jsonschema.validate(data,{"type":"array","items":{"type":"object"}})
        return cls(data,schema,schema_type)

    @classmethod 
    def from_jsonobject(cls,data,schema,schema_type):
        jsonschema.validate(data,{"type":"object"})
        return cls(data,schema,schema_type)
        
    @classmethod
    def from_jsonfile(cls,path,schema,schema_type):
        data = json.loads(Path(path).read_text())
        return cls(data,schema,schema_type)

    def __init__(self,data,schema,schema_type):

        self.data = data #json array
        self.schema = schema
        self.schema_type = schema_type

    def raise_invalid_error(self):
        if not self.report["valid"]:
            raise Exception("These records are not valid")

    def validate(self,against_schema_type):
        if against_schema_type == "jsonschema":
            if self.schema_type == "frictionless":
                schema = convert_frictionless_to_jsonschema(self.schema)
            else:
                schema = self.schema
            report = validate_against_jsonschema(self.data,schema)
        else:
            ## add frictionless 
            ## add pandera -- if needed
            raise NotImplementedError("Still need to implement conversions and validation fxns")

        return {"data":self.data,"schema":schema,"report":report}

def validate_vlmd_json(
    data_or_path,
    schema=healjsonschema,
    input_schema_type="jsonschema",
    validation_schema_type="jsonschema"
    ):
    """
    Validates json data by iterating over every property in every record and comparing to the property 
    specified in the given schema

    Parameters
    ----------
    data_or_path : Path-like object indicating a path to a tabular data source (eg CSV or TSV) or a json array of records (see validate fxn)
    schema : dict, optional
        The schema to compare data_or_path to (default: HEAL frictionless template)

    Returns
    -------
    dict[bool,dict]
        the returned `validate` function object 
    """
    if isinstance(data_or_path, (str, os.PathLike)):
        validator = Validator.from_jsonfile(
            path=data_or_path,
            schema=schema,
            schema_type="jsonschema"
        )
    else:
        validator = Validator.from_jsonobject(
            data=data_or_path,
            schema=schema,
            schema_type="jsonschema"
        )

    package = validator.validate(validation_schema_type)
    report = package["report"]
    # report_summary = []
    errors_list = []
    for error in report["errors"]:
        errors_list.append({"json_path":error["json_path"],
            "message":error["message"]})
        # report_summary.append([error["json_path"],error["message"]])

    package["report"] = {"valid":report["valid"],"errors":errors_list}
    # report_summary_str += "Validation summary for {data_name}"
    # report_summary_str += "\n\n"
    # report_summary_str += "VALID" if report["valid"] else "INVALID"

    # report_summary_str += "## Errors "
    # report_summary_str += "\n\n"

    # report_summary_str+=str(tabulate(
    #     report_summary,
    #     headers=["JsonPath", "Message"],
    #     tablefmt="grid",
    #     maxcolwidths=[5, 5, 90]
    # ))

    # another possible way:
    
    # if not report["valid"]:
    #     print("JSON data dictionary requires modifications:")
    #     console_report = (
    #         pd.DataFrame(data_dictionaries["errors"])
    #         ["jsontemplate"]
    #         ["errors"]
    #         .drop(columns=["json_path"])
    #         .value_counts()
    #     )

    return package
    
def validate_vlmd_csv(
    data_or_path,
    schema=healcsvschema,
    input_schema_type="frictionless",
    validation_schema_type="jsonschema",
    to_sync_fields=True
):
    """
    Validates a json array against the heal variable level metadata
    schema catered for a CSV tabular data dictionary file.

    As there are many options to validate a tabular data file, 
    this function provides options for different different specification
    conversions. The default is to input a frictionless schema and run
    validation with jsonschema library 
    NOTE: (the frictionless v4 tools have some
    issues with pyinstaller currently (haven't tried frictionless v5 though)) 

    Parameters
    ----------
    data_or_path : Path-like object indicating a path to a tabular data source (eg CSV or TSV) or a json array of records (see validate fxn)
    schema : dict, optional
        The schema to compare data_or_path to (default: HEAL frictionless template)
    input_schema_type: str, optional : the type of schema ["jsonschema","frictionless"]
    validation_schema_type: str, optional : the type of schema to use for validation (will convert if input does not eq validation schema types)
    to_sync_fields : bool, optional[default=True]:whether to add missing fields (ie null) in schema before validation. 
        Note, this is different than missing values. Missing values do not equal missing fields (think tabular dataset)
        This also syncs the order of the fields to order of properties in schema.
    Returns
    -------
    dict[bool,dict]
        the returned `validate` function object 
        (eg., `{"valid":False,"errors":[...]}`)
    """

    # instantiate validator object with correct class method depending on input
    if isinstance(data_or_path, (str, os.PathLike)):
        validator = Validator.from_csv_file(path=data_or_path,schema=schema,schema_type=input_schema_type)

    else:
        validator = Validator.from_jsonarray(data=data_or_path,schema=schema,schema_type=input_schema_type)

    # sync fields
    if input_schema_type=="frictionless":
        field_list = [field["name"] for field in schema["fields"]]
    elif input_schema_type=="jsonschema":
        field_list = [fieldname for fieldname in list(schema["items"]["properties"])]
    
    if to_sync_fields:
        validator.data = utils.sync_fields(validator.data, field_list,missing_value="")

    package = validator.validate(validation_schema_type)
    report = package["report"]

    # get most relevant report properties specific to tabular data
    error_list = []
    # report_summary = []
    for error in report["errors"]:
        if error["validator"]=="required":
            row = error["relative_path"][0]
            column = error["validator_value"][-1]
        else:
            row,column = error["relative_path"]

        error_list.append(
            {"row":row,
            "column":column,
            "message":error["message"]}
        )
        # report_summary.append([row,column,error["message"]])

    package["report"] = {"valid":report["valid"],"errors":error_list}

    # report_summary_str += "Validation summary for {data_name}"
    # report_summary_str += "\n\n"
    # report_summary_str += "VALID" if report["valid"] else "INVALID"

    # report_summary_str += "## Errors "
    # report_summary_str += "\n\n"

    # report_summary_str+=str(tabulate(
    #     report_summary,
    #     headers=["Row", "Column", "Message"],
    #     tablefmt="grid",
    #     maxcolwidths=[5, 5, 90]
    # ))



    return package

    

        


