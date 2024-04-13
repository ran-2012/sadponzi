
from ast import arg
import json
import logging
# import resource
import sys

print(sys.executable)

import os
import timeout_decorator
import traceback
import argparse

# from teether.xexploit import combined_exploit
from teether.exploit import combined_exploit
from teether.project import Project
import teether.ponziSchemes as ponziSchemes

logging.basicConfig(level=logging.ERROR)




def hex_encode(d):
    return {k: v.hex() if isinstance(v, bytes) else v for k, v in d.items()}


def main(code_path, target_addr, shellcode_addr, amount, savefile=None, initial_storage_file=None, initial_balance=None,
         flags=None, looplimit=3, output_path=None):


    # read hexdata and generate CFG
    print("code_path: "  + code_path)
    with open(code_path) as infile:
        inbuffer = infile.read().rstrip()
    code = bytes.fromhex(inbuffer)
    p = Project(code)

    amount_check = '+'
    amount = amount.strip()
    if amount[0] in ('=', '+', '-'):
        amount_check = amount[0]
        amount = amount[1:]
    amount = int(amount)

    initial_storage = dict()
    if initial_storage_file:
        with open(initial_storage_file, 'rb') as f:
            initial_storage = {int(k, 16): int(v, 16) for k, v in json.load(f).items()}

    flags = flags or {'CALL', 'CALLCODE', 'DELEGATECALL', 'SELFDESTRUCT'}

    result = combined_exploit(p, int(target_addr, 16), int(shellcode_addr, 16), amount, amount_check,
                              initial_storage, initial_balance, flags=flags, looplimit=looplimit)
    if result:
        report = f"Found: {ponziSchemes.SchemeDict[result[1]]}\n {code_path} \n Reward Expr:\n{result[0]}"
    else:
        report = f"Passed: Non-Ponzi\n {code_path}"
    
    print(report)
    if output_path != None:
        with open(output_path, "w") as f:
            f.write(report)


if __name__ == '__main__':
    # limit memory to 32GB
    # mem_limit = 32 * 1024 * 1024 * 1024
    # try:
    #     rsrc = resource.RLIMIT_VMEM
    # except:
    #     rsrc = resource.RLIMIT_AS
    # resource.setrlimit(rsrc, (mem_limit, mem_limit))

    config = {
        'target-address'   : "0x1234",
        'shellcode-address': "0x1000",
        'target_amount'    :"+1000",
        'savefile'         :None,
        'initial-storage'  :None,
        'initial-balance'  :None,
        'flags'            :None
    }

    parser = argparse.ArgumentParser(description='Usage')
    parser.add_argument('-i', '--input', required=True, type=str, help='runtime code of the smart contract')
    parser.add_argument('-o', '--output', required=False, type=str, help='report output', default = None)
    args = parser.parse_args()

    code = args.input
    print("[+] ============= Processing {} ===================".format(code))
    main(code, config['target-address'], config['shellcode-address'], config['target_amount'],
            config['savefile'], config['initial-storage'], config['initial-balance'], config['flags'], 10, args.output)

