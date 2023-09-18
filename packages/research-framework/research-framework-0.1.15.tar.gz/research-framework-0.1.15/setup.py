from pkg_resources import parse_requirements
from setuptools import setup
from setuptools import setup, find_packages
import pathlib

with pathlib.Path('./requirements.txt').open() as requirements_txt:
    install_requires = [
        str(requirement)
        for requirement
        in parse_requirements(requirements_txt)
    ]

setup(
    name="research-framework",
    version='0.1.15',
    description="framework base para investigación",
    url="https://github.com/manucouto1/research_framework",
    author="Manuel Couto Pintos",
    author_email="manuel.couto.pintos@usc.es",
    license="Apache License",
    packages=find_packages(),
    install_requires=install_requires,

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',  
        'Operating System :: POSIX :: Linux',        
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

)