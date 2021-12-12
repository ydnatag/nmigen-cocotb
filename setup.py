from setuptools import setup, find_packages

setup(
    name='amaranth-cocotb',
    author='Andres Demski',
    packages=find_packages(),
    setup_requires=['cocotb'],
    install_requires=[
        'cocotb-test',
        'amaranth @ git+https://github.com/amaranth-lang/amaranth.git#egg=amaranth',
        'amaranth-yosys'
    ]
)
