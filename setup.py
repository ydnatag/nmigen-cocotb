from setuptools import setup, find_packages

setup(
    name="nmigen_cocotb",
    version="0.1",
    author='Andres Demski',
    py_modules=['nmigen_cocotb'],
    setup_requires=['cocotb'],
    install_requires=['cocotb-test @ git+https://github.com/themperek/cocotb-test.git#egg=cocotb-test',
                      'nmigen @ git+https://github.com/m-labs/nmigen.git#egg=nmigen'],
    #dependency_links=['git+https://github.com/m-labs/nmigen.git#egg=nmigen',
                      #'git+https://github.com/themperek/cocotb-test.git#egg=cocotb-test']
)
