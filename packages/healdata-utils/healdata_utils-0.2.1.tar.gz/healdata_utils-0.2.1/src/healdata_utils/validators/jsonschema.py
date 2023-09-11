""" 
validation of json records against a jsonschema specification 
and conversion of one schema spec to jsonschema specification 
eg frictionless --> jsonschema

""" 

import jsonschema

def validate_against_jsonschema(json_object,schema):
    
    Validator = jsonschema.validators.validator_for(schema)
    validator = Validator(schema)
    report = []
    is_valid = True
    for error in validator.iter_errors(json_object):
        is_valid = False
        error_report = {
            "json_path":error.json_path,
            "message":error.message,
            "absolute_path":list(error.path),
            "relative_path":list(error.relative_path),
            "validator":error.validator,
            "validator_value":error.validator_value
        }
        report.append(error_report)

    return {"valid":is_valid,"errors":report}