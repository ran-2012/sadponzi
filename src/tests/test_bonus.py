from z3 import *
import sys

sys.path.append("/home/toor/SADPonzi/teether")

from teether.exploit import prase_ast

STORAGE_10 = z3.Array('STORAGE_10', z3.BitVecSort(256), z3.BitVecSort(256))
CALLER_10 = BitVec("CALLER_10", 160)
expr = 150*UDiv(Store(STORAGE_10, 0, 1 + STORAGE_10[0])[18569430475105882587588266137607568536673111973893317399460219858819262702948 + 2* Store(STORAGE_10, 0, 1 + STORAGE_10[0])[1] ],  100)

a = prase_ast(expr)
print(a, simplify(a))
print(simplify(a).as_long()/1e20)