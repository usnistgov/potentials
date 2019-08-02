from setuptools import setup, find_packages

def getreadme():
    with open('README.rst') as readme_file:
        return readme_file.read()
   
setup(name = 'potentials',
      version = '0.0.1',
      description = 'Interatomic Potential Repository Python Property Calculations and Tools',
      long_description = getreadme(),
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
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
      url = 'https://github.com/lmhale99/potentials',
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
        'bibtexparser'
      ],
      package_data={'': ['*']},
      zip_safe = False)