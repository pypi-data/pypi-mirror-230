import cyoa_game.config as config

def play():
    print("Welcome to Choose-Your-Own-Adventure!")
    api_key = config.OpenAIKeyManager.get_api_key()
    

if __name__ == '__main__':
    play()