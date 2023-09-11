from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='uglygrep',
    version='0.1.0',
    description="UglyGrep is a desktop application that enables you to perform text searches within multiple files in a directory. Built using Python and PyQt6, it provides an easy-to-use graphical interface for entering search patterns and locating matches across text files with a specified extension.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author="Scott Peterman",
    author_email="scottpeterman@gmail.com",
    url="https://github.com/scottpeterman/UglyGrep",  # Replace with your repository URL
    packages=find_packages(),
    install_requires=[
        'keyring==24.2.0',
        'Pygments==2.16.1',
        'PyQt6>=6.5.1',
        # ... add other dependencies here
    ],
    entry_points={
        'console_scripts': [
            'uglygrep=uglygrep.UglyGrep:main',
        ],
    },
    license="GPL",
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
