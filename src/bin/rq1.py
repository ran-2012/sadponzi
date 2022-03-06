#!/usr/bin/env python3
import json
import logging
import resource
import sys
import os
import timeout_decorator

sys.path.append("/home/toor/SADPonzi/teether")

from teether.exploit import combined_exploit
from teether.project import Project
import teether.ponziSchemes as ponziSchemes


logging.basicConfig(level=logging.ERROR)


def hex_encode(d):
    return {k: v.hex() if isinstance(v, bytes) else v for k, v in d.items()}



def main(code_path, target_addr, shellcode_addr, amount, savefile=None, initial_storage_file=None, initial_balance=None,
         flags=None):
    success = 0
    # read hexdata and generate CFG
    savefilebase = savefile or code_path
    if code_path.endswith('.json'):
        with open(code_path, 'rb') as f:
            jd = json.load(f)
        p = Project.from_json(jd)
    else:
        with open(code_path) as infile:
            inbuffer = infile.read().rstrip()
        code = bytes.fromhex(inbuffer)
        p = Project(code)
        with open('%s.project.json' % savefilebase, 'w') as f:
            json.dump(p.to_json(), f)

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
                              initial_storage, initial_balance, flags=flags)
    return result

    '''
    # report
    if result:

        call, r, model = result

        print(model)

        with open('%s.exploit.json' % savefilebase, 'w') as f:
            json.dump({'paths': [{'index': i, 'path': [ins for ins in res.state.trace if
                                                       ins in p.cfg.bb_addrs or ins == res.state.trace[-1]]} for
                                 i, res in enumerate(r.results)],
                       'calls': [{'index': i, 'call': hex_encode(c)} for i, c in enumerate(call)]}, f)

        for i, res in enumerate(r.results):
            print('%d: %s' % (
                i, '->'.join('%x' % i for i in res.state.trace if i in p.cfg.bb_addrs or i == res.state.trace[-1])))
        print(call)
        print
        for c in call:
            if c['caller'] == c['origin']:
                print('eth.sendTransaction({from:"0x%040x", data:"0x%s", to:"0x4000000000000000000000000000000000000000"%s, gasPrice:0})' % (
                    c['origin'], c.get('payload', b'').hex(),
                    ", value:%d" % c['value'] if c.get('value', 0) else ''))
            else:
                print('eth.sendTransaction({from:"0x%040x", data:"0x%s", to:"0x%040x"%s, gasPrice:0})' % (
                    c['origin'], c.get('payload', b'').hex(), c['caller'],
                    ", value:%d" % c['value'] if c.get('value', 0) else ''))
            if not c.get('payload', b'').hex():
                print("============ Invoke payout()!!! ==================")

        return True
    return False
    '''



if __name__ == '__main__':
    # limit memory to 8GB
    mem_limit = 8 * 1024 * 1024 * 1024
    try:
        rsrc = resource.RLIMIT_VMEM
    except:
        rsrc = resource.RLIMIT_AS
    resource.setrlimit(rsrc, (mem_limit, mem_limit))

    # fields = ['path_to_dataset', 'target-address', 'shellcode-address', 'target_amount', 'savefile', 'initial-storage',
    #           'initial-balance']
    # config = {f: None for f in fields}

    # config['flags'] = set()

    # field_iter = iter(fields)
    # for arg in sys.argv[1:]:
    #     if arg.startswith('--'):
    #         config['flags'].add(arg[2:].upper())
    #     else:
    #         field = next(field_iter)
    #         config[field] = arg

    # if config['target_amount'] is None:
    #     print('Usage: %s [flags] <path_to_dataset> <target-address> <shellcode-address> <target_amount> [savefile] [initial-storage file] [initial-balance]' % \
    #           sys.argv[0], file=sys.stderr)
    #     exit(-1)

    config = {
        'target-address'   : "0x1234",
        'shellcode-address': "0x1000",
        'target_amount'    :"+1000",
        'savefile'         :None,
        'initial-storage'  :None,
        'initial-balance'  :None,
        'flags'            :None
    }
    if len(sys.argv) != 2:
        print('Usage: %s [flags] <path_to_dataset>' % \
                sys.argv[0], file=sys.stderr)
        exit(0)

    dataset_base_path = sys.argv[1]
    succ_cnt = 0
    case_cnt = 0
    fails = list()
    for code in os.listdir(dataset_base_path):
        # if case_cnt > 50:
        #     break
        if not code.endswith(".contract.bin"):
            continue
        case_cnt += 1
        # if code in ["1bb6123913d0b48948de38c3b75fd3eb3b4fe7e3.contract.bin", "e8b55deaced913c5c6890331d2926ea0fcbe59ac.contract.bin", 
        #               "1ce7986760ade2bf0f322f5ef39ce0de3bd0c82b.contract.bin"
        #             "723dff0e27cc38b80556f5e05dfdbdcb721654d7", "feeb8a968f0d7fd58e29fbfc525051f50ee2fedc.contract.bin"]: 
        #     #ethAdv, Fibonzi, PonziICO, DFS, Etheramid2
            
        #     continue
        # if "1bb6123913d0b48948de38c3b75fd3eb3b4fe7e3" in code:
        #     print(code)
        #     continue

        print(f" ==================== processing {code.split('.contract.bin')[0]}=========================")
        try:
            success = main(dataset_base_path + '/' + code, config['target-address'], config['shellcode-address'], config['target_amount'],
                config['savefile'], config['initial-storage'], config['initial-balance'], config['flags'])
            print(success)
            if success:
                print(f"Found: {ponziSchemes.SchemeDict[success]}")
                succ_cnt += 1
            else:
                print(f"Lost: {ponziSchemes.SchemeDict[ponziSchemes.NONPONZI]}")
                fails.append(code)
        except Exception as e:
            fails.append(code)
            print("time out", f"Lost: {ponziSchemes.SchemeDict[ponziSchemes.NONPONZI]}")
            print(e)
            continue
        #['rubixu.contract.bin', 'testTree.contract.bin', 'testPonziICO.contract.bin']

    print(f" ##### {succ_cnt}/{case_cnt} ####")
    print(fails)
 ##### 42/51 ####
# FAIL:: e8b55deaced913c5c6890331d2926ea0fcbe59ac, Fibonzi                  ------ chain + mapping
#        '1bb6123913d0b48948de38c3b75fd3eb3b4fe7e3.contract.bin', EtherAds ----chain



    