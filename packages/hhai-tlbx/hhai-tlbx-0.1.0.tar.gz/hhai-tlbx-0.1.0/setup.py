from setuptools import setup, find_packages
from os.path import abspath, join, dirname


# read the contents of your README file
this_directory = abspath(dirname(__file__))
with open(join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='hhai-tlbx',
    version='0.1.0',
    description='AI toolbox for Hon Hai research institution. Although, the primary utility only provide program configuration and data path preparation, more features will come out later',
    author='JosefHuang',
    author_email='a3285556aa@gmail.com',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
    url='https://github.com/HuangChiEn/hhai-tlbx',
    packages=['hhai_tlbx', 'hhai_tlbx/config_utils', 'hhai_tlbx/config_utils/utils', 'hhai_tlbx/data_utils'],
    keywords=["configuration", "commendline argument", "argument"],
    python_requires='>=3.6',
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
	    'Programming Language :: Python :: 3.9'
    ]
)