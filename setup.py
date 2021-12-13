from setuptools import setup, find_packages

setup(
    name="nmigen_cocotb",
    version="0.1",
    author='Andres Demski',
    py_modules=['nmigen_cocotb'],
    setup_requires=['cocotb'],
    install_requires=['cocotb-test @ git+https://github.com/themperek/cocotb-test.git#egg=cocotb-test',
                      'amaranth @ git+https://github.com/amaranth-lang/amaranth@24c4da2b2f626b9999219fe3644535ad39e044e9'],
)
