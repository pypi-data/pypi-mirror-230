""" convert various frictionless objects to
another format """
from healdata_utils.transforms.jsontemplate.conversion import convert_templatejson
import os 
import yaml
import json
from pathlib import Path

def convert_frictionless_tableschema(
    schema,
    data_dictionary_props:dict=None,
    **kwargs
):
    if isinstance(schema,(os.PathLike,str)):
        if Path(schema).suffixes[-1]==".yaml": #NOTE: not tested
            schemajson = yaml.safe_load(Path(schema).read_text())
        else:
            schemajson = json.loads(Path(schema).read_text())
    else:
        schemajson = schema
    data_dictionaries = convert_templatejson(
        schemajson,
        data_dictionary_props,
        fields_name="fields",
        **kwargs
    )
    return data_dictionaries


def convert_frictionless_to_jsonschema(frictionless_schema):
    """ converts a frictionless schema to jsonschema """
    
    frictionless_fields = list(frictionless_schema.get("fields"))
    assert frictionless_fields,"A frictionless schema MUST have a set of fields"


    # schema level properties

    # frictionless
    missing_values = frictionless_schema.get("missingValues",[None,""])
    primary_keys = frictionless_schema.get("primaryKeys",[])

    # frictionless --> jsonschema per field
    jsonschema_properties = {}
    fieldnames = []
    for field in frictionless_fields:
        fieldnames.append(field["name"])
        jsonschema_properties[field["name"]] = prop = {}

        #base props
        if "description" in field:
            prop["description"] = field["description"]
        if "title" in field:
            prop["title"] = field["title"]
        if "example" in field:
            prop["example"] = field["example"]
        if "type" in field:
            if field["type"]!="any":
                prop["type"] = field["type"]
        
        

        # constraints
        constraints = field.get("constraints",{})
        if "enum" in constraints:
            type_mappings = {
                "integer":int,
                "number":float,
                "string":str
            }
            prop["enum"] = []
            for val in constraints["enum"]:
                if field.get("type","") in type_mappings:
                    coerced_val = type_mappings[field["type"]](val)
                    prop["enum"].append(coerced_val)
                else:
                    prop["enum"].append(val)


        if "pattern" in constraints:
            prop["pattern"] = constraints["pattern"] 

        if "minimum" in constraints:
            prop["minimum"] = constraints["minimum"]

        if "maximum" in constraints:
            prop["maximum"] = constraints["maximum"]


        # all fields are required - missing-ness vs. required in tabular perspective is tacked on to property
        is_required = "required" in constraints or field["name"] in primary_keys

        if is_required:
            # if required value: MUST be NOT missing value and the property
            prop_accounting_for_missing = {
                "allOf":[
                    prop,{"not": {"enum":missing_values}}
                ]
            }
        else:
            # if not required value: MUST be property OR the specified missing value
            prop_accounting_for_missing = {
                "anyOf":[
                    prop,{"enum":missing_values}
            ]}
        
        jsonschema_properties[field["name"]] = prop_accounting_for_missing
            

    
    jsonschema_schema = {
        "type":"object",
        "required":fieldnames, 
        "properties":jsonschema_properties
    }

    schema = frictionless_schema
    for jsonprop in ["description","title","name"]:
        if schema.get(jsonprop):
            jsonschema_schema[jsonprop] = schema[jsonprop]

    return {"type":"array","items":jsonschema_schema}