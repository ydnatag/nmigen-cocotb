from nmigen import *
from nmigen_cocotb import main

design = Module()
a = Signal()
b = Signal()
c = Signal()
ports = [a, b, c]

design.d.comb += b.eq(a)
design.d.sync += c.eq(a)

if __name__ == '__main__':
    main(design, ports=ports, name='toplevel')
