import os
from configparser import ConfigParser


class ConfigManager(ConfigParser):

    def __init__(self, name) -> None:

        self.path = os.path.join(os.path.dirname(__file__), name)

        super().__init__()

        if os.path.exists(self.path):
            self.read(self.path)
        
        else:
            self.set("DEFAULT", "PATH", "{home}/keys.json")
            self.add_section("USER")
            self.save()
    
    def save(self) -> None:
        
        with open(self.path, 'w') as fp:
            self.write(fp)


@lambda iife: iife()
class Storage:

    name: str = "Key-Record"
    
    keys = None
    config = ConfigManager(name="config.ini")
    schema_path: str = os.path.join(os.path.dirname(__file__), "schemas.py")
    
    @property
    def user_path(self) -> str:
        return self.config.get('USER', 'PATH').format(home=os.path.expanduser('~'))
    
    @user_path.setter
    def user_path(self, path: str) -> None:
        self.config.set('USER', 'PATH', path)
    
    @user_path.deleter
    def user_path(self) -> None:
        self.config.remove_option('USER', 'PATH')
