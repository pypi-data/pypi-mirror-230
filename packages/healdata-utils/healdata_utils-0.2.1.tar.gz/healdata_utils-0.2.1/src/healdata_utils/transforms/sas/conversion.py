from ..readstat.conversion import convert_readstat,Path
import click

def convert_sas(
  input_filepath,
  data_dictionary_props,
  sas_catalog_filepath=None,
):

    ext = Path(input_filepath).suffix
    
    if ext != ".sas7bdat":
        raise Exception("Currently the SAS inputtype only support sas7bdat files")
    
    if not sas_catalog_filepath:
        sas_catalog_search = list(Path(input_filepath).parent.glob("*.sas7bcat"))
        if len(sas_catalog_search) == 1:
            sas_catalog_filepath = sas_catalog_search[0]
            click.secho(f"Using the SAS Catalog File: {str(sas_catalog_filepath)}",fg="green")
        elif len(sas_catalog_search) > 1:
            sas_catalog_filepath = sas_catalog_search[0]
            click.secho(f"Warning: Found multiple SAS Catalog files",fg="red")
            click.secho(f"Using the SAS Catalog File: {str(sas_catalog_filepath)}")
        else:
            sas_catalog_filepath = None
            click.secho("No sas catalog file found so value labels will not be applied")

    data_dictionary_package = convert_readstat(
        input_filepath,
        data_dictionary_props,
        sas_catalog_filepath=sas_catalog_filepath,
    )

    return data_dictionary_package