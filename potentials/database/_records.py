# coding: utf-8
# Standard Python libraries
from pathlib import Path

from DataModelDict import DataModelDict as DM

def get_record(self, template, title, localpath=None, local=None,
               remote=None, verbose=False):
    """
    Gets a reference file from localpath or by downloading from
    potentials.nist.gov if a local copy is not found.
    
    Parameters
    ----------
    style : str
        The reference record's style.
    name : str
        The name of the record.
    verbose: bool, optional
        If True, informative print statements will be used.
        
    Returns
    -------
    DataModelDict.DataModelDict
        The record content.
    """
    # Set localpath, local, and remote as given here or during init
    if localpath is None:
        localpath = self.localpath
    if local is None:
        local = self.local
    if remote is None:
        remote = self.remote
    
    # Try local library first
    if local is True and localpath is not None:
        for fmt in ['xml', 'json']:
            fname = Path(localpath, template, f'{title}.{fmt}')
            if fname.is_file():
                if verbose:
                    print('Found record in local library')
                return DM(fname)
    
    # Try remote next
    if remote is True:
        matches = self.cdcs.query(template=template, title=title)
        if len(matches) == 1:
            if verbose:
                print('found record in remote database')
            return DM(matches.iloc[0].xml_content)
            
        elif len(matches) > 0:
            raise ValueError(f'found multiple {title} of {template} records in remote database')
    
    raise ValueError(f'Record {title} of {template} not found')

def download_records(self, template, localpath=None, format='xml', indent=None,
                     verbose=False):
    """
    Download all records associated with a given template from the remote and
    save to localpath.
    
    Parameters
    ----------
    template : str
        The template (schema/style) of records to download.  If given, all
        records with this template will be downloaded.
    localpath : path-like object, optional
        Path to a local directory where the files will be saved to.  If not
        given, will use the localpath value set during object initialization.
    format : str, optional
        The file format to save the file as.  Allowed values are 'xml'
        (default) and 'json'.
    indent : int, optional
        The indentation spacing size to use for the locally saved file.  If not
        given, the JSON/XML content will be compact.
    verbose : bool, optional
        If True, info messages will be printed during operations.  Default
        value is False.
    """
    
    if template == 'potential_LAMMPS':
        raise ValueError('use download_lammps_potentials instead')
    elif template == 'Potential':
        raise ValueError('use download_lammps_potentials instead')
    elif template == 'Citation':
        raise ValueError('use download_citations instead')
    
    # Check localpath values
    if localpath is None:
        localpath = self.localpath
    if localpath is None:
        raise ValueError('localpath must be set to download files')
    
    # Check format value
    format = format.lower()
    allowed_formats = ['xml', 'json']
    if format not in allowed_formats:
        raise ValueError("Format must be 'xml' or 'json'")
    
    # Create save directory if needed
    save_directory = Path(localpath, template)
    if not save_directory.is_dir():
        save_directory.mkdir(parents=True)

    for fmt in allowed_formats:
        if fmt != format:
            numexisting = len([fname for fname in save_directory.glob(f'*.{fmt}')])
            if numexisting > 0:
                raise ValueError(f'{numexisting} records of format {fmt} already saved locally')

    # Download and save
    records = self.cdcs.query(template=template)
    for i in range(len(records)):
        record = records.iloc[i]
        fname = Path(save_directory, f'{record.title}.{format}')
        content = DM(record.xml_content)
        with open(fname, 'w') as f:
            if format == 'xml':
                content.xml(fp=f, indent=indent)
            else:
                content.json(fp=f, indent=indent)
                
    if verbose:
        print(f'Downloaded {len(records)} of {template}')