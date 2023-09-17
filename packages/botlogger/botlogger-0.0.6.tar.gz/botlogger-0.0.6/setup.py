import setuptools

setuptools.setup(
    name="botlogger",
    version="0.0.6",
    author="justacold",
    description="Library to log messages from telegram bots",
    packages=setuptools.find_packages(),
    install_requires=[
        'loguru',
        'aiohttp',
        # Add more dependencies here
    ],
    exclude=['README.md', '*.txt']
)