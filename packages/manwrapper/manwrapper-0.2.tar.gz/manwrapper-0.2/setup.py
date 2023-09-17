from setuptools import setup, find_packages

setup(
    name="manwrapper",
    version="0.2",
    description="A simple command-line tool to view man pages.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author="Alberto Ferrer",
    author_email="albertof@barrahome.org",
    url="https://github.com/bet0x/manwrapper",  # Replace with your project's URL
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'manwrapper=manwrapper.main:main',
        ],
    },
)
