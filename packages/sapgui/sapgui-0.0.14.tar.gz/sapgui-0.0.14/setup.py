from setuptools import setup, find_packages

VERSION = '0.0.14'
DESCRIPTION = 'Python package to control SAP GUI scripting.'
LONG_DESCRIPTION = '''Python package which gives user possibility to build his own
                      RPA base on SAP GUI.
                   '''

# Setting up
setup(
    # the name must match the folder name 'verysimplemodule'
    name="sapgui",
    version=VERSION,
    author="Piotr Kocemba",
    author_email="<KocembaPiotr@gmail.com>",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],  # add any additional packages that
    # needs to be installed along with your package. Eg: 'caer'

    keywords=['python', 'sap'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)