import argparse
from cocotb_test.run import run as cocotb_run
from cocotb_test.simulator import Icarus
from nmigen import Fragment
from nmigen.back import verilog
from nmigen.cli import main_parser, main_runner
import subprocess
import tempfile
import os
import shutil
import inspect


compile_args_waveforms = ['-s', 'cocotb_waveform_module']

verilog_waveforms = """

module cocotb_waveform_module;
   initial begin
      $dumpfile ("{}");
      $dumpvars (0, {});
      #1;
   end
endmodule
"""

def get_current_module():
    module = inspect.getsourcefile(inspect.stack()[1][0])
    return inspect.getmodulename(module)

def get_reset_signal(dut, cd):
    return getattr(dut, cd + '_rst')

def get_clock_signal(dut, cd):
    return getattr(dut, cd + '_clk')

def cocotb_parser():
    parser = main_parser()
    p_action = parser._subparsers._actions[1]
    p_cocotb = p_action.add_parser("cocotb",
        help="generate Verilog from the design and call COCOTB")
    p_cocotb.add_argument("-m", "--module",
        metavar="MODULE", type=str, required=True,
        help="cocotb test module")
    p_cocotb.add_argument("-v", "--vcd-file",
        metavar="VCD-FILE", type=str, default=None,
        help="write execution trace to VCD-FILE")
    p_cocotb.add_argument("--clean",
        action="store_true", default=False,
        help="clean generated files after simulation")
    return parser

def generate_verilog(verilog_file, design, platform, name='top', ports=(), vcd_file=None):
    fragment = Fragment.get(design, platform)
    print(name, ports)
    output = verilog.convert(fragment, name=name, ports=ports)
    with open(verilog_file, 'w') as f:
        f.write('`timescale 1ns/1ps\n')
        f.write(output)
        if vcd_file:
            vcd_file = os.path.abspath(vcd_file)
            f.write(verilog_waveforms.format(vcd_file, name))

def run(design, module, platform=None, ports=(), name='top', verilog_sources=None, vcd_file=None):
    with tempfile.TemporaryDirectory() as d:
        verilog_file = d + '/nmigen_output.v'
        sources = [verilog_file]
        if verilog_sources:
            sources.extend(verilog_sources)
        generate_verilog(verilog_file, design, platform, name, ports, vcd_file)
        os.environ['SIM'] = 'icarus'
        cocotb_run(simulator=Icarus,
                   toplevel=name,
                   module=module,
                   verilog_sources=sources,
                   compile_args=compile_args_waveforms if vcd_file else [])

def cocotb_runner(parser, args, design, platform=None, name="top", ports=()):
    if args.action == "cocotb":
        run(design=design,
            platform=platform,
            module=args.module,
            ports=ports,
            name=name,
            vcd_file=args.vcd_file)
        if args.clean:
            shutil.rmtree('sim_build')

def main(*args, **kwargs):
    parser = cocotb_parser()
    parsed_args = parser.parse_args()
    main_runner(parser, parsed_args, *args, **kwargs)
    cocotb_runner(parser, parsed_args, *args, **kwargs)
