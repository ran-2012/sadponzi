from z3 import *
import sys
import copy
import sha3
from collections import namedtuple

sys.path.append("/home/toor/SADPonzi/teether")
from teether.new_exploit import get_storage_expr_base1, is_caller, debug_hash_map, get_storage_expr_base
CALLER = 0
SYMVAR = 1
DSA    = 2
MAP    = 3


debug_hash_map()

stateResult = namedtuple('stateResult', 'sha_constraints')(dict())

# caller
CALLER_0 = BitVec('CALLER_0', 256)
assert is_caller(Extract(159, 0, CALLER_0))
assert is_caller(Extract(255, 96, 79228162514264337593543950336*CALLER_0))
assert is_caller(Extract(255, 96, CALLER_0*79228162514264337593543950336))

base  = z3.Array('STORAGE_0', z3.BitVecSort(256), z3.BitVecSort(256))
storage = copy.deepcopy(base)

# symvar
Store(storage, 1, CALLER_0)
assert get_storage_expr_base1(stateResult, Extract(159, 0, storage[1])) == (SYMVAR, 1, None)
tmp = Extract(255, 96, 79228162514264337593543950336*storage[1])
assert get_storage_expr_base1(stateResult, simplify(Extract(159, 0, tmp))) == (SYMVAR, 1, None)

tmp = Extract(159, 0, storage[1])
assert get_storage_expr_base1(stateResult, simplify(Extract(159, 0, tmp))) == (SYMVAR, 1, None)

# DSA1:storage[0x0000...001]
one_hash = int(sha3.keccak_256((0).to_bytes(length=32, byteorder='big')).hexdigest(), 16) # 18569430475105882587588266137607568536673111973893317399460219858819262702947

Store(storage, one_hash + 2*1 + 1, CALLER_0)
tmp = storage[one_hash + 2*1 + 1]
assert get_storage_expr_base1(stateResult, simplify(Extract(159, 0, tmp))) == (DSA, 0, 0)


# DSA3:storage[0x0000...000 + 2*storage[1]+1]
Store(storage, 0, 0)
Store(storage, one_hash + 2* + storage[0], CALLER_0)
tmp = storage[one_hash + 2*storage[0] + 1]
# print('main tmp=', tmp)
assert get_storage_expr_base1(stateResult, Extract(159, 0, tmp))[:2] == (DSA, 0)


# mapping: storage[sha3_];sha3 = concat(0, storage)
SHA3_3e = BitVec('SHA3_3e', 256)
tmp = Concat(BitVecVal(0, 256), Extract(159, 0, CALLER_0), BitVecVal(3, 256))
stateResult.sha_constraints[SHA3_3e] = tmp
Store(storage, 0, 0)
Store(storage, SHA3_3e, CALLER_0)
tmp = storage[SHA3_3e]
print( get_storage_expr_base1(stateResult, tmp) )
