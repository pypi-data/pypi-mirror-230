import setuptools
import os
from pathlib import Path
import re

from packaging.version import Version

version_string = os.environ.get("PKG_VERSION")
if version_string is None:
   raise Exception("PKG_VERSION not specified")

version = Version(version_string)
about_file = Path(__file__).parent.absolute() / "src/xcloud/__about__.py"

# read __about__.py file
with open(about_file, "r") as f:
   file_contents = f.read()

# replace __version__ = "0.0.0" string
version_line_code = f'__version__ = "{version}"'
new_contents = re.sub(
   r'^__version__ = ".+"$', 
   version_line_code, 
   file_contents
)

# write content to __about__.py file again
with open(about_file, "w") as f:
   f.write(new_contents)

print("NEW VERSION: {}".format(str(version)))

install_requires = [
   "setuptools",
   "pydantic<=2",
   "numpy",
   "requests",
   "python-dotenv",
   "kserve",
   "click"
]


setuptools.setup(
   name='xcloud',
   version=str(version),
   author='Marcos Rivera Martínez, Sarthak Langde, Glenn Ko, Subhash G N, Toan Do, Roman Ageev',
   author_email='marcos.rm@stochastic.ai, sarthak.langde@stochastic.ai, glenn@stochastic.ai, subhash.gn@stochastic.ai',
   description='',
   long_description_content_type="text/markdown",
   url="",
   classifiers=[
      "Programming Language :: Python :: 3",
      "Operating System :: OS Independent"
   ],
   package_dir={"": "src"},
   packages=setuptools.find_packages(where="src"),
   python_requires=">=3.6",
   install_requires=install_requires,
   entry_points={
      "console_scripts": [
         "xcloud = xcloud.cli:xcloud"
      ]
   }  
)