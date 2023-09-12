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
DESCRIPTION = '''Finds similar songs'''

# Setting up
setup(
    name="sposong",
    version=VERSION,
    license='MIT',
    url = 'https://github.com/hansalemaos/sposong',
    author="Johannes Fischer",
    author_email="aulasparticularesdealemaosp@gmail.com",
    description=DESCRIPTION,
long_description = long_description,
long_description_content_type="text/markdown",
    #packages=['PrettyColorPrinter', 'a_pandas_ex_plode_tool', 'a_selenium2df', 'a_selenium_add_special_keys', 'a_selenium_scroll_down_forever', 'flatten_everything', 'get_consecutive_filename', 'operagxdriver', 'pandas', 'selenium', 'ujson'],
    keywords=['songs'],
    classifiers=['Development Status :: 4 - Beta', 'Programming Language :: Python :: 3 :: Only', 'Programming Language :: Python :: 3.10', 'Topic :: Software Development :: Libraries :: Python Modules', 'Topic :: Utilities'],
    install_requires=['PrettyColorPrinter', 'a_pandas_ex_plode_tool', 'a_selenium2df', 'a_selenium_add_special_keys', 'a_selenium_scroll_down_forever', 'flatten_everything', 'get_consecutive_filename', 'operagxdriver', 'pandas', 'selenium', 'ujson'],
    include_package_data=True
)
#python setup.py sdist bdist_wheel
#twine upload dist/*