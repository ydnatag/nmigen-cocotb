from nmigen import *
from nmigen_cocotb import main

m = Module()
a = Signal()
b = Signal()
c = Signal()
m.d.comb += b.eq(a)
m.d.sync += c.eq(a)
main(m, ports=[a, b, c], name='toplevel')
