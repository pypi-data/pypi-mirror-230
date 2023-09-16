import cyoa_game.config as config
from cyoa_game.adventure import Adventure
import asyncio


async def a_play():
    print("Welcome to Choose-Your-Own-Adventure!")
    api_key = config.OpenAIKeyManager.get_api_key()

    adventure = Adventure(api_key)
    await adventure.start()
    while True:
        await adventure.step()


def play():
    asyncio.run(a_play())


if __name__ == '__main__':
    play()
