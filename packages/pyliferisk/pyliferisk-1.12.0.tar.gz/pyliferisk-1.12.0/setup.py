from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='pyliferisk',
    version='1.12.0',
    packages=find_packages(),
    install_requires=[
        # Lista de dependencias de tu paquete
    ],
    author='Francisco Garate',
    author_email='fgaratesantiago@gmail.com',
    description='A python library for life actuarial calculations, simple, powerful and easy-to-use',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/franciscogarate/pyliferisk',
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Intended Audience :: Financial and Insurance Industry"
    ],
)
