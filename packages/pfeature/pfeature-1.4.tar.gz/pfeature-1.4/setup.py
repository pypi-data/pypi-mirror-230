from setuptools import setup, find_packages
from setuptools import  find_namespace_packages
# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='pfeature',
    version='1.4',
    description='A tool to compute the features of protein and peptide sequences',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license_files = ('LICENSE.txt',),
    url='https://github.com/raghavagps/pfeature', 
    packages=find_namespace_packages(where="src"),
    package_dir={'':'src'},
    package_data={'pfeature.Data':['*']
    },
    entry_points={ 'console_scripts' : ['pfeature_bin = pfeature.python_scripts.pfeature_bin:main', 
                                        'pfeature_comp = pfeature.python_scripts.pfeature_comp:main' ]},
    include_package_data=True,
    python_requires='>=3.6',
    install_requires=[
        'numpy', 'pandas' # Add any Python dependencies here
    ]
)
