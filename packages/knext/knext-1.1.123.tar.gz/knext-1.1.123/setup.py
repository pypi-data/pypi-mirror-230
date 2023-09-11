from setuptools import setup, find_packages

with open("README.md", "r", encoding = "utf-8") as fh:
    long_description = fh.read()
    
setup(
   name='knext',
   version='1.1.123',
   author = "Everest Uriel Castaneda",
   author_email = "Everest_Castaneda1@baylor.edu",
   description = "Kyoto Encylopedia of Genes and Genomes Markup Language File parser and converter",
   long_description = long_description,
   long_description_content_type = "text/markdown",
   url = "https://github.com/everest-castaneda/knext",
   project_urls = {
       "Bug Tracker": "https://github.com/everest-castaneda/knext/issues",
       },
   classifiers = [
       "Programming Language :: Python :: 3",
       "License :: OSI Approved :: MIT License",
       "Operating System :: OS Independent",
       ],
   packages=find_packages(),
   install_requires=[
        "networkx",
        "Click",
        "pandas",
        "typer",
        "requests",
        "pathlib",
        "pytest"
   ],
   entry_points='''
      [console_scripts]
      knext=src.main:cli
      ''',
      )
