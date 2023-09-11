""" General utilities/helper functions"""
import re
from collections.abc import MutableMapping


# individual cell utilities
def strip_html(html_string):
    if html_string:
        return re.sub(r"<[^>]+>", "", html_string)
    else:
        return html_string


def to_int_if_base10(val):
    """
    converts value to a string and if
    float (or a string rep of a float) of base10
    to an integer string representation.

    NOTE:
    """
    string = str(val)

    if "." in string:
        parts = string.split(".")
        if len(parts) == 2 and parts[1] == "0":
            return parts[0]

    return string


def parse_dictionary_str(string, item_sep, keyval_sep):
    """
    parses a stringified dictionary into a dictionary
    based on item separator

    """
    stritems = string.strip().split(item_sep)
    items = {}
    for stritem in stritems:
        item = stritem.split(keyval_sep, 1)
        items[item[0]] = item[1].strip()

    return items


def parse_list_str(string, list_sep):
    return string.strip().split(list_sep)


# dictionary utilities
def flatten_except_if(dictionary, parent_key=False, sep=".", except_keys=["encodings"]):
    """
    Turn a nested dictionary into a flattened dictionary. Taken from gen3
    mds.agg_mds.adapter.flatten
    but added except keys and fixed a bug where parent is always False in MutableMapping

    :param dictionary: The dictionary to flatten
    :param parent_key: The string to prepend to dictionary's keys
    :param sep: The string used to separate flattened keys
    :param except_keys: keys to not flatten. Note, can be nested if using notation specified in sep
    :return: A flattened dictionary
    """

    items = []
    for key, value in dictionary.items():
        new_key = str(parent_key) + sep + key if parent_key else key
        if isinstance(value, MutableMapping) and not new_key in except_keys:
            items.extend(flatten_except_if(value, new_key, sep).items())
        else:
            items.append((new_key, value))
    return dict(items)

def stringify_keys(dictionary):
    orig_keys = list(dictionary.keys())
    for key in orig_keys:
        dictionary[str(key)] = dictionary.pop(key)

def convert_rec_to_json(field):
    """
    converts a flattened dictionary to a nested dictionary
    based on JSON path dot notation indicating nesting
    """
    field_json = {}
    for prop_path, prop in field.items():
        if str(prop) and str(prop) != "<NA>" and str(prop) != "nan":
            # initiate the prop to be added with the entire
            # field
            prop_json = field_json
            # get the inner most dictionary item of the jsonpath
            nested_names = prop_path.split(".")
            for i, prop_name in enumerate(nested_names):
                is_last_nested = i + 1 == len(nested_names)
                if prop_json.get(prop_name) and not is_last_nested:
                    prop_json = prop_json[prop_name]
                # if no object currently
                elif not is_last_nested:
                    prop_json[prop_name] = {}
                    prop_json = prop_json[prop_name]
                # assign property to inner most item
                else:
                    prop_json[prop_name] = prop

    return field_json


# documentation building utilities
def find_docstring_desc(fxn):
    """
    return the description part of a docstring
    (ie text before Parameters)
    """
    exp = "^(.*)Parameters\\n"

    if fxn.__doc__:
        docstring = fxn.__doc__.strip()
    else:
        docstring = "No documentation"
    try:
        return re.search(exp, docstring, re.DOTALL).group(1)
    except AttributeError:
        return docstring


# add missing values and order according to the order of a list


def sync_fields(data, field_list,missing_value=None):
    """
    Sorts fields and adds missing fields (with None value).
    If extra fields exist in a record that are not in field_list, then tacks on at 
    end of record.


    Parameters
    --------------
    data [list]: json array of values
    fields [list]: the list of all fields (e.g., from a schema)

    Returns
    -------------
    list: json array with fields added if missing
    """
    data_with_missing = []

    for record in data:
        extra_fields = list(set(list(record)).difference(field_list))
        new_record = {field:record.get(field, missing_value) 
            for field in field_list+extra_fields}
        data_with_missing.append(new_record)

    
    return data_with_missing