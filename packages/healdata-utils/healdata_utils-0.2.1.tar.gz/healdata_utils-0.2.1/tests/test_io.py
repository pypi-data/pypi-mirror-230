from pathlib import Path
import shutil
import json

from healdata_utils.io import write_vlmd_template,read_excel

from conftest import compare_vlmd_tmp_to_output

def test_write_vlmd_template(fields_propname):



    tmpdir = Path("tmp")

    if tmpdir.exists():
        shutil.rmtree(tmpdir)

    tmpdir.mkdir(exist_ok=True)

    write_vlmd_template(tmpdir.joinpath("heal.json"),numfields=2)
    write_vlmd_template(tmpdir.joinpath("heal.csv"),numfields=2)


    csvoutput = Path("data/templates/twofields.csv").read_text().split("\n")
    jsonoutput = json.loads(Path("data/templates/twofields.json").read_text())

    compare_vlmd_tmp_to_output(tmpdir,csvoutput,jsonoutput,fields_propname)

    shutil.rmtree(tmpdir)


# def test_read_excel():
    
#     excelfile = read_excel("data/misc/multitab-data-dictionary.xlsx")
