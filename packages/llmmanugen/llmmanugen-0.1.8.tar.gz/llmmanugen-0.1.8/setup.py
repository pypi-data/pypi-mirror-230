# run tests: python -m unittest discover -s tests -p 'test*.py'
# create dist: python setup.py sdist bdist_wheel
# publish to pypi: python -m twine upload dist/*

from setuptools import setup, find_packages

setup(
    name='llmmanugen',
    version='0.1.8',
    packages=find_packages(),
    author='Marko T. Manninen',
    author_email='elonmedia@gmail.com',
    description='A Python package for manuscript management, designed to handle hierarchical structures of sections and subsections.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/markomanninen/llmmanugen',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
