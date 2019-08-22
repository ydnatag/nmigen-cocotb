from nmigen_cocotb import run
from toplevel import design, ports

import cocotb
from cocotb.triggers import Timer

@cocotb.test()
def just_a_timer(dut):
    yield Timer(10, 'ns')

def test_module():
    run(design, 'test', ports=ports, vcd_file='output.vcd')

if __name__ == '__main__':
    test_module()
    
    
