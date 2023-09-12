from setuptools import setup, find_packages
from easyass.__version__ import __version_str__

with open(r'README.md', 'r', encoding='utf-8') as fp:
    long_description = fp.read()

setup(
    name='easyass',
    version=__version_str__,
    keywords=['ass', 'subtitle'],
    description='An ass subtitle parsing library',
    license='MIT Licence',
    long_description=long_description,
    long_description_content_type="text/markdown",

    url='https://github.com/hihkm/easyAss',
    author='tikm',
    author_email='hkm@tikm.org',

    include_package_data=True,
    platforms='all',
    install_requires=[],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    packages=find_packages(),
    python_requires='>=3.7',
)
