from setuptools import setup, find_packages

import cdtec

with open("README.md", 'r') as fh:
    long_description = fh.read()

with open("requirements.txt") as req:
    install_req = req.read().splitlines()

setup(name='cdtec',
      version=cdtec.__version__,
      description='Change detection in satellite images',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://framagit.org/benjaminpillot/change_detection',
      author='Benjamin Pillot <benjamin.pillot@ird.fr>, '
             ' Bertrand Ygorra <bertrand.ygorra@inrae.fr>, '
             'Frédéric Frappart <frederic.frappart@legos.obs-mip.fr>, '
             'Thibault Catry <thibault.catry@ird.fr>',
      author_email='benjaminpillot@riseup.net',
      install_requires=install_req,
      python_requires='>=3',
      license='MIT',
      packages=find_packages(),
      zip_safe=False)
