from setuptools import setup, find_packages

def getreadme():
    with open('README.rst') as readme_file:
        return readme_file.read()
   
setup(name = 'potentials',
      version = '0.2.3',
      description = 'API database tools for accessing the NIST Interatomic Potentials Repository: explore and download interatomic potentials and computed properties.',
      long_description = getreadme(),
      classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Scientific/Engineering :: Physics'
      ],
      keywords = [
        'atom', 
        'atomic', 
        'atomistic', 
        'molecular dynamics', 
        'interatomic potential',
        'force field'
      ], 
      url = 'https://github.com/usnistgov/potentials',
      author = 'Lucas Hale',
      author_email = 'lucas.hale@nist.gov',
      packages = find_packages(),
      install_requires = [
        'xmltodict',
        'DataModelDict',
        'numpy', 
        'matplotlib',
        'pandas',
        'requests',
        'habanero',
        'bibtexparser',
        'cdcs==0.1.4',
        'ipywidgets',
      ],
      package_data={'': ['*']},
      zip_safe = False)