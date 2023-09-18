from setuptools import setup

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(

    name='kotikikruto2',
    version='0.1.6',
    packages=['kotikikruto2'],
    install_requires=[
           'click',
       ],
    long_description=long_description,
    long_description_content_type = 'text/markdown'

)