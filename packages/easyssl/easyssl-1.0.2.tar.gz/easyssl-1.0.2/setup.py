from setuptools import setup

setup(
    name='easyssl',
    version='1.0.2',
    author='Blackwell',
    author_email='friendlyblackwell@example.com',
    url='https://github.com/friendlyblackwell/easyssl',
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',
    description='Easy OpenSSL Utilities',
    packages=['easyssl'],
    install_requires=[
        "PyYAML",
    ]
)
