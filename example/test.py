import cocotb
from cocotb.triggers import Timer

@cocotb.test()
def nmigen_test(dut):
    yield Timer(10, 'ns')
