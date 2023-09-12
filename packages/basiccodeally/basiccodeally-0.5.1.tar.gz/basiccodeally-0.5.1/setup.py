import pathlib
from setuptools import setup
from basiccodeally import __version__

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()
LICENSE = (HERE / 'LICENSE').read_text()

setup(
    name="basiccodeally",
    version=__version__,
    author='Humberto A. Sanchez II',
    author_email='Humberto.A.Sanchez.II@gmail.com',
    maintainer='Humberto A. Sanchez II',
    maintainer_email='humberto.a.sanchez.ii@gmail.com',
    description='Humberto`s Basic Common Code',
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/hasii2011/basiccodeally",
    package_data={
        'basiccodeally':  ['py.typed'],
    },

    packages=[
        'basiccodeally',
    ],
    install_requires=['Deprecated~=1.2.14'],
)
