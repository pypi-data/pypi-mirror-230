from setuptools import setup, find_packages

setup(
    name='party-downloader',
    version='0.0.8',
    description='Simple tool to download files from coomer.party',
    packages=find_packages(),
    install_requires=[
        'requests',
        'tqdm',
        'beautifulsoup4',
    ],
)
