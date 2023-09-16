import asyncio
import llm
import textwrap


class Adventure:
    def __init__(self, api_key):
        self.model = llm.get_model("gpt-3.5-turbo")
        self.model.key = api_key

    def inital_prompt(self) -> str:
        return """
write the first paragraphs of a book of the type "chose your own adventure" \
where the reader, which is the main character, is a girl coder that discovers \
something very strange while coding on her linux machine...
"""

    def format_text(self, input_text, width=50):
        return textwrap.fill(input_text, width=width)

    async def start(self):
        response = self.model.prompt(self.inital_prompt(), max_tokens=1000, stop="\n\n")
        formatted_text = self.format_text(response.text())
        print(formatted_text)
        key = input("Make your choice:")

    async def step(self):
        pass


async def test():
    import cyoa_game.config as config

    adventure = Adventure(config.OpenAIKeyManager.get_api_key())
    await adventure.start()
    await adventure.step()


if __name__ == '__main__':
    asyncio.run(test())
