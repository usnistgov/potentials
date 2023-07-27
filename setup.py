from setuptools import setup, find_packages

def getreadme():
    """Fetches readme content"""
    with open('README.rst', encoding='UTF-8') as readme_file:
        return readme_file.read()

def getversion():
    """Fetches version information from VERSION file"""
    with open('potentials/VERSION', encoding='UTF-8') as version_file:
        return version_file.read().strip()

setup(
    name = 'potentials',
    version = getversion(),
    description = ' '.join([
        'API database tools for accessing the NIST Interatomic Potentials Repository:',
        'explore and download interatomic potentials and computed properties.']),
    long_description = getreadme(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
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
        'unidecode',
        'numpy',
        'matplotlib',
        'pandas',
        'requests',
        'habanero',
        'bibtexparser',
        'ipywidgets',
        'cdcs',
        'yabadaba>=0.2.1'
    ],
    include_package_data = True,
    zip_safe = False
)
