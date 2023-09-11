""" 

command line interface for generating HEAL data dictionary/vlmd json files

"""
import json
from pathlib import Path
import petl as etl
import pandas as pd
import csv
from collections import deque
import click
from slugify import slugify

from healdata_utils.transforms.excel.conversion import convert_dataexcel
from healdata_utils.transforms.csvtemplate.conversion import convert_templatecsv
from healdata_utils.transforms.jsontemplate.conversion import convert_templatejson

from healdata_utils.transforms.stata.conversion import convert_stata
from healdata_utils.transforms.spss.conversion import convert_spss
from healdata_utils.transforms.sas.conversion import convert_sas
from healdata_utils.transforms.redcapcsv.conversion import convert_redcapcsv
from healdata_utils.transforms.csvdata.conversion import convert_datacsv
from healdata_utils.transforms.frictionless.conversion import (
    convert_frictionless_tableschema,
)

from healdata_utils.validators.validate import validate_vlmd_json, validate_vlmd_csv
from healdata_utils.utils import find_docstring_desc

choice_fxn = {
    "excel-data":convert_dataexcel,
    "csv-data": convert_datacsv,
    #'csv-data-dict':convert_datadictcsv,
    #'csv-template':convert_templatecsv,
    "spss": convert_spss,
    "stata": convert_stata,
    #'por':convert_readstat,
    "sas": convert_sas,
    #'json-template':convert_templatejson,
    "redcap": convert_redcapcsv,
    "frictionless": convert_frictionless_tableschema,
}

# input_types = " - " + "\n - ".join(list(choice_fxn.keys()))

# input_descriptions = {
#     name: find_docstring_desc(fxn) for name, fxn in choice_fxn.items()
# }

input_short_descriptions = {
    "excel-data":"Data (not metadata) in an excel (xlsx) workbook. Extracts one data dictionary per sheet by default. Runs same inference as csv-data",
    "csv-data":"Data (not metadata) in a csv (or tsv) file.",
    "spss":"A .sav file with data values,variable labels, and value labels.",
    "stata":"A .dta file with data values,variable labels, and value labels.",
    "sas":"A .sas7bdat file with data values and variable labels. Detects format (sas7bcat catalog files) in the same directory.",
    "redcap":"A standardized REDCap csv data dictionary export file.",
    "frictionless":"A frictionless table schema in json format."
}


def _write_vlmd(
    jsontemplate,
    csvtemplate,
    csvreport,
    jsonreport,
    output_filepath="heal-vlmd",
    output_overwrite=False,
    output_csv_quoting=None,
):
    # NOTE: currently the default is to auto generate file name if output_filepath not specified

    # flipped wording around for vars to avoid issues with previous flipping
    templatejson = jsontemplate
    templatecsv = csvtemplate
    reportjson = jsonreport
    reportcsv = csvreport


    output_filepath = Path(output_filepath)

    jsontemplate_path = output_filepath.with_suffix(".json")
    csvtemplate_path = output_filepath.with_suffix(".csv")

    # CHECK existence of directory and output files
    dir_exists = output_filepath.parent.exists()
    json_exists = jsontemplate_path.exists()
    csv_exists = csvtemplate_path.exists()

    if not dir_exists:
        raise NotADirectoryError(
            f"{str(output_filepath.parent)} does not exist so cannot create {output_filepath.name}"
        )

    if not output_overwrite:
        if json_exists and csv_exists:
            raise FileExistsError(
                f"{str(jsontemplate_path)}\nand\n{str(csvtemplate_path)}\nexist."
            )
        elif json_exists:
            raise FileExistsError(f"{str(jsontemplate_path)} exists.")
        elif csv_exists:
            raise FileExistsError(f"{str(csvtemplate_path)} exists.")


    if not reportcsv["valid"] or not reportjson["valid"]:
        reportdir = output_filepath.parent/"reports"
        reportdir.mkdir(exist_ok=True)

    # print JSON data dictionary and report
    jsontemplate_path.write_text(json.dumps(templatejson, indent=4))
    print()
    print(f"JSON data dictionary file written to {str(jsontemplate_path.resolve())}")

    if not reportjson["valid"]:
        reportjson_path = reportdir.joinpath("json-"+output_filepath.with_suffix(".json").name)
        reportjson_path.write_text(
            json.dumps(reportjson, indent=4)
        )
        print(f"but requires additional annotation and/or modifications.")
        print(f"View the report at: {str(reportjson_path.resolve())}")
        print()
    else:
        print()
    
    
    # print CSV data dictionary and report
    quoting = csv.QUOTE_NONNUMERIC if output_csv_quoting else csv.QUOTE_MINIMAL
    # NOTE: quoting non-numeric to allow special characters for nested delimiters within string columns (ie "=")
    # (
    #     etl.fromdicts(templatecsv)
    #     .tocsv(
    #         csvtemplate_path,
    #         quoting=csv.QUOTE_NONNUMERIC if output_csv_quoting else csv.QUOTE_MINIMAL)

    # )
    pd.DataFrame(templatecsv).to_csv(csvtemplate_path, quoting=quoting, index=False)
    print()
    print(f"CSV data dictionary file written to {str(csvtemplate_path.resolve())}")

    if not reportcsv["valid"]:
        reportcsv_path = reportdir.joinpath("csv-"+output_filepath.with_suffix(".json").name)
        reportcsv_path.write_text(
            json.dumps(reportcsv, indent=4)
        )
        print(f"but requires additional annotation and/or modifications.")
        print(f"View the report at: {str(reportcsv_path.resolve())}")
        print()
    else:
        print()



def convert_to_vlmd(
    input_filepath,
    data_dictionary_props=None,
    inputtype=None,
    output_filepath=None,
    output_csv_quoting=None,
    output_overwrite=False,
    **kwargs,
):
    """
    Writes a data dictionary (i.e. variable level metadata) to a HEAL metadata JSON file using a registered function.

    Parameters
    ----------
    input_filepath : str
        Path to input file. See documentation on individual input types for more details.
    inputtype : str, optional
        The input type. If none specified, will default to using the file extension.
        See the currently registered input types in the input_types list.
    data_dictionary_props : dict, optional
        The other data-dictionary level properties. By default, will give the data_dictionary `title` property as the file name stem.
    output_filepath : str
        output file path or directory to where output will go. Note, the extension specified (csv or json will change as necessary)
    output_csv_quoting: bool, optional
        If true, all nonnumeric values will be quoted. This helps reduce ambiguity for programs
        like excel that uses special characters for specific purposes (eg = for formulas)
    
    **kwargs: keyword arguments for specific registered input types
        currently this includes sas catalog file for sas and sheet_names/other params for excel.

    Returns
    -------
    dict
        Dictionary with:
         1. csvtemplated array of fields.
         2. jsontemplated data dictionary object as specified by an originally drafted design doc.
            That is, a dictionary with title:<title>,description:<description>,data_dictionary:<fields>
            where data dictionary is an array of fields as specified by the JSON schema.
         3. error objects for corresponding validators (ie frictionless for csv and jsonschema for json)
    NOTE
    ----
    In future versions, this will be more of a package bundled with corresponding schemas (whether csv or JSON),better organization
    (e.g., see frictionless Package).
    However, right now, it simply returns the csvtemplate and jsontemplate as specified
    in the heal specification repository.
    This is an intermediate solution to socialize a proof-of-concept.


    TODO
    --------

    Convert this to object-oriented framework -- 
    this may be best done for entire package (eg individual types as well)?

    This will require substantial overhaul to framework so this is not included in v.1 milestone.
    E.g., individual field types as objects, individual formats as objects
    
    Separate write and dd extraction -- this should be included in the OO revision above
    """

    input_filepath = Path(input_filepath)

    # infer input type
    if not inputtype:
        ext = "".join(input_filepath.suffixes)[1:].lower()
        inputtype = ext_to_inputtype.get(ext)
        if not inputtype:
            raise Exception(
                f"No inputtype specified as file of type {ext} does not have a registered inputtype"
            )

    if not data_dictionary_props:
        data_dictionary_props = {}
        
    # ## add dd title
    # if not data_dictionary_props.get("title"):
    #     data_dictionary_props["title"] = input_filepath.stem

    # get data dictionary package based on the input type
    data_dictionary_package = choice_fxn[inputtype](
        input_filepath, data_dictionary_props,**kwargs
    )

    # with the need for multiple data dictionaries 
    # (eg within a package-like file resource such as excel or another archive format)
    # need to allow multiple data dictionaries. This was achieved by using the 
    # format similar to platform aggregate metadataservice disicovery page for 
    # data dictionaries: <key as name of dict>: ref to dictionary (or in this case - the actual data dictionary)
    # TODO: better way to identify one package of dds vs. multiple dds (as technically, templatejson/templatecsv could be keys in multiple dds)
    if "templatecsv" in data_dictionary_package and "templatejson" in data_dictionary_package:
        packages = {"":data_dictionary_package}
        onepackage = True
    else:
        packages = data_dictionary_package
        onepackage = False

    packages_with_reports = {}
    for name,package in packages.items():
        # TODO: json validate root AND fields while csv currently only validates fields (ie table) but no reason it cant validate entire data package
        package_csv = validate_vlmd_csv(
            package["templatecsv"]["data_dictionary"], to_sync_fields=True
        )
        package_json = validate_vlmd_json(package["templatejson"])

        # TODO: in future just return the packages (eg reports nested within package and not out of)
        # for now, keep same (report_xxx and templatexxx)

        reportcsv = package_csv["report"]
        reportjson = package_json["report"]
        dd_csv = package_csv["data"]
        dd_json = package_json["data"]


        if onepackage:

            packages_with_reports.update({
            "csvtemplate": dd_csv,
            "jsontemplate": dd_json,
            "errors": {"csvtemplate": reportcsv, "jsontemplate": reportjson},
            })

            output_filepath_with_name = output_filepath

        else:

            packages_with_reports[name] = {
                "csvtemplate": dd_csv,
                "jsontemplate": dd_json,
                "errors": {"csvtemplate": reportcsv, "jsontemplate": reportjson},
            }

            # 
            stem = Path(output_filepath).stem
            ext = Path(output_filepath).suffix
            output_filepath_with_name = Path(output_filepath).parent/(stem+"-"+slugify(name)+ext)

        _write_vlmd(
            jsontemplate=dd_json,
            csvtemplate=dd_csv,
            csvreport=reportcsv,
            jsonreport=reportjson,
            output_filepath=output_filepath_with_name,
            output_overwrite=output_overwrite
        )

                
    return packages_with_reports


