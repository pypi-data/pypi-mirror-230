""" 
Functions for each redcap field type
that uses redcap field info to determine
various pieces of field metadata.

Input assumes a dictionary with key=redcap fieldname;value=redcap value
""" 
import re
from healdata_utils import utils
from .headers import choices_fieldname,slider_fieldname,calc_fieldname,text_valid_fieldname 
# NOTES	- large text box for lots of text
# DROPDOWN	- dropdown menu with options
# RADIO	- radio buttons with options
# CHECKBOX	- checkboxes to allow selection of more than one option
# FILE	- upload a document
# CALC	- perform real-time calculations
# SQL	- select query statement to populate dropdown choices
# DESCRIPTIVE	- text displayed with no data entry and optional image/file attachment
# SLIDER	- visual analogue scale; coded as 0-100
# YESNO	- radio buttons with yes and no options; coded as 1, Yes | 0, No
# TRUEFALSE	- radio buttons with true and false options; coded as 1, True | 0, False

def _parse_field_properties_from_encodings(
    encodings_string
    ):  
    """ 
    Many of the field types have the same logic
    for conversion to data types and just differ
    in presentation (dropbox,radio box) so making
    fxn to support this

    Currently supports strings,ints,and nums for types

    NOTE: this function may be best housed in the general 
    utils but keeping local for now and specific to 
    redcap delimiters
    """ 
    # parse encodings
    fieldencodings = utils.parse_dictionary_str(
        encodings_string, item_sep="|", keyval_sep=",")
    # get enums
    fieldenums = list(fieldencodings.keys())
    #interpret type from enums
    for val in fieldenums:
        val = val.strip()
        if val.isnumeric():
            try:
                int(val)
                fieldtype = "integer"
            except ValueError:
                fieldtype = "number"
        else:
            fieldtype = "string"
    
    return {
        "type":fieldtype,
        "encodings":{key.strip():val.strip() for key,val in fieldencodings.items()},
        "constraints":{
            "enum":[val.strip() for val in fieldenums]
        }
    }

def maptext(field):
    """ 
    TEXT - single-line text box (for text and numbers)

    looks at text validation field
    """
    if field.get(text_valid_fieldname):
        text_validation = field[text_valid_fieldname].lower()
    else:
        text_validation = ""
    fieldformat = None 
    fieldpattern = None
    if "datetime" in text_validation:
        fieldtype = "datetime"
        fieldformat = "any"
    elif "date" in text_validation:
        fieldtype = "date"
        fieldformat = "any" 
    elif text_validation=="email":
        fieldtype = "string"
        fieldformat = "email"
    elif text_validation=="integer":
        fieldtype = "integer"
    elif text_validation=="alpha_only":
        fieldtype = "string"
        fieldpattern = "^[a-zA-Z]+$"
    elif "number" in text_validation:
        fieldtype = "number"
        if "comma_decimal" in text_validation:
            fielddecimal_char = ","
    elif text_validation=="phone":
        fieldtype = "string"
        fieldpattern = "^[0-9]{3}-[0-9]{3}-[0-9]{4}$" 
    elif text_validation=="postalcode_australia":
        fieldtype = "string"
        fieldpattern = "^[0-9]{4}$"
    elif text_validation=="postalcode_canada":
        fieldtype = "string"
        fieldpattern = "^[A-Z][0-9][A-Z] [0-9][A-Z][0-9]$"
    elif text_validation=="ssn":
        fieldtype = "string"
        fieldpattern = "^[0-9]{3}-[0-9]{2}-[0-9]{4}$"
    elif "time" in text_validation:
        fieldtype = "time"
        fieldformat = "any"
    elif text_validation=="vmrn":
        fieldtype = "string"
        fieldpattern = "^[0-9]{10}$"
    elif text_validation=="zipcode":
        fieldtype = "string"
        fieldpattern = "^[0-9]{5}$"
    else:
        fieldtype = "string"
    
    props = dict(zip(
        ["type","format","constraints"],
        [fieldtype,fieldformat,{"pattern":fieldpattern}]
    ))

    # delete props without values (ie None)
    for propname in ["type","format"]:
        if props[propname]==None:
            del props[propname]
    if props["constraints"]["pattern"]==None:
        del props["constraints"]

    return props
def mapnotes(field):
    """ NOTES	
    large text box for lots of text
    """
    return {"type":"string"}

def mapdropdown(field):
    """ 
    DROPDOWN	
    dropdown menu with options

    Determined by "options" (ie Choices, Calculations, OR Slider Labels)
    """
    encodings_string = field[choices_fieldname]
    return _parse_field_properties_from_encodings(encodings_string)

def mapradio(field):
    """ 
    RADIO	- radio buttons with options

    Determined by "options" (ie Choices, Calculations, OR Slider Labels)

    """
    # parse enum/encodings 
    encodings_string = field[choices_fieldname]
    return _parse_field_properties_from_encodings(encodings_string)


def mapcheckbox(field):
    """ 
    CHECKBOX	- checkboxes to allow selection of more than one option


    ## Are data from checkbox (choose all that apply) field types handled differently from other field types when imported or exported?
    Yes. When your data are exported, each option from a checkbox field becomes a separate variable coded 1 or 0 to reflect whether it is checked or unchecked. By default, each option is pre-coded 0, so even if you have not yet collected any data, you will see 0's for each checkbox option. The variable names will be the name of the field followed by the option number. So, for example, if you have a field coded as follows:

    Race

    1, Caucasian

    2, African American

    3, Asian

    4, Other

    In your exported dataset, you will have four variables representing the field Race that will be set as 0 by default, coded 1 if the option was checked for a record. The variable names will consist of the field name. three underscores, and the choice value:

    race___1
    race___2
    race___3
    race___4

    Notes:

    when you import data into a checkbox field, you must code it based on the same model
    negative values can be used as the raw coded values for checkbox fields. Due to certain limitations, negative values will not work when importing values using the Data Import Tool, API and cause problems when exporting data into a statistical analysis package. The workaround is that negative signs are replaced by an underscore in the export/import-specific version of the variable name (e.g., for a checkbox named "race", its choices "2" and "-2" would export as the fields
    race___2

    race____2

    A checkbox field can be thought of as a series of yes/no questions in one field. Therefore, a yes (check) is coded as 1 and a no (uncheck) is coded a 0. An unchecked response on a checkbox field is still regarded as an answer and is not considered missing.
    """
    checkboxname = field['name']
    choices = utils.parse_dictionary_str(
        field[choices_fieldname], item_sep="|", keyval_sep=",")
    fieldtype = "boolean"
    fieldenums = ["0","1"]
    fieldencodings = {"0":"Unchecked","1":"Checked"}

    fieldsnew = [
        {
            "description":f"[choice={choice}]",
            "title": checkboxname.title()+": "+choice,
            "name":checkboxname+"___"+re.sub("^\-","_",val).strip(), #NOTE: REDCAP changes negative sign to underscore
            "type":fieldtype,
            "constraints":{"enum":fieldenums},
            "encodings":fieldencodings
        }
        for val,choice in choices.items()
    ]
    return fieldsnew

def mapfile(field):
    return {"type":"string"}


def mapcalc(field):
    return {
        "description":f"[calculation: {field[calc_fieldname]}]",
        "type": "number"
    }


def mapsql(field):
    return None


def mapyesno(field):
    return {
        "type":"boolean",
        "constraints":{"enum":["0","1"]},
        "encodings":{"0":"No","1":"Yes"}
    }


def maptruefalse(field):
    return {
        "type":"boolean",
        "constraints":{"enum":["0","1"]},
        "encodings":{"0":"False","1":"True"}
    }


def mapslider(field):
    vallist = ["0","50","100"]
    lbllist = utils.parse_list_str(field[slider_fieldname],"|") 
    fieldencodings = {vallist[i]:lbl for i,lbl in enumerate(lbllist)}
    return {
        "type":"integer",
        "constraints":{
            "minimum":0,
            "maximum":100
        },
        "encodings":fieldencodings
    }
def mapdescriptive(field):
    return None


#not mapping descriptives or sql (TODO: mapping sql?)
typemappings = {
    "text":maptext,
    "notes":mapnotes,
    "dropdown":mapdropdown,
    "radio":mapradio,
    "checkbox":mapcheckbox,
    "slider":mapslider,
    "yesno":mapyesno,
    "truefalse":maptruefalse,
    "calc":mapcalc,
    "file":mapfile
}


