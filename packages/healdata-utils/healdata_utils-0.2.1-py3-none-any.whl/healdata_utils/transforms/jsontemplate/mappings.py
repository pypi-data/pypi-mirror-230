
# join mappings for json to csv

def join_iter(iterable,sep_list="|"):
    return sep_list.join([str(p) for p in iterable])

def join_dictvals(dictionary:dict,sep:str):
    return sep.join(dictionary.values())

def join_dictitems(dictionary:dict,sep_keyval='=',sep_items='|'):
    """ joins a mappable collection (ie dictionary) into a string
    representation with specified separators for the key and value
    in addition to items. 

    All items are coerced to the string representation (eg if key or value
    is None, this will be coerced to "None")
    """
    dict_list = []
    for key,val in dictionary.items():
        keystr = str(key)
        valstr = str(val)
        dict_list.append(keystr+sep_keyval+valstr)
    return sep_items.join(dict_list)


joinmap = {
    'constraints.enum': join_iter,
    'cde_id': join_dictvals,
    'ontology_id': join_dictvals,
    'encodings': join_dictitems,
    'missingValues':join_iter,
    'trueValues': join_iter,
    'falseValues':join_iter,
    # TODO: add stats
}

def join_prop(propname,prop):
    return joinmap[propname](prop) if propname in joinmap else prop