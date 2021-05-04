# Standard Python libraries
from pathlib import Path
import json
from copy import deepcopy

# potentials imports
from .tools import screen_input

__all__ = ['settings']

class Settings():
    """
    Class for handling saved settings.
    """
    def __init__(self):
        """
        Class initializer. Calls load.
        """
        self.load()

    @property
    def defaultdirectory(self):
        """pathlib.Path : Path to the default settings directory"""
        return Path(Path.home(), '.NISTpotentials')

    @property
    def defaultfilename(self):
        """pathlib.Path : Path to the default settings.json file"""
        return Path(self.defaultdirectory, 'settings.json')

    @property
    def directory(self):
        """pathlib.Path : Path to the settings directory"""
        return self.__directory

    @property
    def filename(self):
        """pathlib.Path : Path to the settings.json file"""
        return Path(self.directory, 'settings.json')

    @property
    def library_directory(self):
        """pathlib.Path : Path to the library directory."""
        
        # Check library_directory value
        if 'library_directory' in self.__content:
            return Path(self.__content['library_directory'])
        else:
            return Path(self.directory, 'library')

    @property
    def remote(self):
        """The default value for the database initialization parameter 'remote'"""
        return self.__content.get('remote', True)

    @property
    def local(self):
        """The default value for the database initialization parameter 'local'"""
        return self.__content.get('local', True)

    @property
    def pot_dir_style(self):
        """The default value for 'pot_dir_style' used when loading LAMMPS potentials."""
        return self.__content.get('pot_dir_style', 'working')

    @property
    def kim_api_directory(self):
        """pathlib.Path : Path to the directory containing the kim-api."""
        
        # Check kim_api_directory value
        if 'kim_api_directory' in self.__content:
            return Path(self.__content['kim_api_directory'])
        else:
            return None

    @property
    def kim_models_file(self):
        """pathlib.Path : Path to the default KIM models file."""
        return Path(self.directory, 'kim_models.txt')

    def load(self):
        """
        Loads the settings.json file.
        """
        # Load settings.json from the default location
        if self.defaultfilename.is_file():
            with open(self.defaultfilename, 'r') as f:
                self.__defaultcontent = json.load(fp=f)
        else:
            self.__defaultcontent = {}
            
        # Check if forwarding_directory has been set
        if 'forwarding_directory' in self.__defaultcontent:
            self.__directory = Path(self.__defaultcontent['forwarding_directory'])
            
            # Load content from the forwarded location
            if self.filename.is_file():
                with open(self.filename, 'r') as f:
                    self.__content = json.load(fp=f)
            else:
                self.__content = {}

            # Check for recursive forwarding
            if 'forwarding_directory' in self.__content:
                raise ValueError('Multi-level forwarding not allowed.')
        
        # If no forwarding, default is current content
        else:
            self.__content = self.__defaultcontent
            self.__directory = self.defaultdirectory

    def save(self):
        """
        Saves current settings to settings.json.
        """
        if not self.directory.is_dir():
            self.directory.mkdir(parents=True)

        with open(self.filename, 'w') as f:
            json.dump(self.__content, fp=f, indent=4)
        
        # Reload
        self.load()

    def defaultsave(self):
        """
        Saves settings to the default settings.json.  Used by forwarding
        methods.
        """    
        if not self.defaultdirectory.is_dir():
            self.defaultdirectory.mkdir(parents=True)

        with open(self.defaultfilename, 'w') as f:
            json.dump(self.__defaultcontent, fp=f, indent=4)
        
        # Reload
        self.load()

    def set_directory(self, path=None):
        """
        Sets settings directory to a different location.

        Parameters
        ----------
        path : str or Path
            The path to the new settings directory where settings.json (and the
            default library directory) are to be located.
        """
        # Check if a different directory has already been set
        if 'forwarding_directory' in self.__defaultcontent:
            print(f'Settings directory already set to {self.directory}')
            option = screen_input('Overwrite? (yes or no):')
            if option.lower() in ['yes', 'y']:
                pass
            elif option.lower() in ['no', 'n']: 
                return None
            else: 
                raise ValueError('Invalid choice')
        elif len(self.__defaultcontent) != 0:
            raise ValueError(f'directory cannot be changed if other settings exist in {self.defaultfilename}')

        # Ask for path if not given
        if path is None:
            path = screen_input("Enter the path for the new settings directory:")
        self.__defaultcontent['forwarding_directory'] = Path(path).resolve().as_posix()
                
        # Save changes to default
        self.defaultsave()
        
    def unset_directory(self):
        """
        Resets settings directory information back to the default location.
        """
        
        # Check if forwarding_directory has been set
        if 'forwarding_directory' not in self.__defaultcontent:
            print(f'No settings directory set, still using default {self.defaultdirectory}')
        
        else:
            print(f'Remove settings directory {self.directory} and reset to {self.defaultdirectory}?')
            test = screen_input('Delete settings? (must type yes):').lower()
            if test == 'yes':
                del self.__defaultcontent['forwarding_directory']

            # Save changes to default
            self.defaultsave()
            
    def set_library_directory(self, path=None):
        """
        Sets the library directory to a different location.

        Parameters
        ----------
        path : str or Path
            The path to the new library directory where reference files are to be located.
            If not given, will be asked for in a prompt.
        """
        # Check if a different directory has already been set
        if 'library_directory' in self.__content:
            print(f'Library directory already set to {self.library_directory}')
            option = screen_input('Overwrite? (yes or no):')
            if option.lower() in ['yes', 'y']:
                pass
            elif option.lower() in ['no', 'n']: 
                return None
            else: 
                raise ValueError('Invalid choice')
        
        # Ask for path if not given
        if path is None:
            path = screen_input("Enter the path for the new library directory:")
        self.__content['library_directory'] = Path(path).resolve().as_posix()

        # Save changes
        self.save()
        
    def unset_library_directory(self):
        """
        Resets the saved library directory information back to the default
        <Settings.directory>/library/ location.
        """
        
        # Check if library_directory has been set
        if 'library_directory' not in self.__content:
            print(f'Library directory not set: still using {self.library_directory}')
        
        else:
            print(f'Remove library directory {self.library_directory} and reset to {Path(self.directory, "library")}?')
            test = screen_input('Delete settings? (must type yes):').lower()
            if test == 'yes':
                del self.__content['library_directory']

            # Save changes
            self.save()

    def set_remote(self, flag=None):
        """
        Sets the default value for the database initialization parameter
        'remote'.
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

    def set_local(self, flag=None):
        """
        Sets the default value for the database initialization parameter
        'local'.
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

    def set_pot_dir_style(self, value=None):
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

    def set_kim_api_directory(self, path=None):
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
            print(f'kim api directory not set')
        
        else:
            print(f'Remove kim api directory {self.kim_api_directory}?')
            test = screen_input('Delete settings? (must type yes):').lower()
            if test == 'yes':
                del self.__content['kim_api_directory']

            # Save changes
            self.save()

    def set_kim_models(self, kim_models, kim_models_file=None):
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
        
        with open(kim_models_file, 'w') as f:
            for fullid in kim_models:
                f.write(f'{fullid}\n')

    def unset_kim_models(self):
        """
        Removes the default list of kim models.
        """
        if not self.kim_models_file.is_file():
            print(f'List of kim models not set')
        else:
            print(f'Remove the list of kim models?')
            test = screen_input('Delete settings? (must type yes):').lower()
            if test == 'yes':
                self.kim_models_file.unlink()

    @property
    def databases(self):
        """dict: The pre-defined database settings organized by name"""
        if 'iprPy_database' not in self.__content:
            self.__content['iprPy_database'] = {}
        return deepcopy(self.__content['iprPy_database'])

    @property
    def list_databases(self):
        """list: The names of the pre-defined database names"""
        return list(self.databases.keys())

    def set_database(self, name=None, style=None, host=None, **kwargs):
        """
        Allows for database information to be defined in the settings file. Screen
        prompts will be given to allow any necessary database parameters to be
        entered.

        Parameters
        ----------
        name : str, optional
            The name to assign to the database. If not given, the user will be
            prompted to enter one.
        style : str, optional
            The database style associated with the database. If not given, the
            user will be prompted to enter one.
        host : str, optional
            The database host (directory path or url) where the database is
            located. If not given, the user will be prompted to enter one.
        **kwargs : any, optional
            Any other database style-specific parameter settings required to
            properly access the database.
        """
        # Ask for name if not given
        if name is None:
            name = screen_input('Enter a name for the database:')

        # Load database if it exists
        if name in self.list_databases:
            
           # Ask if existing database should be overwritten
            print(f'Database {name} already defined.')
            option = screen_input('Overwrite? (yes or no):')
            if option.lower() in ['yes', 'y']:
                pass
            elif option.lower() in ['no', 'n']: 
                return None
            else: 
                raise ValueError('Invalid choice')
                 
        # Create database entry
        self.__content['iprPy_database'][name] = entry = {} 
            
        # Ask for style if not given
        if style is None: 
            style = screen_input("Enter the database's style:")
        entry['style'] = style

        #Ask for host if not given
        if host is None:
            host = screen_input("Enter the database's host:")
        entry['host'] = str(host)

        # Ask for additional kwargs if not given
        if len(kwargs) == 0:
            print('Enter any other database parameters as key, value')
            print('Exit by leaving key blank')
            while True:
                key = screen_input('key:')
                if key == '': 
                    break
                kwargs[key] = screen_input('value:')
        for key, value in kwargs.items():
            entry[key] = value

        # Save changes
        self.save()
    
    def unset_database(self, name=None):
        """
        Deletes the settings for a pre-defined database from the settings file.

        Parameters
        ----------
        name : str
            The name assigned to a pre-defined database.
        """
        database_names = self.list_databases
                  
        # Ask for name if not given
        if name is None:
            
            if len(database_names) > 0:
                print('Select a database:')
                for i, database in enumerate(database_names):
                    print(i+1, database)
                choice = screen_input(':')
                try:
                    choice = int(choice)
                except:
                    name = choice
                else:
                    name = database_names[choice-1]
            else:
                print('No databases currently set')
                return None

        # Verify listed name exists 
        try:
            i = database_names.index(name)
        except:
            raise ValueError(f'Database {name} not found')

        print(f'Database {name} found')
        test = screen_input('Delete settings? (must type yes):').lower()
        if test == 'yes':
            del(self.__content['iprPy_database'][name])
            self.save()

settings = Settings()