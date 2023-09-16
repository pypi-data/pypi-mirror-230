from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

packages = find_packages()
print(f"{packages=}")
setup(
    name="choose-your-own-adventure",
    version="0.4.0",
    author="Gael Reinaudi",
    author_email="gael.reinaudi@gmail.com",
    description="Choose Your Own Adventure (CYOA) stories using the Language Model LLM.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GaelReinaudi/choose-your-own-adventure",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",

    entry_points={
        'console_scripts': [
            'cyoa=cyoa_game.main:play',
        ],
    },
)
