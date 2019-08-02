from pathlib import Path

from DataModelDict import DataModelDict as DM

import requests

from .. import rootdir

def ipr_meta_to_potentials(refresh_files=False):
    
    oldpath = Path(rootdir, '..', 'data', 'IPR metadata records')
    potpath = Path(rootdir, '..', 'data', 'potential')
    imppath = Path(rootdir, '..', 'data', 'implementation')

    if not oldpath.is_dir():
        raise ValueError(f'{oldpath} not found')
    if not potpath.is_dir():
        potpath.mkdir()
    if not imppath.is_dir():
        imppath.mkdir()

    for fname in oldpath.glob('*.json'):
    
        # Load old model
        oldpotmodel = DM(fname)
        oldpot = oldpotmodel['interatomic-potential']
        potkey = oldpot['key']
        
        # Create new potential model
        newpotmodel = DM()
        newpotmodel['interatomic-potential'] = newpot = DM()
        
        for key1 in oldpot:
            
            # Handle description
            if key1 == 'description':
                newpot['description'] = DM()
                for key2 in oldpot['description']:
                    
                    # Strip citation of everything except DOI
                    if key2 == 'citation':
                        for oldcite in oldpot['description'].iteraslist('citation'):
                            try:
                                newcite = DM([('DOI', oldcite['DOI'])])
                            except:
                                pass
                            else:
                                newpot['description'].append('citation', newcite)
                    else:
                        newpot['description'][key2] = oldpot['description'][key2]
            
            # Handle implementation
            elif key1 == 'implementation':
                # Iterate over implementations in old model
                for oldimp in oldpot.iteraslist('implementation'):
                    newimpmodel = DM()
                    newimpmodel['interatomic-potential-implementation'] = newimp = DM()
                    
                    for key2 in oldimp:
                        newimp[key2] = oldimp[key2]
                        
                        # Add interatomic-potential-key after date
                        if key2 == 'date':
                            newimp['interatomic-potential-key'] = potkey

                    # Save new implementation model
                    impdir = Path(imppath, newimp['key'])
                    if not impdir.is_dir():
                        impdir.mkdir()
                    with open(Path(impdir, 'meta.json'), 'w') as f:
                        newimpmodel.json(fp=f, indent=4)

                    # Download any missing files
                    ipr_fetch_files(newimpmodel, impdir, refresh=refresh_files)
                    
            elif key1 == '@xmlns:xsi':
                pass
                        
            else:
                newpot[key1] = oldpot[key1]  
        
        # Save new potential model
        potkey = newpot['key']
        with open(Path(potpath, f'{potkey}.json'), 'w') as f:
            newpotmodel.json(fp=f, indent=4)

def ipr_fetch_files(impmodel, impdir, refresh=False):
    """
    Downloads potential files for a given implementation

    Parameters
    ----------
    impmodel : DataModelDict.DataModelDict
        The implementation model whose files are to be retrieved
    impdir : Path
        The directory where the files will be saved
    """
    
    # Loop over artifacts listed
    for artifact in impmodel.finds('artifact'):
        
        # Get file url and file name
        try:
            url = artifact['web-link']['URL']
            fname = artifact['web-link']['link-text']
        except:
            print(f'Missing web-link info: {impdir.stem}')
        else:
            
            fpath = Path(impdir, fname)
            try:
                # Download and save if missing
                if refresh or not fpath.is_file():
                    r = requests.get(url)
                    r.raise_for_status()
                    with open(fpath, 'wb') as f:
                        f.write(r.content)
            except:
                print(f'Failed to download: {impdir.stem}/{fname}')