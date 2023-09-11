from setuptools import setup, find_namespace_packages
from pathlib import Path
import os 

os.chdir(Path(__file__).parent)
def generate_long_description():
    return Path("README.md").read_text()

def get_install_requirements():
    return '''petl==1.7.12
jsonschema==4.17.3
# requests==2.28.2
PyYaml==6.0
#frictionless==4.40.8
pandas==1.4
pyreadstat==1.2.0
charset_normalizer==2.1
visions== 0.7.5
click==8.1.3
python-slugify
openpyxl

'''

setup(
    name='healdata_utils',
    version='0.2.1',
    author='Michael Kranz',
    author_email='kranz-michael@norc.org',
    long_description=generate_long_description(),
    long_description_content_type="text/markdown",    
    description='Data packaging tools for the HEAL data ecosystem',
    #TODO: change url to HEAL once migrated.
    url='https://github.com/norc-heal/healdata-utils',
    package_dir={'': 'src'},
    packages=find_namespace_packages(where='src'),
    install_requires=get_install_requirements(),
    entry_points='''
        [console_scripts]
        vlmd=healdata_utils.cli:vlmd
    '''

)
