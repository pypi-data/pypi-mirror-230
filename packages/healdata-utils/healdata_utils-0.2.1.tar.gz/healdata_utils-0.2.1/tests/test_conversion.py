import shutil
from pathlib import Path
from healdata_utils.conversion import convert_to_vlmd,input_short_descriptions,choice_fxn
import json

from conftest import compare_vlmd_tmp_to_output

def test_convert_to_vlmd_with_registered_formats(
    valid_input_params,valid_output_json,valid_output_csv,fields_propname):
    inputtypes = list(valid_input_params.keys())
    outputdir="tmp"

    for inputtype in inputtypes:
   
        # make an empty temporary output directory
        try:
            Path(outputdir).mkdir()
        except FileExistsError:
            shutil.rmtree(outputdir)
            Path(outputdir).mkdir()

        
        _valid_input_params = valid_input_params[inputtype]
        data_dictionaries = convert_to_vlmd(**_valid_input_params)

        outdir = _valid_input_params["output_filepath"].parent
        
        # currently json and csv are produced automatically
        # so should be both a csv and json file (at least 2 files)
        # more than 2 happens in cases of package-like dds formed such as with excel
        if len(list(outdir.glob("*.json"))) > 1 and len(list(outdir.glob("*.csv"))) > 1: 
            for name in data_dictionaries:
                _valid_output_json = json.loads(valid_output_json[inputtype][name].read_text())
                _valid_output_csv = valid_output_csv[inputtype][name].read_text().split("\n")
                compare_vlmd_tmp_to_output(
                    tmpdir=outdir,
                    stemsuffix=name, #stem suffix to detect the csv and json files
                    csvoutput=_valid_output_csv,
                    jsonoutput=_valid_output_json,
                    fields_propname=fields_propname
                )
        else:
            _valid_output_json = json.loads(valid_output_json[inputtype].read_text())
            _valid_output_csv = valid_output_csv[inputtype].read_text().split("\n")
            #no stemsuffix 
            compare_vlmd_tmp_to_output(
                tmpdir=outdir,
                csvoutput=_valid_output_csv,
                jsonoutput=_valid_output_json,
                fields_propname=fields_propname
            )


        # clean up
        shutil.rmtree(outputdir)

def test_short_descriptions():
    
    assert input_short_descriptions.keys() == choice_fxn.keys()