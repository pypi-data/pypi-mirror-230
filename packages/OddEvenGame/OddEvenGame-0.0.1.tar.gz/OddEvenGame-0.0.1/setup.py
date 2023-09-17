from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'This is a game in which you have to play cricket with a computer.'

with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

# Setting up
setup(
    name="OddEvenGame",
    version=VERSION,
    author="Siddharth Yadav",
    author_email="siddharthdis3432@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    url="https://github.com/siddharthdis/OddEvenGame",
    packages=find_packages(),
    install_requires=[],
    py_modules=['OddEvenGame'],
    python_requires='>=3.6',
    package_dir={'': 'src'},
    keywords=['Game', 'Odd', 'Even', 'Odd Even', 'Cricket', 'Cricket Game', 'Game with Computer', "Siddharth Yadav"],
    classifiers=[
        "Development Status :: 1 - Planning",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
