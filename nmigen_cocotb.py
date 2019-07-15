import argparse
from nmigen import Fragment
from nmigen.back import verilog
from nmigen.cli import main_parser, main_runner
import subprocess
import tempfile
import os
import shutil

makefile_template = """\
VERILOG_SOURCES = {}
SIM = icarus
TOPLEVEL = {}
MODULE = {}
"""

makefile_includes = """
COCOTB = $(shell cocotb-config --makefiles)
include $(COCOTB)/Makefile.inc
include $(COCOTB)/Makefile.sim
"""

makefile_waveforms = """
COMPILE_ARGS += -s waveform_module
"""

verilog_waveforms = """
module waveform_module;
   initial begin
      $dumpfile ("{}");
      $dumpvars (0, {});
      #1;
   end
endmodule
"""

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
        help="write execution trace to VCD-FILE")
    return parser

def cocotb_runner(parser, args, design, platform=None, name="top", ports=()):
    if args.action == "cocotb":
        fragment = Fragment.get(design, platform)
        output = verilog.convert(fragment, name=name, ports=ports)
        with tempfile.TemporaryDirectory() as d:
            verilog_file = d + '/nmigen_output.v' 
            with open(verilog_file, 'w') as f:
                f.write('`timescale 1ns/1ps\n')
                f.write(output)
                if args.vcd_file:
                    f.write(verilog_waveforms.format(args.vcd_file, name))
            generate_makefile(verilog_file, name, args.module, args.vcd_file)
            subprocess.run('make', shell=True)
            if args.clean:
                os.remove('Makefile')
                shutil.rmtree('build')
                shutil.rmtree('sim_build')
                shutil.rmtree('__pycache__')
     

def generate_makefile(verilog, top, module, waveform=False):
    makefile = makefile_template.format(verilog, top, module)
    with open('Makefile', 'w') as f:
        f.write(makefile)
        if waveform:
            f.write(makefile_waveforms)
        f.write(makefile_includes)

def main(*args, **kwargs):
    parser = cocotb_parser()
    parsed_args = parser.parse_args()
    main_runner(parser, parsed_args, *args, **kwargs)
    cocotb_runner(parser, parsed_args, *args, **kwargs)
