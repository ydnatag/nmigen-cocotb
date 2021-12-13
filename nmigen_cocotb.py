import argparse
from cocotb_test.simulator import Icarus
from amaranth import Fragment
from amaranth.back import verilog
from amaranth.cli import main_parser, main_runner
import subprocess
import tempfile
import os
import shutil
import inspect

class Icarus_g2005(Icarus):
    def compile_command(self):

        cmd_compile = (
            ["iverilog", "-o", self.sim_file, "-D", "COCOTB_SIM=1", "-s", self.toplevel, "-g2005"]
            + self.get_define_commands(self.defines)
            + self.get_include_commands(self.includes)
            + self.compile_args
            + self.verilog_sources
        )

        return cmd_compile

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

def copy_extra_files(extra_files, path):
    for f in extra_files:
        shutil.copy(f, path)

def dump_file(filename, content, d):
    file_path = d + '/' + filename
    if isinstance(content, bytes):
        content = content.decode('utf-8')
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            c = f.read()
        if c != content:
            raise ValueError("File {!r} already exists"
                             .format(filename))
    else:
        with open(file_path, 'w') as f:
            f.write(content)
    return file_path

def run(design, module, platform=None, ports=(), name='top', verilog_sources=None, extra_files=None, vcd_file=None, extra_args=None):
    with tempfile.TemporaryDirectory() as d:
        verilog_file = d + '/nmigen_output.v'
        generate_verilog(verilog_file, design, platform, name, ports, vcd_file)
        sources = [verilog_file]
        if verilog_sources:
            sources.extend(verilog_sources)
        if extra_files:
            copy_extra_files(extra_files, d)
        if platform:
            for filename, content in platform.extra_files.items():
                filepath = dump_file(filename, content, d)
                if filename.endswith('.v') or filename.endswith('.sv'):
                    sources.append(filepath)
        compile_args = []
        if vcd_file:
            compile_args += compile_args_waveforms
        if extra_args:
            compile_args += extra_args
        os.environ['SIM'] = 'icarus'
        simulator = Icarus_g2005(toplevel=name,
                                 module=module,
                                 verilog_sources=sources,
                                 compile_args=compile_args,
                                 sim_build=d)
        simulator.run()

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
