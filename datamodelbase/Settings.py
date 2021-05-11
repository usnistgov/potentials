# Standard Python libraries
from pathlib import Path
import json
from copy import deepcopy

# relative imports
from .tools import screen_input

__all__ = ['settings']

class Settings():
    """
    Class for handling saved settings.
    """
    def __init__(self, directoryname='.NIST', filename='settings.json'):
        """
        Class initializer. Calls load.
        
        Parameters
        ----------
        directoryname : str, optional
            The default directory where the settings file is expected will be
            in a directory of this name within the user's home directory.
            Default value is ".NIST".
        filename, str, optional
            The name to use for the settings file.  This will be saved in the
            directory path and should have a ".json" extension.  Default value
            is "settings.json".
        """
        self.__directoryname = directoryname
        self.__filename = filename

        self.load()

    ######################## Basic settings operations ########################

    @property
    def defaultdirectory(self):
        """pathlib.Path : Path to the default settings directory"""
        return Path(Path.home(), self.__directoryname)

    @property
    def defaultfilename(self):
        """pathlib.Path : Path to the default settings file"""
        return Path(self.defaultdirectory, self.__filename)

    @property
    def directory(self):
        """pathlib.Path : Path to the settings directory"""
        return self.__directory

    @property
    def filename(self):
        """pathlib.Path : Path to the settings file"""
        return Path(self.directory, self.__filename)

    def load(self):
        """Loads the settings file."""
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
        """Saves current settings to settings.json."""
        if not self.directory.is_dir():
            self.directory.mkdir(parents=True)

        with open(self.filename, 'w') as f:
            json.dump(self.__content, fp=f, indent=4)
        
        # Reload
        self.load()

    def defaultsave(self):
        """Saves forwarding settings to the default settings.json."""
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
        """Resets settings directory information back to the default location."""
        
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
    
    ############################ database settings ############################

    @property
    def databases(self):
        """dict: Any defined database settings organized by name"""
        if 'database' not in self.__content:
            self.__content['database'] = {}
        return deepcopy(self.__content['database'])

    @property
    def list_databases(self):
        """list: The names associated with the defined databases"""
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
        self.__content['database'][name] = entry = {}
            
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
            del(self.__content['database'][name])
            self.save()

settings = Settings()