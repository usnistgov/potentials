# coding: utf-8
# Standard Python libraries
from pathlib import Path
from typing import Optional

# potentials imports
from .tools import screen_input

import yabadaba.Settings

__all__ = ['settings']

class Settings(yabadaba.Settings.Settings):
    """
    Class for handling saved settings.
    """
    def __init__(self):
        """
        Class initializer. Calls load.
        """
        super().__init__('.NISTpotentials', 'settings.json')

    @property
    def remote(self):
        """bool: The default value for the database initialization parameter 'remote'"""
        return self.__content.get('remote', True)

    def set_remote(self,
                   flag: Optional[bool] = None):
        """
        Sets the default value for the database initialization parameter
        'remote'.

        Parameters
        ----------
        flag : bool, optional
            The value to set the default remote value to.  If None (default),
            then a prompt will ask for a value. 
        """      
        # Ask for flag if not given
        if flag is None:
            flag = screen_input("Enter default remote option (True/False):")
        
        if isinstance(flag, str):
            if flag.lower() in ['t', 'true']:
                flag = True
            elif flag.lower() in ['f', 'false']:
                flag = False
            else:
                raise ValueError('Invalid setting: must be True/False')
        
        if not isinstance(flag, bool):
            raise TypeError('remote flag value must be bool')

        if flag is True and 'remote' in self.__content:
            del self.__content['remote']
        elif flag is False:
            self.__content['remote'] = False

        # Save changes
        self.save()

    @property
    def local(self):
        """bool: The default value for the database initialization parameter 'local'"""
        return self.__content.get('local', True)

    def set_local(self,
                  flag: Optional[bool] = None):
        """
        Sets the default value for the database initialization parameter
        'local'.

        Parameters
        ----------
        flag : bool, optional
            The value to set the default remote value to.  If None (default),
            then a prompt will ask for a value. 
        """   
        # Ask for flag if not given
        if flag is None:
            flag = screen_input("Enter default remote option (True/False):")
        if isinstance(flag, str):
            if flag.lower() in ['t', 'true']:
                flag = True
            elif flag.lower() in ['f', 'false']:
                flag = False
            else:
                raise ValueError('Invalid setting: must be True/False')
        
        if not isinstance(flag, bool):
            raise TypeError('local flag value must be bool')


        if flag is True and 'local' in self.__content:
            del self.__content['local']
        elif flag is False:
            self.__content['local'] = False
        
        # Save changes
        self.save()

    def set_local_database(self,
                           localpath: Optional[Path] = None,
                           format: str = 'json',
                           indent: Optional[int] = 4):
        """
        Set the default local interaction settings for potential.Database
        objects.

        Parameters
        ----------
        localpath : path, optional
            The directory to use for the local database.  If not given, will
            use the default path of directory "library" located in the settings
            directory.
        format : str, optional
            The file format that is used: "json" or "xml".  Default value is
            "json".
        indent : int or None, optional
            The number of indentation spacings to use in the files.  If None,
            then the files will be compact.  Default value is 4.
        """
        if localpath is None:
            localpath = Path(self.directory, 'library')

        self.set_database(name='potentials_local', style='local', host=localpath,
                          format=format, indent=indent) 

    @property
    def pot_dir_style(self):
        """str: The default value for 'pot_dir_style' used when loading LAMMPS potentials."""
        return self.__content.get('pot_dir_style', 'working')

    def set_pot_dir_style(self,
                          value: Optional[str] = None):
        """
        Sets the default pot_dir_style option.

        Parameters
        ----------
        value : str
            Specifies which pot_dir_style is to be the default.  Allowed values
            are 'working', 'id', and 'local'. 'working' will set all pot_dir = '',
            meaning parameter files are expected in the working directory when the
            potential is accessed. 'id' sets the pot_dir values to match the
            potential's id. 'local' sets the pot_dir values to the corresponding
            local database paths where the files are expected to be found.
            If not given, will be asked for in a prompt.
        """
        # Ask for value if not given
        if value is None:
            print("Select the pot_dir style option to set as default")
            print("1. working")
            print("2. id")
            print("3. local")
            value = screen_input(":")
            try:
                c = int(value)
            except:
                pass
            else:
                if c < 1 or c > 3:
                    raise ValueError('Invalid selection')
                value = ['working', 'id', 'local'][c-1]
        
        if value not in ['working', 'id', 'local']:
            raise ValueError('Invalid pot_dir_style value: allowed values are "working", "id" and "local"')

        self.__content['pot_dir_style'] = value

        # Save changes
        self.save()

    @property
    def kim_api_directory(self):
        """pathlib.Path : Path to the directory containing the kim-api."""
        
        # Check kim_api_directory value
        if 'kim_api_directory' in self.__content:
            return Path(self.__content['kim_api_directory'])
        else:
            return None

    def set_kim_api_directory(self,
                              path: Optional[Path] = None):
        """
        Sets the default kim api directory.

        Parameters
        ----------
        path : str or Path
            The path to the directory containing the kim api version to set as
            the default.  If not given, will be asked for in a prompt.
        """
        # Check if a different directory has already been set
        if 'kim_api_directory' in self.__content:
            print(f'kim api directory already set to {self.kim_api_directory}')
            option = screen_input('Overwrite? (yes or no):')
            if option.lower() in ['yes', 'y']:
                pass
            elif option.lower() in ['no', 'n']: 
                return None
            else: 
                raise ValueError('Invalid choice')
        
        # Ask for path if not given
        if path is None:
            path = screen_input("Enter the path for the kim api directory:")
        self.__content['kim_api_directory'] = Path(path).resolve().as_posix()

        # Save changes
        self.save()
        
    def unset_kim_api_directory(self):
        """
        Removes the saved kim api directory information.
        """
        
        # Check if kim_api_directory has been set
        if 'kim_api_directory' not in self.__content:
            print('kim api directory not set')
        
        else:
            print(f'Remove kim api directory {self.kim_api_directory}?')
            test = screen_input('Delete settings? (must type yes):').lower()
            if test == 'yes':
                del self.__content['kim_api_directory']

            # Save changes
            self.save()

    @property
    def kim_models_file(self):
        """pathlib.Path : Path to the default KIM models file."""
        return Path(self.directory, 'kim_models.txt')

    def set_kim_models(self,
                       kim_models: list,
                       kim_models_file: Optional[Path] = None):
        """
        Saves a default list of kim models.

        Parameters
        ----------
        kim_models : list
            The list of full kim ids to save.
        kim_models_file : path-like object, optional
            The path to the file to save the list of kim models to.  If not
            given, will use the default file location in the settings
            directory.
        """
        
        if kim_models_file is None:
            kim_models_file = self.kim_models_file
            
        if kim_models_file.is_file():
            print('kim models file already exists.')
            option = screen_input('Overwrite? (yes or no):')
            if option.lower() in ['yes', 'y']:
                pass
            elif option.lower() in ['no', 'n']: 
                return None
            else: 
                raise ValueError('Invalid choice')
        
        with open(kim_models_file, 'w', encoding='UTF-8') as f:
            for fullid in kim_models:
                f.write(f'{fullid}\n')

    def unset_kim_models(self):
        """
        Removes the default list of kim models.
        """
        if not self.kim_models_file.is_file():
            print('List of kim models not set')
        else:
            print('Remove the list of kim models?')
            test = screen_input('Delete settings? (must type yes):').lower()
            if test == 'yes':
                self.kim_models_file.unlink()

settings = Settings()