import os
import getpass

class OpenAIKeyManager:
    
    API_KEY = ''
    CONFIG_PATH = os.path.expanduser("~/.cyoa")

    @classmethod
    def get_api_key(cls):
        if cls.API_KEY:
            return cls.API_KEY
        
        # Try fetching from environment variable
        cls.API_KEY = os.environ.get('OPENAI_API_KEY')

        # Try fetching from the config file
        if not cls.API_KEY and os.path.exists(cls.CONFIG_PATH):
            with open(cls.CONFIG_PATH, 'r') as file:
                cls.API_KEY = file.readline().strip()

        # Prompt the user if not found in either
        if not cls.API_KEY:
            cls.API_KEY = getpass.getpass("Enter your API key (input will be hidden): ")
            cls._save_api_key(cls.API_KEY)
        
        return cls.API_KEY

    @classmethod
    def _save_api_key(cls, key):
        with open(cls.CONFIG_PATH, 'w') as file:
            file.write(key)


if __name__ == '__main__':
    key_manager = OpenAIKeyManager()
    api_key = key_manager.get_api_key()
    print(api_key)
