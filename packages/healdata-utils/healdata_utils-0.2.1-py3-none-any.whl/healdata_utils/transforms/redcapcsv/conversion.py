""" 
convert a redcap data dictionary exported
in csv format to a heal-complieant json data dictionary

""" 

import pandas as pd
from . import headers,schema
from .mappings import typemappings 
from healdata_utils import utils
import numpy as np
from ..jsontemplate.conversion import convert_templatejson
from healdata_utils.io import read_delim
#STEPS
#1 fill section headers
#2 sort rows to allow proper row indexing
#3 make conditionals for each map function

def read(file_path):
    """ 
    Reads in a path to a redcap csv file
    and outputs and dictionary with cleaned up header (field) names
    """ 
    sourcedf = (
        read_delim(file_path)
        .fillna("")
        .rename(columns=headers.mapping)
        .applymap(utils.strip_html)
    )

    #downfill section (if blank -- given we read in with petl, blanks are "" but ffill takes in np.nan)
    sourcedf['section'] = sourcedf.replace({"":np.nan}).groupby('form')['section'].ffill()

    sourcedf.fillna("",inplace=True) 

    return sourcedf.to_dict(orient="records")

def gather(sourcefields):
    """ 
    maps and translates fields based on redcap field type
    to heal json
    """ 
    def __add_description(sourcefield,targetfield):

        if sourcefield.get("label"):
            fieldlabel = sourcefield["label"].strip()
        else:
            fieldlabel = ""

        if sourcefield.get("section"):
            fieldsection = sourcefield['section'].strip()+": "
        else:
            fieldsection = ""

        if targetfield.get("description"):
            fielddescription = targetfield["description"].strip()
        else:
            fielddescription = ""
        
        fielddescription = utils.strip_html((fieldsection+fieldlabel+fielddescription).strip())
        if fielddescription:
            return fielddescription
        else:
            return "No field label for this variable"

    def __add_title(sourcefield,targetfield):
        targettitle = targetfield.get("title","")

        if targettitle:
            return targettitle
        elif sourcefield.get("label"):
            return targettitle + utils.strip_html(sourcefield["label"].strip())
        else:
            return "No field label for this variable"
    
    def __add_module(sourcefield,targetfield):
        if sourcefield.get("form"):
            return sourcefield["form"]
    
    def _add_metadata(sourcefield,targetfield):
        targetfield["description"] = __add_description(sourcefield, targetfield)
        targetfield["title"] = __add_title(sourcefield, targetfield)
        targetfield["module"] = __add_module(sourcefield, targetfield)

    sourcedatafields = [field for field in sourcefields 
        if field["type"] in list(typemappings)]

    targetfields = []
    for sourcefield in sourcedatafields:
        sourcefieldtype = sourcefield["type"]
        targetfield = typemappings[sourcefieldtype](sourcefield)
        #NOTE if one sourcefield generates more than 1 target field (ie checkbox) need to iterate through
        #if list (and hence not one to one mapping with sourcefield), assumes mandatory fields
        if isinstance(targetfield,list):
            for _targetfield in targetfield:
                assert 'name' in _targetfield and 'type' in _targetfield
                _add_metadata(sourcefield,_targetfield)
                targetfields.append(_targetfield)
        else:
            _add_metadata(sourcefield,targetfield)
            targetfield_with_name = {'name':sourcefield['name']}
            targetfield_with_name.update(targetfield)
            targetfields.append(targetfield_with_name)

    return targetfields

def convert_redcapcsv(file_path,
    data_dictionary_props={}):
    """ 
    Takes in an exported Redcap Data Dictionary csv,
    and translates each field into a HEAL specified
    data dictionary based on field type (e.g., checkbox, radio, text and 
    other conditional logic based on Redcap specifications.)


    > While there are a variety of options for Redcap exports (eg directly through
    the API or via an XML), the Redcap CSV provides an easy-to-edit format comfortable by 
    technical and non-technical users.

    Parameters
    ----------
    file_path : str or path-like or an object that can be inferred as data by frictionless's Resource class.
        Data or path to data with the data being a tabular HEAL-specified data dictionary.
        This input can be any data object or path-like string excepted by a frictionless Resource object.
    data_dictionary_props : dict
        The HEAL-specified data dictionary properties.

    Returns
    -------
    dict
        A dictionary with two keys:
            - 'templatejson': the HEAL-specified JSON object.
            - 'templatecsv': the HEAL-specified tabular template.
    """ 



    sourcefields = read(file_path)
    targetfields = gather(sourcefields)

    data_dictionary = data_dictionary_props.copy()
    data_dictionary['data_dictionary'] = targetfields

    package = convert_templatejson(data_dictionary)
    return package 

    
    
    