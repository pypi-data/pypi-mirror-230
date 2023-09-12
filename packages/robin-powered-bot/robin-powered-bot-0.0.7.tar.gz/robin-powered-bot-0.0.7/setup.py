# read the contents of your README file
from pathlib import Path

from setuptools import find_packages, setup

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='robin-powered-bot',
    version='0.0.7',
    description='Provides a set of utilities to simplify communication with robin-powered API and more easily automate bookings.',
    url='https://github.com/donatobarone/robin-powered-bot',
    author='Donato Barone',
    author_email='eng.donato.barone@gmail.com',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=[
        'requests'
    ], zip_safe=False)
