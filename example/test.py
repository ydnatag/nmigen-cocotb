from amaranth_cocotb import run, get_current_module
from toplevel import design, ports

import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def just_a_timer(dut):
    await Timer(10, 'ns')


def test_module():
    run(design, get_current_module(), ports=ports, vcd_file='output.vcd')


if __name__ == '__main__':
    test_module()
