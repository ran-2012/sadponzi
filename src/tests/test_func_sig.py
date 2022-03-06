import sys
sys.path.append("/home/toor/SADPonzi/teether")

# from teether.new_exploit import get_storage_expr_base1, is_caller, debug_hash_map, get_storage_expr_base

# from teether.exploit import combined_exploit
from teether.project import Project



code_path = '../../dataset/rq1/ponzi/1bb6123913d0b48948de38c3b75fd3eb3b4fe7e3.contract.bin'
with open(code_path) as infile:
    inbuffer = infile.read().rstrip()
code = bytes.fromhex(inbuffer)
p = Project(code)
for key, val in p.func_entries.items():
    print(key, '  :  ', val)