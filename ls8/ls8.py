#!/usr/bin/env python3

"""Main."""

import sys
from cpu import *

if len(sys.argv) != 2:
    print("Incorrect Usage..")
    sys.exit(1)


cpu = CPU()
cpu.load(sys.argv[1])
cpu.run()

# cpu = CPU()
#
# cpu.load()
# cpu.run()
