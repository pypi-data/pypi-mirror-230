from setuptools import setup
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='instacreatorapi',
    version='0.0.2',
    description='A Python module based on api to create Instagram Accounts',
    author= 'god_x_gamer',
    url = 'https://github.com/godxgamer/Igcreatorapi',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    keywords=['instagram','instacreatorapi','instagram account creator' 'account creator', 'instagram api','instagrapi'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    py_modules=['instacreatorapi'],
    package_dir={'':'src'},
    install_requires = [
        'requests',
    ]
)
