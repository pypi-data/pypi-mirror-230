"""
The build/compilations setup
>> pip install -r requirements.txt
>> python setup.py install
"""
import logging
import pkg_resources
import setuptools

with open("requirements.txt") as f:
    required = f.read().splitlines()

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='iftc',
    version='1.0.7',
    url='https://gitlab.ftech.ai/nlp/research/ift-correction',
    author='namph',
    author_email='namph@ftech.ai',
    license='MIT',
    description='Spelling Correction for Vietnamese Informal Text',
    include_package_data=True,
    packages=["iftc", "iftc.spell_checker"],
    install_requires=required,
    python_requires='>=3.4',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: Vietnamese",
        "Operating System :: OS Independent",
        'Programming Language :: Python :: 3',
    ],
)
