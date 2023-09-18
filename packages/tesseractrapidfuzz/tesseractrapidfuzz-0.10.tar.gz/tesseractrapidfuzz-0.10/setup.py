from setuptools import setup, find_packages
import codecs
import os
# 
here = os.path.abspath(os.path.dirname(__file__))
# 
with open(os.path.join(os.path.abspath(os.path.dirname(__file__)),'README.md'), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()\

from pathlib import Path
this_directory = Path(__file__).parent
#long_description = (this_directory / "README.md").read_text()

VERSION = '''0.10'''
DESCRIPTION = '''Performs OCR on a list of images using Tesseract and performs fuzzy string matching with a given list of strings.'''

# Setting up
setup(
    name="tesseractrapidfuzz",
    version=VERSION,
    license='MIT',
    url = 'https://github.com/hansalemaos/tesseractrapidfuzz',
    author="Johannes Fischer",
    author_email="aulasparticularesdealemaosp@gmail.com",
    description=DESCRIPTION,
long_description = long_description,
long_description_content_type="text/markdown",
    #packages=['fuzzypandaswuzzy', 'multitessiocr', 'numpy', 'pandas', 'rapidfuzz'],
    keywords=['tesseract', 'ocr', 'fuzzy', 'rapidfuzz', 'fuzzywuzzy'],
    classifiers=['Development Status :: 4 - Beta', 'Programming Language :: Python :: 3 :: Only', 'Programming Language :: Python :: 3.10', 'Topic :: Software Development :: Libraries :: Python Modules', 'Topic :: Utilities'],
    install_requires=['fuzzypandaswuzzy', 'multitessiocr', 'numpy', 'pandas', 'rapidfuzz'],
    include_package_data=True
)
#python setup.py sdist bdist_wheel
#twine upload dist/*