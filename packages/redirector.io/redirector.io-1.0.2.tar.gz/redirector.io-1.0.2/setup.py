from setuptools import setup, find_packages
from pathlib import Path

# read the contents of your README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='redirector.io',
    version='1.0.2',
    author='Tomer',
    author_email='tomerw@illustria.io',
    description='A simple HTTP redirect server',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/redirector',
    project_urls={
        'Documentation': 'https://drive.google.com/uc?export=download&id=1yoJ703Sjj5bzxXj8QXwDckWtqC1xDFPT'
    },
    packages=find_packages()
)

