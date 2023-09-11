''' 

command line interface for generating HEAL data dictionary/vlmd json files

''' 

import click 
import json
from pathlib import Path
import petl as etl
import pandas as pd
import csv
from collections import deque

from healdata_utils.utils import find_docstring_desc
from healdata_utils.conversion import convert_to_vlmd,choice_fxn,input_short_descriptions
from healdata_utils.validators import validate_vlmd_json,validate_vlmd_csv
from healdata_utils.io import write_vlmd_template
from healdata_utils.config import VLMD_DEFS_URL

prompt_file = f"""
{click.style("Enter the path to your file:",bold=True,fg="green")}

This can be an:
1. absolute path (e.g., C:/Users/lastname-firstname/projectfolder/data/filename.csv)
2. relative path (e.g., data/filename.csv)
3. filename (e.g., filename.csv)

"""

inputtype_descs = "\n".join([click.style(name,bold=True)+": "+desc for name,desc in input_short_descriptions.items()])
prompt_extract_inputtypes = f"""
{click.style("What type of file do you want to extract variable level metadata from?",bold=True,fg="green")}

{inputtype_descs}

"""

prompt_template_nfields = f"""
{click.style("How many variables (ie fields) are in your data (ie are going to be in your data dictionary)?",bold=True,fg="green")}

""" 

prompt_template_outputfile = f"""

{click.style("What do you want the output file called?",bold=True,fg="green")}

This can be an:
1. absolute path (e.g., C:/Users/lastname-firstname/projectfolder/heal-data-dictionary.csv)
2. relative path (e.g., heal-data-dictionary.csv)
3. filename (e.g., heal-data-dictionary.csv)

Note, if you specify a csv file, this will generate a HEAL csv templated file and if you specify a json file, this
will generate a HEAL json templated file.

""" 
prompt_extract_outputfile = f""" 

{click.style("What do you want the output file called?",bold=True,fg="green")}

Note, both a json and csv versions will be created.

"""

prompt_overwrite = f"""

{click.style("Do you want to overwrite the specified output files (if they exist)?",bold=True,fg="green")}

"""

def _check_suffix_for_json_or_csv(ctx,param,value):
    fileexts = [".json",".csv"]
    if not Path(value).suffix in fileexts:
        click.secho(f"File must be {' or '.join(fileexts)}",fg="red")
        click.pause(click.style("Press any key to exit program and try again"))
        ctx.exit()


def _check_overwrite(ctx,param,value):

    """ 
    Takes the specified file/outputfile argument 
    if the file exists, prompts user if they want to overwrite.

    Then, if the user has specified no on overwrite, the command 
    will abort. 


    # if no output file, then pass through (as not applicable)
    # if overwrite specified pass through (true)
    # if overwrite not specified (false), check existence and prompt user if they want to overwrite,
    #  if files don't exist, pass through (false)

    NOTE
    ----- 
    Note, both the csv and json files are checked for existence. 
    Reasoning for checking both csv and json is to ensure they are "synced" and
    currently the convert_to_vlmd fxn outputs both csv and json by default

    """
    
    filepath = ctx.params.get("outputfile")


    if not filepath or value:
        return value

    filepath_csv = Path(filepath).with_suffix(".csv")
    filepath_json = Path(filepath).with_suffix(".json")

    if filepath_json.exists() or filepath_csv.exists():

        # Write to console the existence of csv and json files
        # with specified stem
        if filepath_csv.exists():
            click.secho(f"Warning: {filepath_csv} exists",fg="red")

        if filepath_json.exists():
            click.secho(f"Warning: {filepath_json} exists",fg="red")  

        click.secho(f"Given you do not want to overwrite files and files exist, exiting tool.",fg="red")
        click.pause(click.style("Press any key to exit program and try again"))
        ctx.exit()
    
    return value        
                        


@click.group(invoke_without_command=True)
@click.pass_context
def vlmd(ctx):

    if ctx.invoked_subcommand is None:
        subcmds = []
        

        info = ctx.command.to_info_dict(ctx)["commands"]
        prompt_subcmds = f"{click.style('START BY TYPING ONE OF THE THREE COMMANDS:',underline=True)}\n\n"
        for subcmd_name,subcmd_info in info.items():

            subcmds.append(subcmd_name)
            subcmd_help = f"{click.style(subcmd_name,bold=True)}: "
            subcmd_help += f'{subcmd_info["help"]+":" if subcmd_info["help"] else ""}\n'
            prompt_subcmds += subcmd_help + "\n"

        subcmd = click.prompt(
            text=prompt_subcmds,
            type=click.Choice(subcmds)
        )
        # Determine if subcmd has an argument(s)
        has_args = False
        for p in ctx.command.commands[subcmd].params:
            if type(p) is click.core.Argument:
                has_args = True

        # NOTE: prompt for argument here (as prompts only for options)
        if has_args:
            filepath = click.prompt(
                text=prompt_file,
                type=click.Path()
            )
            # invoke subcommand chosen with "all bells and whistles"
            #NOTE: for Command.main method:
            # https://github.com/pallets/click/blob/b63ace28d50b53e74b5260f6cb357ccfe5560133/src/click/core.py#L1255
            ctx.command.commands[subcmd].main(args=[filepath])
        else:
            ctx.command.commands[subcmd].main()
            

# @vlmd.command(help="Lookup the definition and examples for a given field within a given data dictionary format or for both")
# @vlmd.option("--format",
#     default="both",
#     type=click.Choice(["csv","json","both"]),
#     help="Format to look up",
#     prompt="Which format do you want to look up?")
# @vlmd.option("--name",default="description",
# def lookup():
#     pass 

@vlmd.command(help="Extract the variable level metadata from an existing file with a specific type/format")
@click.argument("inputfile",type=click.Path(exists=True))
#TODO: --output-file or --output-filepath?
@click.option('--inputtype',type=click.Choice(list(choice_fxn.keys())),prompt=prompt_extract_inputtypes)
@click.option('--outputfile',
    default="heal-dd",
    prompt=prompt_extract_outputfile)
@click.option('--overwrite',default=False,is_flag=True,callback=_check_overwrite,
    help="If true, will replace (overwrite) the existing file if it exists. If false (the default) and there is a file of same name, will prompt user if they want to overwrite.")
@click.option(
    "--prop",
    "data_dictionary_props",
    multiple=True,nargs=2,
    help="<name of root level data dictionary property> <value of the specified property>. For example, title 'This is my title' Remember quotes if spaces!"
)
def extract(inputfile,outputfile,inputtype,overwrite,data_dictionary_props):

    data_dictionary_props = dict(data_dictionary_props)

   # data_dictionary_props = {}
    #save dds and error reports to files
    #NOTE: ported the sas catalog inference to core function
    data_dictionaries = convert_to_vlmd(
        input_filepath=inputfile,
        #data_dictionary_props=data_dictionary_props,
        output_filepath=outputfile,
        inputtype=inputtype,
        output_overwrite=overwrite,
        data_dictionary_props=data_dictionary_props
    )


@vlmd.command(help="Check (validate) an existing HEAL data dictionary file to see if it follows the HEAL specifications.")
@click.argument("inputfile",type=click.Path(exists=True))
@click.option('--outputfile',help="Write the report to a file. By default, the report will be printed directly to the console.")
@click.option('--overwrite',default=False,is_flag=True,callback=_check_overwrite)
def validate(inputfile,outputfile,overwrite):

    ext = Path(inputfile).suffix.replace(".","")

    if ext == "csv":
        package = validate_vlmd_csv(inputfile, to_sync_fields=True)
        report = package["report"]
    elif ext == "json":
        package = validate_vlmd_json(inputfile)
        report = package["report"]
    else:
        raise Exception("Need to specify either a csv or json file")

    if outputfile:
        Path(outputfile).write_text(
            json.dumps(report, indent=4)
        )
    else:
        #TODO: color code; more informative errors
        click.secho(json.dumps(report, indent=4))
         
@vlmd.command(help="Launch the vlmd data dictionary definitions in the documentation")
def documentation():
    click.launch(VLMD_DEFS_URL)

@vlmd.command(help="Start a data dictionary from an empty template")
@click.argument("outputfile",type=click.Path())
@click.option('--overwrite',default=False,is_flag=True,callback=_check_overwrite)
@click.option("--numfields",default=1,type=int,prompt=prompt_template_nfields,help="The number of fields (variables) in your data dictionary. This is used to make the template to write empty fields in the template.")
def template(outputfile,overwrite,numfields):
    write_vlmd_template(outputfile,output_overwrite=overwrite,numfields=numfields)

        
if __name__=='__main__':
    vlmd()