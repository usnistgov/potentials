# coding: utf-8
# Standard Python libraries
from pathlib import Path

from DataModelDict import DataModelDict as DM

from ..tools import aslist

def get_records(self, template=None, title=None, keyword=None, mongoquery=None,
                localpath=None, local=None, remote=None, verbose=False):
    
    # Set localpath, local, and remote as given here or during init
    if localpath is None:
        localpath = self.localpath
    if local is None:
        local = self.local
    if remote is None:
        remote = self.remote
    
    # Check for competing parameters
    if keyword is not None and title is not None:
        raise ValueError("keyword and title cannot both be given")
    
    matches = {}
    numlocal = 0
    numremote = 0
    
    # Try local library first
    if local is True and localpath is not None:
        if template is None:
            templates = ['*']
        else:
            templates = aslist(template)
        
        # Search by title
        if title is not None:
            titles = aslist(title)
        
            for templatedir in templates:
                for titlename in titles:
                    for fname in Path(localpath, templatedir).glob(f'{titlename}.*'):
                        if fname.suffix in ['.xml', '.json']:
                            matches[titlename] = DM(fname)
                        
        # Search by keyword
        elif keyword is not None:
            keywords = aslist(keyword)
            
            for templatedir in templates:
                for fname in Path(localpath, templatedir).glob('*'):
                    if fname.suffix in ['.xml', '.json']:
                        titlename = fname.stem
                        with open(fname) as f:
                            content = f.read()
                        
                        ismatch = True
                        for kw in keywords:
                            if kw not in content:
                                ismatch = False
                                break
                        if ismatch:
                            matches[titlename] = DM(fname)
                    
        # Add all by template
        else:
            for templatedir in templates:
                for fname in Path(localpath, templatedir).glob('*'):
                    if fname.suffix in ['.xml', '.json']:
                        titlename = fname.stem
                        matches[titlename] = DM(fname)
    
        numlocal = len(matches)
        if verbose:
            print(f'Found {numlocal} records in local library')
    
    # Try remote next
    if remote is True:
        rmatches = self.cdcs.query(template=template, title=title,
                                   keyword=keyword, mongoquery=mongoquery)
        if verbose:
            numremote = len(rmatches)
            print(f'found {numremote} records in remote database')
        
        for i in rmatches.index:
            rmatch = rmatches.loc[i]
            if rmatch.title not in matches:
                matches[rmatch.title] = DM(rmatch.xml_content)
        
    if verbose and numlocal > 0 and numremote > 0:
        numtotal = len(matches)
        print(f'found {numtotal} unique records between local and remote')

    if len(matches) > 0:            
        return list(matches.values())
    else:
        return []

def get_record(self, template=None, title=None, keyword=None, mongoquery=None,
               localpath=None, local=None, remote=None, verbose=False):
    
    records = get_records(self, template=template, title=title, keyword=keyword,
                          mongoquery=mongoquery, localpath=localpath, local=local,
                          remote=remote, verbose=verbose)
    if len(records) == 1:
        return records[0]
    elif len(records) == 0:
        raise ValueError('No matching records found')
    else:
        raise ValueError('Multiple matching records found')

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