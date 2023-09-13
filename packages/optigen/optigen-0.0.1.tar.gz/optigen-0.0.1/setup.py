from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'Genetic Algorithmen Framework'

# Setting up
setup(
    name="optigen",
    version=VERSION,
    author="ShadowFlameFox",
    author_email="<shadow_flame_fox@web.de>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=['random'],
    keywords=['python', 'genetic', 'natural selection', 'algorithmen'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)