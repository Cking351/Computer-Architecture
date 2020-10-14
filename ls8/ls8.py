import sys
from cpu import *

if len(sys.argv) != 2:
    raise TypeError('Enter a filename')

cpu = CPU()

cpu.load()
cpu.run()
