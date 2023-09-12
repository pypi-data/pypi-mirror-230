#this is a setup.py file
from setuptools import setup, find_packages




VERSION = '1.0.3'
DESCRIPTION = 'Python package for analysis of Multicellular-like phenotype formation in yeast species'
LONG_DESCRIPTION = 'Python package for analysis of Multicellular-like phenotype formation in yeast, for more information see https://github.com/BKover99/yeastmlp. For all correspondence, email bence.kover.19 *"at"* ucl.ac.uk'


setup(
    name="yeastmlp",
    version=VERSION,
    author="Bence Kover",
    author_email="<kover.bence@gmail.com>",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['numpy','scipy', 'scikit-image', 'matplotlib', 'pandas'],
    keywords=['python', 'yeast', 'biology', 'multicellularity', 'adhesion', 'flocculation'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)

