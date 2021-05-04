
def get_potentials(self, local=None, remote=None, name=None, key=None, id=None,
                     notes=None, fictional=None, element=None,
                     othername=None, modelname=None, year=None, author=None,
                     abstract=None, return_df=False, verbose=False):

    return self.get_records('Potential', local=local, remote=remote, name=name, key=key, id=id,
                     notes=notes, fictional=fictional, element=element,
                     othername=othername, modelname=modelname, year=year, author=author,
                     abstract=abstract, return_df=return_df, verbose=verbose)

def get_potential(self, local=None, remote=None, name=None, key=None, id=None,
                     notes=None, fictional=None, element=None,
                     othername=None, modelname=None, year=None, author=None,
                     abstract=None, verbose=False):
    
    return self.get_record('Potential', local=local, remote=remote, name=name, key=key, id=id,
                     notes=notes, fictional=fictional, element=element,
                     othername=othername, modelname=modelname, year=year, author=author,
                     abstract=abstract, verbose=verbose)

def download_potentials(self, name=None, key=None, id=None,
                     notes=None, fictional=None, element=None,
                     othername=None, modelname=None, year=None, author=None,
                     abstract=None, overwrite=False, verbose=False):

    self.download_records('Potential', name=name, key=key, id=id,
                     notes=notes, fictional=fictional, element=element,
                     othername=othername, modelname=modelname, year=year, author=author,
                     abstract=abstract, overwrite=overwrite, verbose=verbose)

def upload_potential(self, potential=None, workspace=None, overwrite=False,
                    verbose=False):

    self.upload_record(record=potential, workspace=workspace,
                       overwrite=overwrite, verbose=verbose)

def save_potential(self, potential, overwrite=False, verbose=False):

    self.save_record(record=potential, overwrite=overwrite, verbose=verbose)

def delete_potential(self, potential, local=True, remote=False, verbose=False):

    self.delete_record(self, record=potential, local=local, remote=remote,
                       verbose=verbose)